#!/bin/bash

# 权限系统备份脚本
# 使用方法: ./backup.sh [backup_type]
# backup_type: full|db|config|logs

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 配置
BACKUP_TYPE=${1:-full}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 数据库备份
backup_database() {
    log_info "开始备份数据库..."
    
    local backup_file="$BACKUP_DIR/db_backup_$DATE.sql"
    
    # 使用pg_dump备份数据库
    docker-compose -f "$PROJECT_ROOT/deploy/docker/docker-compose.yml" exec -T postgres \
        pg_dump -U postgres -h localhost permission_system > "$backup_file"
    
    if [ $? -eq 0 ]; then
        # 压缩备份文件
        gzip "$backup_file"
        log_success "数据库备份完成: $backup_file.gz"
        
        # 计算文件大小
        local size=$(du -h "$backup_file.gz" | cut -f1)
        log_info "备份文件大小: $size"
        
        return 0
    else
        log_error "数据库备份失败"
        return 1
    fi
}

# 配置文件备份
backup_config() {
    log_info "开始备份配置文件..."
    
    local config_backup="$BACKUP_DIR/config_backup_$DATE.tar.gz"
    
    # 备份配置目录
    tar -czf "$config_backup" \
        -C "$PROJECT_ROOT" \
        deploy/environments/ \
        deploy/docker/ \
        config/ \
        2>/dev/null || true
    
    if [ -f "$config_backup" ]; then
        log_success "配置文件备份完成: $config_backup"
        
        # 计算文件大小
        local size=$(du -h "$config_backup" | cut -f1)
        log_info "备份文件大小: $size"
        
        return 0
    else
        log_error "配置文件备份失败"
        return 1
    fi
}

# 日志文件备份
backup_logs() {
    log_info "开始备份日志文件..."
    
    local logs_backup="$BACKUP_DIR/logs_backup_$DATE.tar.gz"
    
    # 备份日志目录
    if [ -d "$PROJECT_ROOT/logs" ]; then
        tar -czf "$logs_backup" \
            -C "$PROJECT_ROOT" \
            logs/ \
            2>/dev/null || true
        
        if [ -f "$logs_backup" ]; then
            log_success "日志文件备份完成: $logs_backup"
            
            # 计算文件大小
            local size=$(du -h "$logs_backup" | cut -f1)
            log_info "备份文件大小: $size"
            
            return 0
        else
            log_warning "日志文件备份失败或日志目录为空"
            return 1
        fi
    else
        log_warning "日志目录不存在，跳过日志备份"
        return 0
    fi
}

