"""
同步剩余重要API到数据库
"""
import asyncio
import asyncpg
from pathlib import Path
from collections import defaultdict
import re
from datetime import datetime

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

# 剩余重要模块的分类和描述
REMAINING_CATEGORIES = {
    '权限性能监控': '权限检查性能监控、缓存优化、性能分析',
    '元数据管理': '字段管理、模型管理、映射配置、数据同步',
    '权限配置': '权限端点配置、规则管理、版本控制',
    'TDengine管理': 'TDengine服务器管理、数据库查询、连接配置',
    '文档管理': 'API文档、Swagger、变更日志、版本管理',
    'AI异常检测': 'AI异常检测、异常记录、异常处理',
    'AI特征提取': 'AI特征提取、批量提取、特征类型',
    'AI趋势预测': 'AI趋势预测、批量预测、方法对比',
    '系统监控': '系统性能监控、健康检查、指标统计',
    '安全管理': '安全事件、威胁检测、IP统计',
    '批量操作': '批量操作、权限验证、模拟执行',
    '数据查询': '实时数据查询、统计查询、模型预览',
    '动态模型': '动态模型生成、缓存管理、字段信息',
    'Mock数据': 'Mock数据规则管理、开关控制',
    '健康检查': '系统健康检查、版本信息',
    'Swagger文档': 'Swagger文档生成、API文档',
}

# 路由前缀映射
PREFIX_MAP = {
    'app/api/monitoring.py': '/api/monitoring',
    'app/api/security.py': '/api/security',
    'app/api/tdengine.py': '/api/tdengine',
    'app/api/v2/metadata.py': '/api/v2/metadata',
    'app/api/v2/metadata_sync.py': '/api/v2/metadata',
    'app/api/v2/permission_config.py': '/api/v2/permission-config',
    'app/api/v2/docs.py': '/api/v2/docs',
    'app/api/v2/ai/anomaly_detection.py': '/api/v2/ai/anomaly',
    'app/api/v2/ai/feature_extraction.py': '/api/v2/ai/features',
    'app/api/v2/ai/trend_prediction.py': '/api/v2/ai/trend',
    'app/api/v2/batch_operations.py': '/api/v2/batch',
    'app/api/v2/data_query.py': '/api/v2/data',
    'app/api/v2/dynamic_models.py': '/api/v2/dynamic-models',
    'app/api/v2/mock_data.py': '/api/v2/mock',
    'app/api/v2/health.py': '/api/v2/health',
    'app/api/v2/system_health.py': '/api/v2/system',
    'app/controllers/permission_performance_controller.py': '/api/v2/permission/performance',
    'app/controllers/permission_performance_optimization_controller.py': '/api/v2/permission/optimization',
    'app/controllers/batch_operation_controller.py': '/api/v2/batch',
    'app/core/swagger_config.py': '',
}

def classify_api(file_path):
    """根据文件路径分类API"""
    file_lower = file_path.lower()
    
    if 'permission_performance' in file_lower:
        return '权限性能监控'
    elif 'metadata' in file_lower:
        return '元数据管理'
    elif 'permission_config' in file_lower:
        return '权限配置'
    elif 'tdengine' in file_lower:
        return 'TDengine管理'
    elif 'docs.py' in file_lower:
        return '文档管理'
    elif 'anomaly_detection' in file_lower:
        return 'AI异常检测'
    elif 'feature_extraction' in file_lower:
        return 'AI特征提取'
    elif 'trend_prediction' in file_lower:
        return 'AI趋势预测'
    elif 'monitoring.py' in file_lower:
        return '系统监控'
    elif 'security.py' in file_lower:
        return '安全管理'
    elif 'batch_operation' in file_lower:
        return '批量操作'
    elif 'data_query' in file_lower:
        return '数据查询'
    elif 'dynamic_model' in file_lower:
        return '动态模型'
    elif 'mock_data' in file_lower:
        return 'Mock数据'
    elif 'health.py' in file_lower:
        return '健康检查'
    elif 'swagger_config' in file_lower:
        return 'Swagger文档'
    
    return None

def scan_remaining_routes():
    """扫描剩余的重要路由"""
    routes = []
    
    # 重要文件列表
    important_files = [
        'app/api/monitoring.py',
        'app/api/security.py', 
        'app/api/tdengine.py',
        'app/api/v2/metadata.py',
        'app/api/v2/metadata_sync.py',
        'app/api/v2/permission_config.py',
        'app/api/v2/docs.py',
        'app/api/v2/ai/anomaly_detection.py',
        'app/api/v2/ai/feature_extraction.py',
        'app/api/v2/ai/trend_prediction.py',
        'app/api/v2/batch_operations.py',
        'app/api/v2/data_query.py',
        'app/api/v2/dynamic_models.py',
        'app/api/v2/mock_data.py',
        'app/api/v2/health.py',
        'app/api/v2/system_health.py',
        'app/controllers/permission_performance_controller.py',
        'app/controllers/permission_performance_optimization_controller.py',
        'app/controllers/batch_operation_controller.py',
        'app/core/swagger_config.py',
    ]
    
    for file_path in important_files:
        py_file = Path(file_path)
        if not py_file.exists():
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            
            for match in re.finditer(pattern, content):
                method = match.group(1).upper()
                path = match.group(2)
                file_str = str(py_file).replace('\\', '/')
                category = classify_api(file_str)
                
                if category:
                    routes.append({
                        'file': file_str,
                        'method': method,
                        'path': path,
                        'category': category
                    })
        except Exception as e:
            print(f"⚠️  读取文件 {py_file} 失败: {e}")
    
    return routes

