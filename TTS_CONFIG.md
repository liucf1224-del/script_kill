# 剧本杀 TTS 语音播报配置指南

## 📚 MiMo TTS 音色列表

### 中文音色

| 音色名称 | Voice ID | 性别 | 特点 | 适合角色 |
|---------|----------|------|------|---------|
| 冰糖 | 冰糖 | 女 | 温柔甜美 | 年轻女性、旁白 |
| 茉莉 | 茉莉 | 女 | 知性优雅 | 成熟女性、知识分子 |
| 苏打 | 苏打 | 男 | 沉稳理性 | 律师、医生、商人 |
| 白桦 | 白桦 | 男 | 成熟磁性 | 企业家、权威人物 |

### 英文音色

| 音色名称 | Voice ID | 性别 | 特点 |
|---------|----------|------|------|
| Mia | Mia | 女 | 活泼明快 |
| Chloe | Chloe | 女 | 温柔优雅 |
| Milo | Milo | 男 | 年轻活力 |
| Dean | Dean | 男 | 成熟稳重 |

### 默认音色
- **mimo_default**: 中国集群默认为"冰糖"，其他集群默认为"Mia"

---

## 🎭 《遗嘱未眠》角色音色配置

### 推荐配置

```json
{
  "characters": [
    {
      "id": 3001,
      "name": "林砚舟",
      "voice": "白桦",
      "voice_description": "男，32岁，冷静强势的集团总裁，需要成熟稳重的男声"
    },
    {
      "id": 3002,
      "name": "林晚棠",
      "voice": "茉莉",
      "voice_description": "女，27岁，温和疏离的养女，知性优雅的女声"
    },
    {
      "id": 3003,
      "name": "周予衡",
      "voice": "苏打",
      "voice_description": "男，35岁，理性谨慎的律师，沉稳理性的男声"
    }
  ],
  "narrator_voice": "冰糖",
  "narrator_description": "旁白、场景描述、公开线索使用默认甜美女声"
}
```

---

## 📍 语音播报位置规划

### 1. 旁白类内容（使用旁白音色）

✅ **每轮场景描述**
- 位置：每轮顶部的场景介绍区域
- 内容：`scenePrompt` 字段
- 示例：_"窗外暴雨未停，旧楼只剩书房亮着灯..."_

✅ **主持提示**
- 位置：场景描述下方（只房主可见）
- 内容：`hostGuide` 字段
- 示例：_"让每名玩家说出自己何时到过书房..."_

✅ **公开线索**
- 位置：线索卡片内容区域
- 内容：每张线索的 `content` 字段
- 示例：_"书房门禁记录：21:42林启山进入书房..."_

✅ **讨论问题**
- 位置：问题卡片区域
- 内容：`questions` 数组内容
- 示例：_"谁最后一次确认林启山仍然活着？"_

### 2. 角色专属内容（使用角色音色）

✅ **角色介绍**
- 位置：选角界面的角色卡片
- 内容：`introduce` 字段
- 示例（林砚舟）：_"男，32岁，林氏集团执行总裁..."_

✅ **私密剧本**
- 位置：角色详情对话框
- 内容：`data.script` 字段
- 示例：_"你是林砚舟。父亲林启山死前一周..."_

✅ **角色秘密**
- 位置：角色详情对话框的"你的秘密"区域
- 内容：`data.secret` 字段
- 示例：_"你在22:55返回过书房门口..."_

✅ **角色任务**
- 位置：角色详情对话框的"角色任务"区域
- 内容：`data.task` 字段

✅ **角色线索**
- 位置：角色详情对话框的"你的线索"区域
- 内容：`data.discovery` 数组的每条线索

---

## 🔧 API 调用示例

### Python 后端实现

```python
import requests

MIMO_API_KEY = "your_api_key_here"
MIMO_API_URL = "https://api.mimo.mi.com/v1/audio/speech"

def generate_speech(text: str, voice: str = "冰糖") -> bytes:
    """
    生成语音
    
    Args:
        text: 要合成的文本
        voice: 音色ID（冰糖/茉莉/苏打/白桦等）
    
    Returns:
        音频数据（bytes）
    """
    response = requests.post(
        MIMO_API_URL,
        headers={
            "Authorization": f"Bearer {MIMO_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mimo-v2.5-tts",
            "input": text,
            "voice": voice
        },
        timeout=30
    )
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"TTS API 错误: {response.status_code}")
```

### 前端播放实现

```javascript
async function playTTS(text, voice = '冰糖') {
  const response = await fetch('/api/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, voice })
  });
  
  const audioBlob = await response.blob();
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  await audio.play();
}
```

---

## 📝 配置剧本指南（给 Hermes）

### 步骤 1：为每个角色添加音色字段

在剧本 JSON 文件的 `characters` 数组中，为每个角色添加 `voice` 字段：

```json
{
  "characters": [
    {
      "id": 3001,
      "name": "角色名",
      "voice": "白桦",  // 👈 添加这个字段
      "introduce": "角色介绍..."
    }
  ]
}
```

### 步骤 2：选择合适的音色

**角色类型推荐：**
- 👨‍💼 **成熟男性**（企业家、长辈）→ `白桦`
- 👔 **理性男性**（律师、医生、警察）→ `苏打`
- 👩‍💼 **知性女性**（职场精英、成熟女性）→ `茉莉`
- 👧 **年轻女性**（学生、活泼角色）→ `冰糖`

### 步骤 3：测试音色

可以通过 MiMo 官网的试听功能测试每个音色是否符合角色设定。

### 步骤 4：配置旁白音色（可选）

在剧本根级别添加：

```json
{
  "scriptName": "遗嘱未眠",
  "narrator_voice": "冰糖",  // 👈 旁白音色
  "characters": [...]
}
```

---

## 🎯 实施优先级建议

### Phase 1：基础播报（优先）
- ✅ 角色介绍播报（选角时）
- ✅ 私密剧本播报（角色详情）
- ✅ 场景描述播报（每轮开始）

### Phase 2：进阶功能
- ⏸️ 播放控制（暂停/继续/停止）
- 📊 播放进度条
- 🔊 音量控制

### Phase 3：优化体验
- 💾 音频缓存（相同文本不重复生成）
- ⚡ 预加载（提前生成下一轮音频）
- 🎭 情感控制（通过自然语言指令）

---

## ⚠️ 注意事项

1. **API 配额**：MiMo API 可能有调用次数限制，注意监控用量
2. **网络延迟**：首次播放需要等待 2-5 秒生成时间
3. **文本长度**：单次合成建议不超过 500 字，过长文本需分段
4. **缓存策略**：相同文本可以缓存音频，避免重复调用
5. **错误处理**：API 调用失败时显示友好提示，不影响游戏流程

---

## 🔗 相关文档

- MiMo TTS 官方文档: https://mimo.mi.com/docs/en-US/quick-start/usage-guide/audio/speech-synthesis-v2.5
- 支持的模型列表: mimo-v2.5-tts, mimo-v2.5-tts-voicedesign, mimo-v2.5-tts-voiceclone

---

**更新时间**: 2026/6/18  
**维护者**: AI 助手
