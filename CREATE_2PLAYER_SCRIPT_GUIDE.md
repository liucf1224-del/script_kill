# 剧本杀2人本创作指南 - Hermes 使用文档

> **目标**: 生成符合系统规范的2人剧本杀JSON文件，包含完整的角色、线索、轮次和TTS音频路径配置。

---

## 📋 任务概述

你需要创作一个**2人剧本杀**，参考 `demo/yizhu_weimian_demo.json` 的结构，但调整为2个角色。

---

## 📂 文件输出位置

```
项目根目录/
├── demo/
│   └── [你的剧本名称].json    ← 输出到这里
├── public/
│   ├── audio/                  ← TTS音频会自动生成到这里
│   ├── default_cover.png       ← 默认封面
│   └── sleep.mp3              ← 默认背景音乐
└── ...
```

**输出文件名格式**: `demo/[剧本英文名]_2player.json`  
例如：`demo/midnight_library_2player.json`

---

## 🎯 2人本特点

### 与3人本的区别

| 项目 | 3人本（遗嘱未眠） | 2人本 |
|------|------------------|-------|
| 玩家数量 | 3人 | 2人 |
| 角色关系 | 三角关系/多方博弈 | 双人对抗/合作/秘密 |
| 线索数量 | 每轮2条公开线索 | 每轮1-2条公开线索 |
| 讨论问题 | 每轮2个问题 | 每轮1-2个问题 |
| 游戏时长 | 5-8分钟 | 建议4-7分钟 |
| 推理难度 | 中等 | 稍简单（线索更集中）|

### 2人本剧情建议

**适合的题材**：
- 🎭 **双人对抗**：凶手vs侦探、竞争者vs竞争者
- 💔 **情感剧**：恋人、亲人、挚友之间的误会或秘密
- 🤝 **合作推理**：两人共同揭开真相
- 🎪 **身份反转**：互相隐藏身份或目的

**不适合的题材**：
- ❌ 复杂的多方博弈（需要3人以上）
- ❌ 过于依赖第三方中立者的剧情

---

## 📝 完整JSON结构模板

