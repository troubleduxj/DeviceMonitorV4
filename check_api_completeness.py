"""
检查接口权限配置的完整性
对比数据库中的API配置与实际的后端路由
"""
import asyncio
import os
from pathlib import Path
from collections import defaultdict
import re
import asyncpg

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

async def get_db_apis():
    """获取数据库中的API配置"""
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        # 查询API端点
        rows = await conn.fetch("""
            SELECT 
                e.id, 
                e.api_name, 
                e.api_path, 
                e.http_method, 
                e.group_id,
                e.version,
                e.is_public,
                e.is_deprecated,
                e.status,
                g.group_name as group_name
            FROM t_sys_api_endpoints e
            LEFT JOIN t_sys_api_groups g ON e.group_id = g.id
            ORDER BY e.group_id, e.id
        """)
        return [dict(row) for row in rows]
    finally:
        await conn.close()

def scan_backend_routes():
    """扫描后端实际的路由定义"""
    routes = []
    app_dir = Path('app')
    
    if not app_dir.exists():
        print("❌ app目录不存在")
        return routes
    
    # 扫描所有Python文件
    for py_file in app_dir.rglob('*.py'):
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # 查找路由装饰器
            # @router.get("/path")
            # @router.post("/path")
            # @router.put("/path")
            # @router.delete("/path")
            patterns = [
                r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    method = match.group(1).upper()
                    path = match.group(2)
                    
                    # 获取函数名（用于参考）
                    func_pattern = r'@router\.' + match.group(1) + r'\(["\']' + re.escape(path) + r'["\'][^\n]*\n\s*async def (\w+)'
                    func_match = re.search(func_pattern, content)
                    func_name = func_match.group(1) if func_match else 'unknown'
                    
                    routes.append({
                        'file': str(py_file).replace('\\', '/'),
                        'method': method,
                        'path': path,
                        'function': func_name
                    })
        except Exception as e:
            # 忽略路径错误
            pass
    
    return routes

def normalize_path(path):
    """标准化路径，用于比较"""
    # 移除路径参数的具体名称，只保留占位符
    # /api/v2/users/{id} -> /api/v2/users/{id}
    # /api/v2/users/{user_id} -> /api/v2/users/{id}
    normalized = re.sub(r'\{[^}]+\}', '{id}', path)
    return normalized.strip('/')

async def analyze_completeness():
    """分析完整性"""
    print("=" * 80)
    print("🔍 接口权限完整性分析")
    print("=" * 80)
    
    # 1. 获取数据库中的API
    db_apis = await get_db_apis()
    
    print(f"\n📊 数据库中的API数量: {len(db_apis)}")
    
    # 按分组统计
    api_by_group = defaultdict(list)
    for api in db_apis:
        group_name = api.get('group_name') or '未分组'
        api_by_group[group_name].append(api)
    
    print("\n按分组统计:")
    for group_name, apis in sorted(api_by_group.items()):
        print(f"  - {group_name}: {len(apis)} 个")
    
    # 2. 扫描实际路由
    print("\n🔍 扫描后端路由...")
    backend_routes = scan_backend_routes()
    print(f"📊 扫描到的路由数量: {len(backend_routes)}")
    
    # 按模块分组
    routes_by_module = defaultdict(list)
    for route in backend_routes:
        # 从文件路径提取模块名
        file_path = route['file']
        if 'api' in file_path:
            parts = file_path.split(os.sep)
            if 'api' in parts:
                api_idx = parts.index('api')
                if api_idx + 1 < len(parts):
                    module = parts[api_idx + 1]
                    routes_by_module[module].append(route)
    
    print("\n按模块分组:")
    for module, routes in sorted(routes_by_module.items()):
        print(f"  - {module}: {len(routes)} 个路由")
    
    # 3. 对比分析
    print("\n" + "=" * 80)
    print("📋 对比分析")
    print("=" * 80)
    
    # 构建数据库API的索引
    db_api_index = {}
    for api in db_apis:
        path = api.get('api_path', '')
        method = api.get('http_method', '')
        key = f"{method}:{normalize_path(path)}"
        db_api_index[key] = api
    
    print(f"\n数据库中的API端点: {len(db_api_index)} 个")
    
    # 构建后端路由索引
    backend_route_index = {}
    for route in backend_routes:
        path = route['path']
        method = route['method']
        key = f"{method}:{normalize_path(path)}"
        backend_route_index[key] = route
    
    # 找出数据库中有但后端没有的
    print("\n❌ 数据库中配置但后端不存在的API:")
    db_only = []
    for key, api in db_api_index.items():
        if key not in backend_route_index:
            db_only.append(api)
            status_flag = "🚫" if api.get('is_deprecated') else "⚠️"
            print(f"  {status_flag} {api['http_method']} {api['api_path']} ({api['api_name']})")
    
    if not db_only:
        print("  ✅ 无")
    
    # 找出后端有但数据库没有的
    print("\n⚠️  后端存在但数据库未配置的API:")
    backend_only = []
    for key, route in backend_route_index.items():
        if key not in db_api_index:
            backend_only.append(route)
            print(f"  - {route['method']} {route['path']} (函数: {route['function']}, 文件: {route['file']})")
    
    if not backend_only:
        print("  ✅ 无")
    
    # 4. 统计摘要
    print("\n" + "=" * 80)
    print("📊 统计摘要")
    print("=" * 80)
    print(f"数据库API总数: {len(db_apis)}")
    print(f"后端路由总数: {len(backend_routes)}")
    print(f"匹配的API: {len(db_api_index) - len(db_only)}")
    print(f"数据库多余/废弃: {len(db_only)}")
    print(f"数据库缺失: {len(backend_only)}")
    
    coverage = ((len(db_api_index) - len(db_only)) / len(backend_routes) * 100) if backend_routes else 0
    print(f"\n覆盖率: {coverage:.1f}%")
    
    if backend_only:
        print("\n💡 建议:")
        print("以下API需要添加到数据库配置中:")
        
        # 按模块分组显示
        missing_by_module = defaultdict(list)
        for route in backend_only:
            file_path = route['file']
            if 'api' in file_path:
                parts = file_path.split(os.sep)
                if 'api' in parts:
                    api_idx = parts.index('api')
                    if api_idx + 1 < len(parts):
                        module = parts[api_idx + 1]
                        missing_by_module[module].append(route)
        
        for module, routes in sorted(missing_by_module.items()):
            print(f"\n  【{module}模块】")
            for route in routes:
                print(f"    {route['method']} {route['path']}")

if __name__ == '__main__':
    asyncio.run(analyze_completeness())
