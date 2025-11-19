"""
检查剩余未同步的API
"""
import asyncio
import asyncpg
from pathlib import Path
import re
from collections import defaultdict

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

# 完整的路由前缀映射
PREFIX_MAP = {
    'app/api/v1/avatar/avatar.py': '/api/v1/avatar',
    'app/api/v1/base/base.py': '/api/v1/base',
    'app/api/v1/dashboard/dashboard.py': '/api/v1/dashboard',
    'app/api/v1/devices/devices.py': '/api/v1/devices',
    'app/api/v1/devices/device_data.py': '/api/v1/devices',
    'app/api/v1/devices/device_types.py': '/api/v1/devices',
    'app/api/v1/devices/universal_data.py': '/api/v1/devices',
    'app/api/v2/alarms.py': '/api/v2/alarms',
    'app/api/v2/apis.py': '/api/v2/apis',
    'app/api/v2/api_groups.py': '/api/v2/api-groups',
    'app/api/v2/api_classification.py': '/api/v2/api-classification',
    'app/api/v2/auth.py': '/api/v2/auth',
    'app/api/v2/avatar.py': '/api/v2/avatar',
    'app/api/v2/base.py': '/api/v2/base',
    'app/api/v2/batch_operations.py': '/api/v2/batch',
    'app/api/v2/data_query.py': '/api/v2/data',
    'app/api/v2/departments.py': '/api/v2/departments',
    'app/api/v2/devices.py': '/api/v2/devices',
    'app/api/v2/device_field_config.py': '/api/v2/device',
    'app/api/v2/device_maintenance.py': '/api/v2/device/maintenance',
    'app/api/v2/device_process.py': '/api/v2/device',
    'app/api/v2/device_repair_records.py': '/api/v2/device/maintenance',
    'app/api/v2/device_repair_records_simple.py': '/api/v2/device/maintenance',
    'app/api/v2/dict_data.py': '/api/v2/dict-data',
    'app/api/v2/dict_types.py': '/api/v2/dict-types',
    'app/api/v2/docs.py': '/api/v2/docs',
    'app/api/v2/dynamic_models.py': '/api/v2/dynamic-models',
    'app/api/v2/health.py': '/api/v2/health',
    'app/api/v2/menus.py': '/api/v2/menus',
    'app/api/v2/metadata.py': '/api/v2/metadata',
    'app/api/v2/metadata_sync.py': '/api/v2/metadata',
    'app/api/v2/mock_data.py': '/api/v2/mock',
    'app/api/v2/permission_config.py': '/api/v2/permission-config',
    'app/api/v2/roles.py': '/api/v2/roles',
    'app/api/v2/system_health.py': '/api/v2/system',
    'app/api/v2/system_params.py': '/api/v2/system-params',
    'app/api/v2/users.py': '/api/v2/users',
    'app/api/v2/audit.py': '/api/v2/audit',
    'app/api/v2/audit_logs.py': '/api/v2/audit-logs',
    'app/api/monitoring.py': '/api/monitoring',
    'app/api/security.py': '/api/security',
    'app/api/tdengine.py': '/api/tdengine',
    'app/api/v2/ai/anomaly_detection.py': '/api/v2/ai/anomaly',
    'app/api/v2/ai/feature_extraction.py': '/api/v2/ai/features',
    'app/api/v2/ai/health_scoring.py': '/api/v2/ai/health-scoring',
    'app/api/v2/ai/health_scores.py': '/api/v2/ai/health-scores',
    'app/api/v2/ai/trend_prediction.py': '/api/v2/ai/trend',
    'app/api/v2/ai/predictions.py': '/api/v2/ai/predictions',
    'app/api/v2/ai/prediction_analytics.py': '/api/v2/ai/prediction-analytics',
    'app/api/v2/ai/models.py': '/api/v2/ai/models',
    'app/api/v2/ai/annotations.py': '/api/v2/ai/annotations',
    'app/controllers/user_management_controller.py': '/api/v2/users',
    'app/controllers/role_management_controller.py': '/api/v2/roles',
    'app/controllers/menu_permission_controller.py': '/api/v2/menus',
    'app/controllers/department_permission_controller.py': '/api/v2/departments',
    'app/controllers/audit_controller.py': '/api/v2/audit',
    'app/controllers/batch_operation_controller.py': '/api/v2/batch',
    'app/controllers/permission_performance_controller.py': '/api/v2/permission/performance',
    'app/controllers/permission_performance_optimization_controller.py': '/api/v2/permission/optimization',
}

