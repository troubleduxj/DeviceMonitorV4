#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全自动化测试脚本
自动启动后端、测试API、生成报告
"""

import subprocess
import time
import sys
from pathlib import Path
try:
    import httpx
except ImportError:
    print("[ERROR] httpx not installed")
    sys.exit(1)

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_section(title):
    """打印章节"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_backend_running():
    """检查后端是否运行"""
    try:
        response = httpx.get("http://localhost:8001/api/v2/health", timeout=2.0)
        return response.status_code == 200
    except:
        return False


def start_backend():
    """启动后端服务"""
    print_section("Starting Backend Service")
    
    python_exe = project_root / ".venv" / "Scripts" / "python.exe"
    run_py = project_root / "run.py"
    
    if not python_exe.exists():
        print(f"[ERROR] Python not found: {python_exe}")
        return None
    
    if not run_py.exists():
        print(f"[ERROR] run.py not found: {run_py}")
        return None
    
    print(f"[START] Launching backend: {python_exe} {run_py}")
    
    # 启动后端进程
    process = subprocess.Popen(
        [str(python_exe), str(run_py)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    print(f"[INFO] Backend process started (PID: {process.pid})")
    print("[WAIT] Waiting for backend to initialize...")
    
    # 等待后端启动（最多30秒）
    for i in range(30):
        time.sleep(1)
        if check_backend_running():
            print(f"[SUCCESS] Backend is ready! (waited {i+1}s)")
            return process
        print(f"   Waiting... {i+1}/30")
    
    print("[WARNING] Backend may not be fully ready")
    return process


def test_api():
    """测试API"""
    print_section("Testing API Endpoints")
    
    test_script = project_root / "scripts" / "test_prediction_api.py"
    python_exe = project_root / ".venv" / "Scripts" / "python.exe"
    
    result = subprocess.run(
        [str(python_exe), str(test_script)],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("[STDERR]:", result.stderr)
    
    return result.returncode == 0


def main():
    """主函数"""
    print_section("AI Prediction Management - Auto Test")
    print(f"[TIME] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    backend_process = None
    
    try:
        # 1. 检查后端是否已运行
        if check_backend_running():
            print("[INFO] Backend is already running")
        else:
            # 2. 启动后端
            backend_process = start_backend()
            if not backend_process:
                print("[ERROR] Failed to start backend")
                return 1
        
        # 3. 测试API
        success = test_api()
        
        # 4. 输出结果
        print_section("Final Result")
        if success:
            print("[SUCCESS] All tests passed!")
            print()
            print("Next steps:")
            print("   1. Start frontend: cd web && npm run dev")
            print("   2. Visit: http://localhost:3000")
            print("   3. Test: AI Monitor > Trend Prediction > Refresh Data")
            return 0
        else:
            print("[FAILED] Some tests failed")
            print("Check logs above for details")
            return 1
            
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # 不关闭后端进程，让它继续运行
        if backend_process:
            print(f"\n[INFO] Backend process still running (PID: {backend_process.pid})")
            print("[INFO] Use Ctrl+C in backend window to stop it")


if __name__ == '__main__':
    sys.exit(main())