# 应用数据备份
backup_app_data() {
    log_info "开始备份应用数据..."
    
    local app_data_backup="$BACKUP_DIR/app_data_backup_$DATE.tar.gz"
    
    # 备份上传文件和其他应用数据
    local data_dirs=()
    
    if [ -d "$PROJECT_ROOT/uploads" ]; then
        data_dirs+=("uploads/")
    fi
    
    if [ -d "$PROJECT_ROOT/temp" ]; then
        data_dirs+=("temp/")
    fi
    
    if [ ${#data_dirs[@]} -gt 0 ]; then
        tar -czf "$app_data_backup" \
            -C "$PROJECT_ROOT" \
            "${data_dirs[@]}" \
            2>/dev/null || true
        
        if [ -f "$app_data_backup" ]; then
            log_success "应用数据备份完成: $app_data_backup"
            
            # 计算文件大小
            local size=$(du -h "$app_data_backup" | cut -f1)
            log_info "备份文件大小: $size"
            
            return 0
        else
            log_warning "应用数据备份失败或数据目录为空"
            return 1
        fi
    else
        log_warning "应用数据目录不存在，跳过应用数据备份"
        return 0
    fi
}

# 完整备份
backup_full() {
    log_info "开始完整备份..."
    
    local full_backup="$BACKUP_DIR/full_backup_$DATE.tar.gz"
    local temp_dir="$BACKUP_DIR/temp_$DATE"
    
    mkdir -p "$temp_dir"
    
    # 执行各项备份到临时目录
    cd "$temp_dir"
    
    # 数据库备份
    if backup_database; then
        mv "$BACKUP_DIR"/db_backup_*.gz . 2>/dev/null || true
    fi
    
    # 配置备份
    if backup_config; then
        mv "$BACKUP_DIR"/config_backup_*.tar.gz . 2>/dev/null || true
    fi
    
    # 日志备份
    if backup_logs; then
        mv "$BACKUP_DIR"/logs_backup_*.tar.gz . 2>/dev/null || true
    fi
    
    # 应用数据备份
    if backup_app_data; then
        mv "$BACKUP_DIR"/app_data_backup_*.tar.gz . 2>/dev/null || true
    fi
    
    # 创建完整备份
    cd "$BACKUP_DIR"
    tar -czf "$full_backup" -C "$temp_dir" .
    
    # 清理临时目录
    rm -rf "$temp_dir"
    
    if [ -f "$full_backup" ]; then
        log_success "完整备份完成: $full_backup"
        
        # 计算文件大小
        local size=$(du -h "$full_backup" | cut -f1)
        log_info "备份文件大小: $size"
        
        return 0
    else
        log_error "完整备份失败"
        return 1
    fi
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理旧备份文件..."
    
    # 保留最近7天的备份
    find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
    
    log_success "旧备份文件清理完成"
}

# 验证备份
verify_backup() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi
    
    # 检查文件大小
    local size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$size" -lt 1024 ]; then
        log_error "备份文件太小，可能备份失败: $backup_file"
        return 1
    fi
    
    # 检查压缩文件完整性
    if [[ "$backup_file" == *.gz ]]; then
        if ! gzip -t "$backup_file" 2>/dev/null; then
            log_error "备份文件损坏: $backup_file"
            return 1
        fi
    elif [[ "$backup_file" == *.tar.gz ]]; then
        if ! tar -tzf "$backup_file" >/dev/null 2>&1; then
            log_error "备份文件损坏: $backup_file"
            return 1
        fi
    fi
    
    log_success "备份文件验证通过: $backup_file"
    return 0
}

# 生成备份报告
generate_backup_report() {
    local report_file="$BACKUP_DIR/backup_report_$DATE.txt"
    
    cat > "$report_file" << EOF
权限系统备份报告
================

备份时间: $(date)
备份类型: $BACKUP_TYPE
备份目录: $BACKUP_DIR

备份文件列表:
EOF
    
    # 列出当前备份的文件
    find "$BACKUP_DIR" -name "*_$DATE.*" -type f | while read file; do
        local size=$(du -h "$file" | cut -f1)
        echo "  $(basename "$file") - $size" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

备份目录总大小: $(du -sh "$BACKUP_DIR" | cut -f1)
可用磁盘空间: $(df -h "$BACKUP_DIR" | awk 'NR==2 {print $4}')

备份状态: 成功
EOF
    
    log_success "备份报告生成: $report_file"
}

# 主函数
main() {
    log_info "=========================================="
    log_info "权限系统备份脚本 v1.0"
    log_info "备份类型: $BACKUP_TYPE"
    log_info "=========================================="
    
    # 检查Docker服务
    if ! docker-compose -f "$PROJECT_ROOT/deploy/docker/docker-compose.yml" ps | grep -q "Up"; then
        log_warning "部分服务未运行，备份可能不完整"
    fi
    
    # 执行备份
    case "$BACKUP_TYPE" in
        "db"|"database")
            backup_database
            ;;
        "config")
            backup_config
            ;;
        "logs")
            backup_logs
            ;;
        "app-data")
            backup_app_data
            ;;
        "full")
            backup_full
            ;;
        *)
            log_error "未知的备份类型: $BACKUP_TYPE"
            log_info "支持的备份类型: full, db, config, logs, app-data"
            exit 1
            ;;
    esac
    
    # 清理旧备份
    cleanup_old_backups
    
    # 生成备份报告
    generate_backup_report
    
    log_success "=========================================="
    log_success "备份完成！"
    log_success "备份目录: $BACKUP_DIR"
    log_success "=========================================="
}

# 错误处理
trap 'log_error "备份过程中发生错误，退出码: $?"' ERR

# 执行主函数
main "$@"