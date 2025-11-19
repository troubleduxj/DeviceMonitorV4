"""
API分类和数据库同步脚本
按模块分类整理API，并逐步同步到数据库
"""
import asyncio
import os
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
    """
    根据路由信息对API进行分类
    """
    file_path = route['file'].lower()
    path = route['path'].lower()
    method = route['method']
    
    # 计算每个分类的匹配分数
    scores = {}
    for category, rules in API_CLASSIFICATION.items():
        score = 0
        
        # 检查路径关键词
        for keyword in rules['keywords']:
            if keyword in path or keyword in file_path:
                score += 10
        
        # 检查文件路径
        for rule_path in rules['paths']:
            if rule_path.lower() in file_path or rule_path.lower() in path:
                score += 20
        
        if score > 0:
            scores[category] = score
    
    # 返回得分最高的分类
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    
    return '其他'

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
            patterns = [
                r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    method = match.group(1).upper()
                    path = match.group(2)
                    
                    # 尝试获取函数名和注释
                    func_pattern = r'@router\.' + match.group(1) + r'\(["\']' + re.escape(path) + r'["\'][^\n]*\n(?:\s*"""([^"]+)"""\s*\n)?\s*async def (\w+)'
                    func_match = re.search(func_pattern, content)
                    
                    func_name = 'unknown'
                    description = ''
                    if func_match:
                        if func_match.group(1):
                            description = func_match.group(1).strip()
                        func_name = func_match.group(2)
                    
                    routes.append({
                        'file': str(py_file).replace('\\', '/'),
                        'method': method,
                        'path': path,
                        'function': func_name,
                        'description': description
                    })
        except Exception:
            pass
    
    return routes

def infer_router_prefix(file_path):
    """
    从文件路径推断路由前缀
    """
    # 常见的路由前缀映射
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
        'app/api/v2/audit_logs.py': '/api/v2/audit-logs',
        'app/api/v2/docs.py': '/api/v2/docs',
        'app/api/v2/device_maintenance.py': '/api/v2/device/maintenance',
        'app/api/v2/device_process.py': '/api/v2/device',
        'app/api/v2/device_field_config.py': '/api/v2/device',
        'app/api/v2/device_repair_records_simple.py': '/api/v2/device/maintenance',
        'app/api/v2/data_query.py': '/api/v2/data',
        'app/api/v2/batch_operations.py': '/api/v2/batch',
        'app/api/v2/metadata.py': '/api/v2/metadata',
        'app/api/v2/metadata_sync.py': '/api/v2/metadata',
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

def generate_api_name(method, path, description=''):
    """
    生成API的中文名称
    """
    if description:
        return description
    
    # 根据路径和方法生成名称
    path_parts = [p for p in path.split('/') if p and not p.startswith('{')]
    
    method_names = {
        'GET': '获取',
        'POST': '创建',
        'PUT': '更新',
        'DELETE': '删除',
        'PATCH': '部分更新'
    }
    
    if path_parts:
        resource = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
        return f"{method_names.get(method, method)} {resource}"
    
    return f"{method} {path}"

async def get_or_create_api_group(conn, group_name, description):
    """
    获取或创建API分组
    """
    # 检查分组是否存在
    row = await conn.fetchrow("""
        SELECT id FROM t_sys_api_groups 
        WHERE group_name = $1
    """, group_name)
    
    if row:
        return row['id']
    
    # 创建新分组
    row = await conn.fetchrow("""
        INSERT INTO t_sys_api_groups (group_name, description, created_at, updated_at)
        VALUES ($1, $2, $3, $4)
        RETURNING id
    """, group_name, description, datetime.now(), datetime.now())
    
    return row['id']

async def sync_apis_by_category(category, routes, dry_run=True):
    """
    按分类同步API到数据库
    """
    print(f"\n{'='*80}")
    print(f"📦 处理分类: {category}")
    print(f"{'='*80}")
    print(f"API数量: {len(routes)}")
    
    if dry_run:
        print("\n🔍 预览模式 - 不会实际写入数据库\n")
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取或创建分组
        group_description = API_CLASSIFICATION.get(category, {}).get('description', category)
        group_id = await get_or_create_api_group(conn, category, group_description)
        print(f"✅ 分组ID: {group_id}")
        
        created_count = 0
        skipped_count = 0
        
        for route in routes:
            # 推断完整路径
            prefix = infer_router_prefix(route['file'])
            full_path = prefix + route['path'] if prefix else route['path']
            
            # 生成API名称
            api_name = generate_api_name(
                route['method'],
                full_path,
                route.get('description', '')
            )
            
            # 生成API编码
            api_code = f"{route['method'].lower()}_{full_path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}"
            
            # 检查是否已存在
            existing = await conn.fetchrow("""
                SELECT id FROM t_sys_api_endpoints
                WHERE api_path = $1 AND http_method = $2
            """, full_path, route['method'])
            
            if existing:
                print(f"  ⏭️  跳过: {route['method']} {full_path} (已存在)")
                skipped_count += 1
                continue
            
            if dry_run:
                print(f"  📝 将创建: {route['method']} {full_path}")
                print(f"      名称: {api_name}")
                print(f"      编码: {api_code}")
                print(f"      文件: {route['file']}")
                created_count += 1
            else:
                # 插入数据库
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
                print(f"  ✅ 已创建: {route['method']} {full_path} - {api_name}")
                created_count += 1
        
        print(f"\n📊 统计:")
        print(f"  - 新创建: {created_count}")
        print(f"  - 已跳过: {skipped_count}")
        
    finally:
        await conn.close()
    
    return created_count, skipped_count

async def main():
    """主函数"""
    print("="*80)
    print("🚀 API分类和数据库同步工具")
    print("="*80)
    
    # 1. 扫描后端路由
    print("\n📡 扫描后端路由...")
    routes = scan_backend_routes()
    print(f"✅ 扫描到 {len(routes)} 个路由")
    
    # 2. 分类整理
    print("\n🏷️  分类整理...")
    classified_routes = defaultdict(list)
    for route in routes:
        category = classify_api(route)
        classified_routes[category].append(route)
    
    print(f"✅ 分为 {len(classified_routes)} 个类别")
    print("\n分类统计:")
    for category, routes_list in sorted(classified_routes.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  - {category}: {len(routes_list)} 个API")
    
    # 3. 询问用户操作模式
    print("\n" + "="*80)
    print("请选择操作模式:")
    print("  1. 预览模式 (只显示将要创建的API，不写入数据库)")
    print("  2. 同步模式 (实际写入数据库)")
    print("  3. 按分类逐步同步 (可以选择要同步的分类)")
    print("="*80)
    
    mode = input("\n请输入选项 (1/2/3): ").strip()
    
    if mode == '1':
        # 预览模式
        print("\n🔍 预览模式")
        total_created = 0
        total_skipped = 0
        
        for category in sorted(classified_routes.keys()):
            created, skipped = await sync_apis_by_category(
                category,
                classified_routes[category],
                dry_run=True
            )
            total_created += created
            total_skipped += skipped
        
        print(f"\n{'='*80}")
        print(f"📊 总计:")
        print(f"  - 将创建: {total_created}")
        print(f"  - 将跳过: {total_skipped}")
        print(f"{'='*80}")
        
    elif mode == '2':
        # 全部同步
        confirm = input("\n⚠️  确认要同步所有API到数据库吗? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ 已取消")
            return
        
        print("\n🚀 开始同步...")
        total_created = 0
        total_skipped = 0
        
        for category in sorted(classified_routes.keys()):
            created, skipped = await sync_apis_by_category(
                category,
                classified_routes[category],
                dry_run=False
            )
            total_created += created
            total_skipped += skipped
        
        print(f"\n{'='*80}")
        print(f"✅ 同步完成!")
        print(f"📊 总计:")
        print(f"  - 已创建: {total_created}")
        print(f"  - 已跳过: {total_skipped}")
        print(f"{'='*80}")
        
    elif mode == '3':
        # 按分类逐步同步
        print("\n📋 可用分类:")
        categories = sorted(classified_routes.keys())
        for i, category in enumerate(categories, 1):
            print(f"  {i}. {category} ({len(classified_routes[category])} 个API)")
        
        print("\n请输入要同步的分类编号 (多个用逗号分隔，输入 'all' 同步全部):")
        selection = input("选择: ").strip()
        
        if selection.lower() == 'all':
            selected_categories = categories
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(',')]
                selected_categories = [categories[i-1] for i in indices if 1 <= i <= len(categories)]
            except:
                print("❌ 无效的输入")
                return
        
        if not selected_categories:
            print("❌ 没有选择任何分类")
            return
        
        print(f"\n将同步以下分类: {', '.join(selected_categories)}")
        confirm = input("确认? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ 已取消")
            return
        
        print("\n🚀 开始同步...")
        total_created = 0
        total_skipped = 0
        
        for category in selected_categories:
            created, skipped = await sync_apis_by_category(
                category,
                classified_routes[category],
                dry_run=False
            )
            total_created += created
            total_skipped += skipped
        
        print(f"\n{'='*80}")
        print(f"✅ 同步完成!")
        print(f"📊 总计:")
        print(f"  - 已创建: {total_created}")
        print(f"  - 已跳过: {total_skipped}")
        print(f"{'='*80}")
    
    else:
        print("❌ 无效的选项")

if __name__ == '__main__':
    asyncio.run(main())
