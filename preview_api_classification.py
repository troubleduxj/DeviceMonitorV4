"""
API分类预览脚本 - 非交互式
生成分类报告，不需要用户输入
"""
import asyncio
from pathlib import Path
from collections import defaultdict
import re
import asyncpg
from datetime import datetime

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

# API分类规则
API_CLASSIFICATION = {
    '认证管理': {
        'keywords': ['auth', 'login', 'logout', 'token', 'password', 'userinfo'],
        'paths': ['/api/v2/auth', '/api/v2/base/access_token'],
        'description': '用户认证、登录登出、密码管理'
    },
    '用户管理': {
        'keywords': ['user', 'profile'],
        'paths': ['/api/v2/users', 'app/api/v2/users.py', 'app/controllers/user_management'],
        'description': '用户增删改查、角色分配、状态管理'
    },
    '角色管理': {
        'keywords': ['role'],
        'paths': ['/api/v2/roles', 'app/api/v2/roles.py', 'app/controllers/role_management'],
        'description': '角色增删改查、权限分配、层级管理'
    },
    '菜单管理': {
        'keywords': ['menu'],
        'paths': ['/api/v2/menus', 'app/controllers/menu_permission'],
        'description': '菜单增删改查、权限配置、可见性控制'
    },
    '部门管理': {
        'keywords': ['department', 'dept'],
        'paths': ['/api/v2/departments', 'app/controllers/department'],
        'description': '部门增删改查、层级管理、权限范围'
    },
    'API管理': {
        'keywords': ['api', 'endpoint'],
        'paths': ['/api/v2/apis', 'app/api/v2/apis.py'],
        'description': 'API端点管理、分组管理、权限配置'
    },
    'API分组管理': {
        'keywords': ['api-group', 'api_group'],
        'paths': ['/api/v2/api-groups', 'app/api/v2/api_groups.py'],
        'description': 'API分组的增删改查'
    },
    '设备管理': {
        'keywords': ['device'],
        'paths': ['/api/v2/devices', 'app/api/v1/devices', 'app/api/v2/devices.py'],
        'description': '设备增删改查、类型管理、状态监控'
    },
    '设备维护管理': {
        'keywords': ['maintenance', 'repair'],
        'paths': ['maintenance', 'repair-record'],
        'description': '设备维护记录、维修记录、计划管理'
    },
    '设备工艺管理': {
        'keywords': ['process'],
        'paths': ['processes', 'device_process'],
        'description': '工艺管理、执行记录、模板管理'
    },
    '设备字段配置': {
        'keywords': ['field', 'device-field'],
        'paths': ['device-field', 'device_field_config'],
        'description': '设备字段配置、缓存管理'
    },
    '报警管理': {
        'keywords': ['alarm'],
        'paths': ['/api/v2/alarms', 'app/api/v2/alarms.py'],
        'description': '报警记录、处理、统计'
    },
    '字典管理': {
        'keywords': ['dict'],
        'paths': ['/api/v2/dict', 'app/api/v2/dict'],
        'description': '字典类型、字典数据管理'
    },
    '系统参数': {
        'keywords': ['system-param', 'param'],
        'paths': ['/api/v2/system-params', 'app/api/v2/system_params'],
        'description': '系统参数配置'
    },
    '审计日志': {
        'keywords': ['audit', 'log'],
        'paths': ['/api/v2/audit', 'app/api/v2/audit', 'app/controllers/audit'],
        'description': '审计日志、安全事件、操作记录'
    },
    '文档管理': {
        'keywords': ['docs', 'doc', 'swagger', 'changelog'],
        'paths': ['/api/v2/docs', 'app/api/v2/docs.py'],
        'description': 'API文档、变更日志、版本管理'
    },
    '数据查询': {
        'keywords': ['query', 'search'],
        'paths': ['data_query'],
        'description': '实时数据查询、统计查询'
    },
    '批量操作': {
        'keywords': ['batch'],
        'paths': ['batch_operation'],
        'description': '批量操作、权限验证、模拟执行'
    },
    '权限性能监控': {
        'keywords': ['permission', 'performance'],
        'paths': ['permission_performance'],
        'description': '权限检查性能监控、缓存优化'
    },
    '系统监控': {
        'keywords': ['monitoring', 'health', 'metric'],
        'paths': ['app/api/monitoring.py', 'system_health'],
        'description': '系统性能监控、健康检查、指标统计'
    },
    '安全管理': {
        'keywords': ['security', 'threat'],
        'paths': ['app/api/security.py'],
        'description': '安全事件、威胁检测、IP统计'
    },
    'TDengine管理': {
        'keywords': ['tdengine', 'server', 'database'],
        'paths': ['app/api/tdengine.py'],
        'description': 'TDengine服务器管理、数据库查询'
    },
    '元数据管理': {
        'keywords': ['metadata', 'field', 'model', 'mapping'],
        'paths': ['app/api/v2/metadata'],
        'description': '字段管理、模型管理、映射配置'
    },
    '动态模型': {
        'keywords': ['dynamic'],
        'paths': ['dynamic_model'],
        'description': '动态模型生成、缓存管理'
    },
    'Mock数据': {
        'keywords': ['mock'],
        'paths': ['mock_data'],
        'description': 'Mock数据规则管理'
    },
    '权限配置': {
        'keywords': ['permission-config', 'endpoint', 'rule'],
        'paths': ['permission_config'],
        'description': '权限端点配置、规则管理、版本控制'
    },
    'AI分析': {
        'keywords': ['analysis', 'ai'],
        'paths': ['app/api/v2/ai/analysis'],
        'description': 'AI分析任务、结果查询'
    },
    'AI标注': {
        'keywords': ['annotation'],
        'paths': ['app/api/v2/ai/annotations'],
        'description': 'AI标注数据管理'
    },
    'AI健康评分': {
        'keywords': ['health-score', 'health_score'],
        'paths': ['app/api/v2/ai/health_scores'],
        'description': 'AI健康评分、趋势分析'
    },
    'AI模型': {
        'keywords': ['model', 'train', 'deploy'],
        'paths': ['app/api/v2/ai/models'],
        'description': 'AI模型管理、训练、部署'
    },
    'AI预测': {
        'keywords': ['predict', 'prediction'],
        'paths': ['app/api/v2/ai/predictions', 'app/api/v2/ai/prediction_analytics'],
        'description': 'AI预测、风险评估、报告生成'
    },
    '头像管理': {
        'keywords': ['avatar'],
        'paths': ['avatar'],
        'description': '用户头像生成和管理'
    },
    '基础服务': {
        'keywords': ['base', 'health'],
        'paths': ['/api/v2/base', 'app/api/v2/base.py'],
        'description': '基础服务接口'
    },
}

