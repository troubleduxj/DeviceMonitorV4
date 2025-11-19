"""
批量同步API到数据库
按优先级分批次同步
"""
import asyncio
from sync_api_to_database import (
    scan_backend_routes,
    classify_api,
    sync_apis_by_category,
    API_CLASSIFICATION
)
from collections import defaultdict

# 定义同步优先级
SYNC_PRIORITY = {
    '优先级1-核心业务': [
        '认证管理',
        '用户管理',
        '角色管理',
        '菜单管理',
        '部门管理',
    ],
    '优先级2-设备核心': [
        '设备管理',
        '设备维护管理',
        '设备工艺管理',
        '设备字段配置',
        '报警管理',
    ],
    '优先级3-系统管理': [
        'API管理',
        'API分组管理',
        '字典管理',
        '系统参数',
        '审计日志',
    ],
    '优先级4-高级功能': [
        '批量操作',
        '权限配置',
        '权限性能监控',
        '文档管理',
    ],
    '优先级5-数据服务': [
        'TDengine管理',
        '数据查询',
        '元数据管理',
        '动态模型',
    ],
    '优先级6-监控安全': [
        '系统监控',
        '安全管理',
    ],
    '优先级7-AI功能': [
        'AI分析',
        'AI预测',
        'AI模型',
        'AI健康评分',
        'AI标注',
    ],
    '优先级8-其他': [
        '基础服务',
        '头像管理',
        'Mock数据',
        '其他',
    ],
}

async def sync_by_priority(priority_name, categories, classified_routes, dry_run=False):
    """按优先级同步一批分类"""
    print(f"\n{'='*80}")
    print(f"🎯 {priority_name}")
    print(f"{'='*80}")
    
    total_created = 0
    total_skipped = 0
    
    for category in categories:
        if category not in classified_routes:
            print(f"⚠️  分类 '{category}' 未找到，跳过")
            continue
        
        routes_list = classified_routes[category]
        created, skipped = await sync_apis_by_category(
            category,
            routes_list,
            dry_run=dry_run
        )
        total_created += created
        total_skipped += skipped
    
    print(f"\n📊 {priority_name} 统计:")
    print(f"  - 新创建: {total_created}")
    print(f"  - 已跳过: {total_skipped}")
    
    return total_created, total_skipped

async def main():
    """主函数"""
    print("="*80)
    print("🚀 批量同步API到数据库")
    print("="*80)
    
    # 1. 扫描和分类
    print("\n📡 扫描后端路由...")
    routes = scan_backend_routes()
    print(f"✅ 扫描到 {len(routes)} 个路由")
    
    print("\n🏷️  分类整理...")
    classified_routes = defaultdict(list)
    for route in routes:
        category = classify_api(route)
        classified_routes[category].append(route)
    print(f"✅ 分为 {len(classified_routes)} 个类别")
    
    # 2. 显示同步计划
    print("\n" + "="*80)
    print("📋 同步计划")
    print("="*80)
    
    for priority_name, categories in SYNC_PRIORITY.items():
        total_apis = sum(len(classified_routes.get(cat, [])) for cat in categories)
        print(f"\n{priority_name}:")
        for cat in categories:
            count = len(classified_routes.get(cat, []))
            if count > 0:
                print(f"  - {cat}: {count} 个API")
        print(f"  小计: {total_apis} 个API")
    
    # 3. 询问操作模式
    print("\n" + "="*80)
    print("请选择操作模式:")
    print("  1. 预览模式 (只显示，不写入)")
    print("  2. 同步优先级1 (核心业务)")
    print("  3. 同步优先级1-2 (核心业务+设备核心)")
    print("  4. 同步优先级1-3 (核心业务+设备核心+系统管理)")
    print("  5. 同步优先级1-4 (核心业务+设备核心+系统管理+高级功能)")
    print("  6. 同步全部")
    print("="*80)
    
    mode = input("\n请输入选项 (1-6): ").strip()
    
    if mode == '1':
        # 预览模式
        print("\n🔍 预览模式")
        grand_total_created = 0
        grand_total_skipped = 0
        
        for priority_name, categories in SYNC_PRIORITY.items():
            created, skipped = await sync_by_priority(
                priority_name,
                categories,
                classified_routes,
                dry_run=True
            )
            grand_total_created += created
            grand_total_skipped += skipped
        
        print(f"\n{'='*80}")
        print(f"📊 总计:")
        print(f"  - 将创建: {grand_total_created}")
        print(f"  - 将跳过: {grand_total_skipped}")
        print(f"{'='*80}")
        
    elif mode in ['2', '3', '4', '5', '6']:
        # 确定要同步的优先级
        priority_levels = {
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            '6': 8,
        }
        max_level = priority_levels[mode]
        
        priorities_to_sync = list(SYNC_PRIORITY.items())[:max_level]
        
        print(f"\n将同步以下优先级:")
        for priority_name, categories in priorities_to_sync:
            print(f"  - {priority_name}")
        
        confirm = input("\n⚠️  确认要同步到数据库吗? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ 已取消")
            return
        
        print("\n🚀 开始同步...")
        grand_total_created = 0
        grand_total_skipped = 0
        
        for priority_name, categories in priorities_to_sync:
            created, skipped = await sync_by_priority(
                priority_name,
                categories,
                classified_routes,
                dry_run=False
            )
            grand_total_created += created
            grand_total_skipped += skipped
        
        print(f"\n{'='*80}")
        print(f"✅ 同步完成!")
        print(f"📊 总计:")
        print(f"  - 已创建: {grand_total_created}")
        print(f"  - 已跳过: {grand_total_skipped}")
        print(f"{'='*80}")
    
    else:
        print("❌ 无效的选项")

if __name__ == '__main__':
    asyncio.run(main())
