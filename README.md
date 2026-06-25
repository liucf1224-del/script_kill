# 剧本杀项目 - 快速开始

> 支持2-4人多人本 + 单人沉浸式剧本（《问佛》风格）

---

## 🚀 快速开始

### 本地开发（Windows）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动开发服务器（支持热更新）
python dev.py

# 3. 访问
http://localhost:8080
```

**✅ 修改代码自动重启，无需手动重启服务器**

---

### VPS部署（Linux - Docker）

```bash
# 1. 上传代码到VPS
scp -r script_kill root@your-vps:/root/

# 2. SSH登录
ssh root@your-vps

# 3. 启动Docker
cd /root/script_kill
docker-compose up -d

# 4. 访问
http://your-vps-ip:8080
```

---

## 📁 项目结构

```
script_kill/
├── 📖 创作指南
│   ├── CREATE_2PLAYER_SCRIPT_GUIDE.md   # 2人本指南
│   ├── CREATE_4PLAYER_SCRIPT_GUIDE.md   # 4人本指南
│   └── CREATE_SOLO_SCRIPT_GUIDE.md      # 单人本指南（《问佛》风格）
│
├── 🚀 部署配置
│   ├── DEPLOYMENT_GUIDE.md              # 详细部署指南
│   ├── Dockerfile                       # Docker镜像
│   ├── docker-compose.yml               # Docker编排
│   └── requirements.txt                 # Python依赖
│
├── 💻 服务端
│   ├── server.py                        # Flask服务器
│   ├── dev.py                           # 开发服务器（热更新）
│   └── generate_audio.py                # TTS音频生成
│
├── 🎨 前端
│   └── public/
│       ├── index.html
│       ├── app.js                       # ✅ 已实现房间号自动填充
│       └── styles.css
│
└── 📚 剧本
    └── demo/
        ├── yizhu_weimian_demo.json      # 3人本示例（遗嘱未眠）
        ├── diaochan_fengyun.json        # 3人本（貂蝉风云录·诙谐三国野史）
        └── huagu_solo.json              # 单人本示例（画骨·沉浸式解谜）
```

---

## 🎯 核心功能

### ✅ 已实现
- **多人本系统**：2-4人剧本杀
- **单人本系统**：沉浸式解谜（《问佛》风格）
- **房间号功能**：
  - ✅ URL链接分享自动填充
  - ✅ 粘贴文本智能提取
  - ✅ 一键复制邀请
- **TTS语音**：Edge-TTS自动生成
- **WebSocket**：实时同步
- **热更新**：dev.py开发模式

---

## 📝 创作剧本

### 让 Hermes 创作剧本

```bash
# 单人本（《问佛》风格）
请阅读 CREATE_SOLO_SCRIPT_GUIDE.md
创作一个单人沉浸式剧本杀
输出到：demo/xxx_solo.json

# 2人本
请阅读 CREATE_2PLAYER_SCRIPT_GUIDE.md
创作一个2人剧本杀
输出到：demo/xxx_2player.json

# 4人本
请阅读 CREATE_4PLAYER_SCRIPT_GUIDE.md
创作一个4人剧本杀
输出到：demo/xxx_4player.json
```

### 生成TTS音频（可选）

```bash
python generate_audio.py
```

---

## 🔥 工作流

```
┌─────────────────────────────────────────────────┐
│ 本地开发（Windows）                              │
│                                                 │
│ python dev.py      ← 热更新，快速迭代           │
│ 修改代码自动重启                                 │
└──────────────────┬──────────────────────────────┘
                   │
                   ↓ 测试通过
                   │
┌──────────────────┴──────────────────────────────┐
│ VPS部署（Linux）                                 │
│                                                 │
│ docker-compose up -d  ← 稳定运行，环境隔离      │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ 技术栈

- **后端**：Python 3.12 + Flask + WebSocket
- **前端**：原生 JavaScript + CSS
- **数据库**：SQLite3
- **TTS**：Edge-TTS
- **部署**：Docker + docker-compose

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | 详细部署指南 |
| [CREATE_2PLAYER_SCRIPT_GUIDE.md](CREATE_2PLAYER_SCRIPT_GUIDE.md) | 2人本创作指南 |
| [CREATE_4PLAYER_SCRIPT_GUIDE.md](CREATE_4PLAYER_SCRIPT_GUIDE.md) | 4人本创作指南 |
| [CREATE_SOLO_SCRIPT_GUIDE.md](CREATE_SOLO_SCRIPT_GUIDE.md) | 单人本创作指南 |
| [TTS_CONFIG.md](TTS_CONFIG.md) | TTS音色配置 |
| [AUDIO_GUIDE.md](AUDIO_GUIDE.md) | 音频生成指南 |

---

## 🎮 使用说明

### 1. 启动服务

**本地开发**：
```bash
python dev.py
```

**VPS演示**：
```bash
docker-compose up -d
```

### 2. 访问游戏

```
http://localhost:8080        # 本地
http://your-vps-ip:8080     # VPS
```

### 3. 创建房间

1. 登录（输入昵称）
2. 选择剧本
3. 点击"创建/回到我的房间"
4. 复制邀请链接发给好友

### 4. 加入房间

**方式1：点击链接**（推荐）
```
好友发来：http://xxx/?room=9CA37F
点击后自动填充房间号
```

**方式2：粘贴文本**
```
粘贴："房间号 9CA37F"
自动提取：9CA37F
```

**方式3：手动输入**
```
直接输入6位房间号
```

---

## 🆘 常见问题

### Q: 本地开发如何热更新？
```bash
python dev.py  # 修改代码自动重启
```

### Q: VPS如何查看日志？
```bash
docker-compose logs -f
```

### Q: 如何停止服务？
```bash
# 本地：Ctrl+C
# VPS：docker-compose down
```

### Q: 如何重新构建Docker镜像？
```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## 📞 快速命令

```bash
# 本地开发
pip install -r requirements.txt
python dev.py

# VPS部署
docker-compose up -d
docker-compose logs -f
docker-compose down
docker-compose restart

# 生成TTS音频
python generate_audio.py
```

---

## 🎉 版本信息

- **版本**：v1.0
- **更新日期**：2026/6/23
- **Python**：3.12+
- **Docker**：20.10+

---

**🚀 开始使用：`python dev.py`**
