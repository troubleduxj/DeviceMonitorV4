#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志分析工具
自动分析前后端日志，识别错误、警告和关键事件
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
LOGS_DIR = ROOT_DIR / 'logs'


class LogAnalyzer:
    """日志分析器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.network_errors = []
        self.auth_issues = []
        self.api_errors = []
        self.mock_issues = []
        self.performance_issues = []
        self.statistics = defaultdict(int)
        
    def analyze_file(self, file_path, log_type='unknown'):
        """分析单个日志文件"""
        print(f"\n📄 分析 {log_type} 日志: {file_path.name}")
        print("=" * 60)
        
        if not file_path.exists():
            print(f"⚠️  文件不存在: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            if not lines:
                print("ℹ️  日志文件为空")
                return
                
            print(f"📊 总行数: {len(lines)}")
            
            # 分析每一行
            for line_num, line in enumerate(lines, 1):
                self._analyze_line(line, line_num, log_type)
            
            # 输出统计
            self._print_statistics(log_type)
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
    
    def _analyze_line(self, line, line_num, log_type):
        """分析单行日志"""
        line_lower = line.lower()
        
        # 统计不同类型的日志
        if 'error' in line_lower:
            self.statistics['errors'] += 1
            self.errors.append((log_type, line_num, line.strip()))
            
            # 识别具体错误类型
            if 'network error' in line_lower or 'econnrefused' in line_lower:
                self.network_errors.append((log_type, line_num, line.strip()))
            elif 'auth' in line_lower or 'token' in line_lower or '401' in line:
                self.auth_issues.append((log_type, line_num, line.strip()))
            elif 'api' in line_lower or '404' in line or '422' in line or '500' in line:
                self.api_errors.append((log_type, line_num, line.strip()))
                
        if 'warning' in line_lower or 'warn' in line_lower:
            self.statistics['warnings'] += 1
            self.warnings.append((log_type, line_num, line.strip()))
            
        if 'mock' in line_lower:
            self.statistics['mock_related'] += 1
            if 'error' in line_lower or 'fail' in line_lower:
                self.mock_issues.append((log_type, line_num, line.strip()))
                
        if 'timeout' in line_lower or 'slow' in line_lower:
            self.performance_issues.append((log_type, line_num, line.strip()))
            
        # 统计特定关键字
        if 'success' in line_lower or '成功' in line:
            self.statistics['success'] += 1
        if 'fail' in line_lower or '失败' in line:
            self.statistics['failures'] += 1
    
    def _print_statistics(self, log_type):
        """打印统计信息"""
        print(f"\n📈 {log_type} 统计:")
        print(f"  - 错误: {self.statistics.get('errors', 0)}")
        print(f"  - 警告: {self.statistics.get('warnings', 0)}")
        print(f"  - 成功: {self.statistics.get('success', 0)}")
        print(f"  - 失败: {self.statistics.get('failures', 0)}")
        print(f"  - Mock相关: {self.statistics.get('mock_related', 0)}")
    
    def generate_report(self):
        """生成综合报告"""
        print("\n" + "=" * 80)
        print("📊 综合分析报告")
        print("=" * 80)
        
        # 1. 整体统计
        print(f"\n🔢 整体统计:")
        print(f"  - 总错误数: {len(self.errors)}")
        print(f"  - 总警告数: {len(self.warnings)}")
        print(f"  - 网络错误: {len(self.network_errors)}")
        print(f"  - 认证问题: {len(self.auth_issues)}")
        print(f"  - API错误: {len(self.api_errors)}")
        print(f"  - Mock问题: {len(self.mock_issues)}")
        print(f"  - 性能问题: {len(self.performance_issues)}")
        
        # 2. 关键问题
        if self.errors:
            print(f"\n❌ 错误详情 (最近10条):")
            for log_type, line_num, line in self.errors[-10:]:
                print(f"  [{log_type}:{line_num}] {line[:100]}")
        
        if self.network_errors:
            print(f"\n🌐 网络错误 (最近5条):")
            for log_type, line_num, line in self.network_errors[-5:]:
                print(f"  [{log_type}:{line_num}] {line[:100]}")
        
        if self.auth_issues:
            print(f"\n🔐 认证问题 (最近5条):")
            for log_type, line_num, line in self.auth_issues[-5:]:
                print(f"  [{log_type}:{line_num}] {line[:100]}")
        
        if self.api_errors:
            print(f"\n🔌 API错误 (最近5条):")
            for log_type, line_num, line in self.api_errors[-5:]:
                print(f"  [{log_type}:{line_num}] {line[:100]}")
        
        if self.mock_issues:
            print(f"\n🎭 Mock问题:")
            for log_type, line_num, line in self.mock_issues:
                print(f"  [{log_type}:{line_num}] {line[:100]}")
        
        # 3. 建议
        print(f"\n💡 问题诊断与建议:")
        
        if self.network_errors:
            print("  ⚠️  检测到网络错误:")
            print("     1. 确认后端服务是否正常运行 (http://localhost:8001)")
            print("     2. 检查防火墙设置")
            print("     3. 验证端口8001没有被占用")
        
        if self.auth_issues:
            print("  ⚠️  检测到认证问题:")
            print("     1. 检查Token是否有效")
            print("     2. 尝试重新登录")
            print("     3. 运行: window.authDiagnose() 在浏览器控制台")
        
        if self.mock_issues:
            print("  ⚠️  检测到Mock问题:")
            print("     1. 检查Mock是否已启用但干扰了正常请求")
            print("     2. 访问: http://localhost:3001/mock-control.html")
            print("     3. 如需禁用Mock: localStorage.setItem('mock_enabled', 'false')")
        
        if len(self.errors) == 0:
            print("  ✅ 未检测到严重问题，系统运行正常！")
        
        # 4. 输出报告文件
        self._save_report()
    
    def _save_report(self):
        """保存报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = LOGS_DIR / f"analysis_report_{timestamp}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("日志分析报告\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"总错误数: {len(self.errors)}\n")
                f.write(f"总警告数: {len(self.warnings)}\n")
                f.write(f"网络错误: {len(self.network_errors)}\n")
                f.write(f"认证问题: {len(self.auth_issues)}\n")
                f.write(f"API错误: {len(self.api_errors)}\n")
                f.write(f"Mock问题: {len(self.mock_issues)}\n\n")
                
                if self.errors:
                    f.write("错误详情:\n")
                    f.write("-" * 80 + "\n")
                    for log_type, line_num, line in self.errors:
                        f.write(f"[{log_type}:{line_num}] {line}\n")
                    f.write("\n")
                
                if self.warnings:
                    f.write("警告详情:\n")
                    f.write("-" * 80 + "\n")
                    for log_type, line_num, line in self.warnings[-20:]:
                        f.write(f"[{log_type}:{line_num}] {line}\n")
                    f.write("\n")
            
            print(f"\n💾 详细报告已保存: {report_file}")
            
        except Exception as e:
            print(f"⚠️  保存报告失败: {e}")


def find_latest_logs():
    """查找最新的日志文件"""
    if not LOGS_DIR.exists():
        print(f"❌ 日志目录不存在: {LOGS_DIR}")
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
    print("=" * 80)
    print("🔍 设备监控系统 - 日志分析工具")
    print("=" * 80)
    
    # 查找最新日志
    backend_log, frontend_log = find_latest_logs()
    
    if not backend_log and not frontend_log:
        print("\n❌ 未找到日志文件！")
        print("\n💡 请先启动系统:")
        print("   python scripts\\start_with_logging.bat")
        return
    
    # 创建分析器
    analyzer = LogAnalyzer()
    
    # 分析后端日志
    if backend_log:
        analyzer.analyze_file(backend_log, '后端')
    else:
        print("\n⚠️  未找到后端日志")
    
    # 分析前端日志
    if frontend_log:
        analyzer.analyze_file(frontend_log, '前端')
    else:
        print("\n⚠️  未找到前端日志")
    
    # 生成综合报告
    analyzer.generate_report()
    
    print("\n" + "=" * 80)
    print("✅ 分析完成！")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 分析过程出错: {e}")
        import traceback
        traceback.print_exc()