```json
{
  "err": 0,
  "msg": "",
  "params": {
    "userId": 10001,
    "script": {
      "scriptId": 900002,
      "scriptName": "午夜图书馆",
      "status": 1,
      "narrator_voice": "冰糖",
      "album": "",
      "cover": "/default_cover.png",
      "music": "/sleep.mp3",
      "player": 2,
      "introduce": "深夜的大学图书馆，两名学生意外发现了一本不应该存在的手稿。随着他们翻阅内容，过去的真相逐渐浮现，而他们之间的关系也变得扑朔迷离。这不是偶然的相遇，而是命运早已安排好的重逢...",
      "scene": "现代悬疑·大学图书馆",
      "author": "Hermes AI",
      "score": 0,
      "round": 3,
      "playedCount": 0,
      "price": 0,
      "duration": "用户自定义",
      "difficulty": "新手友好",
      "style": "轻推理 / 情感还原 / 双人秘密",
      "hostTip": "适合2人游戏：角色之间有秘密联系，推理线索相对集中。主持人引导两名玩家互相试探，逐步揭开真相。",
      "flow": [
        {
          "step": 1,
          "title": "开场与选角",
          "duration": "1分钟",
          "content": "展示故事简介、两名角色卡，让玩家选择角色并阅读私密剧本。"
        },
        {
          "step": 2,
          "title": "三轮搜证问答",
          "duration": "3-4分钟",
          "content": "每轮展示场景提示、公开线索和讨论问题，引导玩家拼出时间线和真相。"
        },
        {
          "step": 3,
          "title": "最终还原",
          "duration": "1-2分钟",
          "content": "玩家选择真相答案，展示标准答案和结局。"
        }
      ],
      "tags": [
        "现代",
        "悬疑",
        "校园",
        "推理",
        "二人本",
        "短时长"
      ],
      "characters": [
        {
          "id": 4001,
          "name": "角色A名字",
          "voice": "白桦",
          "introduce": "男/女，年龄，身份背景，性格特点。",
          "avatar": "",
          "flag": 1,
          "roleTag": "角色标签",
          "publicGoal": "公开目标描述",
          "data": {
            "script": "你是XX。（第一人称叙述角色背景、当前困境、隐藏的秘密）",
            "task": "我的任务：\n1、XXX\n2、XXX\n3、XXX\n4、XXX",
            "secret": "你隐瞒的秘密：（关键信息，不能让对方知道）",
            "discovery": [
              {
                "id": 5001,
                "keyword": "私密线索1",
                "type": "类型",
                "content": "线索详细内容...",
                "isPublic": false,
                "content_audio": "/audio/[剧本英文名]/characters/4001/discovery_0.mp3"
              },
              {
                "id": 5002,
                "keyword": "私密线索2",
                "type": "类型",
                "content": "线索详细内容...",
                "isPublic": true,
                "content_audio": "/audio/[剧本英文名]/characters/4001/discovery_1.mp3"
              }
            ],
            "script_audio": "/audio/[剧本英文名]/characters/4001/script.mp3",
            "secret_audio": "/audio/[剧本英文名]/characters/4001/secret.mp3",
            "task_audio": "/audio/[剧本英文名]/characters/4001/task.mp3"
          },
          "introduce_audio": "/audio/[剧本英文名]/characters/4001/introduce.mp3"
        },
        {
          "id": 4002,
          "name": "角色B名字",
          "voice": "茉莉",
          "introduce": "女/男，年龄，身份背景，性格特点。",
          "avatar": "",
          "flag": 2,
          "roleTag": "角色标签",
          "publicGoal": "公开目标描述",
          "data": {
            "script": "你是XX。（第一人称叙述）",
            "task": "我的任务：\n1、XXX\n2、XXX\n3、XXX\n4、XXX",
            "secret": "你隐瞒的秘密：（关键信息）",
            "discovery": [
              {
                "id": 5003,
                "keyword": "私密线索1",
                "type": "类型",
                "content": "线索详细内容...",
                "isPublic": false,
                "content_audio": "/audio/[剧本英文名]/characters/4002/discovery_0.mp3"
              },
              {
                "id": 5004,
                "keyword": "私密线索2",
                "type": "类型",
                "content": "线索详细内容...",
                "isPublic": true,
                "content_audio": "/audio/[剧本英文名]/characters/4002/discovery_1.mp3"
              }
            ],
            "script_audio": "/audio/[剧本英文名]/characters/4002/script.mp3",
            "secret_audio": "/audio/[剧本英文名]/characters/4002/secret.mp3",
            "task_audio": "/audio/[剧本英文名]/characters/4002/task.mp3"
          },
          "introduce_audio": "/audio/[剧本英文名]/characters/4002/introduce.mp3"
        }
      ],
      "rounds": [
        {
          "round": 1,
          "title": "第一轮标题",
          "duration": "1-2分钟",
          "scenePrompt": "场景描述：营造氛围，引出第一轮线索...",
          "goal": "本轮目标：玩家需要了解什么信息",
          "hostGuide": "主持提示：如何引导玩家讨论",
          "publicClues": [
            {
              "id": 6001,
              "keyword": "公开线索1",
              "type": "类型",
              "content": "线索详细内容...",
              "content_audio": "/audio/[剧本英文名]/rounds/1/clue_0.mp3"
            },
            {
              "id": 6002,
              "keyword": "公开线索2",
              "type": "类型",
              "content": "线索详细内容...",
              "content_audio": "/audio/[剧本英文名]/rounds/1/clue_1.mp3"
            }
          ],
          "questions": [
            {
              "text": "讨论问题1：引导玩家思考的问题？",
              "audio": "/audio/[剧本英文名]/rounds/1/question_0.mp3"
            },
            {
              "text": "讨论问题2：深入推理的问题？",
              "audio": "/audio/[剧本英文名]/rounds/1/question_1.mp3"
            }
          ],
          "scenePrompt_audio": "/audio/[剧本英文名]/rounds/1/scene.mp3",
          "hostGuide_audio": "/audio/[剧本英文名]/rounds/1/guide.mp3"
        },
        {
          "round": 2,
          "title": "第二轮标题",
          "duration": "1-2分钟",
          "scenePrompt": "场景描述...",
          "goal": "本轮目标...",
          "hostGuide": "主持提示...",
          "publicClues": [
            {
              "id": 6003,
              "keyword": "公开线索3",
              "type": "类型",
              "content": "线索详细内容...",
              "content_audio": "/audio/[剧本英文名]/rounds/2/clue_0.mp3"
            }
          ],
          "questions": [
            {
              "text": "讨论问题：关键问题？",
              "audio": "/audio/[剧本英文名]/rounds/2/question_0.mp3"
            }
          ],
          "scenePrompt_audio": "/audio/[剧本英文名]/rounds/2/scene.mp3",
          "hostGuide_audio": "/audio/[剧本英文名]/rounds/2/guide.mp3"
        },
        {
          "round": 3,
          "title": "第三轮标题（真相揭晓）",
          "duration": "1-2分钟",
          "scenePrompt": "场景描述：最后的证据...",
          "goal": "本轮目标：还原完整真相",
          "hostGuide": "主持提示：引导玩家做最终判断",
          "publicClues": [
            {
              "id": 6004,
              "keyword": "关键证据",
              "type": "类型",
              "content": "决定性线索...",
              "content_audio": "/audio/[剧本英文名]/rounds/3/clue_0.mp3"
            }
          ],
          "questions": [
            {
              "text": "最终问题：真相是什么？",
              "audio": "/audio/[剧本英文名]/rounds/3/question_0.mp3"
            }
          ],
          "scenePrompt_audio": "/audio/[剧本英文名]/rounds/3/scene.mp3",
          "hostGuide_audio": "/audio/[剧本英文名]/rounds/3/guide.mp3"
        }
      ],
      "finalQuestions": [
        {
          "id": 7001,
          "title": "问题1标题",
          "options": [
            "选项A",
            "选项B",
            "选项C"
          ],
          "answer": "正确答案"
        },
        {
          "id": 7002,
          "title": "问题2标题",
          "options": [
            "选项A",
            "选项B",
            "选项C"
          ],
          "answer": "正确答案"
        }
      ],
      "answers": {
        "truth": "完整的真相揭示：事件的完整经过、角色的真实动机、隐藏的关系...",
        "keyEvidence": [
          "关键证据1",
          "关键证据2",
          "关键证据3"
        ],
        "finalChoice": "结局说明：开放式结局或明确结局的描述",
        "hostReveal": "主持复盘提示：按什么顺序揭示真相",
        "rewards": {
          "winner_message": "🏆 答题最佳！奖励2瓶啤酒 🍺🍺",
          "loser_message": "😅 再接再厉，罚喝3杯啤酒 🍺🍺🍺"
        }
      }
    }
  }
}
```

