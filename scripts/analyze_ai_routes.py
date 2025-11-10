#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析所有AI相关路由
检查重复和前缀混乱问题
"""

import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def analyze_routes():
    """分析路由"""
    
    print("=" * 80)
    print("  AI Routes Analysis - Checking Duplicates and Prefix Issues")
    print("=" * 80)
    print()
    
    try:
        from app.api.v2 import v2_router
        from app.settings.ai_settings import ai_settings
        
        print(f"[CONFIG] AI Module Enabled: {ai_settings.ai_module_enabled}")
        print(f"[CONFIG] Trend Prediction: {ai_settings.ai_trend_prediction_enabled}")
        print()
        
        # 收集所有AI相关路由
        ai_routes = []
        for route in v2_router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                path = route.path
                if 'ai' in path.lower() or 'prediction' in path.lower() or 'health' in path.lower():
                    methods = list(route.methods)
                    tags = list(route.tags) if hasattr(route, 'tags') else []
                    name = route.name if hasattr(route, 'name') else 'unknown'
                    
                    ai_routes.append({
                        'methods': methods,
                        'path': path,
                        'name': name,
                        'tags': tags
                    })
        
        print(f"[INFO] Found {len(ai_routes)} AI-related routes")
        print()
        
        # 按前缀分组
        print("=" * 80)
        print("  Routes Grouped by Prefix")
        print("=" * 80)
        print()
        
        prefix_groups = defaultdict(list)
        for route in ai_routes:
            path = route['path']
            
            # 提取前缀
            if path.startswith('/ai-monitor/'):
                prefix = '/ai-monitor/'
            elif path.startswith('/ai/'):
                prefix = '/ai/'
            else:
                prefix = 'other'
            
            prefix_groups[prefix].append(route)
        
        for prefix, routes in sorted(prefix_groups.items()):
            print(f"\n[PREFIX] {prefix}")
            print(f"   Count: {len(routes)} routes")
            print()
            
            # 按标签分组
            tag_groups = defaultdict(list)
            for route in routes:
                tag = route['tags'][0] if route['tags'] else 'No Tag'
                tag_groups[tag].append(route)
            
            for tag, tag_routes in sorted(tag_groups.items()):
                print(f"   [{tag}] ({len(tag_routes)} routes)")
                for route in sorted(tag_routes, key=lambda r: r['path']):
                    methods_str = ','.join(sorted(route['methods']))
                    print(f"      {methods_str:12} {route['path']}")
            print()
        
        # 检查重复路由
        print("=" * 80)
        print("  Checking for Duplicates")
        print("=" * 80)
        print()
        
        path_count = defaultdict(list)
        for route in ai_routes:
            key = (frozenset(route['methods']), route['path'])
            path_count[key].append(route)
        
        duplicates_found = False
        for key, routes in path_count.items():
            if len(routes) > 1:
                methods, path = key
                print(f"[DUPLICATE] {','.join(methods)} {path}")
                print(f"   Found {len(routes)} times:")
                for route in routes:
                    print(f"      - {route['name']} (tags: {route['tags']})")
                print()
                duplicates_found = True
        
        if not duplicates_found:
            print("[OK] No duplicate routes found")
            print()
        
        # 检查相似路由（可能的冲突）
        print("=" * 80)
        print("  Checking for Similar Routes (Potential Conflicts)")
        print("=" * 80)
        print()
        
        path_patterns = defaultdict(list)
        for route in ai_routes:
            # 提取路径模式（去掉参数）
            pattern = route['path'].split('{')[0].rstrip('/')
            path_patterns[pattern].append(route)
        
        for pattern, routes in sorted(path_patterns.items()):
            if len(routes) > 1:
                print(f"\n[PATTERN] {pattern}*")
                print(f"   {len(routes)} routes with this pattern:")
                for route in routes:
                    methods_str = ','.join(sorted(route['methods']))
                    print(f"      {methods_str:12} {route['path']}")
                    print(f"         Tags: {route['tags']}")
        
        print()
        print("=" * 80)
        print("  Analysis Complete")
        print("=" * 80)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    analyze_routes()

