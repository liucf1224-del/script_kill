# 剧本杀项目部署指南

## 📋 VPS环境配置

```bash
Docker: 29.4.1
Python: 3.12.3 (python3)
Node.js: v22.22.0
npm: 10.9.4
```

---

## 🎯 推荐方案：Docker部署（最适合演示）

### ✅ 为什么选择Docker？

1. **环境隔离**：完全独立，不污染系统
2. **一键部署**：构建一次，到处运行
3. **易于维护**：容器化管理，方便更新
4. **演示友好**：快速启动/停止，易于演示
5. **已安装Docker**：你的VPS已有Docker 29.4.1

---

## 📦 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **Docker** | 环境隔离、易部署、适合演示 | 需要Dockerfile | ⭐⭐⭐⭐⭐ |
| uv + venv | 快速、现代、轻量 | VPS没装uv，需要安装 | ⭐⭐⭐⭐ |
| python3 -m venv | 系统自带、无需安装 | 手动管理依赖 | ⭐⭐⭐ |
| conda | 环境管理强大 | VPS没装，体积大 | ⭐⭐ |

---

## 🚀 推荐部署方案：Docker

### 1. 创建 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python3", "server.py"]
```

### 2. 创建 .dockerignore

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.db
*.sqlite3
.env
.venv/
venv/
.git/
.gitignore
node_modules/
*.log
```

### 3. 创建 docker-compose.yml（可选）

```yaml
version: '3.8'

services:
  script-kill:
    build: .
    container_name: script-kill-app
    ports:
      - "8080:8080"
    volumes:
      - ./data.json:/app/data.json
      - ./demo:/app/demo
      - ./public:/app/public
      - ./script_kill.sqlite3:/app/script_kill.sqlite3
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
```

### 4. 部署命令

```bash
# 本地构建镜像
docker build -t script-kill:latest .

# 本地测试
docker run -p 8080:8080 script-kill:latest

# 或使用docker-compose（推荐）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 5. VPS部署流程

```bash
# 1. 上传代码到VPS
scp -r d:\ai_code\script_kill root@your-vps-ip:/root/

# 2. SSH登录VPS
ssh root@your-vps-ip

# 3. 进入项目目录
cd /root/script_kill

# 4. 构建并启动
docker-compose up -d

# 5. 查看状态
docker ps
docker-compose logs -f
```

---

## 🔧 备选方案1：uv + venv（现代化）

如果你想用uv（VPS需先安装）：

```bash
# VPS安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活环境
source .venv/bin/activate  # Linux
# 或 .venv\Scripts\activate  # Windows本地

# 安装依赖
uv pip install -r requirements.txt

# 运行
python3 server.py

# 后台运行
nohup python3 server.py > app.log 2>&1 &
```

---

## 🔧 备选方案2：原生python3 + venv（最简单）

无需安装任何工具，直接用系统的python3：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活环境
source venv/bin/activate  # Linux/VPS
# 或 venv\Scripts\activate  # Windows本地

# 安装依赖
pip install -r requirements.txt

# 运行
python3 server.py

# 后台运行（生产环境）
nohup python3 server.py > app.log 2>&1 &
```

---

## 📝 requirements.txt

确保你有完整的依赖文件：

```txt
flask==3.0.0
flask-cors==4.0.0
websockets==12.0
edge-tts==6.1.9
aiohttp==3.9.1
```

---

## 🎯 演示场景推荐

### 快速演示（5分钟内）
**推荐：Docker**
```bash
# 一键启动
docker-compose up -d

# 演示完毕
docker-compose down
```

### 本地开发
**推荐：原生python3 + venv**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

### 生产部署
**推荐：Docker + nginx反向代理**
```bash
docker-compose up -d
# 配置nginx SSL证书
```

---

## 🔥 最佳实践建议

### 演示级部署（推荐）

```bash
# VPS上操作
cd /root/script_kill

# 方式1：Docker（最推荐）
docker-compose up -d

# 方式2：原生venv（最简单）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nohup python3 server.py > app.log 2>&1 &
```

### 开发环境（本地）

```bash
# Windows本地开发
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python server.py

# 或用uv（更快）
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
python server.py
```

---

## 🌐 端口和访问

```bash
# 服务器监听
0.0.0.0:8080

# 本地访问
http://localhost:8080

# VPS访问
http://your-vps-ip:8080

# 建议配置nginx反向代理
# http://your-domain.com → http://localhost:8080
```

---

## 📊 方案总结

| 场景 | 推荐方案 | 命令 |
|------|----------|------|
| **VPS演示** | Docker | `docker-compose up -d` |
| **VPS快速测试** | python3 venv | `python3 -m venv venv && source venv/bin/activate` |
| **本地开发（Windows）** | 原生python + venv | `python -m venv venv && venv\Scripts\activate` |
| **本地开发（现代化）** | uv + venv | `uv venv && .venv\Scripts\activate` |

---

## 🎬 演示流程（Docker版）

### 准备阶段（一次性）
```bash
# 1. 创建Dockerfile、docker-compose.yml
# 2. 上传到VPS
scp -r script_kill root@vps:/root/

# 3. VPS构建
cd /root/script_kill
docker-compose build
```

### 演示阶段（每次演示）
```bash
# 启动（5秒内）
docker-compose up -d

# 查看状态
docker ps

# 访问
http://your-vps-ip:8080

# 演示完毕
docker-compose down
```

---

## 💡 最终建议（推荐工作流）

### 📌 明确的开发/部署分离

| 环境 | 方案 | 命令 | 说明 |
|------|------|------|------|
| **本地开发** | `dev.py` 热更新 | `python dev.py` | ✅ 修改代码自动重启 |
| **VPS演示** | Docker稳定运行 | `docker-compose up -d` | ✅ 环境隔离、一键部署 |

### 🔥 标准工作流

```
本地开发（Windows）
   ↓
python dev.py        ← 热更新，快速迭代
   ↓
测试通过
   ↓
上传VPS（Linux）
   ↓
docker-compose up -d ← 稳定运行，无需热更新
```

### ⚙️ 为什么这样设计？

1. **本地开发不需要Docker**
   - `dev.py`已支持热更新（watchdog）
   - 直接运行，调试方便
   - 修改代码立即生效

2. **VPS部署用Docker**
   - 环境隔离，不污染系统
   - 一键启动/停止，适合演示
   - 稳定运行，无需热更新
   - Docker内热更新意义不大（volume映射有性能损耗）

---

## 🚀 立即开始

选择你的方案：

### A. Docker部署（推荐）
```bash
# 1. 创建Dockerfile和docker-compose.yml（见上文）
# 2. 上传到VPS
# 3. 运行
docker-compose up -d
```

### B. 原生venv部署（最简单）
```bash
# VPS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

---

**选择建议：演示用Docker，开发用原生venv** 🎯