---

## 🎤 音色配置指南

### 参考 `TTS_CONFIG.md` 选择音色

| 角色类型 | 推荐音色 | Voice ID |
|---------|---------|----------|
| 成熟男性（30岁以上） | 白桦 | 白桦 |
| 理性男性（律师/医生/警察） | 苏打 | 苏打 |
| 知性女性（职场/成熟） | 茉莉 | 茉莉 |
| 年轻女性（学生/活泼） | 冰糖 | 冰糖 |
| 旁白/场景描述 | 冰糖 | 冰糖 |

### 2人本音色搭配建议

**对比型配对**（推荐）：
- 🎭 男+女：白桦 + 茉莉 / 苏打 + 冰糖
- 👥 同性但年龄差异：白桦 + 苏打（成熟vs年轻） / 茉莉 + 冰糖

**相似型配对**（特殊情节）：
- 👯‍♀️ 两位女性：茉莉 + 冰糖
- 👬 两位男性：白桦 + 苏打

---

## 📍 音频路径规范

### 命名规则

```
/audio/[剧本英文名]/
├── characters/
│   ├── 4001/                          ← 角色A
│   │   ├── introduce.mp3             ← 角色介绍
│   │   ├── script.mp3                ← 私密剧本
│   │   ├── secret.mp3                ← 角色秘密
│   │   ├── task.mp3                  ← 角色任务
│   │   ├── discovery_0.mp3           ← 私密线索1
│   │   └── discovery_1.mp3           ← 私密线索2
│   └── 4002/                          ← 角色B
│       └── (同上结构)
└── rounds/
    ├── 1/
    │   ├── scene.mp3                 ← 场景描述
    │   ├── guide.mp3                 ← 主持提示
    │   ├── clue_0.mp3                ← 公开线索1
    │   ├── clue_1.mp3                ← 公开线索2
    │   ├── question_0.mp3            ← 讨论问题1
    │   └── question_1.mp3            ← 讨论问题2
    ├── 2/
    │   └── (同上结构)
    └── 3/
        └── (同上结构)
```