def scan_all_routes():
    """扫描所有路由"""
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
                routes.append({
                    'file': file_str,
                    'method': method,
                    'path': path,
                })
        except:
            pass
    return routes

async def main():
    print("="*80)
    print("🔍 检查剩余未同步的API")
    print("="*80)
    
    # 扫描所有路由
    print("\n📡 扫描所有后端路由...")
    all_routes = scan_all_routes()
    print(f"✅ 扫描到 {len(all_routes)} 个路由")
    
    # 连接数据库
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取数据库中的API
        db_apis = await conn.fetch("SELECT api_path, http_method FROM t_sys_api_endpoints")
        existing_set = {(row['api_path'], row['http_method']) for row in db_apis}
        print(f"✅ 数据库中有 {len(existing_set)} 个API")
        
        # 找出未同步的API
        missing_routes = []
        for route in all_routes:
            prefix = PREFIX_MAP.get(route['file'], '')
            full_path = prefix + route['path'] if prefix else route['path']
            
            if (full_path, route['method']) not in existing_set:
                missing_routes.append({
                    **route,
                    'full_path': full_path
                })
        
        print(f"\n⚠️  未同步的API: {len(missing_routes)} 个")
        
        # 按文件分组
        by_file = defaultdict(list)
        for route in missing_routes:
            by_file[route['file']].append(route)
        
        print(f"\n📋 按文件分组:")
        for file_path in sorted(by_file.keys()):
            count = len(by_file[file_path])
            print(f"\n  {file_path} ({count}个)")
            for route in by_file[file_path][:5]:  # 只显示前5个
                print(f"    {route['method']:6} {route['full_path']}")
            if count > 5:
                print(f"    ... 还有 {count-5} 个")
        
        # 按模块分类
        print(f"\n{'='*80}")
        print("📊 按模块统计未同步的API")
        print(f"{'='*80}\n")
        
        module_stats = defaultdict(int)
        for route in missing_routes:
            file_path = route['file']
            if '/ai/' in file_path:
                if 'anomaly' in file_path:
                    module_stats['AI异常检测'] += 1
                elif 'feature' in file_path:
                    module_stats['AI特征提取'] += 1
                elif 'trend' in file_path:
                    module_stats['AI趋势预测'] += 1
                else:
                    module_stats['AI其他'] += 1
            elif 'monitoring' in file_path:
                module_stats['系统监控'] += 1
            elif 'security' in file_path:
                module_stats['安全管理'] += 1
            elif 'tdengine' in file_path:
                module_stats['TDengine管理'] += 1
            elif 'metadata' in file_path:
                module_stats['元数据管理'] += 1
            elif 'dynamic_model' in file_path:
                module_stats['动态模型'] += 1
            elif 'mock' in file_path:
                module_stats['Mock数据'] += 1
            elif 'permission_config' in file_path:
                module_stats['权限配置'] += 1
            elif 'permission_performance' in file_path:
                module_stats['权限性能监控'] += 1
            elif 'batch_operation' in file_path:
                module_stats['批量操作'] += 1
            elif 'data_query' in file_path:
                module_stats['数据查询'] += 1
            elif 'docs' in file_path:
                module_stats['文档管理'] += 1
            elif 'health' in file_path:
                module_stats['健康检查'] += 1
            elif 'swagger' in file_path:
                module_stats['Swagger文档'] += 1
            else:
                module_stats['其他'] += 1
        
        for module, count in sorted(module_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {module}: {count} 个API")
        
        print(f"\n{'='*80}")
        print(f"📊 总结")
        print(f"{'='*80}")
        print(f"后端路由总数: {len(all_routes)}")
        print(f"数据库已有: {len(existing_set)}")
        print(f"剩余未同步: {len(missing_routes)}")
        print(f"覆盖率: {len(existing_set)/len(all_routes)*100:.1f}%")
        print(f"{'='*80}")
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(main())
