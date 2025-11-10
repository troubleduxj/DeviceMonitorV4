#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时日志监控工具
持续监控前后端日志，实时显示新增内容和错误
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
LOGS_DIR = ROOT_DIR / 'logs'


class LogMonitor:
    """日志监控器"""
    
    def __init__(self, backend_log=None, frontend_log=None):
        self.backend_log = backend_log
        self.frontend_log = frontend_log
        self.backend_pos = 0
        self.frontend_pos = 0
        self.error_count = 0
        self.warning_count = 0
        
    def start(self):
        """开始监控"""
        print("=" * 80)
        print("📡 实时日志监控")
        print("=" * 80)
        print(f"后端日志: {self.backend_log.name if self.backend_log else '无'}")
        print(f"前端日志: {self.frontend_log.name if self.frontend_log else '无'}")
        print("\n💡 按 Ctrl+C 停止监控\n")
        print("=" * 80)
        
        try:
            while True:
                # 检查后端日志
                if self.backend_log and self.backend_log.exists():
                    self._check_file(self.backend_log, 'backend', '🔵')
                
                # 检查前端日志
                if self.frontend_log and self.frontend_log.exists():
                    self._check_file(self.frontend_log, 'frontend', '🟢')
                
                time.sleep(1)  # 每秒检查一次
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 80)
            print("📊 监控统计:")
            print(f"  - 检测到的错误: {self.error_count}")
            print(f"  - 检测到的警告: {self.warning_count}")
            print("=" * 80)
            print("✅ 监控已停止")
    
    def _check_file(self, file_path, log_type, icon):
        """检查单个日志文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 跳到上次读取的位置
                if log_type == 'backend':
                    f.seek(self.backend_pos)
                else:
                    f.seek(self.frontend_pos)
                
                # 读取新内容
                new_lines = f.readlines()
                
                # 更新位置
                if log_type == 'backend':
                    self.backend_pos = f.tell()
                else:
                    self.frontend_pos = f.tell()
                
                # 处理新行
                for line in new_lines:
                    self._process_line(line, log_type, icon)
                    
        except Exception as e:
            pass  # 静默失败
    
    def _process_line(self, line, log_type, icon):
        """处理单行日志"""
        line = line.strip()
        if not line:
            return
        
        line_lower = line.lower()
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 检测错误
        if 'error' in line_lower and 'errorlevel' not in line_lower:
            self.error_count += 1
            print(f"{icon} [{timestamp}] [{log_type}] ❌ {line[:200]}")
        
        # 检测警告
        elif 'warning' in line_lower or 'warn' in line_lower:
            self.warning_count += 1
            print(f"{icon} [{timestamp}] [{log_type}] ⚠️  {line[:200]}")
        
        # 检测Mock相关
        elif 'mock' in line_lower:
            print(f"{icon} [{timestamp}] [{log_type}] 🎭 {line[:200]}")
        
        # 检测网络错误
        elif 'network error' in line_lower or 'econnrefused' in line_lower:
            self.error_count += 1
            print(f"{icon} [{timestamp}] [{log_type}] 🌐 {line[:200]}")
        
        # 检测认证问题
        elif ('token' in line_lower or 'auth' in line_lower) and ('fail' in line_lower or 'error' in line_lower):
            self.error_count += 1
            print(f"{icon} [{timestamp}] [{log_type}] 🔐 {line[:200]}")
        
        # 检测成功消息（静默，只在verbose模式显示）
        elif 'success' in line_lower or '成功' in line:
            pass  # 不显示成功消息，避免刷屏
        
        # 检测启动消息
        elif 'running on' in line_lower or 'local:' in line_lower or 'network:' in line_lower:
            print(f"{icon} [{timestamp}] [{log_type}] 🚀 {line}")


def find_latest_logs():
    """查找最新的日志文件"""
    if not LOGS_DIR.exists():
        return None, None
    
    # 查找最新的前后端日志
    backend_logs = sorted(LOGS_DIR.glob('backend_*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
    frontend_logs = sorted(LOGS_DIR.glob('frontend_*.log'), key=lambda x: x.stat().st_mtime, reverse=True)
    
    backend_log = backend_logs[0] if backend_logs else None
    frontend_log = frontend_logs[0] if frontend_logs else None
    
    # 如果没有带时间戳的日志，尝试固定名称的日志
    if not backend_log and (LOGS_DIR / 'app.log').exists():
        backend_log = LOGS_DIR / 'app.log'
    if not backend_log and (LOGS_DIR / 'info.log').exists():
        backend_log = LOGS_DIR / 'info.log'
    if not frontend_log and (LOGS_DIR / 'frontend-log.md').exists():
        frontend_log = LOGS_DIR / 'frontend-log.md'
    
    return backend_log, frontend_log


def main():
    """主函数"""
    backend_log, frontend_log = find_latest_logs()
    
    if not backend_log and not frontend_log:
        print("❌ 未找到日志文件！")
        print("\n💡 请先启动系统:")
        print("   scripts\\start_with_logging.bat")
        return
    
    monitor = LogMonitor(backend_log, frontend_log)
    monitor.start()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ 监控失败: {e}")
        import traceback
        traceback.print_exc()

