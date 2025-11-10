#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库优化执行脚本

运行数据库索引分析并生成优化建议
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from app.settings import settings
from app.core.database_optimizer import run_database_optimization, db_optimizer
from app.log import logger


async def main():
    """主函数"""
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        logger.info("=" * 60)
        logger.info("开始数据库优化分析")
        logger.info("=" * 60)
        
        # 运行优化分析
        analysis_results = await run_database_optimization()
        
        if analysis_results:
            print("\n数据库优化建议摘要:")
            print("-" * 40)
            
            total_suggestions = 0
            for model_name, suggestions in analysis_results.items():
                high_priority = [s for s in suggestions if s['priority'] == 'high']
                medium_priority = [s for s in suggestions if s['priority'] == 'medium']
                
                total_suggestions += len(suggestions)
                
                print(f"\n{model_name}:")
                print(f"  高优先级建议: {len(high_priority)} 个")
                print(f"  中优先级建议: {len(medium_priority)} 个")
                
                # 显示高优先级建议的详情
                if high_priority:
                    print("  高优先级建议详情:")
                    for suggestion in high_priority:
                        print(f"    - {suggestion['reason']}")
            
            print(f"\n总计: {total_suggestions} 个优化建议")
            print(f"优化脚本已生成: database_optimization.sql")
            print("\n注意事项:")
            print("1. 请在生产环境执行前先备份数据库")
            print("2. 建议在低峰期执行以减少对系统性能的影响")
            print("3. 可以根据实际情况选择性执行优化建议")
        
        else:
            print("✅ 数据库索引配置良好，暂无需要优化的项目")
        
        # 检查现有索引
        print("\n检查现有索引...")
        existing_indexes = await db_optimizer.check_existing_indexes()
        
        if existing_indexes:
            print("现有索引统计:")
            for table_name, indexes in existing_indexes.items():
                if indexes:
                    print(f"  {table_name}: {len(indexes)} 个索引")
        
        logger.info("数据库优化分析完成")
        
    except Exception as e:
        logger.error(f"数据库优化分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)