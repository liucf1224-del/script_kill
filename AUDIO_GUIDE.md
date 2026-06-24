# 🎙️ TTS 音频生成使用指南

## 快速开始

### 1. 安装依赖
```bash
pip install requests
```

### 2. 生成音频
```bash
python generate_audio.py
```

脚本会自动：
- 读取 `demo/yizhu_weimian_demo.json`
- 提取所有需要TTS的文本（约40段）
- 调用MiMo API生成音频
- 保存到 `public/audio/yizhu_weimian/`
- 生成更新后的JSON: `demo/yizhu_weimian_demo_with_audio.json`

### 3. 替换配置文件
生成成功后，用更新后的JSON替换原文件：
```bash
# Windows
copy demo\yizhu_weimian_demo_with_audio.json demo\yizhu_weimian_demo.json

# Linux/Mac
cp demo/yizhu_weimian_demo_with_audio.json demo/yizhu_weimian_demo.json
```

### 4. 启动服务器
```bash
python server.py
# 或使用热更新模式
python dev.py
```

### 5. 刷新网页
前端会自动检测音频字段并显示播放按钮 🔊

---

## 📁 生成的文件结构

```
public/audio/yizhu_weimian/
├── characters/
│   ├── 3001/               # 林砚舟
│   │   ├── introduce.mp3   # 角色介绍
│   │   ├── script.mp3      # 私密剧本
│   │   ├── secret.mp3      # 秘密
│   │   ├── task.mp3        # 任务
│   │   ├── discovery_0.mp3 # 线索1
│   │   └── discovery_1.mp3 # 线索2
│   ├── 3002/               # 林晚棠
│   └── 3003/               # 周予衡
└── rounds/
    ├── 1/                  # 第1轮
    │   ├── scene.mp3       # 场景描述
    │   ├── guide.mp3       # 主持提示
    │   ├── clue_0.mp3      # 公开线索1
    │   ├── clue_1.mp3      # 公开线索2
    │   ├── question_0.mp3  # 讨论问题1
    │   └── question_1.mp3  # 讨论问题2
    ├── 2/                  # 第2轮
    └── 3/                  # 第3轮
```

---

## ⚙️ 配置说明

### 修改API Key
编辑 `generate_audio.py`，修改以下行：
```python
MIMO_API_KEY = "your_api_key_here"
```

### 生成其他剧本
修改脚本中的配置：
```python
SCRIPT_JSON = "demo/your_script.json"
OUTPUT_DIR = "public/audio/your_script_name"
```

---

## 🎯 JSON配置示例

生成后，JSON会自动添加音频路径：

**角色介绍：**
```json
{
  "introduce": "男，32岁，林氏集团执行总裁...",
  "introduce_audio": "/audio/yizhu_weimian/characters/3001/introduce.mp3"
}
```

**场景描述：**
```json
{
  "scenePrompt": "窗外暴雨未停...",
  "scenePrompt_audio": "/audio/yizhu_weimian/rounds/1/scene.mp3"
}
```

**线索内容：**
```json
{
  "keyword": "书房门禁记录",
  "content": "21:42林启山进入书房...",
  "content_audio": "/audio/yizhu_weimian/rounds/1/clue_0.mp3"
}
```

---

## ⏱️ 生成时间

- 单个音频：2-5秒
- 总计40个音频：约2-4分钟
- **只需生成一次，永久使用**

---

## 🔧 故障排除

### 问题1：requests模块未找到
```bash
pip install requests
```

### 问题2：API调用失败
检查：
- API Key是否正确
- 网络连接是否正常
- 是否超过API配额

### 问题3：音频文件无法播放
检查：
- 文件是否生成成功（查看文件大小）
- 浏览器控制台是否有错误
- 音频路径是否正确

---

## 📝 后续新剧本自动化

### 方案：Hermes生成 + AI批量音频

**工作流：**
```
1. Hermes生成剧本JSON
2. 修改 generate_audio.py 配置
3. 运行生成脚本
4. 替换JSON文件
5. 刷新网页
```

**未来可以写一个自动化脚本，完全无人工干预！**

---

## 🎉 完成效果

用户在使用时会看到：
- 角色卡片旁有 🔊 按钮
- 点击即可播放角色介绍
- 场景、线索、问题都可播放
- 本地音频，即点即播，无延迟

---

**生成日期：** 2026/6/23  
**维护者：** AI 助手
