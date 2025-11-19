"""
同步优先级2（设备核心）API到数据库
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

# 优先级2的分类和描述
PRIORITY2_CATEGORIES = {
    '设备管理': '设备增删改查、类型管理、状态监控',
    '设备维护管理': '设备维护记录、维修记录、计划管理',
    '设备工艺管理': '工艺管理、执行记录、模板管理',
    '设备字段配置': '设备字段配置、缓存管理',
    '报警管理': '报警记录、处理、统计',
}

# 路由前缀映射
PREFIX_MAP = {
    'app/api/v1/devices/devices.py': '/api/v1/devices',
    'app/api/v1/devices/device_data.py': '/api/v1/devices',
    'app/api/v1/devices/device_types.py': '/api/v1/devices',
    'app/api/v1/devices/universal_data.py': '/api/v1/devices',
    'app/api/v1/devices/weld_record.py': '/api/v1/devices',
    'app/api/v2/devices.py': '/api/v2/devices',
    'app/api/v2/device_maintenance.py': '/api/v2/device/maintenance',
    'app/api/v2/device_process.py': '/api/v2/device',
    'app/api/v2/device_field_config.py': '/api/v2/device',
    'app/api/v2/device_repair_records.py': '/api/v2/device/maintenance',
    'app/api/v2/device_repair_records_simple.py': '/api/v2/device/maintenance',
    'app/api/v2/alarms.py': '/api/v2/alarms',
}

def classify_api(file_path, path):
    """分类API"""
    file_lower = file_path.lower()
    path_lower = path.lower()
    
    if 'alarm' in file_lower or 'alarm' in path_lower:
        return '报警管理'
    elif 'maintenance' in file_lower or 'repair' in file_lower or 'maintenance' in path_lower or 'repair' in path_lower:
        return '设备维护管理'
    elif 'process' in file_lower or 'process' in path_lower:
        return '设备工艺管理'
    elif 'field' in file_lower and 'device' in file_lower:
        return '设备字段配置'
    elif 'device' in file_lower or 'device' in path_lower:
        return '设备管理'
    return None

def scan_routes():
    """扫描路由"""
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
                if category in PRIORITY2_CATEGORIES:
                    routes.append({
                        'file': file_str,
                        'method': method,
                        'path': path,
                        'category': category
                    })
        except:
            pass
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
    print("🚀 同步优先级2（设备核心）API到数据库")
    print("="*80)
    
    if dry_run:
        print("\n🔍 预览模式 - 不会实际写入数据库\n")
    
    # 扫描路由
    print("\n📡 扫描设备核心API...")
    routes = scan_routes()
    
    # 按分类整理
    by_category = defaultdict(list)
    for route in routes:
        by_category[route['category']].append(route)
    
    print(f"✅ 找到 {len(routes)} 个设备核心API\n")
    
    # 连接数据库
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取已存在的API
        existing = await conn.fetch("SELECT api_path, http_method FROM t_sys_api_endpoints")
        existing_set = {(row['api_path'], row['http_method']) for row in existing}
        
        total_created = 0
        total_skipped = 0
        
        # 按分类同步
        for category, description in PRIORITY2_CATEGORIES.items():
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
        print("\n⚠️  即将同步优先级2（设备核心）API到数据库")
        print("如果只想预览，请使用: python sync_priority2_apis.py --dry-run")
        confirm = input("\n确认继续? (yes/no): ").strip().lower()
        if confirm == 'yes':
            await sync_apis(dry_run=False)
        else:
            print("❌ 已取消")

if __name__ == '__main__':
    asyncio.run(main())