def classify_api(route):
    """根据路由信息对API进行分类"""
    file_path = route['file'].lower()
    path = route['path'].lower()
    
    scores = {}
    for category, rules in API_CLASSIFICATION.items():
        score = 0
        for keyword in rules['keywords']:
            if keyword in path or keyword in file_path:
                score += 10
        for rule_path in rules['paths']:
            if rule_path.lower() in file_path or rule_path.lower() in path:
                score += 20
        if score > 0:
            scores[category] = score
    
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return '其他'

def scan_backend_routes():
    """扫描后端实际的路由定义"""
    routes = []
    app_dir = Path('app')
    
    if not app_dir.exists():
        return routes
    
    for py_file in app_dir.rglob('*.py'):
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding='utf-8')
            patterns = [
                r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            ]
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    method = match.group(1).upper()
                    path = match.group(2)
                    routes.append({
                        'file': str(py_file).replace('\\', '/'),
                        'method': method,
                        'path': path,
                        'function': 'unknown'
                    })
        except:
            pass
    return routes

def infer_router_prefix(file_path):
    """从文件路径推断路由前缀"""
    prefix_map = {
        'app/api/v2/users.py': '/api/v2/users',
        'app/api/v2/roles.py': '/api/v2/roles',
        'app/api/v2/menus.py': '/api/v2/menus',
        'app/api/v2/departments.py': '/api/v2/departments',
        'app/api/v2/devices.py': '/api/v2/devices',
        'app/api/v2/alarms.py': '/api/v2/alarms',
        'app/api/v2/auth.py': '/api/v2/auth',
        'app/api/v2/base.py': '/api/v2/base',
        'app/api/v2/apis.py': '/api/v2/apis',
        'app/api/v2/api_groups.py': '/api/v2/api-groups',
        'app/api/v2/dict_data.py': '/api/v2/dict-data',
        'app/api/v2/dict_types.py': '/api/v2/dict-types',
        'app/api/v2/system_params.py': '/api/v2/system-params',
        'app/api/v2/audit.py': '/api/v2/audit',
        'app/api/v2/docs.py': '/api/v2/docs',
        'app/api/v2/device_maintenance.py': '/api/v2/device/maintenance',
        'app/api/v2/device_process.py': '/api/v2/device',
        'app/api/v2/device_field_config.py': '/api/v2/device',
        'app/api/v2/device_repair_records_simple.py': '/api/v2/device/maintenance',
        'app/api/v2/data_query.py': '/api/v2/data',
        'app/api/v2/batch_operations.py': '/api/v2/batch',
        'app/api/v2/metadata.py': '/api/v2/metadata',
        'app/api/v2/dynamic_models.py': '/api/v2/dynamic-models',
        'app/api/v2/mock_data.py': '/api/v2/mock',
        'app/api/v2/permission_config.py': '/api/v2/permission-config',
        'app/api/v2/system_health.py': '/api/v2/system',
        'app/api/v2/avatar.py': '/api/v2/avatar',
        'app/api/v2/health.py': '/api/v2/health',
        'app/api/monitoring.py': '/api/monitoring',
        'app/api/security.py': '/api/security',
        'app/api/tdengine.py': '/api/tdengine',
        'app/api/v2/ai/analysis.py': '/api/v2/ai/analysis',
        'app/api/v2/ai/annotations.py': '/api/v2/ai/annotations',
        'app/api/v2/ai/health_scores.py': '/api/v2/ai/health-scores',
        'app/api/v2/ai/models.py': '/api/v2/ai/models',
        'app/api/v2/ai/predictions.py': '/api/v2/ai/predictions',
        'app/api/v2/ai/prediction_analytics.py': '/api/v2/ai/prediction-analytics',
        'app/controllers/user_management_controller.py': '/api/v2/users',
        'app/controllers/role_management_controller.py': '/api/v2/roles',
        'app/controllers/menu_permission_controller.py': '/api/v2/menus',
        'app/controllers/department_permission_controller.py': '/api/v2/departments',
        'app/controllers/audit_controller.py': '/api/v2/audit',
        'app/controllers/batch_operation_controller.py': '/api/v2/batch',
        'app/controllers/permission_performance_controller.py': '/api/v2/permission/performance',
        'app/controllers/permission_performance_optimization_controller.py': '/api/v2/permission/optimization',
    }
    return prefix_map.get(file_path, '')

