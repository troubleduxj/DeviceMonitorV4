import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple

from fastapi import HTTPException
from loguru import logger
from tortoise.expressions import Q

from app.core.crud import CRUDBase
from app.models.device import DeviceInfo, DeviceType, DeviceRealTimeData
from app.models.system import SysDictData
from app.schemas.devices import DeviceRealTimeDataCreate, DeviceRealtimeQuery
from app.core.tdengine_connector import TDengineConnector
from app.core.database import get_db_connection
from app.settings.config import settings


class DeviceDataController(CRUDBase[DeviceInfo, DeviceRealTimeDataCreate, dict]):
    """设备数据控制器

    提供设备实时数据和历史数据的CRUD操作和业务逻辑处理
    """

    def __init__(self):
        super().__init__(model=DeviceRealTimeData)

    async def create_realtime_data(self, obj_in: DeviceRealTimeDataCreate) -> DeviceInfo:
        """创建设备实时数据

        Args:
            obj_in: 实时数据创建对象

        Returns:
            创建的实时数据对象

        Raises:
            HTTPException: 当设备不存在或创建失败时
        """
        try:
            # 检查设备是否存在
            device = await DeviceInfo.filter(id=obj_in.device_id).first()
            if not device:
                raise HTTPException(status_code=404, detail="设备不存在")

            # 创建实时数据记录
            now = datetime.now()
            create_data = obj_in.dict()
            create_data.update({"created_at": now, "updated_at": now})

            realtime_data = await self.model.create(**create_data)

            return realtime_data

        except HTTPException:
            raise
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail={"message": "创建实时数据失败", "error": str(e), "error_type": type(e).__name__}
            )

    async def get_device_latest_data(self, device_id: int) -> Optional[DeviceRealTimeData]:
        """获取设备最新实时数据

        Args:
            device_id: 设备ID

        Returns:
            最新实时数据对象或None
        """
        return await self.model.filter(device_id=device_id).order_by("-data_timestamp").first()

    async def get_device_latest_data_by_code(self, device_code: str) -> Optional[DeviceRealTimeData]:
        """根据设备编号获取最新实时数据

        Args:
            device_code: 设备编号

        Returns:
            最新实时数据对象或None
        """
        return await self.model.filter(device__device_code=device_code).order_by("-data_timestamp").first()

    async def get_devices_status_summary(self) -> List[dict]:
        """获取所有设备状态汇总

        Returns:
            设备状态汇总列表
        """
        try:
            # 获取所有设备及其最新数据
            devices = await DeviceInfo.all()
            summary = []

            for device in devices:
                latest_data = await self.get_device_latest_data(device.id)

                device_summary = {
                    "device_id": device.id,
                    "device_code": device.device_code,
                    "device_name": device.device_name,
                    "device_type": device.device_type,
                    "install_location": device.install_location,
                    "current_status": latest_data.status if latest_data else "offline",
                    "last_update": latest_data.data_timestamp if latest_data else None,
                    "voltage": latest_data.voltage if latest_data else None,
                    "current": latest_data.current if latest_data else None,
                    "power": latest_data.power if latest_data else None,
                    "temperature": latest_data.temperature if latest_data else None,
                }
                summary.append(device_summary)

            return summary

        except Exception as e:
            import traceback

            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail={"message": "获取设备状态汇总失败", "error": str(e), "error_type": type(e).__name__},
            )

    async def get_online_devices_count(self) -> int:
        """获取在线设备数量

        Returns:
            在线设备数量
        """
        # 获取最新状态为online的设备数量
        # 这里需要一个子查询来获取每个设备的最新记录
        from tortoise.query_utils import Q

        # 简化实现：获取所有设备，然后检查每个设备的最新状态
        devices = await DeviceInfo.all()
        online_count = 0

        for device in devices:
            latest_data = await self.get_device_latest_data(device.id)
            if latest_data and latest_data.status == "online":
                online_count += 1

        return online_count

    async def get_device_history_data(
        self,
        device_id: Optional[int] = None,
        device_code: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[int, List[dict]]:
        """查询设备历史数据

        Args:
            device_id: 设备ID
            device_code: 设备编号
            start_time: 开始时间
            end_time: 结束时间
            status: 设备状态
            page: 页码
            page_size: 每页数量

        Returns:
            元组(总数量, 历史数据列表)
        """
        from app.core.tdengine_connector import TDengineConnector
        from app.models.device import DeviceInfo, DeviceType
        from datetime import datetime, timezone

        logger.debug(
            f"get_device_history_data called with: device_id={device_id}, device_code={device_code}, start_time={start_time}, end_time={end_time}, status={status}, page={page}, page_size={page_size}"
        )

        # 构建查询条件
        conditions = []
        table_name = None

        if device_code:
            # 验证设备编号是否存在
            device_info = await DeviceInfo.filter(device_code=device_code).first()
            if not device_info:
                logger.warning(f"设备编号 {device_code} 不存在，无法查询历史数据")
                return 0, []
            # TDengine 的表名是 t_device_code
            table_name = f"t_{device_code}"
            logger.debug(f"Constructed TDengine table name: {table_name}")
        else:
            logger.warning("未提供设备编号，无法查询历史数据")
            return 0, []  # 设备编号是必须的

        if start_time:
            # TDengine 时间戳格式
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            conditions.append(f"ts >= '{start_time_str}'")
        if end_time:
            # TDengine 时间戳格式
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            conditions.append(f"ts <= '{end_time_str}'")
        if status:
            conditions.append(f"device_status = '{status}'")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 获取TDengine配置并初始化连接器
        from app.settings.config import settings, TDengineCredentials

        tdengine_creds = TDengineCredentials()
        td_connector = TDengineConnector(
            host=tdengine_creds.host,
            port=tdengine_creds.port,
            user=tdengine_creds.user,
            password=tdengine_creds.password,
            database=tdengine_creds.database,
        )
        try:
            # 查询总数
            count_sql = f"SELECT count(*) FROM {table_name} WHERE {where_clause}"
            logger.debug(f"Executing count SQL: {count_sql}")
            count_result = await td_connector.query_data(count_sql)
            total_count = count_result["data"][0][0] if count_result and count_result.get("data") else 0
            logger.debug(f"Total count: {total_count}")

            # 对于历史曲线图，返回时间段内的所有数据点（不分页）
            # 对于表格视图，仍然使用分页
            if page_size >= 1000:  # 当page_size很大时，认为是图表查询，返回所有数据
                query_sql = f"SELECT ts, team_name, device_code, device_status, lock_status, preset_current, preset_voltage, weld_current, weld_voltage, material, wire_diameter, gas_type, weld_method, weld_control, staff_id, workpiece_id FROM {table_name} WHERE {where_clause} ORDER BY ts ASC"
                logger.debug(f"Executing full data query SQL for chart: {query_sql}")
            else:
                # 构建分页查询
                offset = (page - 1) * page_size
                limit = page_size
                query_sql = f"SELECT ts, team_name, device_code, device_status, lock_status, preset_current, preset_voltage, weld_current, weld_voltage, material, wire_diameter, gas_type, weld_method, weld_control, staff_id, workpiece_id FROM {table_name} WHERE {where_clause} ORDER BY ts DESC LIMIT {limit} OFFSET {offset}"
                logger.debug(f"Executing paginated data query SQL: {query_sql}")

            query_result = await td_connector.query_data(query_sql)
            records = query_result.get("data", []) if query_result else []
            logger.debug(f"Query records count: {len(records)}")

            # 将查询结果转换为字典列表
            result_list = []
            if records:
                # 根据实际的 welding_real_data 超级表结构定义列名
                column_names = [
                    "ts",
                    "team_name",
                    "device_code",
                    "device_status",
                    "lock_status",
                    "preset_current",
                    "preset_voltage",
                    "weld_current",
                    "weld_voltage",
                    "material",
                    "wire_diameter",
                    "gas_type",
                    "weld_method",
                    "weld_control",
                    "staff_id",
                    "workpiece_id",
                ]
                for record in records:
                    record_dict = dict(zip(column_names, record))
                    # 时间戳已经是字符串格式，直接使用
                    record_dict["data_timestamp"] = record_dict["ts"]
                    result_list.append(record_dict)

            return total_count, result_list

        except Exception as e:
            logger.error(f"查询设备历史数据失败: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"查询设备历史数据失败: {e}")

    async def update_device_realtime_data(self, device_id: int, data: dict) -> DeviceRealTimeData:
        """更新设备实时数据（覆盖式更新）

        Args:
            device_id: 设备ID
            data: 更新数据

        Returns:
            更新后的实时数据对象
        """
        try:
            # 检查设备是否存在
            device = await DeviceInfo.filter(id=device_id).first()
            if not device:
                raise HTTPException(status_code=404, detail="设备不存在")

            # 获取或创建实时数据记录
            realtime_data = await self.get_device_latest_data(device_id)

            now = datetime.now()
            data.update({"updated_at": now, "data_timestamp": now})

            if realtime_data:
                # 更新现有记录
                await self.model.filter(id=realtime_data.id).update(**data)
                realtime_data = await self.model.filter(id=realtime_data.id).first()
            else:
                # 创建新记录
                data.update({"device_id": device_id, "created_at": now})
                realtime_data = await self.model.create(**data)

            # 同时创建历史数据记录
            history_data = data.copy()
            history_data.update({"device_id": device_id, "created_at": now})
            await DeviceHistoryData.create(**history_data)

            return realtime_data

        except HTTPException:
            raise
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail={"message": "更新实时数据失败", "error": str(e), "error_type": type(e).__name__}
            )

    async def get_device_realtime_data(self, query: DeviceRealtimeQuery) -> dict:
        """
        获取设备实时数据

        Args:
            query: 查询参数，包含分页、设备代码等信息

        Returns:
            dict: 包含设备实时数据的字典
        """
        if query.paged:
            return await self._get_device_realtime_data_paged(query)
        else:
            return await self._get_device_realtime_data_unpaged(query)

    async def _get_device_realtime_data_unpaged(self, query: DeviceRealtimeQuery) -> dict:
        """
        获取设备实时数据（旧版-全量查询）
        """
        try:
            # 验证设备存在性（如果指定了device_code或device_codes）
            if query.device_code:
                device_exists = await DeviceInfo.filter(
                    device_code=query.device_code, device_type=query.type_code
                ).exists()
                if not device_exists:
                    raise HTTPException(status_code=404, detail=f"设备 {query.device_code} 不存在或类型不匹配")
            elif query.device_codes:
                # 验证设备编码列表中的设备是否存在
                existing_devices = await DeviceInfo.filter(
                    device_code__in=query.device_codes, device_type=query.type_code
                ).values_list("device_code", flat=True)

                missing_devices = set(query.device_codes) - set(existing_devices)
                if missing_devices:
                    raise HTTPException(
                        status_code=404, detail=f"以下设备不存在或类型不匹配: {', '.join(missing_devices)}"
                    )

            # 根据type_code查询对应类型的设备信息
            # 1. 从PostgreSQL查询指定类型的设备
            device_filter = {"device_type": query.type_code}
            if query.device_code:
                device_filter["device_code"] = query.device_code
            elif query.device_codes:
                device_filter["device_code__in"] = query.device_codes

            devices = await DeviceInfo.filter(**device_filter).all()

            if not devices:
                return {
                    "items": [],
                    "total": 0,
                    "page": query.page,
                    "page_size": query.page_size,
                    "type_code": query.type_code,
                }

            # 2. 计算分页范围
            total_devices = len(devices)
            start_index = (query.page - 1) * query.page_size
            end_index = start_index + query.page_size

            # 3. 获取当前页的设备列表
            current_page_devices = devices[start_index:end_index]

            # 4. 批量从TDengine查询实时数据（性能优化）
            realtime_data_list = []

            # 初始化TDengine连接器（移到循环外）
            from app.settings.config import TDengineCredentials

            tdengine_creds = TDengineCredentials()
            logger.info(
                f"初始化TDengine连接器: host={tdengine_creds.host}, port={tdengine_creds.port}, database={tdengine_creds.database}"
            )
            tdengine_connector = TDengineConnector(
                host=tdengine_creds.host,
                port=tdengine_creds.port,
                user=tdengine_creds.user,
                password=tdengine_creds.password,
                database=tdengine_creds.database,
            )
            logger.info("TDengine连接器初始化完成")

            # 根据设备类型获取对应的TDengine超级表名
            device_type_obj = await DeviceType.filter(type_code=query.type_code, is_active=True).first()
            if not device_type_obj:
                raise HTTPException(status_code=404, detail=f"设备类型 {query.type_code} 不存在或未激活")
            
            super_table_name = device_type_obj.tdengine_stable_name
            logger.info(f"使用TDengine超级表: {super_table_name} (设备类型: {query.type_code})")

            where_clause = ""
            if query.device_codes:
                codes_str = ", ".join([f"'{code}'" for code in query.device_codes])
                where_clause = f"WHERE device_code IN ({codes_str})"
            elif query.device_code:
                where_clause = f"WHERE device_code = '{query.device_code}'"

            if where_clause:
                batch_sql = (
                    f"SELECT LAST_ROW(*), device_code FROM {super_table_name} {where_clause} GROUP BY device_code;"
                )
            else:
                batch_sql = f"SELECT LAST_ROW(*), device_code FROM {super_table_name} GROUP BY device_code;"

            logger.info(f"准备执行TDengine超级表查询")
            logger.debug(f"超级表查询SQL: {batch_sql}")

            if current_page_devices:
                try:
                    raw_result = await tdengine_connector.execute_sql(batch_sql, target_db=tdengine_creds.database)
                    device_data_map = {}
                    if isinstance(raw_result, dict) and "data" in raw_result and "column_meta" in raw_result:
                        columns = [col[0] for col in raw_result["column_meta"]]
                        rows = raw_result["data"]
                        for row in rows:
                            row_dict = dict(zip(columns, row))
                            device_code = row_dict.get("device_code")
                            if device_code:
                                device_data_map[device_code] = row_dict
                            else:
                                logger.warning(f"Row data missing device_code: {row_dict}. This row will be skipped.")

                    for device in current_page_devices:
                        row_data = device_data_map.get(device.device_code)
                        if row_data:
                            data_fields = {}
                            # 根据welding_real_data表结构，TAGS字段应该是device_code和name
                            tag_fields = {
                                "device_code": device.device_code,
                                "name": device.device_name or ""
                            }

                            def get_field_value(row_data, field_name):
                                if field_name in row_data:
                                    return row_data.get(field_name)
                                last_row_field = f"last_row({field_name})"
                                if last_row_field in row_data:
                                    return row_data.get(last_row_field)
                                return None

                            if query.type_code == "welding":
                                data_fields = {
                                    "preset_current": get_field_value(row_data, "preset_current"),
                                    "preset_voltage": get_field_value(row_data, "preset_voltage"),
                                    "weld_current": get_field_value(row_data, "weld_current"),
                                    "weld_voltage": get_field_value(row_data, "weld_voltage"),
                                    "device_status": get_field_value(row_data, "device_status") or "unknown",
                                    "lock_status": get_field_value(row_data, "lock_status"),
                                    "team_name": get_field_value(row_data, "team_name"),
                                    "operator": get_field_value(row_data, "operator"),
                                    "material": get_field_value(row_data, "material"),
                                    "wire_diameter": get_field_value(row_data, "wire_diameter"),
                                    "gas_type": get_field_value(row_data, "gas_type"),
                                    "weld_method": get_field_value(row_data, "weld_method"),
                                    "weld_control": get_field_value(row_data, "weld_control"),
                                    "staff_id": get_field_value(row_data, "staff_id"),
                                    "workpiece_id": get_field_value(row_data, "workpiece_id"),
                                    "ip_quality": get_field_value(row_data, "ip_quality"),
                                }
                                # TAGS字段只包含device_code和name，不包含operator

                            ts_value = get_field_value(row_data, "ts")
                            ts_formatted = str(ts_value) if ts_value else None

                            device_data = {
                                "device_code": device.device_code,
                                "device_name": get_field_value(row_data, "name") or "",
                                "type_code": query.type_code,
                                "ts": ts_formatted,
                            }
                            device_data.update(data_fields)
                            device_data.update(tag_fields)
                            realtime_data_list.append(device_data)
                        else:
                            device_data = {
                                "device_code": device.device_code,
                                "device_name": "",
                                "type_code": query.type_code,
                                "ts": None,
                                "preset_current": None,
                                "preset_voltage": None,
                                "weld_current": None,
                                "weld_voltage": None,
                                "device_status": "offline",
                                "lock_status": None,
                                "team_name": None,
                                "operator": None,
                                "material": None,
                                "wire_diameter": None,
                                "gas_type": None,
                                "weld_method": None,
                                "weld_control": None,
                                "staff_id": None,
                                "workpiece_id": None,
                                "ip_quality": None,
                                "name": device.device_name or "",
                            }
                            realtime_data_list.append(device_data)
                except Exception as device_error:
                    logger.error(f"处理设备实时数据时发生错误: {str(device_error)}", exc_info=True)
                    for device_in_page in current_page_devices:
                        device_data = {
                            "device_code": device_in_page.device_code,
                            "device_name": "",
                            "type_code": query.type_code,
                            "ts": None,
                            "preset_current": None,
                            "preset_voltage": None,
                            "weld_current": None,
                            "weld_voltage": None,
                            "device_status": "error",
                            "lock_status": None,
                            "team_name": None,
                            "operator": None,
                            "material": None,
                            "wire_diameter": None,
                            "gas_type": None,
                            "weld_method": None,
                            "weld_control": None,
                            "staff_id": None,
                            "workpiece_id": None,
                            "ip_quality": None,
                            "name": device_in_page.device_name or "",
                        }
                        realtime_data_list.append(device_data)

            await tdengine_connector.close()

            return {
                "items": realtime_data_list,
                "total": total_devices,
                "page": query.page,
                "page_size": query.page_size,
                "type_code": query.type_code,
            }
        except Exception as e:
            logger.error(f"获取设备实时数据失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={"message": "获取设备实时数据失败", "error": str(e), "error_type": type(e).__name__},
            )

    async def _get_device_realtime_data_paged(self, query: DeviceRealtimeQuery) -> dict:
        """
        获取设备实时数据（新版-分页优化）
        """
        tdengine_connector = None
        try:
            # 1. 构建基础查询，并应用分页
            device_query = DeviceInfo.filter(device_type=query.type_code)
            if query.device_code:
                device_query = device_query.filter(device_code=query.device_code)
            elif query.device_codes:
                device_query = device_query.filter(device_code__in=query.device_codes)

            total_devices = await device_query.count()

            # 在数据库层面进行分页
            current_page_devices = await device_query.offset((query.page - 1) * query.page_size).limit(query.page_size)

            if not current_page_devices:
                return {
                    "items": [],
                    "total": 0,
                    "page": query.page,
                    "page_size": query.page_size,
                    "type_code": query.type_code,
                }

            # 2. 仅针对当前页的设备查询TDengine
            device_codes_for_tdengine = [d.device_code for d in current_page_devices]
            realtime_data_list = []

            from app.settings.config import TDengineCredentials

            tdengine_creds = TDengineCredentials()
            tdengine_connector = TDengineConnector(
                host=tdengine_creds.host,
                port=tdengine_creds.port,
                user=tdengine_creds.user,
                password=tdengine_creds.password,
                database=tdengine_creds.database,
            )

            # 根据设备类型获取对应的TDengine超级表名
            device_type_obj = await DeviceType.filter(type_code=query.type_code, is_active=True).first()
            if not device_type_obj:
                raise HTTPException(status_code=404, detail=f"设备类型 {query.type_code} 不存在或未激活")
            
            super_table_name = device_type_obj.tdengine_stable_name
            logger.info(f"使用TDengine超级表: {super_table_name} (设备类型: {query.type_code})")
            codes_str = ", ".join([f"'{code}'" for code in device_codes_for_tdengine])
            where_clause = f"WHERE device_code IN ({codes_str})"

            batch_sql = f"SELECT LAST_ROW(*), device_code FROM {super_table_name} {where_clause} GROUP BY device_code;"
            logger.debug(f"PAGED - TDengine SQL: {batch_sql}")

            raw_result = await tdengine_connector.execute_sql(batch_sql, target_db=tdengine_creds.database)

            device_data_map = {}
            if isinstance(raw_result, dict) and "data" in raw_result and "column_meta" in raw_result:
                columns = [col[0] for col in raw_result["column_meta"]]
                for row in raw_result["data"]:
                    row_dict = dict(zip(columns, row))
                    if row_dict.get("device_code"):
                        device_data_map[row_dict["device_code"]] = row_dict

            # 3. 合并数据
            for device in current_page_devices:
                row_data = device_data_map.get(device.device_code)
                if row_data:

                    def get_field_value(row_data, field_name):
                        return row_data.get(field_name) or row_data.get(f"last_row({field_name})")

                    data_fields = {
                        "preset_current": get_field_value(row_data, "preset_current"),
                        "preset_voltage": get_field_value(row_data, "preset_voltage"),
                        "weld_current": get_field_value(row_data, "weld_current"),
                        "weld_voltage": get_field_value(row_data, "weld_voltage"),
                        "device_status": get_field_value(row_data, "device_status") or "unknown",
                        # 扩展字段 - 前端表格需要的字段
                        "team_name": get_field_value(row_data, "team_name"),
                        "operator": get_field_value(row_data, "operator"),
                        "staff_id": get_field_value(row_data, "staff_id"),
                        "material": get_field_value(row_data, "material"),
                        "wire_diameter": get_field_value(row_data, "wire_diameter"),
                        "gas_type": get_field_value(row_data, "gas_type"),
                        "weld_method": get_field_value(row_data, "weld_method"),
                        "weld_control": get_field_value(row_data, "weld_control"),
                        "workpiece_id": get_field_value(row_data, "workpiece_id"),
                        "lock_status": get_field_value(row_data, "lock_status"),
                        "ip_quality": get_field_value(row_data, "ip_quality"),
                    }
                    ts_value = get_field_value(row_data, "ts")
                    # 从TDengine的name标签获取设备名称
                    tdengine_name = get_field_value(row_data, "name") or ""

                    device_data = {
                        "device_code": device.device_code,
                        "device_name": tdengine_name,
                        "type_code": query.type_code,
                        "ts": str(ts_value) if ts_value else None,
                        **data_fields,
                    }
                    realtime_data_list.append(device_data)
                else:
                    # TDengine中无数据
                    device_data = {
                        "device_code": device.device_code,
                        "device_name": "",
                        "type_code": query.type_code,
                        "ts": None,
                        "device_status": "offline",  # ... other fields null
                    }
                    realtime_data_list.append(device_data)

            return {
                "items": realtime_data_list,
                "total": total_devices,
                "page": query.page,
                "page_size": query.page_size,
                "type_code": query.type_code,
            }
        except Exception as e:
            logger.error(f"获取设备实时数据失败(分页): {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail={"message": "获取设备实时数据失败(分页)", "error": str(e)})
        finally:
            if tdengine_connector:
                await tdengine_connector.close()

    async def get_realtime_device_status(self, device_type: str) -> dict:
        """获取指定类型设备的实时状态统计

        从一个包含聚合数据的普通表中获取最新一条记录。

        Args:
            device_type: 设备类型代码 (e.g., 'welding')

        Returns:
            设备实时状态统计字典
        """
        tdengine_connector = None
        try:
            logger.info(f"开始获取设备聚合状态，类型: {device_type}")
            db_name = "hlzg_db"

            # 从数据字典获取表名
            dict_entry = await SysDictData.filter(dict_type__type_code='welding_indicator_mapping', data_label='实时状态统计').first()
            if not dict_entry:
                logger.error("未找到数据字典中'焊机统计指标对照'类型下'实时状态统计'的配置。")
                return {
                    "total_devices": 0,
                    "standby_devices": 0,
                    "welding_devices": 0,
                    "alarm_devices": 0,
                    "shutdown_devices": 0,
                    "standby_rate": 0.0,
                    "welding_rate": 0.0,
                    "alarm_rate": 0.0,
                    "shutdown_rate": 0.0,
                    "last_update_time": None,
                }
            table_name = dict_entry.data_value
            logger.debug(f"目标表名: {table_name}，数据库: {db_name}")

            from app.settings.config import TDengineCredentials

            tdengine_creds = TDengineCredentials()

            tdengine_connector = TDengineConnector(
                host=tdengine_creds.host,
                port=tdengine_creds.port,
                user=tdengine_creds.user,
                password=tdengine_creds.password,
                database=tdengine_creds.database,
            )

            # 使用 last_row(*) 查询获取最新数据
            query_sql = f"SELECT last_row(*) FROM {table_name}"

            logger.info(f"准备执行TDengine查询: {query_sql} on database {db_name}")
            result = await tdengine_connector.execute_sql(query_sql, target_db=db_name)
            logger.info("TDengine查询执行完毕。")
            logger.debug(f"TDengine返回的原始结果: {result}")

            # last_row(*) 返回的数据结构需要解析
            logger.info(f"检查TDengine结果: result存在={bool(result)}, data存在={bool(result and result.get('data'))}, column_meta存在={bool(result and result.get('column_meta'))}")
            logger.info(f"result类型: {type(result)}, result内容: {result}")
            
            # 详细检查每个条件
            result_exists = bool(result)
            data_exists = bool(result and result.get('data'))
            column_meta_exists = bool(result and result.get('column_meta'))
            
            logger.info(f"条件检查详情: result_exists={result_exists}, data_exists={data_exists}, column_meta_exists={column_meta_exists}")
            
            if not (result and result.get("data") and result.get("column_meta")):
                logger.warning(f"在表 {table_name} 中未找到任何数据，返回全0结果")
                return {
                    "total_devices": 0,
                    "standby_devices": 0,
                    "welding_devices": 0,
                    "alarm_devices": 0,
                    "shutdown_devices": 0,
                    "standby_rate": 0.0,
                    "welding_rate": 0.0,
                    "alarm_rate": 0.0,
                    "shutdown_rate": 0.0,
                    "last_update_time": None,
                }

            # 将列名和数据行组合成字典
            columns = [meta[0] for meta in result["column_meta"]]
            row_values = result["data"][0]
            latest_data = dict(zip(columns, row_values))
            
            logger.info(f"解析后的数据字典: {latest_data}")

            # 从带有 'last_row()' 前缀的键中获取数据
            # 根据实际表结构获取数据
            standby_devices = int(latest_data.get("last_row(status_standby)", 0))
            welding_devices = int(latest_data.get("last_row(status_welding)", 0))
            alarm_devices = int(latest_data.get("last_row(status_alarm)", 0))
            shutdown_devices = int(latest_data.get("last_row(status_shutdown)", 0))
            last_update_time = latest_data.get("last_row(ts)")
            
            logger.info(f"解析的设备数量 - standby: {standby_devices}, welding: {welding_devices}, alarm: {alarm_devices}, shutdown: {shutdown_devices}")
            
            # 计算总设备数
            total_devices = standby_devices + welding_devices + alarm_devices + shutdown_devices
            logger.info(f"计算的总设备数: {total_devices}")
            
            # 计算总设备数
            total_devices = standby_devices + welding_devices + alarm_devices + shutdown_devices

            # 计算比率
            standby_rate = (standby_devices / total_devices * 100) if total_devices > 0 else 0.0
            welding_rate = (welding_devices / total_devices * 100) if total_devices > 0 else 0.0
            alarm_rate = (alarm_devices / total_devices * 100) if total_devices > 0 else 0.0
            shutdown_rate = (shutdown_devices / total_devices * 100) if total_devices > 0 else 0.0

            # 处理时间戳格式
            formatted_time = None
            if last_update_time:
                try:
                    # 如果是datetime对象，直接转换
                    if hasattr(last_update_time, 'isoformat'):
                        formatted_time = last_update_time.isoformat()
                    else:
                        # 如果是字符串，直接使用
                        formatted_time = str(last_update_time)
                except Exception as time_error:
                    logger.warning(f"时间戳格式转换失败: {time_error}, 原始值: {last_update_time}")
                    formatted_time = str(last_update_time)

            return {
                "total_devices": total_devices,
                "standby_devices": standby_devices,
                "welding_devices": welding_devices,
                "alarm_devices": alarm_devices,
                "shutdown_devices": shutdown_devices,
                "standby_rate": round(standby_rate, 1),
                "welding_rate": round(welding_rate, 1),
                "alarm_rate": round(alarm_rate, 1),
                "shutdown_rate": round(shutdown_rate, 1),
                "last_update_time": formatted_time,
            }



        except Exception as e:
            logger.error(f"获取设备聚合状态时发生严重错误: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail={"message": f"获取设备实时状态失败: {e}", "error_type": type(e).__name__}
            )
        finally:
            if tdengine_connector:
                await tdengine_connector.close()

    async def get_device_status_statistics(self, type_code: Optional[str] = None) -> dict:
        """获取设备状态统计信息

        直接从TDengine的hlzg_db.welding_status_real_summary表获取实时汇总数据

        Args:
            type_code: 设备类型代码，暂时保留参数但不使用（汇总表是全局统计）

        Returns:
            设备状态统计字典
        """
        try:
            # 获取TDengine配置并初始化连接器
            from app.settings.config import TDengineCredentials

            tdengine_creds = TDengineCredentials()
            tdengine_connector = TDengineConnector(
                host=tdengine_creds.host,
                port=tdengine_creds.port,
                user=tdengine_creds.user,
                password=tdengine_creds.password,
                database=tdengine_creds.database,
            )

            # 查询最新的设备状态汇总数据
            query_sql = """
                SELECT status_standby, status_welding, status_alarm, status_shutdown, ts
                FROM hlzg_db.welding_status_real_summary 
                WHERE name='welding_status_real_summary' 
                ORDER BY ts DESC 
                LIMIT 1
            """

            logger.info(f"执行TDengine查询: {query_sql}")
            result = await tdengine_connector.execute_sql(query_sql)

            # 关闭TDengine连接
            await tdengine_connector.close()

            # 解析TDengine REST API响应格式
            data_rows = []
            if isinstance(result, dict) and "data" in result:
                data_rows = result["data"]
            elif isinstance(result, list):
                data_rows = result

            if not data_rows or len(data_rows) == 0:
                logger.warning("未找到设备状态汇总数据")
                return {
                    "total_devices": 0,
                    "standby_devices": 0,
                    "welding_devices": 0,
                    "alarm_devices": 0,
                    "shutdown_devices": 0,
                    "standby_rate": 0.0,
                    "welding_rate": 0.0,
                    "alarm_rate": 0.0,
                    "shutdown_rate": 0.0,
                    "last_update_time": None,
                }

            # 解析查询结果
            row = data_rows[0]
            standby_count = int(row[0]) if row[0] is not None else 0
            welding_count = int(row[1]) if row[1] is not None else 0
            alarm_count = int(row[2]) if row[2] is not None else 0
            shutdown_count = int(row[3]) if row[3] is not None else 0
            last_update_time = row[4] if row[4] is not None else None

            # 计算总设备数
            total_devices = standby_count + welding_count + alarm_count + shutdown_count

            # 计算各状态占比
            if total_devices > 0:
                standby_rate = round(standby_count / total_devices * 100, 1)
                welding_rate = round(welding_count / total_devices * 100, 1)
                alarm_rate = round(alarm_count / total_devices * 100, 1)
                shutdown_rate = round(shutdown_count / total_devices * 100, 1)
            else:
                standby_rate = welding_rate = alarm_rate = shutdown_rate = 0.0

            return {
                "total_devices": total_devices,
                "standby_devices": standby_count,
                "welding_devices": welding_count,
                "alarm_devices": alarm_count,
                "shutdown_devices": shutdown_count,
                "standby_rate": standby_rate,
                "welding_rate": welding_rate,
                "alarm_rate": alarm_rate,
                "shutdown_rate": shutdown_rate,
                "last_update_time": str(last_update_time) if last_update_time else None,
            }

        except Exception as e:
            logger.error(f"获取设备状态统计失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={"message": "获取设备状态统计失败", "error": str(e), "error_type": type(e).__name__},
            )

    async def get_device_online_rate_history(self, type_code: Optional[str] = None, days: int = 7) -> List[dict]:
        """获取设备在线率历史数据

        Args:
            type_code: 设备类型代码，不提供则查询所有类型
            days: 查询天数，默认7天

        Returns:
            在线率历史数据列表
        """
        try:
            from datetime import datetime, timedelta
            import asyncio

            # 计算查询时间范围
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days - 1)

            # 构建设备查询条件
            device_filter = {}
            if type_code:
                device_filter["device_type"] = type_code

            devices = await DeviceInfo.filter(**device_filter).all()
            total_devices = len(devices)

            if total_devices == 0:
                return []

            # 生成日期列表
            date_list = []
            current_date = start_date
            while current_date <= end_date:
                date_list.append(current_date)
                current_date += timedelta(days=1)

            # 为每一天计算在线率
            history_data = []
            for date in date_list:
                # 简化实现：使用当前状态作为历史数据
                # 在实际项目中，应该查询历史数据表或时序数据库
                online_count = 0
                for device in devices:
                    latest_data = await self.get_device_latest_data(device.id)
                    if latest_data and latest_data.status and latest_data.status.lower() == "online":
                        online_count += 1

                online_rate = round(online_count / total_devices * 100, 1) if total_devices > 0 else 0
                history_data.append(
                    {
                        "date": date.strftime("%m月%d日"),
                        "online_rate": online_rate,
                        "online_count": online_count,
                        "total_count": total_devices,
                    }
                )

            return history_data

        except Exception as e:
            logger.error(f"获取设备在线率历史数据失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={"message": "获取设备在线率历史数据失败", "error": str(e), "error_type": type(e).__name__},
            )

    async def get_online_rate_statistics(
        self,
        device_type: Optional[str] = None,
        device_group: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:
        """获取在线率统计数据
        
        从TDengine查询在线率统计数据
        
        Args:
            device_type: 设备类型代码
            device_group: 设备组
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            
        Returns:
            在线率统计数据列表，每个元素包含一天的数据
        """
        tdengine_connector = None
        try:
            from datetime import datetime, timedelta
            from app.settings.config import TDengineCredentials
            
            logger.info(f"获取在线率统计数据 - 设备类型: {device_type}, 设备组: {device_group}, 开始日期: {start_date}, 结束日期: {end_date}")
            
            # 解析日期范围
            if start_date and end_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                # 默认查询最近7天
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=6)
            
            # 初始化TDengine连接
            tdengine_creds = TDengineCredentials()
            tdengine_connector = TDengineConnector(
                host=tdengine_creds.host,
                port=tdengine_creds.port,
                user=tdengine_creds.user,
                password=tdengine_creds.password,
                database=tdengine_creds.database,
            )
            
            # 根据 device_type 动态选择表名
            from app.models.system import SysDictData
            table_name = ""
            if device_type == "welding":
                dict_entry = await SysDictData.filter(dict_type__type_code='welding_indicator_mapping', data_label='焊机数据表').first()
                if dict_entry:
                    table_name = dict_entry.data_value
                else:
                    logger.error("未找到数据字典中'welding_indicator_mapping'类型下'焊机数据表'的配置。")
                    raise HTTPException(status_code=500, detail="未找到焊机数据表配置")
            else:
                # 对于其他 device_type，可以添加相应的映射逻辑或抛出错误
                logger.error(f"不支持的设备类型: {device_type}")
                raise HTTPException(status_code=400, detail=f"不支持的设备类型: {device_type}")

            # 构建查询条件
            where_conditions = []
            # device_type 用于选择表名，而不是作为查询条件
            # if device_type:
            #     where_conditions.append(f"device_type = '{device_type}'")
            if device_group:
                where_conditions.append(f"device_group = '{device_group}'")
            
            where_clause = " AND " + " AND ".join(where_conditions) if where_conditions else ""
            
            # 查询每日在线率统计数据
            statistics_data = []
            current_date = start_dt
            
            while current_date <= end_dt:
                date_str = current_date.strftime("%Y-%m-%d")
                next_date = current_date + timedelta(days=1)
                next_date_str = next_date.strftime("%Y-%m-%d")
                
                # 查询当日设备状态统计 - 从日汇总表获取数据
                query = f"""
                SELECT 
                    COUNT(*) as total_devices,
                    SUM(online_minutes) as total_online_minutes,
                    SUM(welding_minutes) as total_welding_minutes,
                    SUM(alarm_minutes) as total_alarm_minutes,
                    AVG(welding_minutes) as avg_welding_time,
                    AVG(online_rate) as avg_online_rate
                FROM hlzg_db.{table_name} 
                WHERE ts >= '{date_str}T00:00:00.000+08:00' AND ts < '{next_date_str}T00:00:00.000+08:00' {where_clause}
                """
                logger.info(f"TDengine查询SQL ({date_str}): {query.strip()}")
                
                try:
                    result = await tdengine_connector.execute_sql(query)
                    logger.info(f"TDengine查询结果 ({date_str}): {result}")
                    
                    if result and len(result) > 0:
                        row = result[0]
                        total_devices = int(row[0]) if row[0] is not None else 0
                        total_online_minutes = float(row[1]) if row[1] is not None else 0.0
                        total_welding_minutes = float(row[2]) if row[2] is not None else 0.0
                        total_alarm_minutes = float(row[3]) if row[3] is not None else 0.0
                        avg_welding_time = float(row[4]) if row[4] is not None else 0.0
                        avg_online_rate = float(row[5]) if row[5] is not None else 0.0
                        
                        # 计算设备数量（基于时长数据推算）
                        # 假设一天有1440分钟，如果设备有在线时长，则认为是在线设备
                        online_devices = total_devices if total_online_minutes > 0 else 0
                        welding_devices = total_devices if total_welding_minutes > 0 else 0
                        fault_devices = total_devices if total_alarm_minutes > 0 else 0
                        
                        # 使用平均在线率或计算在线率
                        online_rate = round(avg_online_rate, 1) if avg_online_rate > 0 else 0.0
                        welding_rate = round((total_welding_minutes / (total_devices * 1440)) * 100, 1) if total_devices > 0 else 0.0
                        logger.info(f"计算指标 ({date_str}): 总设备数={total_devices}, 在线率={online_rate}, 焊接率={welding_rate}")
                        
                    else:
                        # 如果没有数据，使用默认值
                        total_devices = 0
                        online_devices = 0
                        welding_devices = 0
                        fault_devices = 0
                        avg_welding_time = 0.0
                        online_rate = 0.0
                        welding_rate = 0.0
                        
                except Exception as query_error:
                    logger.error(f"TDengine查询或数据处理失败 ({date_str}): {query_error}", exc_info=True)
                    # 查询失败时使用默认值
                    total_devices = 0
                    online_devices = 0
                    welding_devices = 0
                    fault_devices = 0
                    avg_welding_time = 0.0
                    online_rate = 0.0
                    welding_rate = 0.0
                
                daily_data = {
                    "date": int(current_date.timestamp() * 1000),  # 转换为毫秒时间戳
                    "onlineRate": online_rate,
                    "weldingRate": welding_rate,
                    "onlineDevices": online_devices,
                    "weldingDevices": welding_devices,
                    "totalDevices": total_devices,
                    "avgWeldingTime": round(avg_welding_time, 1),
                    "faultDevices": fault_devices,
                }
                
                statistics_data.append(daily_data)
                current_date += timedelta(days=1)
            
            logger.info(f"成功获取在线率统计数据，共 {len(statistics_data)} 天的数据。")
            return statistics_data
            
        except Exception as e:
            logger.error(f"获取在线率统计数据过程中发生未预期错误: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={"message": "获取在线率统计数据失败", "error": str(e), "error_type": type(e).__name__},
            )
        finally:
            if tdengine_connector:
                await tdengine_connector.close()
                logger.info("TDengine连接已关闭。")


    async def get_weld_time_statistics(
        self,
        device_type: Optional[str] = None,
        device_group: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict]:
        """获取焊接时长统计数据
        
        从TDengine查询焊接时长统计数据
        
        Args:
            device_type: 设备类型代码
            device_group: 设备组
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            
        Returns:
            焊接时长统计数据列表，每个元素包含一天的数据
        """
        tdengine_connector = None
        try:
            from datetime import datetime, timedelta
            from app.settings.config import TDengineCredentials
            
            logger.info(f"获取焊接时长统计数据 - 设备类型: {device_type}, 设备组: {device_group}, 开始日期: {start_date}, 结束日期: {end_date}")
            
            # 解析日期范围
            if start_date and end_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                # 默认查询最近7天
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=6)
            
            # 初始化TDengine连接
            tdengine_creds = TDengineCredentials()
            tdengine_connector = TDengineConnector(
                host=tdengine_creds.host,
                port=tdengine_creds.port,
                user=tdengine_creds.user,
                password=tdengine_creds.password,
                database=tdengine_creds.database,
            )
            
            # 构建查询条件
            where_conditions = []
            if device_type:
                where_conditions.append(f"device_type = '{device_type}'")
            if device_group:
                where_conditions.append(f"device_group = '{device_group}'")
            
            where_clause = " AND " + " AND ".join(where_conditions) if where_conditions else ""
            
            # 查询每日焊接时长统计数据
            statistics_data = []
            current_date = start_dt
            
            while current_date <= end_dt:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # 查询当日焊接时长统计
                query = f"""
                SELECT 
                    COUNT(DISTINCT device_code) as active_devices,
                    SUM(CASE WHEN status = 'welding' AND welding_duration > 0 THEN welding_duration ELSE 0 END) as total_weld_time,
                    AVG(CASE WHEN status = 'welding' AND welding_duration > 0 THEN welding_duration ELSE NULL END) as avg_weld_time,
                    MAX(CASE WHEN status = 'welding' AND welding_duration > 0 THEN welding_duration ELSE 0 END) as max_weld_time,
                    MIN(CASE WHEN status = 'welding' AND welding_duration > 0 THEN welding_duration ELSE NULL END) as min_weld_time,
                    COUNT(CASE WHEN status = 'welding' THEN 1 ELSE NULL END) as weld_count
                FROM device_realtime_data 
                WHERE ts >= '{date_str} 00:00:00' AND ts < '{date_str} 23:59:59'{where_clause}
                """
                
                try:
                    result = await tdengine_connector.execute_query(query)
                    
                    if result and len(result) > 0:
                        row = result[0]
                        active_devices = int(row[0]) if row[0] is not None else 0
                        total_weld_time = float(row[1]) if row[1] is not None else 0.0
                        avg_weld_time = float(row[2]) if row[2] is not None else 0.0
                        max_weld_time = float(row[3]) if row[3] is not None else 0.0
                        min_weld_time = float(row[4]) if row[4] is not None else 0.0
                        weld_count = int(row[5]) if row[5] is not None else 0
                        
                        # 计算焊接效率（假设一天工作8小时）
                        working_hours = 8.0
                        welding_efficiency = round(total_weld_time / (active_devices * working_hours) * 100, 1) if active_devices > 0 else 0.0
                        
                    else:
                        # 如果没有数据，使用默认值
                        active_devices = 0
                        total_weld_time = 0.0
                        avg_weld_time = 0.0
                        max_weld_time = 0.0
                        min_weld_time = 0.0
                        weld_count = 0
                        welding_efficiency = 0.0
                        
                except Exception as query_error:
                    logger.warning(f"查询日期 {date_str} 的焊接时长数据失败: {str(query_error)}，使用默认值")
                    # 查询失败时使用默认值
                    active_devices = 0
                    total_weld_time = 0.0
                    avg_weld_time = 0.0
                    max_weld_time = 0.0
                    min_weld_time = 0.0
                    weld_count = 0
                    welding_efficiency = 0.0
                
                daily_data = {
                    "date": int(current_date.timestamp() * 1000),  # 转换为毫秒时间戳
                    "totalWeldTime": round(total_weld_time, 1),
                    "avgWeldTime": round(avg_weld_time, 1),
                    "weldingEfficiency": welding_efficiency,
                    "activeDevices": active_devices,
                    "maxWeldTime": round(max_weld_time, 1),
                    "minWeldTime": round(min_weld_time, 1),
                    "weldCount": weld_count,
                }
                
                statistics_data.append(daily_data)
                current_date += timedelta(days=1)
            
            logger.info(f"查询了 {len(statistics_data)} 天的焊接时长统计数据")
            return statistics_data
            
        except Exception as e:
            logger.error(f"获取焊接时长统计数据失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={"message": "获取焊接时长统计数据失败", "error": str(e), "error_type": type(e).__name__},
            )
        finally:
            if tdengine_connector:
                await tdengine_connector.close()

    async def get_alarm_category_summary(
        self, 
        start_time: str, 
        end_time: str
    ) -> dict:
        """获取报警类型分布统计数据
        
        Args:
            start_time: 开始时间 (YYYY-MM-DD)
            end_time: 结束时间 (YYYY-MM-DD)
            
        Returns:
            包含各报警类型的记录数和持续时间统计
        """
        try:
            logger.info(f"开始获取报警类型分布统计数据，时间范围: {start_time} 到 {end_time}")
            
            from datetime import datetime
            
            async with get_db_connection() as conn:
                # 查询t_welding_alarm_his表，按alarm_message分组统计
                alarm_summary_sql = """
                    SELECT alarm_message, 
                           COUNT(*) AS record_count, 
                           SUM(alarm_duration_sec) AS record_time 
                    FROM public.t_welding_alarm_his 
                    WHERE alarm_time >= $1 AND alarm_time <= $2
                    GROUP BY alarm_message
                    ORDER BY record_count DESC
                """
                
                # 转换日期格式为datetime对象
                start_datetime = datetime.strptime(start_time, '%Y-%m-%d')
                end_datetime = datetime.strptime(end_time, '%Y-%m-%d')
                # 结束时间设置为当天的23:59:59
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                
                result = await conn.fetch(alarm_summary_sql, start_datetime, end_datetime)
                
                # 处理查询结果
                alarm_categories = []
                total_records = 0
                total_duration = 0
                
                for row in result:
                    record_count = row['record_count'] or 0
                    record_time = row['record_time'] or 0
                    
                    alarm_categories.append({
                        "alarm_message": row['alarm_message'],
                        "record_count": record_count,
                        "record_time": record_time
                    })
                    
                    total_records += record_count
                    total_duration += record_time
                
                logger.info(f"查询到 {len(alarm_categories)} 种报警类型，总记录数: {total_records}，总持续时间: {total_duration}秒")
                
                return {
                    "alarm_categories": alarm_categories,
                    "total_records": total_records,
                    "total_duration": total_duration,
                    "start_time": start_time,
                    "end_time": end_time
                }
                
        except Exception as e:
            logger.error("获取报警类型分布统计数据失败", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="获取报警类型分布统计数据失败"
            )

    async def get_online_welding_rate_statistics(
        self, 
        start_time: str, 
        end_time: str
    ) -> dict:
        """获取在线率和焊接率统计数据
        
        Args:
            start_time: 开始时间 (YYYY-MM-DD)
            end_time: 结束时间 (YYYY-MM-DD)
            
        Returns:
            包含每日数据的字典，包括设备总数、焊接设备数、开机设备数、关机设备数、在线率、焊接率
        """
        try:
            logger.info(f"开始获取在线率和焊接率统计数据，时间范围: {start_time} 到 {end_time}")
            
            from datetime import datetime, timedelta
            
            async with get_db_connection() as conn:
                # 1. 查询设备总数（device_type=welding）
                total_devices_sql = """
                    SELECT COUNT(*) as total_devices
                    FROM t_device_info 
                    WHERE device_type = 'welding'
                """
                total_result = await conn.fetchrow(total_devices_sql)
                total_devices = total_result['total_devices'] if total_result else 0
                
                # 2. 生成日期范围内的每一天
                start_date = datetime.strptime(start_time, '%Y-%m-%d')
                end_date = datetime.strptime(end_time, '%Y-%m-%d')
                
                daily_data = []
                current_date = start_date
                
                while current_date <= end_date:
                    date_str = current_date.strftime('%Y-%m-%d')
                    
                    # 查询当天的焊接设备数（welding_duration_seconds > 0）
                    welding_devices_sql = """
                        SELECT COUNT(DISTINCT prod_code) as welding_devices
                        FROM t_welding_daily_report 
                        WHERE report_date = $1
                        AND welding_duration_seconds > 0
                    """
                    welding_result = await conn.fetchrow(welding_devices_sql, current_date.date())
                    welding_devices = welding_result['welding_devices'] if welding_result else 0
                    
                    # 查询当天的开机设备数（有日报记录的设备）
                    online_devices_sql = """
                        SELECT COUNT(DISTINCT prod_code) as online_devices
                        FROM t_welding_daily_report 
                        WHERE report_date = $1
                    """
                    online_result = await conn.fetchrow(online_devices_sql, current_date.date())
                    online_devices = online_result['online_devices'] if online_result else 0
                    
                    # 计算关机设备数
                    shutdown_devices = total_devices - online_devices
                    
                    # 计算在线率和焊接率
                    online_rate = round((online_devices / total_devices * 100), 1) if total_devices > 0 else 0.0
                    welding_rate = round((welding_devices / online_devices * 100), 1) if online_devices > 0 else 0.0
                    
                    daily_data.append({
                        "date": date_str,
                        "total_devices": total_devices,
                        "welding_devices": welding_devices,
                        "online_devices": online_devices,
                        "shutdown_devices": shutdown_devices,
                        "online_rate": online_rate,
                        "welding_rate": welding_rate
                    })
                    
                    logger.info(f"日期 {date_str} - 总设备数: {total_devices}, 焊接设备数: {welding_devices}, 开机设备数: {online_devices}, 在线率: {online_rate}%, 焊接率: {welding_rate}%")
                    
                    current_date += timedelta(days=1)
                
                # 计算整个时间段的平均值
                if daily_data:
                    avg_online_rate = round(sum(d['online_rate'] for d in daily_data) / len(daily_data), 1)
                    avg_welding_rate = round(sum(d['welding_rate'] for d in daily_data) / len(daily_data), 1)
                    total_welding_devices = sum(d['welding_devices'] for d in daily_data)
                    total_online_devices = sum(d['online_devices'] for d in daily_data)
                else:
                    avg_online_rate = 0.0
                    avg_welding_rate = 0.0
                    total_welding_devices = 0
                    total_online_devices = 0
                
                return {
                    "total_devices": total_devices,
                    "welding_devices": total_welding_devices,
                    "online_devices": total_online_devices,
                    "shutdown_devices": total_devices - total_online_devices,
                    "online_rate": avg_online_rate,
                    "welding_rate": avg_welding_rate,
                    "daily_data": daily_data
                }
                
        except Exception as e:
            logger.error("获取在线率和焊接率统计数据失败", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="获取在线率和焊接率统计数据失败"
            )

    async def get_alarm_record_top(
        self, 
        start_time: str, 
        end_time: str,
        top: int = 10
    ) -> dict:
        """获取报警时长Top排名统计数据
        
        Args:
            start_time: 开始时间 (YYYY-MM-DD)
            end_time: 结束时间 (YYYY-MM-DD)
            top: 返回Top数量，默认10
            
        Returns:
            包含设备编码、设备名称、报警时长的Top排名数据
        """
        try:
            logger.info(f"开始获取报警时长Top{top}排名统计数据，时间范围: {start_time} 到 {end_time}")
            
            from datetime import datetime
            
            async with get_db_connection() as conn:
                # 查询t_welding_alarm_his表，按设备分组统计报警时长
                alarm_top_sql = """
                    SELECT 
                        a.prod_code, 
                        d.device_name, 
                        SUM(a.alarm_duration_sec) AS record_time 
                    FROM 
                        public.t_welding_alarm_his a 
                    JOIN 
                        public.t_device_info d 
                        ON a.prod_code = d.device_code 
                    WHERE 
                        a.alarm_time >= $1 AND a.alarm_time <= $2
                    GROUP BY 
                        a.prod_code, d.device_name 
                    ORDER BY 
                        record_time DESC 
                    LIMIT $3
                """
                
                # 转换日期格式为datetime对象
                start_datetime = datetime.strptime(start_time, '%Y-%m-%d')
                end_datetime = datetime.strptime(end_time, '%Y-%m-%d')
                # 结束时间设置为当天的23:59:59
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                
                result = await conn.fetch(alarm_top_sql, start_datetime, end_datetime, top)
                
                # 处理查询结果
                alarm_records = []
                total_alarm_time = 0
                
                for index, row in enumerate(result, 1):
                    record_time = row['record_time'] or 0
                    
                    alarm_records.append({
                        "rank": index,
                        "prod_code": row['prod_code'],
                        "device_name": row['device_name'],
                        "record_time": record_time
                    })
                    
                    total_alarm_time += record_time
                
                logger.info(f"查询到 {len(alarm_records)} 条报警记录，总报警时长: {total_alarm_time}秒")
                
                return {
                    "alarm_records": alarm_records,
                    "total_alarm_time": total_alarm_time,
                    "start_time": start_time,
                    "end_time": end_time,
                    "top": top
                }
                
        except Exception as e:
            logger.error("获取报警时长Top排名统计数据失败", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="获取报警时长Top排名统计数据失败"
            )


# 创建控制器实例
device_data_controller = DeviceDataController()