### 示例

如果剧本英文名是 `midnight_library`，路径应该是：
```
/audio/midnight_library/characters/4001/introduce.mp3
/audio/midnight_library/rounds/1/scene.mp3
```

---

## ✅ 必填字段清单

### 剧本基础信息
- ✅ `scriptId`：唯一ID（不能与其他剧本重复，建议从900002开始递增）
- ✅ `scriptName`：剧本中文名称
- ✅ `narrator_voice`：旁白音色（默认"冰糖"）
- ✅ `cover`：封面路径（默认 `/default_cover.png`）
- ✅ `music`：背景音乐（默认 `/sleep.mp3`）
- ✅ `player`：固定为 `2`
- ✅ `introduce`：剧本简介（100-200字）
- ✅ `scene`：场景标签
- ✅ `duration`：游戏时长（用户自定义）
- ✅ `tags`：标签数组

### 角色信息（2个角色）
每个角色必须包含：
- ✅ `id`：唯一ID（4001, 4002）
- ✅ `name`：角色名
- ✅ `voice`：音色ID
- ✅ `introduce`：角色介绍
- ✅ `roleTag`：角色标签
- ✅ `publicGoal`：公开目标
- ✅ `data.script`：私密剧本
- ✅ `data.task`：角色任务
- ✅ `data.secret`：角色秘密
- ✅ `data.discovery`：至少2条私密线索
- ✅ 所有音频路径字段

### 轮次信息（3轮）
每轮必须包含：
- ✅ `round`：轮次编号（1, 2, 3）
- ✅ `title`：轮次标题
- ✅ `scenePrompt`：场景描述
- ✅ `hostGuide`：主持提示
- ✅ `publicClues`：至少1条公开线索
- ✅ `questions`：至少1个讨论问题
- ✅ 所有音频路径字段

### 最终问题
- ✅ 至少2个最终问题
- ✅ 每个问题包含title、options、answer

### 答案部分
- ✅ `truth`：完整真相
- ✅ `keyEvidence`：关键证据列表
- ✅ `rewards`：胜负奖励

---

## 🎨 创作提示

### 剧情设计建议

1. **核心冲突明确**
   - 两个角色之间有清晰的利益冲突或情感纠葛
   - 避免需要第三方调停的剧情

2. **秘密层次分明**
   - 每个角色有1-2个关键秘密
   - 秘密之间有关联，最终拼出完整真相

3. **线索分布合理**
   - 第1轮：建立时间线和基本关系
   - 第2轮：揭示关键矛盾或疑点
   - 第3轮：决定性证据出现

4. **推理难度适中**
   - 线索不要过于隐晦（2人本信息量较少）
   - 但也要有反转或意外

### 题材示例

**推荐题材**：
- 🎓 **校园悬案**：两位同学卷入神秘事件
- 💼 **职场阴谋**：同事之间的竞争与背叛
- 💔 **情感纠葛**：恋人/前任之间的误会
- 🏠 **家族秘密**：兄弟姐妹/亲子之间的隐情
- 🔍 **双重身份**：两人都隐藏真实身份

**避免题材**：
- ❌ 需要裁判/中立者的法庭戏
- ❌ 三方势力博弈
- ❌ 过于复杂的商业阴谋

---

## 📤 输出要求

### 文件命名
```
demo/[剧本英文名]_2player.json
```

例如：
- `demo/midnight_library_2player.json`
- `demo/broken_promise_2player.json`
- `demo/last_train_2player.json`

