"""
预览优先级1（核心业务）的API同步
"""
import asyncio
import asyncpg
from pathlib import Path
from collections import defaultdict
import re

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

# 优先级1的分类
PRIORITY1_CATEGORIES = [
    '认证管理',
    '用户管理',
    '角色管理',
    '菜单管理',
    '部门管理',
]

# 简化的分类规则
def classify_api(file_path, path):
    file_lower = file_path.lower()
    path_lower = path.lower()
    
    if 'auth' in file_lower or 'auth' in path_lower or 'login' in path_lower or 'password' in path_lower:
        return '认证管理'
    elif 'user' in file_lower or 'user' in path_lower:
        return '用户管理'
    elif 'role' in file_lower or 'role' in path_lower:
        return '角色管理'
    elif 'menu' in file_lower or 'menu' in path_lower:
        return '菜单管理'
    elif 'department' in file_lower or 'dept' in file_lower:
        return '部门管理'
    return None

def scan_routes():
    routes = []
    app_dir = Path('app')
    
    for py_file in app_dir.rglob('*.py'):
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            for match in re.finditer(pattern, content):
                method = match.group(1).upper()
                path = match.group(2)
                file_str = str(py_file).replace('\\', '/')
                category = classify_api(file_str, path)
                if category in PRIORITY1_CATEGORIES:
                    routes.append({
                        'file': file_str,
                        'method': method,
                        'path': path,
                        'category': category
                    })
        except:
            pass
    return routes

# 路由前缀映射
PREFIX_MAP = {
    'app/api/v2/users.py': '/api/v2/users',
    'app/api/v2/roles.py': '/api/v2/roles',
    'app/api/v2/menus.py': '/api/v2/menus',
    'app/api/v2/departments.py': '/api/v2/departments',
    'app/api/v2/auth.py': '/api/v2/auth',
    'app/api/v2/base.py': '/api/v2/base',
    'app/controllers/user_management_controller.py': '/api/v2/users',
    'app/controllers/role_management_controller.py': '/api/v2/roles',
    'app/controllers/menu_permission_controller.py': '/api/v2/menus',
    'app/controllers/department_permission_controller.py': '/api/v2/departments',
}

async def main():
    print("="*80)
    print("🔍 优先级1（核心业务）API预览")
    print("="*80)
    
    # 扫描路由
    print("\n📡 扫描核心业务API...")
    routes = scan_routes()
    
    # 按分类整理
    by_category = defaultdict(list)
    for route in routes:
        by_category[route['category']].append(route)
    
    print(f"✅ 找到 {len(routes)} 个核心业务API\n")
    
    # 连接数据库
    conn = await asyncpg.connect(**DB_CONFIG)
    existing = await conn.fetch("SELECT api_path, http_method FROM t_sys_api_endpoints")
    existing_set = {(row['api_path'], row['http_method']) for row in existing}
    await conn.close()
    
    # 显示每个分类的详情
    for category in PRIORITY1_CATEGORIES:
        if category not in by_category:
            continue
        
        print(f"\n## {category}")
        print(f"{'='*80}")
        
        routes_list = by_category[category]
        new_apis = []
        existing_apis = []
        
        for route in routes_list:
            prefix = PREFIX_MAP.get(route['file'], '')
            full_path = prefix + route['path'] if prefix else route['path']
            
            if (full_path, route['method']) in existing_set:
                existing_apis.append((route['method'], full_path))
            else:
                new_apis.append((route['method'], full_path, route['file']))
        
        print(f"总数: {len(routes_list)}")
        print(f"已存在: {len(existing_apis)}")
        print(f"需新增: {len(new_apis)}")
        
        if new_apis:
            print(f"\n### 需要新增的API:")
            for method, path, file in new_apis:
                print(f"  {method:6} {path}")
                print(f"         来源: {file}")
    
    # 总计
    total = len(routes)
    total_new = sum(1 for route in routes 
                   if (PREFIX_MAP.get(route['file'], '') + route['path'], route['method']) not in existing_set)
    total_existing = total - total_new
    
    print(f"\n{'='*80}")
    print(f"📊 总计")
    print(f"{'='*80}")
    print(f"总API数: {total}")
    print(f"已存在: {total_existing}")
    print(f"需新增: {total_new}")
    print(f"{'='*80}")

if __name__ == '__main__':
    asyncio.run(main())
