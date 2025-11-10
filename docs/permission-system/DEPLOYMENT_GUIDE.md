# 权限系统部署指南

## 概述

本指南详细介绍权限系统的部署流程，包括环境准备、配置说明、部署步骤和验证方法。

## 目录

- [环境要求](#环境要求)
- [部署架构](#部署架构)
- [快速部署](#快速部署)
- [生产部署](#生产部署)
- [配置说明](#配置说明)
- [故障排除](#故障排除)

## 环境要求

### 1. 硬件要求

#### 最小配置
- CPU: 2核心
- 内存: 4GB RAM
- 磁盘: 20GB 可用空间
- 网络: 100Mbps

#### 推荐配置
- CPU: 4核心或更多
- 内存: 8GB RAM或更多
- 磁盘: 100GB SSD
- 网络: 1Gbps

#### 生产环境配置
- CPU: 8核心或更多
- 内存: 16GB RAM或更多
- 磁盘: 500GB SSD（支持RAID）
- 网络: 10Gbps（冗余网络）

### 2. 软件要求

#### 必需软件
```bash
# Docker
Docker Engine 20.10+
Docker Compose 2.0+

# 操作系统
Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
或其他支持Docker的Linux发行版

# 网络
开放端口: 80, 443, 8000 (可选)
```

#### 可选软件
```bash
# 监控工具
Prometheus
Grafana
ELK Stack

# 负载均衡
Nginx
HAProxy

# 数据库（如果外部部署）
PostgreSQL 13+
Redis 6+
```

## 部署架构

### 1. 单机部署架构
```
┌─────────────────────────────────────┐
│              服务器                  │
├─────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐          │
│  │  Nginx  │  │   App   │          │
│  │  :80    │  │  :8000  │          │
│  │  :443   │  │         │          │
│  └─────────┘  └─────────┘          │
│  ┌─────────┐  ┌─────────┐          │
│  │PostgreSQL│ │  Redis  │          │
│  │  :5432  │  │  :6379  │          │
│  └─────────┘  └─────────┘          │
└─────────────────────────────────────┘
```

### 2. 高可用部署架构
```
┌─────────────────┐    ┌─────────────────┐
│   负载均衡器     │    │   负载均衡器     │
│   (主)          │    │   (备)          │
└─────────────────┘    └─────────────────┘
         │                       │
    ┌────┴───────────────────────┴────┐
    │                                 │
┌───▼────┐  ┌─────────┐  ┌─────────┐ │
│ App 1  │  │ App 2   │  │ App 3   │ │
│ :8000  │  │ :8000   │  │ :8000   │ │
└────────┘  └─────────┘  └─────────┘ │
    │           │           │        │
    └───────────┼───────────┘        │
                │                    │
    ┌───────────▼───────────┐        │
    │    PostgreSQL 集群     │        │
    │   (主从复制/读写分离)   │        │
    └───────────────────────┘        │
                │                    │
    ┌───────────▼───────────┐        │
    │     Redis 集群        │        │
    │   (哨兵模式/集群模式)   │        │
    └───────────────────────┘        │
└─────────────────────────────────────┘
```

## 快速部署

### 1. 开发环境部署

#### 克隆代码
```bash
git clone https://github.com/your-org/permission-system.git
cd permission-system
```

#### 配置环境
```bash
# 复制环境配置文件
cp deploy/environments/development/.env.example .env

# 编辑配置文件
vim .env
```

#### 启动服务
```bash
# 使用Docker Compose启动
docker-compose -f deploy/docker/docker-compose.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 初始化数据
```bash
# 运行数据库迁移
docker-compose exec permission-app python -m alembic upgrade head

# 创建超级用户
docker-compose exec permission-app python scripts/create_superuser.py
```

### 2. 测试环境部署

#### 使用部署脚本
```bash
# 赋予执行权限
chmod +x deploy/scripts/deploy.sh

# 部署到测试环境
./deploy/scripts/deploy.sh testing v2.0.1
```

#### 验证部署
```bash
# 健康检查
curl http://localhost/health

# 登录测试
curl -X POST http://localhost/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 生产部署

### 1. 部署前准备

#### 服务器准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 创建应用用户
sudo useradd -m -s /bin/bash appuser
sudo usermod -aG docker appuser
```

#### 安全配置
```bash
# 配置防火墙
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 禁用root登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 配置fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 2. SSL证书配置

#### 使用Let's Encrypt
```bash
# 安装certbot
sudo apt install certbot -y

# 获取SSL证书
sudo certbot certonly --standalone -d yourdomain.com

# 复制证书到部署目录
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deploy/docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deploy/docker/ssl/key.pem
sudo chown appuser:appuser deploy/docker/ssl/*
```

#### 自动续期
```bash
# 添加续期任务
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### 3. 生产环境配置

#### 环境变量配置
```bash
# 编辑生产环境配置
vim deploy/environments/production/.env

# 必须修改的配置项
SECRET_KEY=your-super-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
DB_PASSWORD=your-strong-database-password
REDIS_PASSWORD=your-redis-password
```

#### 数据库配置优化
```bash
# PostgreSQL配置优化
cat >> deploy/docker/postgresql.conf << EOF
# 内存配置
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# 连接配置
max_connections = 200
superuser_reserved_connections = 3

# 检查点配置
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# 日志配置
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
EOF
```

### 4. 执行生产部署

#### 使用部署脚本
```bash
# 切换到应用用户
sudo su - appuser

# 克隆代码
git clone https://github.com/your-org/permission-system.git
cd permission-system

# 执行部署
./deploy/scripts/deploy.sh production v2.0.1
```

#### 手动部署步骤
```bash
# 1. 构建镜像
docker build -f deploy/docker/Dockerfile -t permission-system:v2.0.1 .

# 2. 启动服务
cd deploy/docker
docker-compose up -d

# 3. 等待服务启动
sleep 30

# 4. 运行迁移
docker-compose exec permission-app python -m alembic upgrade head

# 5. 创建超级用户
docker-compose exec permission-app python scripts/create_superuser.py

# 6. 健康检查
curl -f http://localhost/health
```

## 配置说明

### 1. 应用配置

#### 核心配置
```bash
# 应用基础配置
APP_NAME=权限系统
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# 安全配置
SECRET_KEY=your-secret-key  # 至少32字符
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### 数据库配置
```bash
# PostgreSQL配置
DB_HOST=postgres
DB_PORT=5432
DB_NAME=permission_system
DB_USER=postgres
DB_PASSWORD=your-password
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# 连接池配置
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
```

#### 缓存配置
```bash
# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-password
REDIS_DB=0
REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}

# 缓存TTL配置
CACHE_TTL=3600
PERMISSION_CACHE_TTL=1800
USER_CACHE_TTL=900
```

### 2. 安全配置

#### CORS配置
```bash
# 跨域配置
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*
```

#### 限流配置
```bash
# API限流
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/hour
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_SENSITIVE=5/minute
```

### 3. 监控配置

#### 日志配置
```bash
# 日志设置
LOG_FORMAT=json
LOG_FILE=/app/logs/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10
LOG_ROTATION=daily
```

#### 指标配置
```bash
# Prometheus指标
ENABLE_METRICS=true
METRICS_PORT=9090
METRICS_PATH=/metrics
```

## 故障排除

### 1. 常见部署问题

#### 服务启动失败
```bash
# 检查Docker服务
sudo systemctl status docker

# 检查容器状态
docker-compose ps

# 查看容器日志
docker-compose logs permission-app
docker-compose logs postgres
docker-compose logs redis
```

#### 端口冲突
```bash
# 检查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
sudo netstat -tlnp | grep :8000

# 修改端口配置
vim docker-compose.yml
```

#### 权限问题
```bash
# 检查文件权限
ls -la deploy/docker/ssl/
ls -la logs/

# 修复权限
sudo chown -R appuser:appuser /app
sudo chmod 600 deploy/docker/ssl/key.pem
```

### 2. 数据库问题

#### 连接失败
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U postgres

# 测试连接
docker-compose exec postgres psql -U postgres -d permission_system -c "SELECT 1;"

# 检查配置
docker-compose exec permission-app env | grep DATABASE_URL
```

#### 迁移失败
```bash
# 检查迁移状态
docker-compose exec permission-app python -m alembic current

# 查看迁移历史
docker-compose exec permission-app python -m alembic history

# 手动执行迁移
docker-compose exec permission-app python -m alembic upgrade head
```

### 3. 网络问题

#### SSL证书问题
```bash
# 检查证书有效性
openssl x509 -in deploy/docker/ssl/cert.pem -text -noout

# 测试SSL连接
openssl s_client -connect localhost:443

# 更新证书
sudo certbot renew
```

#### 负载均衡问题
```bash
# 检查Nginx配置
docker-compose exec nginx nginx -t

# 重新加载配置
docker-compose exec nginx nginx -s reload

# 查看访问日志
docker-compose logs nginx
```

## 升级指南

### 1. 版本升级流程

#### 准备升级
```bash
# 1. 备份数据
./deploy/scripts/backup.sh

# 2. 检查新版本兼容性
git diff v2.0.0..v2.1.0 -- database/migrations/

# 3. 在测试环境验证
./deploy/scripts/deploy.sh testing v2.1.0
```

#### 执行升级
```bash
# 1. 停止服务
docker-compose down

# 2. 更新代码
git pull origin main
git checkout v2.1.0

# 3. 重新部署
./deploy/scripts/deploy.sh production v2.1.0

# 4. 验证升级
curl -f https://yourdomain.com/health
```

#### 回滚流程
```bash
# 如果升级失败，执行回滚
git checkout v2.0.0
./deploy/scripts/deploy.sh production v2.0.0

# 恢复数据库（如果需要）
./deploy/scripts/restore.sh backup_file.sql
```

### 2. 零停机升级

#### 蓝绿部署
```bash
# 1. 部署新版本到绿环境
./deploy/scripts/deploy.sh production-green v2.1.0

# 2. 验证绿环境
curl -f https://green.yourdomain.com/health

# 3. 切换流量到绿环境
./deploy/scripts/switch_traffic.sh green

# 4. 验证切换成功
curl -f https://yourdomain.com/health

# 5. 停止蓝环境
./deploy/scripts/stop_environment.sh blue
```

## 性能调优

### 1. 应用层优化

#### 连接池配置
```python
# 数据库连接池
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}

# Redis连接池
REDIS_CONFIG = {
    "connection_pool_kwargs": {
        "max_connections": 50,
        "retry_on_timeout": True,
        "socket_keepalive": True,
        "socket_keepalive_options": {}
    }
}
```

#### 缓存优化
```bash
# Redis内存优化
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# 缓存预热
docker-compose exec permission-app python scripts/warm_cache.py
```

### 2. 系统层优化

#### 内核参数调优
```bash
# 网络优化
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65535' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf

# 文件描述符限制
echo '* soft nofile 65535' >> /etc/security/limits.conf
echo '* hard nofile 65535' >> /etc/security/limits.conf

# 应用生效
sysctl -p
```

#### Docker优化
```bash
# Docker daemon配置
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65536,
      "Soft": 65536
    }
  }
}
EOF

sudo systemctl restart docker
```

---

**文档版本**: v2.0  
**最后更新**: 2025-10-10  
**适用版本**: 权限系统 v2.0+