async def check_existing_apis(conn):
    """检查数据库中已存在的API"""
    rows = await conn.fetch("""
        SELECT api_path, http_method FROM t_sys_api_endpoints
    """)
    return {(row['api_path'], row['http_method']) for row in rows}

async def main():
    """主函数"""
    print("="*80)
    print("🔍 API分类预览报告")
    print("="*80)
    
    # 扫描路由
    print("\n📡 扫描后端路由...")
    routes = scan_backend_routes()
    print(f"✅ 扫描到 {len(routes)} 个路由")
    
    # 分类整理
    print("\n🏷️  分类整理...")
    classified_routes = defaultdict(list)
    for route in routes:
        category = classify_api(route)
        classified_routes[category].append(route)
    
    print(f"✅ 分为 {len(classified_routes)} 个类别\n")
    
    # 连接数据库检查已存在的API
    print("🔗 连接数据库检查已存在的API...")
    conn = await asyncpg.connect(**DB_CONFIG)
    existing_apis = await check_existing_apis(conn)
    await conn.close()
    print(f"✅ 数据库中已有 {len(existing_apis)} 个API\n")
    
    # 生成详细报告
    print("="*80)
    print("📊 分类详情")
    print("="*80)
    
    total_new = 0
    total_existing = 0
    
    report_lines = []
    
    for category in sorted(classified_routes.keys(), key=lambda x: len(classified_routes[x]), reverse=True):
        routes_list = classified_routes[category]
        
        # 统计新增和已存在的
        new_apis = []
        existing_count = 0
        
        for route in routes_list:
            prefix = infer_router_prefix(route['file'])
            full_path = prefix + route['path'] if prefix else route['path']
            
            if (full_path, route['method']) in existing_apis:
                existing_count += 1
            else:
                new_apis.append((route['method'], full_path, route['file']))
        
        new_count = len(new_apis)
        total_new += new_count
        total_existing += existing_count
        
        report_lines.append(f"\n## {category}")
        report_lines.append(f"- 总数: {len(routes_list)}")
        report_lines.append(f"- 已存在: {existing_count}")
        report_lines.append(f"- 需新增: {new_count}")
        report_lines.append(f"- 描述: {API_CLASSIFICATION.get(category, {}).get('description', '')}")
        
        if new_count > 0:
            report_lines.append(f"\n### 需要新增的API ({new_count}个):")
            for method, path, file in new_apis[:10]:  # 只显示前10个
                report_lines.append(f"  - {method} {path}")
            if new_count > 10:
                report_lines.append(f"  ... 还有 {new_count - 10} 个")
    
    # 打印到控制台
    for line in report_lines:
        print(line)
    
    # 保存到文件
    report_content = "\n".join(report_lines)
    with open('API分类预览报告.md', 'w', encoding='utf-8') as f:
        f.write(f"# API分类预览报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## 总体统计\n\n")
        f.write(f"- 扫描到的路由总数: {len(routes)}\n")
        f.write(f"- 数据库已存在: {total_existing}\n")
        f.write(f"- 需要新增: {total_new}\n")
        f.write(f"- 分类数量: {len(classified_routes)}\n\n")
        f.write(report_content)
    
    print(f"\n{'='*80}")
    print(f"📊 总体统计")
    print(f"{'='*80}")
    print(f"扫描到的路由总数: {len(routes)}")
    print(f"数据库已存在: {total_existing}")
    print(f"需要新增: {total_new}")
    print(f"分类数量: {len(classified_routes)}")
    print(f"\n✅ 详细报告已保存到: API分类预览报告.md")
    print(f"{'='*80}")

if __name__ == '__main__':
    asyncio.run(main())
