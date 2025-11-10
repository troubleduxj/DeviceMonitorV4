#!/bin/bash
# 开发环境自动重启脚本 (Linux/macOS版本)
# 用于清理Python缓存、终止进程并重启服务

set -e

# 默认参数
SKIP_CACHE=false
SKIP_KILL=false
ONLY_CLEAN=false
PORT=8000

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-cache)
            SKIP_CACHE=true
            shift
            ;;
        --skip-kill)
            SKIP_KILL=true
            shift
            ;;
        --only-clean)
            ONLY_CLEAN=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

echo "🔄 开发环境重启脚本启动..."

# 1. 终止现有Python进程
if [ "$SKIP_KILL" = false ]; then
    echo "🔪 终止现有Python进程..."
    if pgrep -f "python.*run.py" > /dev/null; then
        pkill -f "python.*run.py" || true
        sleep 2
        echo "✅ Python进程已终止"
    else
        echo "ℹ️  没有找到运行中的Python进程"
    fi
fi

# 2. 清理Python缓存
if [ "$SKIP_CACHE" = false ]; then
    echo "🧹 清理Python缓存..."
    
    # 清理.pyc文件
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理__pycache__目录
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # 清理.pytest_cache
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    echo "✅ Python缓存清理完成"
fi

# 3. 检查端口占用
echo "🔍 检查端口 $PORT 占用情况..."
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "  端口 $PORT 被占用，尝试释放..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "✅ 端口已释放"
else
    echo "✅ 端口 $PORT 可用"
fi

# 4. 如果只是清理，则退出
if [ "$ONLY_CLEAN" = true ]; then
    echo "🎯 仅清理模式，任务完成"
    exit 0
fi

# 5. 验证虚拟环境
echo "🔍 验证虚拟环境..."
if [ ! -f "./.venv/bin/python" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi
echo "✅ 虚拟环境验证通过"

# 6. 测试导入
echo "🧪 测试应用导入..."
if ./.venv/bin/python -c "from app import app; print('Import successful')" 2>/dev/null; then
    echo "✅ 应用导入测试通过"
else
    echo "❌ 应用导入失败"
    exit 1
fi

# 7. 启动开发服务器
echo "🚀 启动开发服务器..."
echo "   端口: $PORT"
echo "   访问地址: http://127.0.0.1:$PORT"
echo "   按 Ctrl+C 停止服务器"
echo ""

./.venv/bin/python run.py