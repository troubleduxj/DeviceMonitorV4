"""
全面检查所有API分组，查找重复、相似或命名不规范的问题
"""
import asyncio
import asyncpg
from collections import defaultdict
import re

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 5432,
    'user': 'postgres',
    'password': 'Hanatech@123',
    'database': 'devicemonitor'
}

async def check_all_api_issues():
    """全面检查所有API问题"""
    print("="*80)
    print("🔍 全面检查所有API分组")
    print("="*80)
    
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # 获取所有API
        apis = await conn.fetch("""
            SELECT 
                a.id,
                a.api_code,
                a.api_name,
                a.api_path,
                a.http_method,
                a.description,
                g.group_name,
                g.group_code,
                g.id as group_id
            FROM t_sys_api_endpoints a
            LEFT JOIN t_sys_api_groups g ON a.group_id = g.id
            ORDER BY g.group_name, a.api_path, a.http_method
        """)
        
        print(f"\n✅ 查询到 {len(apis)} 个API\n")
        
        # 问题统计
        issues = {
            'exact_duplicates': [],      # 完全重复（路径+方法相同）
            'similar_paths': [],          # 相似路径（参数名不同）
            'poor_naming': [],            # 命名不规范
            'missing_description': [],    # 缺少描述
            'generic_names': [],          # 通用名称（如"获取 xxx"）
        }
        
        # 1. 检查完全重复的API（路径+方法相同）
        print("="*80)
        print("1️⃣  检查完全重复的API")
        print("="*80 + "\n")
        
        path_method_map = defaultdict(list)
        for api in apis:
            key = (api['api_path'], api['http_method'])
            path_method_map[key].append(api)
        
        duplicates = {k: v for k, v in path_method_map.items() if len(v) > 1}
        
        if duplicates:
            print(f"⚠️  发现 {len(duplicates)} 组完全重复的API:\n")
            for (path, method), api_list in sorted(duplicates.items()):
                print(f"  {method} {path}")
                for api in api_list:
                    print(f"    - ID:{api['id']:4} | {api['group_name']} | {api['api_name']}")
                print()
                issues['exact_duplicates'].append({
                    'path': path,
                    'method': method,
                    'apis': api_list
                })
        else:
            print("✅ 没有发现完全重复的API\n")
        
        # 2. 检查相似路径（参数名不同）
        print("="*80)
        print("2️⃣  检查相似路径（参数名不同）")
        print("="*80 + "\n")
        
        # 将路径参数标准化为 *
        normalized_paths = defaultdict(list)
        for api in apis:
            normalized = re.sub(r'\{[^}]+\}', '*', api['api_path'])
            normalized_paths[(normalized, api['http_method'])].append(api)
        
        similar_paths = {k: v for k, v in normalized_paths.items() if len(v) > 1}
        
        if similar_paths:
            print(f"⚠️  发现 {len(similar_paths)} 组相似路径的API:\n")
            for (normalized, method), api_list in sorted(similar_paths.items()):
                # 检查是否真的是不同的路径（不是同一个路径）
                unique_paths = set(api['api_path'] for api in api_list)
                if len(unique_paths) > 1:
                    print(f"  模式: {method} {normalized}")
                    for api in api_list:
                        print(f"    - {api['api_path']:50} | {api['group_name']}")
                    print()
                    issues['similar_paths'].append({
                        'pattern': normalized,
                        'method': method,
                        'apis': api_list
                    })
        else:
            print("✅ 没有发现相似路径的API\n")
        
        # 3. 检查命名不规范的API
        print("="*80)
        print("3️⃣  检查命名不规范的API")
        print("="*80 + "\n")
        
        poor_naming_count = 0
        for api in apis:
            name = api['api_name']
            # 检查是否是通用名称（如"获取 xxx", "创建 xxx"等）
            if re.match(r'^(获取|创建|更新|删除)\s+[a-z\s]+$', name):
                poor_naming_count += 1
                if poor_naming_count <= 20:  # 只显示前20个
                    print(f"  ⚠️  {api['http_method']:6} {api['api_path']:50} | {name}")
                    issues['generic_names'].append(api)
        
        if poor_naming_count > 20:
            print(f"\n  ... 还有 {poor_naming_count - 20} 个类似问题")
        
        if poor_naming_count == 0:
            print("✅ 所有API命名都很规范\n")
        else:
            print(f"\n⚠️  共发现 {poor_naming_count} 个命名不够具体的API\n")
        
        # 4. 检查缺少描述的API
        print("="*80)
        print("4️⃣  检查缺少描述的API")
        print("="*80 + "\n")
        
        missing_desc = [api for api in apis if not api['description'] or api['description'].strip() == '']
        
        if missing_desc:
            print(f"⚠️  发现 {len(missing_desc)} 个缺少描述的API:\n")
            for api in missing_desc[:20]:  # 只显示前20个
                print(f"  {api['http_method']:6} {api['api_path']:50} | {api['api_name']}")
                issues['missing_description'].append(api)
            if len(missing_desc) > 20:
                print(f"\n  ... 还有 {len(missing_desc) - 20} 个")
            print()
        else:
            print("✅ 所有API都有描述\n")
        
        # 5. 按分组检查问题
        print("="*80)
        print("5️⃣  按分组统计问题")
        print("="*80 + "\n")
        
        group_issues = defaultdict(lambda: {
            'total': 0,
            'generic_names': 0,
            'missing_desc': 0,
            'similar_paths': 0
        })
        
        for api in apis:
            group_name = api['group_name'] or '未分组'
            group_issues[group_name]['total'] += 1
            
            # 统计通用名称
            if re.match(r'^(获取|创建|更新|删除)\s+[a-z\s]+$', api['api_name']):
                group_issues[group_name]['generic_names'] += 1
            
            # 统计缺少描述
            if not api['description'] or api['description'].strip() == '':
                group_issues[group_name]['missing_desc'] += 1
        
        # 统计相似路径
        for issue in issues['similar_paths']:
            for api in issue['apis']:
                group_name = api['group_name'] or '未分组'
                group_issues[group_name]['similar_paths'] += 1
        
        # 显示有问题的分组
        problem_groups = {
            k: v for k, v in group_issues.items()
            if v['generic_names'] > 0 or v['missing_desc'] > 0 or v['similar_paths'] > 0
        }
        
        if problem_groups:
            print(f"发现 {len(problem_groups)} 个分组存在问题:\n")
            for group_name, stats in sorted(problem_groups.items()):
                print(f"📦 {group_name} (共{stats['total']}个API)")
                if stats['generic_names'] > 0:
                    print(f"  ⚠️  通用名称: {stats['generic_names']} 个")
                if stats['missing_desc'] > 0:
                    print(f"  ⚠️  缺少描述: {stats['missing_desc']} 个")
                if stats['similar_paths'] > 0:
                    print(f"  ⚠️  相似路径: {stats['similar_paths']} 个")
                print()
        else:
            print("✅ 所有分组都没有明显问题\n")
        
        # 6. 总结报告
        print("="*80)
        print("📊 问题总结")
        print("="*80 + "\n")
        
        total_issues = (
            len(issues['exact_duplicates']) +
            len(issues['similar_paths']) +
            len(issues['generic_names']) +
            len(issues['missing_description'])
        )
        
        print(f"完全重复的API: {len(issues['exact_duplicates'])} 组")
        print(f"相似路径的API: {len(issues['similar_paths'])} 组")
        print(f"通用名称的API: {len(issues['generic_names'])} 个")
        print(f"缺少描述的API: {len(issues['missing_description'])} 个")
        print(f"\n总问题数: {total_issues}")
        
        if total_issues == 0:
            print("\n🎉 恭喜！所有API都很规范，没有发现明显问题！")
        else:
            print("\n⚠️  建议优先处理:")
            if issues['exact_duplicates']:
                print("  1. 完全重复的API（最高优先级）")
            if issues['similar_paths']:
                print("  2. 相似路径的API（需要确认是否重复）")
            if issues['generic_names']:
                print("  3. 通用名称的API（建议改为更具体的名称）")
            if issues['missing_description']:
                print("  4. 缺少描述的API（建议补充描述）")
        
        print("\n" + "="*80)
        
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(check_all_api_issues())