def generate_api_name(method, path):
    """生成API名称"""
    method_names = {
        'GET': '获取',
        'POST': '创建',
        'PUT': '更新',
        'DELETE': '删除',
        'PATCH': '部分更新'
    }
    
    # 路径解析
    parts = [p for p in path.split('/') if p and not p.startswith('{')]
    if parts:
        resource = parts[-1].replace('-', ' ').replace('_', ' ')
        return f"{method_names.get(method, method)} {resource}"
    return f"{method} {path}"

async def sync_apis(dry_run=False):
    """同步API"""
    print("="*80)
    print("🚀 同步剩余重要API到数据库")
    print("="*80)
    
    if dry_run:
        print("\n🔍 预览模式 - 不会实际写入数据库\n")
    
    # 扫描路由
    print("\n📡 扫描剩余重要API...")
    routes = scan_remaining_routes()
    
    # 按分类整理
    by_category = defaultdict(list)
    for route in routes:
        by_category[route['category']].append(route)
    
    print(f"✅ 找到 {len(routes)} 个重要API\n")
    
    # 连接数据库
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取已存在的API
        existing = await conn.fetch("SELECT api_path, http_method FROM t_sys_api_endpoints")
        existing_set = {(row['api_path'], row['http_method']) for row in existing}
        
        total_created = 0
        total_skipped = 0
        
        # 按分类同步
        for category, description in REMAINING_CATEGORIES.items():
            if category not in by_category:
                continue
            
            print(f"\n{'='*80}")
            print(f"📦 {category}")
            print(f"{'='*80}")
            
            # 获取或创建分组
            group = await conn.fetchrow("""
                SELECT id FROM t_sys_api_groups WHERE group_name = $1
            """, category)
            
            if not group:
                if not dry_run:
                    # 生成group_code
                    group_code = category.replace(' ', '_').lower()
                    group = await conn.fetchrow("""
                        INSERT INTO t_sys_api_groups (group_code, group_name, description, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5)
                        RETURNING id
                    """, group_code, category, description, datetime.now(), datetime.now())
                    print(f"✅ 创建分组: {category} (ID: {group['id']})")
                else:
                    print(f"📝 将创建分组: {category}")
                    group = {'id': 0}
            else:
                print(f"✅ 使用现有分组: {category} (ID: {group['id']})")
            
            group_id = group['id']
            
            # 同步API
            routes_list = by_category[category]
            created = 0
            skipped = 0
            
            for route in routes_list:
                prefix = PREFIX_MAP.get(route['file'], '')
                full_path = prefix + route['path'] if prefix else route['path']
                
                # 检查是否已存在
                if (full_path, route['method']) in existing_set:
                    skipped += 1
                    continue
                
                # 生成API信息
                api_name = generate_api_name(route['method'], full_path)
                api_code = f"{route['method'].lower()}_{full_path.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_').strip('_')}"
                
                if dry_run:
                    print(f"  📝 {route['method']:6} {full_path}")
                    print(f"      名称: {api_name}")
                    created += 1
                else:
                    try:
                        await conn.execute("""
                            INSERT INTO t_sys_api_endpoints (
                                api_code, api_name, api_path, http_method,
                                description, version, group_id, is_public,
                                status, created_at, updated_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        """,
                            api_code,
                            api_name,
                            full_path,
                            route['method'],
                            f"来源: {route['file']}",
                            'v2',
                            group_id,
                            False,
                            'active',
                            datetime.now(),
                            datetime.now()
                        )
                        print(f"  ✅ {route['method']:6} {full_path} - {api_name}")
                        created += 1
                    except Exception as e:
                        print(f"  ❌ 失败: {route['method']} {full_path} - {str(e)[:100]}")
            
            print(f"\n📊 {category} 统计:")
            print(f"  - 新创建: {created}")
            print(f"  - 已跳过: {skipped}")
            
            total_created += created
            total_skipped += skipped
        
        print(f"\n{'='*80}")
        print(f"📊 总计")
        print(f"{'='*80}")
        print(f"新创建: {total_created}")
        print(f"已跳过: {total_skipped}")
        print(f"{'='*80}")
        
    finally:
        await conn.close()

async def main():
    """主函数"""
    import sys
    
    # 检查参数
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
    
    if dry_run:
        await sync_apis(dry_run=True)
    else:
        print("\n⚠️  即将同步剩余重要API到数据库")
        print("如果只想预览，请使用: python sync_remaining_priority_apis.py --dry-run")
        confirm = input("\n确认继续? (yes/no): ").strip().lower()
        if confirm == 'yes':
            await sync_apis(dry_run=False)
        else:
            print("❌ 已取消")

if __name__ == '__main__':
    asyncio.run(main())
