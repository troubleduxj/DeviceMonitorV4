# 📋 日志系统使用指南

## 概述

设备监控系统配备了完整的日志记录和分析工具，帮助您快速定位和解决问题。

---

## 🚀 快速开始

### 方法1：带日志记录的启动（推荐）

```bash
# Windows
scripts\start_with_logging.bat

# 这将：
# 1. 自动启动前后端服务
# 2. 将日志记录到 logs/ 目录
# 3. 使用时间戳命名日志文件
```

### 方法2：分析现有日志

```bash
# 分析最新的日志文件
python scripts\analyze_logs.py

# 生成详细的分析报告
```

### 方法3：实时监控日志

```bash
# 实时显示新增日志（类似tail -f）
python scripts\monitor_logs.py

# 按 Ctrl+C 停止监控
```

---

## 📁 日志文件结构

```
logs/
├── backend_20251030_123456.log      # 后端日志（带时间戳）
├── frontend_20251030_123456.log     # 前端日志（带时间戳）
├── combined_20251030_123456.log     # 合并日志
├── analysis_report_20251030_123456.txt  # 分析报告
├── app.log                          # 后端应用日志（固定名称）
├── error.log                        # 后端错误日志
├── info.log                         # 后端信息日志
└── frontend-log.md                  # 前端日志（Markdown格式）
```

---

## 🔍 日志分析功能

### 自动识别的问题类型

1. **❌ 错误 (Error)**
   - 网络连接错误
   - API请求失败
   - 数据库错误
   - Mock拦截问题

2. **⚠️  警告 (Warning)**
   - 配置问题
   - 性能警告
   - 弃用提示

3. **🔐 认证问题**
   - Token过期
   - 登录失败
   - 权限不足

4. **🌐 网络问题**
   - ECONNREFUSED
   - Timeout
   - Network Error

5. **🎭 Mock相关**
   - Mock规则匹配
   - Mock拦截失败
   - Mock配置错误

---

## 📊 分析报告示例

运行 `python scripts\analyze_logs.py` 后，你会看到：

```
================================================================================
📊 综合分析报告
================================================================================

🔢 整体统计:
  - 总错误数: 5
  - 总警告数: 12
  - 网络错误: 2
  - 认证问题: 1
  - API错误: 2
  - Mock问题: 0
  - 性能问题: 1

❌ 错误详情 (最近10条):
  [后端:123] ERROR: Database connection failed
  [前端:456] Network Error: Failed to fetch
  ...

💡 问题诊断与建议:
  ⚠️  检测到网络错误:
     1. 确认后端服务是否正常运行 (http://localhost:8001)
     2. 检查防火墙设置
     3. 验证端口8001没有被占用

💾 详细报告已保存: logs/analysis_report_20251030_123456.txt
```

---

## 💡 使用场景

### 场景1：系统启动后检查

```bash
# 1. 启动系统（带日志）
scripts\start_with_logging.bat

# 2. 等待10秒

# 3. 分析日志
python scripts\analyze_logs.py

# 4. 查看报告
# 如果有错误，按照建议修复
```

### 场景2：实时调试

```bash
# 在一个终端窗口：启动系统
scripts\start_with_logging.bat

# 在另一个终端窗口：实时监控
python scripts\monitor_logs.py

# 你会实时看到：
# 🔵 [10:30:45] [backend] ❌ Database connection failed
# 🟢 [10:30:46] [frontend] ⚠️  Token not found
```

### 场景3：问题排查

```bash
# 1. 发现问题后，分析日志
python scripts\analyze_logs.py

# 2. 查看详细报告
type logs\analysis_report_*.txt

# 3. 根据建议修复

# 4. 重新测试并分析
```

---

## 🎯 日志监控示例

### 实时监控输出

```
================================================================================
📡 实时日志监控
================================================================================
后端日志: backend_20251030_123456.log
前端日志: frontend_20251030_123456.log

💡 按 Ctrl+C 停止监控

================================================================================
🔵 [10:30:45] [backend] 🚀 INFO:     Uvicorn running on http://127.0.0.1:8001
🟢 [10:30:50] [frontend] 🚀 Local:   http://localhost:3001/
🟢 [10:30:55] [frontend] ⚠️  Token not found in localStorage
🔵 [10:31:00] [backend] ❌ ERROR: Database query failed
🟢 [10:31:02] [frontend] 🌐 Network Error: Failed to fetch
🟢 [10:31:05] [frontend] 🎭 [Mock拦截器] 加载了 6 条Mock规则
```

---

## ⚙️ 配置选项

### 自定义日志位置

编辑 `scripts/start_with_logging.bat`:

```batch
REM 修改日志目录
set LOG_DIR=D:\MyLogs
```

### 自定义分析规则

编辑 `scripts/analyze_logs.py`:

```python
# 添加自定义关键字检测
if 'my_custom_error' in line_lower:
    self.custom_errors.append((log_type, line_num, line.strip()))
```

---

## 🛠️ 常见问题

### Q1: 日志文件太大怎么办？

**A:** 使用日志轮转：

```bash
# 手动清理旧日志
del logs\*.log
del logs\analysis_report_*.txt

# 或者只保留最近3天的日志
python scripts\clean_old_logs.py --days 3
```

### Q2: 如何只分析特定类型的错误？

**A:** 使用grep或findstr过滤：

```bash
# 只查看错误
type logs\backend_*.log | findstr /i "error"

# 只查看Mock相关
type logs\frontend_*.log | findstr /i "mock"
```

### Q3: 分析报告在哪里？

**A:** 在 `logs/` 目录下，文件名格式为 `analysis_report_YYYYMMDD_HHMMSS.txt`

---

## 📚 进阶技巧

### 1. 自动化日志分析

创建计划任务，每小时自动分析日志：

```bash
# Windows任务计划
schtasks /create /tn "LogAnalysis" /tr "python D:\path\to\scripts\analyze_logs.py" /sc hourly
```

### 2. 日志告警

修改 `analyze_logs.py`，在检测到严重错误时发送邮件/通知。

### 3. 日志可视化

将日志导入ELK Stack或其他可视化工具进行图表分析。

---

## 🎉 总结

| 工具 | 用途 | 命令 |
|------|------|------|
| 带日志启动 | 启动系统并记录日志 | `scripts\start_with_logging.bat` |
| 日志分析 | 分析历史日志 | `python scripts\analyze_logs.py` |
| 实时监控 | 实时查看新日志 | `python scripts\monitor_logs.py` |

**建议工作流：**
1. 使用 `start_with_logging.bat` 启动系统
2. 在另一个终端使用 `monitor_logs.py` 实时监控
3. 遇到问题时使用 `analyze_logs.py` 分析
4. 根据报告建议修复问题

---

## 💬 反馈

如有问题或建议，请查看：
- `docs/user_docs/` - 用户文档
- `README.md` - 项目说明

