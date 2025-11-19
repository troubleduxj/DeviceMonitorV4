"""
同步AI监测相关API到数据库
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

# AI模块的分类和描述
AI_CATEGORIES = {
    'AI异常检测': 'AI异常检测、异常记录、异常处理',
    'AI特征提取': 'AI特征提取、批量提取、特征类型',
    'AI健康评分': 'AI健康评分、趋势分析、配置管理',
    'AI趋势预测': 'AI趋势预测、批量预测、方法对比',
    'AI预测分析': 'AI预测分析、风险评估、报告生成',
    'AI模型管理': 'AI模型管理、训练、部署',
    'AI标注管理': 'AI标注项目、数据管理',
}

# 路由前缀映射
PREFIX_MAP = {
    'app/api/v2/ai/anomaly_detection.py': '/api/v2/ai/anomaly',
    'app/api/v2/ai/feature_extraction.py': '/api/v2/ai/features',
    'app/api/v2/ai/health_scoring.py': '/api/v2/ai/health-scoring',
    'app/api/v2/ai/health_scores.py': '/api/v2/ai/health-scores',
    'app/api/v2/ai/trend_prediction.py': '/api/v2/ai/trend',
    'app/api/v2/ai/predictions.py': '/api/v2/ai/predictions',
    'app/api/v2/ai/prediction_analytics.py': '/api/v2/ai/prediction-analytics',
    'app/api/v2/ai/models.py': '/api/v2/ai/models',
    'app/api/v2/ai/annotations.py': '/api/v2/ai/annotations',
}

def classify_api(file_path):
    """根据文件路径分类API"""
    file_lower = file_path.lower()
    
    if 'anomaly_detection' in file_lower:
        return 'AI异常检测'
    elif 'feature_extraction' in file_lower:
        return 'AI特征提取'
    elif 'health_scor' in file_lower:  # 匹配 health_scoring 和 health_scores
        return 'AI健康评分'
    elif 'trend_prediction' in file_lower:
        return 'AI趋势预测'
    elif 'prediction_analytics' in file_lower:
        return 'AI预测分析'
    elif 'predictions.py' in file_lower:
        return 'AI预测分析'
    elif 'models.py' in file_lower and '/ai/' in file_lower:
        return 'AI模型管理'
    elif 'annotations' in file_lower:
        return 'AI标注管理'
    
    return None

def scan_ai_routes():
    """扫描AI相关的路由"""
    routes = []
    ai_dir = Path('app/api/v2/ai')
    
    if not ai_dir.exists():
        print("❌ AI目录不存在")
        return routes
    
    for py_file in ai_dir.glob('*.py'):
        if py_file.name.startswith('__'):
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
    print("🚀 同步AI监测相关API到数据库")
    print("="*80)
    
    if dry_run:
        print("\n🔍 预览模式 - 不会实际写入数据库\n")
    
    # 扫描路由
    print("\n📡 扫描AI监测API...")
    routes = scan_ai_routes()
    
    # 按分类整理
    by_category = defaultdict(list)
    for route in routes:
        by_category[route['category']].append(route)
    
    print(f"✅ 找到 {len(routes)} 个AI监测API\n")
    
    # 连接数据库
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取已存在的API
        existing = await conn.fetch("SELECT api_path, http_method FROM t_sys_api_endpoints")
        existing_set = {(row['api_path'], row['http_method']) for row in existing}
        
        total_created = 0
        total_skipped = 0
        
        # 按分类同步
        for category, description in AI_CATEGORIES.items():
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
        print("\n⚠️  即将同步AI监测相关API到数据库")
        print("如果只想预览，请使用: python sync_ai_apis.py --dry-run")
        confirm = input("\n确认继续? (yes/no): ").strip().lower()
        if confirm == 'yes':
            await sync_apis(dry_run=False)
        else:
            print("❌ 已取消")

if __name__ == '__main__':
    asyncio.run(main())
