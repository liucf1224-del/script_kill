"""
剧本杀 TTS 音频批量生成脚本

功能：
1. 读取剧本JSON文件
2. 提取所有需要语音播报的文本
3. 调用MiMo API批量生成音频
4. 保存到指定目录
5. 更新JSON配置，添加音频路径

使用方法:
1. 配置API Key (在脚本中或环境变量)
2. 运行: python generate_audio.py
3. 音频文件会保存到 public/audio/{script_name}/
4. 更新后的JSON会保存为 demo/{script_name}_with_audio.json

依赖:
pip install requests
"""

import json
import os
import time
import base64
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库，请先安装:")
    print("   pip install requests")
    exit(1)

# ==================== 配置 ====================

# MiMo API 配置
MIMO_API_KEY = "tp-csicbb3fxt0xysqjvo5lifti3ebrfh28kb367jox9i28atri"
MIMO_API_URL = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"

# 文件路径
SCRIPT_JSON = "demo/yizhu_weimian_demo.json"
OUTPUT_DIR = "public/audio/yizhu_weimian"

# ==================== 核心功能 ====================

def generate_speech(text: str, voice: str, output_path: str) -> bool:
    """
    调用MiMo API生成语音并保存
    
    Args:
        text: 要合成的文本
        voice: 音色ID（冰糖/茉莉/苏打/白桦）
        output_path: 输出文件路径
    
    Returns:
        是否成功
    """
    try:
        response = requests.post(
            MIMO_API_URL,
            headers={
                "Authorization": f"Bearer {MIMO_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mimo-v2.5-tts",
                "messages": [
                    {
                        "role": "assistant",
                        "content": text
                    }
                ],
                "audio": {
                    "format": "mp3",
                    "voice": voice
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            audio_base64 = data["choices"][0]["message"]["audio"]["data"]
            audio_bytes = base64.b64decode(audio_base64)
            
            # 保存音频文件
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            return True
        else:
            print(f"  ❌ API错误 {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ 生成失败: {e}")
        return False


def extract_texts_from_script(script: Dict) -> List[Tuple[str, str, str, str]]:
    """
    从剧本中提取所有需要TTS的文本
    
    Returns:
        List of (text, voice, category, filename)
    """
    texts = []
    narrator_voice = script.get("narrator_voice", "冰糖")
    
    # 1. 角色介绍、剧本、秘密、任务、线索
    for char in script.get("characters", []):
        char_id = char.get("id")
        char_name = char.get("name")
        char_voice = char.get("voice", "冰糖")
        
        # 角色介绍
        if char.get("introduce"):
            texts.append((
                char.get("introduce"),
                char_voice,
                f"characters/{char_id}",
                "introduce.mp3"
            ))
        
        # 私密数据
        data = char.get("data", {})
        
        # 私密剧本
        if data.get("script"):
            texts.append((
                data.get("script"),
                char_voice,
                f"characters/{char_id}",
                "script.mp3"
            ))
        
        # 秘密
        if data.get("secret"):
            texts.append((
                data.get("secret"),
                char_voice,
                f"characters/{char_id}",
                "secret.mp3"
            ))
        
        # 任务
        if data.get("task"):
            texts.append((
                data.get("task"),
                char_voice,
                f"characters/{char_id}",
                "task.mp3"
            ))
        
        # 角色线索
        for idx, discovery in enumerate(data.get("discovery", [])):
            if discovery.get("content"):
                texts.append((
                    f"{discovery.get('keyword')}：{discovery.get('content')}",
                    char_voice,
                    f"characters/{char_id}",
                    f"discovery_{idx}.mp3"
                ))
    
    # 2. 每轮的场景、提示、线索、问题
    for round_data in script.get("rounds", []):
        round_num = round_data.get("round")
        
        # 场景描述
        if round_data.get("scenePrompt"):
            texts.append((
                round_data.get("scenePrompt"),
                narrator_voice,
                f"rounds/{round_num}",
                "scene.mp3"
            ))
        
        # 主持提示
        if round_data.get("hostGuide"):
            texts.append((
                round_data.get("hostGuide"),
                narrator_voice,
                f"rounds/{round_num}",
                "guide.mp3"
            ))
        
        # 公开线索
        for idx, clue in enumerate(round_data.get("publicClues", [])):
            if clue.get("content"):
                texts.append((
                    f"{clue.get('keyword')}：{clue.get('content')}",
                    narrator_voice,
                    f"rounds/{round_num}",
                    f"clue_{idx}.mp3"
                ))
        
        # 讨论问题
        for idx, question in enumerate(round_data.get("questions", [])):
            texts.append((
                question,
                narrator_voice,
                f"rounds/{round_num}",
                f"question_{idx}.mp3"
            ))
    
    return texts


def update_json_with_audio_paths(script: Dict, audio_mapping: Dict[str, str]) -> Dict:
    """
    更新JSON配置，添加音频路径
    
    Args:
        script: 原始剧本数据
        audio_mapping: {文本内容: 音频路径}
    
    Returns:
        更新后的剧本数据
    """
    # 更新角色数据
    for char in script.get("characters", []):
        if char.get("introduce"):
            key = char.get("introduce")
            if key in audio_mapping:
                char["introduce_audio"] = audio_mapping[key]
        
        data = char.get("data", {})
        if data.get("script") and data.get("script") in audio_mapping:
            data["script_audio"] = audio_mapping[data.get("script")]
        
        if data.get("secret") and data.get("secret") in audio_mapping:
            data["secret_audio"] = audio_mapping[data.get("secret")]
        
        if data.get("task") and data.get("task") in audio_mapping:
            data["task_audio"] = audio_mapping[data.get("task")]
        
        for discovery in data.get("discovery", []):
            content_key = f"{discovery.get('keyword')}：{discovery.get('content')}"
            if content_key in audio_mapping:
                discovery["content_audio"] = audio_mapping[content_key]
    
    # 更新轮次数据
    for round_data in script.get("rounds", []):
        if round_data.get("scenePrompt") in audio_mapping:
            round_data["scenePrompt_audio"] = audio_mapping[round_data.get("scenePrompt")]
        
        if round_data.get("hostGuide") in audio_mapping:
            round_data["hostGuide_audio"] = audio_mapping[round_data.get("hostGuide")]
        
        for clue in round_data.get("publicClues", []):
            content_key = f"{clue.get('keyword')}：{clue.get('content')}"
            if content_key in audio_mapping:
                clue["content_audio"] = audio_mapping[content_key]
        
        for idx, question in enumerate(round_data.get("questions", [])):
            if question in audio_mapping:
                round_data["questions"][idx] = {
                    "text": question,
                    "audio": audio_mapping[question]
                }
    
    return script


def main():
    print("=" * 60)
    print("🎙️  剧本杀 TTS 音频批量生成")
    print("=" * 60)
    
    # 1. 读取剧本
    print(f"\n📖 读取剧本: {SCRIPT_JSON}")
    try:
        with open(SCRIPT_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            script = data.get("params", {}).get("script", data.get("script", data))
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return
    
    script_name = script.get("scriptName", "unknown")
    print(f"   剧本名: {script_name}")
    
    # 2. 提取文本
    print(f"\n🔍 提取需要TTS的文本...")
    texts = extract_texts_from_script(script)
    print(f"   共找到 {len(texts)} 段文本")
    
    # 3. 生成音频
    print(f"\n🎵 开始生成音频...")
    print(f"   输出目录: {OUTPUT_DIR}")
    
    audio_mapping = {}
    success_count = 0
    
    for idx, (text, voice, category, filename) in enumerate(texts, 1):
        # 构建输出路径
        output_path = os.path.join(OUTPUT_DIR, category, filename)
        web_path = f"/audio/yizhu_weimian/{category}/{filename}"
        
        # 显示进度
        short_text = text[:30] + "..." if len(text) > 30 else text
        print(f"\n[{idx}/{len(texts)}] {short_text}")
        print(f"   音色: {voice}")
        print(f"   路径: {output_path}")
        
        # 生成音频
        if generate_speech(text, voice, output_path):
            print(f"   ✅ 生成成功")
            audio_mapping[text] = web_path
            success_count += 1
        else:
            print(f"   ❌ 生成失败")
        
        # 避免API限流，稍微延迟
        if idx < len(texts):
            time.sleep(0.5)
    
    # 4. 更新JSON
    print(f"\n📝 更新JSON配置...")
    updated_script = update_json_with_audio_paths(script, audio_mapping)
    
    # 保存更新后的JSON
    output_json = SCRIPT_JSON.replace(".json", "_with_audio.json")
    
    # 保持原始JSON结构
    if "params" in data:
        data["params"]["script"] = updated_script
    else:
        data = updated_script
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ 已保存到: {output_json}")
    
    # 5. 总结
    print("\n" + "=" * 60)
    print("✅ 生成完成！")
    print("=" * 60)
    print(f"总计: {len(texts)} 段文本")
    print(f"成功: {success_count} 个音频")
    print(f"失败: {len(texts) - success_count} 个")
    print(f"\n📁 音频文件: {OUTPUT_DIR}")
    print(f"📄 更新后的JSON: {output_json}")
    print("\n💡 下一步:")
    print("   1. 检查生成的音频文件")
    print("   2. 用更新后的JSON替换原文件")
    print("   3. 前端会自动加载音频路径")
    print("=" * 60)


if __name__ == "__main__":
    main()
