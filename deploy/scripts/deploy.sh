#!/bin/bash

# 权限系统部署脚本
# 使用方法: ./deploy.sh [环境] [版本]
# 示例: ./deploy.sh production v2.0.1

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}

log_info "开始部署权限系统"
log_info "环境: $ENVIRONMENT"
log_info "版本: $VERSION"

# 配置文件路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_DIR="$PROJECT_ROOT/deploy"
ENV_FILE="$DEPLOY_DIR/environments/$ENVIRONMENT/.env"

# 检查环境文件
if [ ! -f "$ENV_FILE" ]; then
    log_error "环境配置文件不存在: $ENV_FILE"
    exit 1
fi

# 加载环境变量
source "$ENV_FILE"

# 检查必要的环境变量
check_env_vars() {
    local required_vars=(
        "SECRET_KEY"
        "DB_PASSWORD"
        "DATABASE_URL"
        "REDIS_URL"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "必需的环境变量未设置: $var"
            exit 1
        fi
    done
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 备份数据库
backup_database() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "备份生产数据库..."
        
        BACKUP_DIR="$DEPLOY_DIR/backups"
        mkdir -p "$BACKUP_DIR"
        
        BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"
        
        # 使用 pg_dump 备份数据库
        docker-compose -f "$DEPLOY_DIR/docker/docker-compose.yml" exec -T postgres \
            pg_dump -U postgres permission_system > "$BACKUP_FILE"
        
        if [ $? -eq 0 ]; then
            log_success "数据库备份完成: $BACKUP_FILE"
        else
            log_error "数据库备份失败"
            exit 1
        fi
    fi
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    cd "$PROJECT_ROOT"
    
    # 构建应用镜像
    docker build -f deploy/docker/Dockerfile -t "permission-system:$VERSION" .
    
    if [ $? -eq 0 ]; then
        log_success "镜像构建完成"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 更新配置文件
update_configs() {
    log_info "更新配置文件..."
    
    # 复制环境特定的配置文件
    cp "$DEPLOY_DIR/environments/$ENVIRONMENT/docker-compose.override.yml" \
       "$DEPLOY_DIR/docker/docker-compose.override.yml" 2>/dev/null || true
    
    # 生成 SSL 证书（如果不存在）
    SSL_DIR="$DEPLOY_DIR/docker/ssl"
    if [ ! -f "$SSL_DIR/cert.pem" ] || [ ! -f "$SSL_DIR/key.pem" ]; then
        log_info "生成自签名 SSL 证书..."
        mkdir -p "$SSL_DIR"
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$SSL_DIR/key.pem" \
            -out "$SSL_DIR/cert.pem" \
            -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
        
        log_success "SSL 证书生成完成"
    fi
}

# 部署服务
deploy_services() {
    log_info "部署服务..."
    
    cd "$DEPLOY_DIR/docker"
    
    # 设置环境变量
    export VERSION="$VERSION"
    
    # 停止现有服务
    docker-compose down
    
    # 启动新服务
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        log_success "服务部署完成"
    else
        log_error "服务部署失败"
        exit 1
    fi
}

# 等待服务启动
wait_for_services() {
    log_info "等待服务启动..."
    
    # 等待数据库
    log_info "等待数据库启动..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose -f "$DEPLOY_DIR/docker/docker-compose.yml" exec -T postgres pg_isready -U postgres &>/dev/null; then
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "数据库启动超时"
        exit 1
    fi
    
    # 等待应用
    log_info "等待应用启动..."
    timeout=120
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health &>/dev/null; then
            break
        fi
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "应用启动超时"
        exit 1
    fi
    
    log_success "所有服务启动完成"
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    docker-compose -f "$DEPLOY_DIR/docker/docker-compose.yml" exec -T permission-app \
        python -m alembic upgrade head
    
    if [ $? -eq 0 ]; then
        log_success "数据库迁移完成"
    else
        log_error "数据库迁移失败"
        exit 1
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查应用健康状态
    if curl -f http://localhost:8000/health; then
        log_success "应用健康检查通过"
    else
        log_error "应用健康检查失败"
        exit 1
    fi
    
    # 检查数据库连接
    if docker-compose -f "$DEPLOY_DIR/docker/docker-compose.yml" exec -T permission-app \
        python -c "from app.core.database import database; print('Database OK')"; then
        log_success "数据库连接检查通过"
    else
        log_error "数据库连接检查失败"
        exit 1
    fi
    
    # 检查 Redis 连接
    if docker-compose -f "$DEPLOY_DIR/docker/docker-compose.yml" exec -T redis redis-cli ping; then
        log_success "Redis 连接检查通过"
    else
        log_error "Redis 连接检查失败"
        exit 1
    fi
}

# 清理旧镜像
cleanup() {
    log_info "清理旧镜像..."
    
    # 删除未使用的镜像
    docker image prune -f
    
    # 删除旧版本镜像（保留最近3个版本）
    docker images "permission-system" --format "table {{.Tag}}\t{{.ID}}" | \
        tail -n +4 | awk '{print $2}' | xargs -r docker rmi
    
    log_success "清理完成"
}

# 发送通知
send_notification() {
    if [ -n "$WEBHOOK_URL" ]; then
        log_info "发送部署通知..."
        
        curl -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{
                \"text\": \"权限系统部署完成\",
                \"attachments\": [{
                    \"color\": \"good\",
                    \"fields\": [
                        {\"title\": \"环境\", \"value\": \"$ENVIRONMENT\", \"short\": true},
                        {\"title\": \"版本\", \"value\": \"$VERSION\", \"short\": true},
                        {\"title\": \"时间\", \"value\": \"$(date)\", \"short\": false}
                    ]
                }]
            }" &>/dev/null
        
        log_success "部署通知已发送"
    fi
}

# 主函数
main() {
    log_info "=========================================="
    log_info "权限系统部署脚本 v1.0"
    log_info "=========================================="
    
    # 执行部署步骤
    check_env_vars
    check_dependencies
    
    if [ "$ENVIRONMENT" = "production" ]; then
        backup_database
    fi
    
    build_images
    update_configs
    deploy_services
    wait_for_services
    run_migrations
    health_check
    cleanup
    send_notification
    
    log_success "=========================================="
    log_success "权限系统部署完成！"
    log_success "环境: $ENVIRONMENT"
    log_success "版本: $VERSION"
    log_success "访问地址: https://localhost"
    log_success "=========================================="
}

# 错误处理
trap 'log_error "部署过程中发生错误，退出码: $?"' ERR

# 执行主函数
main "$@"