#!/usr/bin/env python3
"""
数据同步脚本：将备份表数据同步到正式表
将sys_dict_data_backup、sys_dict_type_backup、sys_config_backup中的数据同步到
t_sys_dict_data、t_sys_dict_type、t_sys_config表
"""

import asyncio
import asyncpg
from typing import List, Dict, Any
from datetime import datetime
import json


class DataSyncManager:
    """数据同步管理器"""
    
    def __init__(self):
        self.db_config = {
            'host': '127.0.0.1',
            'port': 5432,
            'user': 'postgres',
            'password': 'Hanatech@123',
            'database': 'devicemonitor'
        }
        self.sync_report = {
            'start_time': None,
            'end_time': None,
            'tables_synced': {},
            'errors': [],
            'success': False
        }
    
    async def sync_all_tables(self):
        """同步所有表数据"""
        self.sync_report['start_time'] = datetime.now().isoformat()
        
        conn = await asyncpg.connect(**self.db_config)
        
        try:
            # 开始事务
            async with conn.transaction():
                print("=== 开始数据同步 ===")
                
                # 同步字典类型表
                await self._sync_dict_types(conn)
                
                # 同步字典数据表
                await self._sync_dict_data(conn)
                
                # 同步系统配置表
                await self._sync_sys_config(conn)
                
                print("\n=== 数据同步完成 ===")
                self.sync_report['success'] = True
                
        except Exception as e:
            error_msg = f"数据同步失败: {e}"
            print(f"❌ {error_msg}")
            self.sync_report['errors'].append(error_msg)
            raise
        finally:
            await conn.close()
            self.sync_report['end_time'] = datetime.now().isoformat()
            await self._save_sync_report()
    
    async def _sync_dict_types(self, conn):
        """同步字典类型表"""
        print("\n--- 同步字典类型表 ---")
        
        # 检查备份表是否存在
        backup_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'sys_dict_type_backup'
            )
        """)
        
        if not backup_exists:
            print("⚠️ 备份表 sys_dict_type_backup 不存在，跳过同步")
            return
        
        # 获取备份表数据
        backup_data = await conn.fetch("SELECT * FROM sys_dict_type_backup ORDER BY id")
        print(f"📋 备份表中有 {len(backup_data)} 条记录")
        
        if not backup_data:
            print("⚠️ 备份表中没有数据，跳过同步")
            return
        
        # 清空目标表（可选，根据需求决定）
        # await conn.execute("DELETE FROM t_sys_dict_type")
        
        # 插入数据（使用 ON CONFLICT 处理重复数据）
        inserted_count = 0
        updated_count = 0
        
        for row in backup_data:
            try:
                # 检查记录是否已存在
                existing = await conn.fetchval(
                    "SELECT id FROM t_sys_dict_type WHERE type_code = $1",
                    row['type_code']
                )
                
                if existing:
                    # 更新现有记录
                    updated_at = row['updated_at']
                    if updated_at and hasattr(updated_at, 'tzinfo') and updated_at.tzinfo:
                        updated_at = updated_at.replace(tzinfo=None)
                    
                    await conn.execute("""
                        UPDATE t_sys_dict_type 
                        SET type_name = $1, description = $2, updated_at = $3
                        WHERE type_code = $4
                    """, row['type_name'], row['description'], 
                    updated_at or datetime.now(), row['type_code'])
                    updated_count += 1
                    print(f"✅ 更新字典类型: {row['type_code']} - {row['type_name']}")
                else:
                    # 插入新记录
                    created_at = row['created_at']
                    updated_at = row['updated_at']
                    
                    if created_at and hasattr(created_at, 'tzinfo') and created_at.tzinfo:
                        created_at = created_at.replace(tzinfo=None)
                    if updated_at and hasattr(updated_at, 'tzinfo') and updated_at.tzinfo:
                        updated_at = updated_at.replace(tzinfo=None)
                    
                    await conn.execute("""
                        INSERT INTO t_sys_dict_type (type_code, type_name, description, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5)
                    """, row['type_code'], row['type_name'], row['description'],
                    created_at or datetime.now(), updated_at or datetime.now())
                    inserted_count += 1
                    print(f"✅ 插入字典类型: {row['type_code']} - {row['type_name']}")
                    
            except Exception as e:
                error_msg = f"同步字典类型记录失败 {row['type_code']}: {e}"
                print(f"❌ {error_msg}")
                self.sync_report['errors'].append(error_msg)
        
        self.sync_report['tables_synced']['t_sys_dict_type'] = {
            'inserted': inserted_count,
            'updated': updated_count,
            'total_processed': len(backup_data)
        }
        
        print(f"📊 字典类型同步完成: 插入 {inserted_count} 条，更新 {updated_count} 条")
    
    async def _sync_dict_data(self, conn):
        """同步字典数据表"""
        print("\n--- 同步字典数据表 ---")
        
        # 检查备份表是否存在
        backup_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'sys_dict_data_backup'
            )
        """)
        
        if not backup_exists:
            print("⚠️ 备份表 sys_dict_data_backup 不存在，跳过同步")
            return
        
        # 获取备份表数据
        backup_data = await conn.fetch("SELECT * FROM sys_dict_data_backup ORDER BY id")
        print(f"📋 备份表中有 {len(backup_data)} 条记录")
        
        if not backup_data:
            print("⚠️ 备份表中没有数据，跳过同步")
            return
        
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        
        for row in backup_data:
            try:
                # 通过备份表中的字典类型ID获取对应的type_code
                backup_type_code = await conn.fetchval(
                    "SELECT type_code FROM sys_dict_type_backup WHERE id = $1",
                    row['dict_type_id']
                )
                
                if not backup_type_code:
                    print(f"⚠️ 跳过记录，备份表中字典类型ID {row['dict_type_id']} 不存在: {row['data_label']}")
                    skipped_count += 1
                    continue
                
                # 在正式表中查找对应的字典类型ID
                target_dict_type_id = await conn.fetchval(
                    "SELECT id FROM t_sys_dict_type WHERE type_code = $1",
                    backup_type_code
                )
                
                if not target_dict_type_id:
                    print(f"⚠️ 跳过记录，正式表中字典类型 {backup_type_code} 不存在: {row['data_label']}")
                    skipped_count += 1
                    continue
                
                # 检查记录是否已存在（基于dict_type_id和data_value的唯一约束）
                existing = await conn.fetchval(
                    "SELECT id FROM t_sys_dict_data WHERE dict_type_id = $1 AND data_value = $2",
                    target_dict_type_id, row['data_value']
                )
                
                if existing:
                    # 更新现有记录
                    updated_at = row['updated_at']
                    if updated_at and hasattr(updated_at, 'tzinfo') and updated_at.tzinfo:
                        updated_at = updated_at.replace(tzinfo=None)
                    
                    await conn.execute("""
                        UPDATE t_sys_dict_data 
                        SET data_label = $1, sort_order = $2, description = $3, 
                            is_enabled = $4, updated_at = $5
                        WHERE dict_type_id = $6 AND data_value = $7
                    """, row['data_label'], row['sort_order'], row.get('description', ''),
                    row['is_enabled'], updated_at or datetime.now(),
                    target_dict_type_id, row['data_value'])
                    updated_count += 1
                    print(f"✅ 更新字典数据: {row['data_label']} ({row['data_value']}) -> 类型: {backup_type_code}")
                else:
                    # 插入新记录
                    created_at = row['created_at']
                    updated_at = row['updated_at']
                    
                    if created_at and hasattr(created_at, 'tzinfo') and created_at.tzinfo:
                        created_at = created_at.replace(tzinfo=None)
                    if updated_at and hasattr(updated_at, 'tzinfo') and updated_at.tzinfo:
                        updated_at = updated_at.replace(tzinfo=None)
                    
                    await conn.execute("""
                        INSERT INTO t_sys_dict_data 
                        (dict_type_id, data_label, data_value, sort_order, description, is_enabled, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """, target_dict_type_id, row['data_label'], row['data_value'],
                    row['sort_order'], row.get('description', ''), row['is_enabled'],
                    created_at or datetime.now(), updated_at or datetime.now())
                    inserted_count += 1
                    print(f"✅ 插入字典数据: {row['data_label']} ({row['data_value']}) -> 类型: {backup_type_code}")
                    
            except Exception as e:
                error_msg = f"同步字典数据记录失败 {row['data_label']}: {e}"
                print(f"❌ {error_msg}")
                self.sync_report['errors'].append(error_msg)
        
        self.sync_report['tables_synced']['t_sys_dict_data'] = {
            'inserted': inserted_count,
            'updated': updated_count,
            'skipped': skipped_count,
            'total_processed': len(backup_data)
        }
        
        print(f"📊 字典数据同步完成: 插入 {inserted_count} 条，更新 {updated_count} 条，跳过 {skipped_count} 条")
    
    async def _sync_sys_config(self, conn):
        """同步系统配置表"""
        print("\n--- 同步系统配置表 ---")
        
        # 检查备份表是否存在
        backup_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'sys_config_backup'
            )
        """)
        
        if not backup_exists:
            print("⚠️ 备份表 sys_config_backup 不存在，跳过同步")
            return
        
        # 获取备份表数据
        backup_data = await conn.fetch("SELECT * FROM sys_config_backup ORDER BY id")
        print(f"📋 备份表中有 {len(backup_data)} 条记录")
        
        if not backup_data:
            print("⚠️ 备份表中没有数据，跳过同步")
            return
        
        inserted_count = 0
        updated_count = 0
        
        for row in backup_data:
            try:
                # 检查记录是否已存在（基于param_key的唯一约束）
                existing = await conn.fetchval(
                    "SELECT id FROM t_sys_config WHERE param_key = $1",
                    row['param_key']
                )
                
                if existing:
                    # 更新现有记录
                    updated_at = row['updated_at']
                    if updated_at and hasattr(updated_at, 'tzinfo') and updated_at.tzinfo:
                        updated_at = updated_at.replace(tzinfo=None)
                    
                    await conn.execute("""
                        UPDATE t_sys_config 
                        SET param_value = $1, param_name = $2, param_type = $3, 
                            description = $4, is_editable = $5, is_system = $6, 
                            is_active = $7, updated_at = $8
                        WHERE param_key = $9
                    """, row['param_value'], row['param_name'], row['param_type'],
                    row['description'], row['is_editable'], row['is_system'],
                    row['is_active'], updated_at or datetime.now(), row['param_key'])
                    updated_count += 1
                    print(f"✅ 更新系统配置: {row['param_key']} - {row['param_name']}")
                else:
                    # 插入新记录
                    created_at = row['created_at']
                    updated_at = row['updated_at']
                    
                    if created_at and hasattr(created_at, 'tzinfo') and created_at.tzinfo:
                        created_at = created_at.replace(tzinfo=None)
                    if updated_at and hasattr(updated_at, 'tzinfo') and updated_at.tzinfo:
                        updated_at = updated_at.replace(tzinfo=None)
                    
                    await conn.execute("""
                        INSERT INTO t_sys_config 
                        (param_key, param_value, param_name, param_type, description, 
                         is_editable, is_system, is_active, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """, row['param_key'], row['param_value'], row['param_name'],
                    row['param_type'], row['description'], row['is_editable'],
                    row['is_system'], row['is_active'],
                    created_at or datetime.now(), updated_at or datetime.now())
                    inserted_count += 1
                    print(f"✅ 插入系统配置: {row['param_key']} - {row['param_name']}")
                    
            except Exception as e:
                error_msg = f"同步系统配置记录失败 {row['param_key']}: {e}"
                print(f"❌ {error_msg}")
                self.sync_report['errors'].append(error_msg)
        
        self.sync_report['tables_synced']['t_sys_config'] = {
            'inserted': inserted_count,
            'updated': updated_count,
            'total_processed': len(backup_data)
        }
        
        print(f"📊 系统配置同步完成: 插入 {inserted_count} 条，更新 {updated_count} 条")
    
    async def _save_sync_report(self):
        """保存同步报告"""
        report_file = f"sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 同步报告已保存: {report_file}")
        except Exception as e:
            print(f"⚠️ 保存同步报告失败: {e}")
    
    def print_summary(self):
        """打印同步摘要"""
        print("\n" + "="*50)
        print("数据同步摘要")
        print("="*50)
        
        if self.sync_report['success']:
            print("✅ 同步状态: 成功")
        else:
            print("❌ 同步状态: 失败")
        
        print(f"⏰ 开始时间: {self.sync_report['start_time']}")
        print(f"⏰ 结束时间: {self.sync_report['end_time']}")
        
        print("\n📊 同步统计:")
        for table_name, stats in self.sync_report['tables_synced'].items():
            print(f"  {table_name}:")
            print(f"    - 插入: {stats.get('inserted', 0)} 条")
            print(f"    - 更新: {stats.get('updated', 0)} 条")
            if 'skipped' in stats:
                print(f"    - 跳过: {stats['skipped']} 条")
            print(f"    - 总处理: {stats.get('total_processed', 0)} 条")
        
        if self.sync_report['errors']:
            print("\n❌ 错误信息:")
            for error in self.sync_report['errors']:
                print(f"  - {error}")
        else:
            print("\n✅ 无错误")


async def main():
    """主函数"""
    sync_manager = DataSyncManager()
    
    try:
        await sync_manager.sync_all_tables()
        sync_manager.print_summary()
        
        if sync_manager.sync_report['success']:
            print("\n🎉 数据同步成功完成！")
        else:
            print("\n💥 数据同步失败，请检查错误信息")
            
    except Exception as e:
        print(f"\n💥 同步过程中发生严重错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())