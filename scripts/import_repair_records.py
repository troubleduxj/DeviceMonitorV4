#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
焊机维修记录数据导入脚本

功能：
1. 读取焊机维修记录表格数据
2. 创建或查找对应的设备信息
3. 导入维修记录到数据库

作者：AI Assistant
创建时间：2025-01-09
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.device import DeviceInfo, DeviceRepairRecord, DeviceType
from app.schemas.devices import DeviceCreate, DeviceRepairRecordCreate
from app.controllers.device import DeviceController
from tortoise import Tortoise
from app.settings.config import settings


class RepairRecordImporter:
    """维修记录导入器"""
    
    def __init__(self):
        self.device_controller = DeviceController()
        self.imported_count = 0
        self.error_count = 0
        self.errors = []
    
    async def init_database(self):
        """初始化数据库连接"""
        await Tortoise.init(config=settings.tortoise_orm.model_dump())
    
    async def close_database(self):
        """关闭数据库连接"""
        await Tortoise.close_connections()
    
    def parse_repair_records_data(self) -> List[Dict[str, Any]]:
        """解析维修记录数据
        
        Returns:
            解析后的维修记录数据列表
        """
        # 焊机维修记录表格数据
        repair_data = [
            {
                "序号": 1,
                "报修日期": "2024-01-15",
                "类别": "焊机",
                "申请人": "张三",
                "焊机编号": "WM001",
                "故障现象": "焊接电流不稳定",
                "故障原因": "电源模块老化",
                "维修内容": "更换电源模块",
                "维修人员": "李工",
                "维修日期": "2024-01-16",
                "维修费用": 1200.00,
                "备注": "已测试正常"
            },
            {
                "序号": 2,
                "报修日期": "2024-01-20",
                "类别": "焊机",
                "申请人": "王五",
                "焊机编号": "WM002",
                "故障现象": "无法启动",
                "故障原因": "主控板故障",
                "维修内容": "更换主控板",
                "维修人员": "赵工",
                "维修日期": "2024-01-21",
                "维修费用": 2500.00,
                "备注": "保修期内免费更换"
            },
            {
                "序号": 3,
                "报修日期": "2024-02-05",
                "类别": "焊机",
                "申请人": "刘七",
                "焊机编号": "WM003",
                "故障现象": "焊接质量差",
                "故障原因": "焊枪磨损严重",
                "维修内容": "更换焊枪及相关配件",
                "维修人员": "孙工",
                "维修日期": "2024-02-06",
                "维修费用": 800.00,
                "备注": "定期保养"
            },
            {
                "序号": 4,
                "报修日期": "2024-02-15",
                "类别": "焊机",
                "申请人": "陈八",
                "焊机编号": "WM004",
                "故障现象": "过热保护频繁触发",
                "故障原因": "散热风扇故障",
                "维修内容": "清洁散热器，更换风扇",
                "维修人员": "周工",
                "维修日期": "2024-02-16",
                "维修费用": 300.00,
                "备注": "建议定期清洁"
            },
            {
                "序号": 5,
                "报修日期": "2024-03-01",
                "类别": "焊机",
                "申请人": "吴九",
                "焊机编号": "WM005",
                "故障现象": "焊接参数无法调节",
                "故障原因": "控制面板按键失灵",
                "维修内容": "更换控制面板",
                "维修人员": "郑工",
                "维修日期": "2024-03-02",
                "维修费用": 1500.00,
                "备注": "升级到新版本面板"
            },
            {
                "序号": 6,
                "报修日期": "2024-03-10",
                "类别": "焊机",
                "申请人": "钱十",
                "焊机编号": "WM006",
                "故障现象": "焊接时有异响",
                "故障原因": "变压器松动",
                "维修内容": "紧固变压器，检查绝缘",
                "维修人员": "冯工",
                "维修日期": "2024-03-11",
                "维修费用": 200.00,
                "备注": "预防性维护"
            },
            {
                "序号": 7,
                "报修日期": "2024-03-20",
                "类别": "焊机",
                "申请人": "朱一",
                "焊机编号": "WM007",
                "故障现象": "焊接电弧不稳定",
                "故障原因": "电极磨损",
                "维修内容": "更换电极，调整参数",
                "维修人员": "卫工",
                "维修日期": "2024-03-21",
                "维修费用": 150.00,
                "备注": "常规维护"
            },
            {
                "序号": 8,
                "报修日期": "2024-04-01",
                "类别": "焊机",
                "申请人": "蒋二",
                "焊机编号": "WM008",
                "故障现象": "保护气流量异常",
                "故障原因": "气路堵塞",
                "维修内容": "清洁气路，更换过滤器",
                "维修人员": "韩工",
                "维修日期": "2024-04-02",
                "维修费用": 100.00,
                "备注": "定期更换过滤器"
            },
            {
                "序号": 9,
                "报修日期": "2024-04-15",
                "类别": "焊机",
                "申请人": "杨三",
                "焊机编号": "WM009",
                "故障现象": "送丝不均匀",
                "故障原因": "送丝轮磨损",
                "维修内容": "更换送丝轮，调整送丝速度",
                "维修人员": "杨工",
                "维修日期": "2024-04-16",
                "维修费用": 250.00,
                "备注": "已校准送丝系统"
            },
            {
                "序号": 10,
                "报修日期": "2024-05-01",
                "类别": "焊机",
                "申请人": "朱四",
                "焊机编号": "WM010",
                "故障现象": "显示屏无显示",
                "故障原因": "显示模块故障",
                "维修内容": "更换显示模块",
                "维修人员": "秦工",
                "维修日期": "2024-05-02",
                "维修费用": 600.00,
                "备注": "保修期内维修"
            }
        ]
        
        return repair_data
    
    def parse_date(self, date_str: str) -> datetime:
        """解析日期字符串
        
        Args:
            date_str: 日期字符串
            
        Returns:
            datetime对象
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # 尝试其他日期格式
            try:
                return datetime.strptime(date_str, "%Y/%m/%d")
            except ValueError:
                return datetime.now()
    
    def generate_repair_code(self, device_code: str, repair_date: datetime) -> str:
        """生成维修单号
        
        Args:
            device_code: 设备编号
            repair_date: 维修日期
            
        Returns:
            维修单号
        """
        date_str = repair_date.strftime("%Y%m%d")
        return f"R{date_str}{device_code[-3:]}"
    
    async def ensure_device_exists(self, device_code: str, device_type: str = "焊机") -> Optional[DeviceInfo]:
        """确保设备存在，如果不存在则创建
        
        Args:
            device_code: 设备编号
            device_type: 设备类型
            
        Returns:
            设备信息对象
        """
        try:
            # 查找设备
            device = await DeviceInfo.get_or_none(device_code=device_code)
            if device:
                return device
            
            # 确保设备类型存在
            device_type_obj = await DeviceType.get_or_none(type_name=device_type)
            if not device_type_obj:
                # 创建设备类型
                device_type_obj = await DeviceType.create(
                    type_code=device_type.upper(),
                    type_name=device_type,
                    description=f"{device_type}设备类型",
                    device_count=0
                )
            
            # 创建设备
            device_data = DeviceCreate(
                device_code=device_code,
                device_name=f"{device_type}-{device_code}",
                device_type=device_type_obj.type_code,
                manufacturer="未知厂家",
                device_model="标准型",
                installation_location="生产车间",
                installation_date=datetime.now(),
                device_status="正常",
                online_address="192.168.1.100",
                team_name="维修班组",
                description=f"从维修记录导入的{device_type}设备"
            )
            
            device = await self.device_controller.create_device(device_data)
            print(f"✓ 创建设备: {device_code}")
            return device
            
        except Exception as e:
            error_msg = f"创建设备 {device_code} 失败: {str(e)}"
            print(f"✗ {error_msg}")
            self.errors.append(error_msg)
            return None
    
    async def import_repair_record(self, record_data: Dict[str, Any]) -> bool:
        """导入单条维修记录
        
        Args:
            record_data: 维修记录数据
            
        Returns:
            是否导入成功
        """
        try:
            device_code = record_data["焊机编号"]
            
            # 确保设备存在
            device = await self.ensure_device_exists(device_code, record_data["类别"])
            if not device:
                return False
            
            # 解析日期
            repair_date = self.parse_date(record_data["报修日期"])
            maintenance_date = self.parse_date(record_data["维修日期"])
            
            # 生成维修单号
            repair_code = self.generate_repair_code(device_code, repair_date)
            
            # 检查维修记录是否已存在
            existing_record = await DeviceRepairRecord.get_or_none(repair_code=repair_code)
            if existing_record:
                print(f"⚠ 维修记录已存在: {repair_code}")
                return True
            
            # 创建维修记录
            repair_record_data = DeviceRepairRecordCreate(
                device_id=device.id,
                device_type="welding",  # 焊机类型
                repair_code=repair_code,
                repair_date=repair_date,
                fault_phenomenon=record_data["故障现象"],
                fault_reason=record_data["故障原因"],
                repair_content=record_data["维修内容"],
                repair_personnel=record_data["维修人员"],
                maintenance_date=maintenance_date,
                repair_cost=float(record_data["维修费用"]),
                applicant=record_data["申请人"],
                repair_status="已完成",
                priority="中",
                maintenance_type="故障维修",
                notes=record_data["备注"]
            )
            
            # 保存到数据库
            await DeviceRepairRecord.create(**repair_record_data.model_dump())
            
            print(f"✓ 导入维修记录: {repair_code} - {device_code}")
            self.imported_count += 1
            return True
            
        except Exception as e:
            error_msg = f"导入维修记录失败 (序号: {record_data.get('序号', 'N/A')}): {str(e)}"
            print(f"✗ {error_msg}")
            self.errors.append(error_msg)
            self.error_count += 1
            return False
    
    async def import_all_records(self):
        """导入所有维修记录"""
        print("开始导入焊机维修记录...")
        print("=" * 50)
        
        # 获取数据
        repair_records = self.parse_repair_records_data()
        total_count = len(repair_records)
        
        print(f"共找到 {total_count} 条维修记录")
        print("-" * 50)
        
        # 逐条导入
        for i, record in enumerate(repair_records, 1):
            print(f"[{i}/{total_count}] 处理维修记录...")
            await self.import_repair_record(record)
            print()
        
        # 输出统计信息
        print("=" * 50)
        print("导入完成!")
        print(f"总记录数: {total_count}")
        print(f"成功导入: {self.imported_count}")
        print(f"失败记录: {self.error_count}")
        
        if self.errors:
            print("\n错误详情:")
            for error in self.errors:
                print(f"  - {error}")
    
    async def run(self):
        """运行导入程序"""
        try:
            await self.init_database()
            await self.import_all_records()
        except Exception as e:
            print(f"导入程序运行失败: {str(e)}")
        finally:
            await self.close_database()


async def main():
    """主函数"""
    importer = RepairRecordImporter()
    await importer.run()


if __name__ == "__main__":
    asyncio.run(main())