### 字符编码
- ✅ UTF-8 编码
- ✅ 确保中文字符正常显示

### JSON格式
- ✅ 严格遵守JSON语法
- ✅ 使用2空格缩进
- ✅ 所有字符串用双引号
- ✅ 数组和对象格式正确

---

## 🚀 给 Hermes 的完整提示词模板

```
请按照以下要求创作一个2人剧本杀：

【剧本设定】
- 题材：[你想要的题材，如"大学校园悬疑案"]
- 风格：轻推理 / 情感还原
- 时长：用户自定义
- 人数：2人

【要求】
1. 严格参考项目中的 `demo/yizhu_weimian_demo.json` 文件结构
2. 参考 `TTS_CONFIG.md` 选择合适的角色音色
3. 使用默认封面 `/default_cover.png`
4. 使用默认音乐 `/sleep.mp3`
5. 剧本ID使用 900002（如果已存在则递增）
6. 输出完整的JSON文件到 `demo/` 目录

【角色要求】
- 2个角色，每个角色有清晰的动机和秘密
- 音色配置参考TTS_CONFIG.md
- 每个角色至少2条私密线索

【轮次要求】
- 3轮搜证
- 每轮1-2条公开线索
- 每轮1-2个讨论问题

【真相设计】
- 最终真相需要两名玩家拼凑各自线索才能还原
- 至少2个最终问题
- 提供完整的真相揭示

【项目位置】
- 当前项目在：[告诉Hermes你的项目路径]
- 输出文件到：demo/ 目录
- 文件名：demo/[剧本英文名]_2player.json

请开始创作！
```

---

## 📋 检查清单

创作完成后，请检查：

### 结构完整性
- [ ] JSON格式正确，无语法错误
- [ ] 所有必填字段都已填写
- [ ] scriptId唯一且不重复
- [ ] player字段为2

### 角色配置
- [ ] 2个角色，ID分别为4001和4002
- [ ] 每个角色都有voice字段
- [ ] 每个角色至少2条discovery
- [ ] 所有音频路径格式正确

### 轮次配置
- [ ] 3轮游戏，编号1-3
- [ ] 每轮至少1条publicClues
- [ ] 每轮至少1个questions
- [ ] 所有音频路径格式正确

### 默认资源
- [ ] cover使用 `/default_cover.png`
- [ ] music使用 `/sleep.mp3`
- [ ] narrator_voice设置为 `冰糖`

### 音频路径
- [ ] 所有音频路径遵循 `/audio/[剧本英文名]/` 格式
- [ ] 角色音频路径正确
- [ ] 轮次音频路径正确

---

## 💡 示例剧本构思

### 示例1：《午夜图书馆》
- **题材**：校园悬疑
- **角色**：
  - 学生A（白桦）：表面来借书，实际在寻找某个秘密文件
  - 学生B（茉莉）：图书管理员，知道某些不能说的真相
- **冲突**：两人各有目的，但真相需要合作才能揭开
- **反转**：他们其实是多年前某个事件的见证者，现在重新相遇

### 示例2：《最后一班车》
- **题材**：悬疑推理
- **角色**：
  - 乘客A（苏打）：神秘的陌生人
  - 乘客B（冰糖）：深夜赶车的都市白领
- **冲突**：车上发生了某个事件，两人互相怀疑
- **反转**：原来是精心设计的局

---

## 📞 需要帮助？

如果生成过程中遇到问题：
1. 检查 `demo/yizhu_weimian_demo.json` 参考结构
2. 查看 `TTS_CONFIG.md` 确认音色配置
3. 确保JSON格式正确（使用JSON验证工具）
4. 确认所有音频路径格式一致

---

**版本**: v1.0  
**更新日期**: 2026/6/23  
**创建者**: AI Assistant

---

## 🎉 开始创作吧！

按照这个指南，你可以创作出符合系统规范的高质量2人剧本。记住：
- ✅ 结构规范
- ✅ 音频路径正确
- ✅ 使用默认资源
- ✅ 剧情紧凑有趣

祝创作顺利！🚀
