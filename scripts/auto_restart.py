#!/usr/bin/env python3
"""
智能自动重启脚本
检测常见问题并自动处理
"""

import os
import sys
import time
import signal
import psutil
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
import argparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DevServerManager:
    """开发服务器管理器"""
    
    def __init__(self, port: int = 8000, project_root: Optional[str] = None):
        self.port = port
        self.project_root = Path(project_root or os.getcwd())
        self.venv_python = self._find_python_executable()
        
    def _find_python_executable(self) -> Path:
        """查找Python可执行文件"""
        # Windows
        windows_path = self.project_root / ".venv" / "Scripts" / "python.exe"
        if windows_path.exists():
            return windows_path
        
        # Linux/macOS
        unix_path = self.project_root / ".venv" / "bin" / "python"
        if unix_path.exists():
            return unix_path
        
        raise FileNotFoundError("虚拟环境Python可执行文件未找到")
    
    def kill_existing_processes(self) -> bool:
        """终止现有的Python进程"""
        logger.info("🔪 终止现有Python进程...")
        killed_count = 0
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline'] or []
                        if any('run.py' in arg for arg in cmdline):
                            logger.info(f"  终止进程 PID: {proc.info['pid']}")
                            proc.kill()
                            killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if killed_count > 0:
                time.sleep(2)  # 等待进程完全终止
                logger.info(f"✅ 已终止 {killed_count} 个Python进程")
            else:
                logger.info("ℹ️  没有找到运行中的Python进程")
            
            return True
            
        except Exception as e:
            logger.error(f"⚠️  终止进程时出现错误: {e}")
            return False
    
    def kill_port_processes(self) -> bool:
        """终止占用指定端口的进程"""
        logger.info(f"🔍 检查端口 {self.port} 占用情况...")
        killed_count = 0
        
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == self.port and conn.status == 'LISTEN':
                    try:
                        proc = psutil.Process(conn.pid)
                        logger.info(f"  端口 {self.port} 被进程 PID:{conn.pid} ({proc.name()}) 占用，终止中...")
                        proc.kill()
                        killed_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            if killed_count > 0:
                time.sleep(1)
                logger.info(f"✅ 已释放端口 {self.port}")
            else:
                logger.info(f"✅ 端口 {self.port} 可用")
            
            return True
            
        except Exception as e:
            logger.error(f"⚠️  检查端口时出现错误: {e}")
            return False
    
    def clear_python_cache(self) -> bool:
        """清理Python缓存"""
        logger.info("🧹 清理Python缓存...")
        cleared_count = 0
        
        try:
            # 清理.pyc文件
            for pyc_file in self.project_root.rglob("*.pyc"):
                try:
                    pyc_file.unlink()
                    cleared_count += 1
                except Exception:
                    continue
            
            # 清理__pycache__目录
            for pycache_dir in self.project_root.rglob("__pycache__"):
                try:
                    shutil.rmtree(pycache_dir)
                    cleared_count += 1
                except Exception:
                    continue
            
            # 清理.pytest_cache目录
            for pytest_cache in self.project_root.rglob(".pytest_cache"):
                try:
                    shutil.rmtree(pytest_cache)
                    cleared_count += 1
                except Exception:
                    continue
            
            logger.info(f"✅ Python缓存清理完成，清理了 {cleared_count} 个项目")
            return True
            
        except Exception as e:
            logger.error(f"⚠️  清理缓存时出现错误: {e}")
            return False
    
    def test_import(self) -> bool:
        """测试应用导入"""
        logger.info("🧪 测试应用导入...")
        
        try:
            result = subprocess.run(
                [str(self.venv_python), "-c", "from app import app; print('Import successful')"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ 应用导入测试通过")
                return True
            else:
                logger.error("❌ 应用导入失败:")
                logger.error(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ 导入测试超时")
            return False
        except Exception as e:
            logger.error(f"❌ 导入测试异常: {e}")
            return False
    
    def start_server(self) -> bool:
        """启动开发服务器"""
        logger.info("🚀 启动开发服务器...")
        logger.info(f"   端口: {self.port}")
        logger.info(f"   访问地址: http://127.0.0.1:{self.port}")
        logger.info("   按 Ctrl+C 停止服务器")
        logger.info("")
        
        try:
            # 启动服务器
            process = subprocess.Popen(
                [str(self.venv_python), "run.py"],
                cwd=self.project_root
            )
            
            # 等待服务器启动
            time.sleep(3)
            
            # 检查进程是否还在运行
            if process.poll() is None:
                logger.info("✅ 服务器启动成功")
                
                # 等待进程结束或接收中断信号
                try:
                    process.wait()
                except KeyboardInterrupt:
                    logger.info("🛑 接收到中断信号，正在停止服务器...")
                    process.terminate()
                    process.wait(timeout=5)
                    logger.info("✅ 服务器已停止")
                
                return True
            else:
                logger.error("❌ 服务器启动失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 启动服务器时出现异常: {e}")
            return False
    
    def full_restart(self, skip_cache: bool = False, skip_kill: bool = False) -> bool:
        """完整重启流程"""
        logger.info("🔄 开发环境重启脚本启动...")
        
        success = True
        
        # 1. 终止现有进程
        if not skip_kill:
            success &= self.kill_existing_processes()
            success &= self.kill_port_processes()
        
        # 2. 清理缓存
        if not skip_cache:
            success &= self.clear_python_cache()
        
        # 3. 测试导入
        success &= self.test_import()
        
        if not success:
            logger.error("❌ 重启过程中出现错误，请检查日志")
            return False
        
        # 4. 启动服务器
        return self.start_server()
    
    def clean_only(self) -> bool:
        """仅清理模式"""
        logger.info("🎯 仅清理模式启动...")
        
        success = True
        success &= self.kill_existing_processes()
        success &= self.kill_port_processes()
        success &= self.clear_python_cache()
        
        if success:
            logger.info("🎯 清理完成")
        else:
            logger.error("❌ 清理过程中出现错误")
        
        return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能开发服务器重启脚本")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--skip-cache", action="store_true", help="跳过缓存清理")
    parser.add_argument("--skip-kill", action="store_true", help="跳过进程终止")
    parser.add_argument("--only-clean", action="store_true", help="仅清理，不启动服务器")
    parser.add_argument("--project-root", help="项目根目录路径")
    
    args = parser.parse_args()
    
    try:
        manager = DevServerManager(
            port=args.port,
            project_root=args.project_root
        )
        
        if args.only_clean:
            success = manager.clean_only()
        else:
            success = manager.full_restart(
                skip_cache=args.skip_cache,
                skip_kill=args.skip_kill
            )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("🛑 用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ 脚本执行异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()