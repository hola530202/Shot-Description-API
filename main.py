"""
Shot Description Generator API
-------------------------------
輸入旁白或場景描述文字，回傳分鏡建議：
- 建議鏡頭類型（特寫、中景、全景等）
- 構圖方式
- 情緒基調
- 運鏡建議
- 燈光風格
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Shot Description Generator API",
    description="輸入場景旁白或描述，自動回傳專業分鏡建議，包含鏡頭類型、構圖、情緒基調與運鏡。",
    version="1.0.0"
)

# ──────────────────────────────────────────
# 資料結構定義
# ──────────────────────────────────────────

class SceneInput(BaseModel):
    description: str   # 場景旁白或描述文字
    mood: str = ""     # 可選：情緒提示（例如 "緊張"、"溫馨"、"懸疑"）

class ShotSuggestion(BaseModel):
    shot_number: int
    shot_type: str          # 鏡頭類型
    composition: str        # 構圖建議
    camera_movement: str    # 運鏡方式
    mood_tone: str          # 情緒基調
    lighting: str           # 燈光風格
    description: str        # 該鏡頭的畫面說明

class ShotBreakdown(BaseModel):
    shots: List[ShotSuggestion]
    total_shots: int
    estimated_screen_time: str   # 預估銀幕時間
    summary: str

# ──────────────────────────────────────────
# 鏡頭類型規則庫
# ──────────────────────────────────────────

SHOT_TYPES = {
    "close_up": "特寫（Close-up）",
    "medium": "中景（Medium Shot）",
    "wide": "全景（Wide Shot）",
    "extreme_close": "大特寫（Extreme Close-up）",
    "over_shoulder": "過肩鏡（Over-the-Shoulder）",
    "two_shot": "雙人鏡（Two Shot）",
    "pov": "主觀鏡（POV）",
    "establishing": "確立鏡（Establishing Shot）",
}

CAMERA_MOVES = {
    "static": "固定鏡頭",
    "pan": "橫搖（Pan）",
    "tilt": "仰俯搖（Tilt）",
    "dolly": "推拉鏡（Dolly）",
    "handheld": "手持搖晃",
    "crane": "升降鏡（Crane）",
}

LIGHTING_STYLES = {
    "natural": "自然光",
    "dramatic": "高反差戲劇性燈光",
    "soft": "柔光（Low-key）",
    "backlit": "逆光",
    "golden": "黃金時段暖光",
    "cold": "冷色調藍光",
}

# ──────────────────────────────────────────
# 場景分析邏輯
# ──────────────────────────────────────────

def detect_mood(text: str, hint: str = "") -> str:
    text_lower = (text + hint).lower()

    if any(k in text_lower for k in ["緊張", "追", "逃", "衝", "爆炸", "打", "危險", "tension", "chase", "fight", "danger"]):
        return "緊張刺激"
    elif any(k in text_lower for k in ["溫馨", "擁抱", "笑", "家", "愛", "warm", "hug", "love", "smile"]):
        return "溫馨感動"
    elif any(k in text_lower for k in ["悲", "哭", "離開", "死", "失去", "sad", "cry", "loss", "death"]):
        return "悲傷沉重"
    elif any(k in text_lower for k in ["神秘", "黑暗", "影子", "詭異", "mystery", "dark", "shadow", "eerie"]):
        return "懸疑神秘"
    elif any(k in text_lower for k in ["開心", "慶祝", "勝利", "party", "celebrate", "victory", "joy"]):
        return "歡快輕鬆"
    else:
        return "平靜敘事"

def build_shots(description: str, mood: str) -> List[ShotSuggestion]:
    """
    根據場景描述和情緒，生成一組分鏡建議。
    邏輯：每個場景通常由 確立鏡 → 中景/雙人鏡 → 特寫 → 反應鏡 組成。
    """
    detected_mood = detect_mood(description, mood) if not mood else mood
    shots = []

    # 判斷是否為對話場景
    has_dialogue = any(k in description for k in ["說", "問", "答", "告訴", "回答", "對話", "said", "asked", "told", "replied", ":"])
    # 判斷是否為動作場景
    has_action = any(k in description for k in ["跑", "走", "追", "打", "跳", "衝", "run", "walk", "chase", "fight", "jump"])
    # 判斷是否有情緒描寫
    has_emotion = any(k in description for k in ["感覺", "覺得", "想", "心", "眼淚", "feel", "thought", "heart", "tear"])

    # 鏡頭 1：確立鏡（交代環境）
    shots.append(ShotSuggestion(
        shot_number=1,
        shot_type=SHOT_TYPES["establishing"],
        composition="黃金比例構圖，主體置於畫面 1/3 處",
        camera_movement=CAMERA_MOVES["static"] if detected_mood in ["平靜敘事", "溫馨感動"] else CAMERA_MOVES["dolly"],
        mood_tone=detected_mood,
        lighting=LIGHTING_STYLES["natural"] if detected_mood in ["平靜敘事", "溫馨感動", "歡快輕鬆"] else LIGHTING_STYLES["dramatic"],
        description=f"交代場景環境，建立空間感。{description[:40]}..."
    ))

    # 鏡頭 2：主要行動鏡
    if has_action:
        shots.append(ShotSuggestion(
            shot_number=2,
            shot_type=SHOT_TYPES["wide"],
            composition="主體置中，保留動作空間",
            camera_movement=CAMERA_MOVES["handheld"] if detected_mood == "緊張刺激" else CAMERA_MOVES["pan"],
            mood_tone=detected_mood,
            lighting=LIGHTING_STYLES["dramatic"] if detected_mood == "緊張刺激" else LIGHTING_STYLES["natural"],
            description="捕捉完整動作幅度，展現身體語言"
        ))
    elif has_dialogue:
        shots.append(ShotSuggestion(
            shot_number=2,
            shot_type=SHOT_TYPES["two_shot"],
            composition="兩人面對面，各佔畫面左右",
            camera_movement=CAMERA_MOVES["static"],
            mood_tone=detected_mood,
            lighting=LIGHTING_STYLES["soft"],
            description="建立對話雙方的空間關係"
        ))
    else:
        shots.append(ShotSuggestion(
            shot_number=2,
            shot_type=SHOT_TYPES["medium"],
            composition="主體腰部以上入鏡，背景虛化",
            camera_movement=CAMERA_MOVES["dolly"],
            mood_tone=detected_mood,
            lighting=LIGHTING_STYLES["natural"],
            description="跟隨主角，展現肢體動作與表情"
        ))

    # 鏡頭 3：情緒特寫
    if has_emotion or has_dialogue:
        shots.append(ShotSuggestion(
            shot_number=3,
            shot_type=SHOT_TYPES["close_up"],
            composition="臉部特寫，眼神為焦點",
            camera_movement=CAMERA_MOVES["static"],
            mood_tone=detected_mood,
            lighting=LIGHTING_STYLES["soft"] if detected_mood in ["溫馨感動", "悲傷沉重"] else LIGHTING_STYLES["dramatic"],
            description="捕捉角色細微表情，強化情緒張力"
        ))

    # 鏡頭 4：反應鏡或收尾鏡
    if has_dialogue:
        shots.append(ShotSuggestion(
            shot_number=len(shots) + 1,
            shot_type=SHOT_TYPES["over_shoulder"],
            composition="前景人物佔 1/3，後景說話者清晰可見",
            camera_movement=CAMERA_MOVES["static"],
            mood_tone=detected_mood,
            lighting=LIGHTING_STYLES["soft"],
            description="過肩反應鏡，切換說話方視角"
        ))
    else:
        shots.append(ShotSuggestion(
            shot_number=len(shots) + 1,
            shot_type=SHOT_TYPES["wide"],
            composition="留白構圖，主體偏移一側",
            camera_movement=CAMERA_MOVES["crane"] if detected_mood in ["悲傷沉重", "平靜敘事"] else CAMERA_MOVES["tilt"],
            mood_tone=detected_mood,
            lighting=LIGHTING_STYLES["golden"] if detected_mood in ["溫馨感動"] else LIGHTING_STYLES["cold"],
            description="收尾鏡，提供情緒緩衝與餘韻"
        ))

    return shots


# ──────────────────────────────────────────
# 主要 API 端點
# ──────────────────────────────────────────

@app.post("/predict", response_model=ShotBreakdown)
async def generate_shots(input: SceneInput):
    """
    輸入場景旁白或描述，回傳專業分鏡建議。

    **輸入欄位：**
    - description：場景文字描述（必填）
    - mood：情緒提示，例如「緊張」「溫馨」「懸疑」（選填）

    **回傳欄位：**
    - shots：每顆鏡頭的詳細建議（鏡頭類型、構圖、運鏡、燈光、情緒）
    - total_shots：建議鏡頭總數
    - estimated_screen_time：預估銀幕時間
    - summary：整體分鏡摘要
    """
    desc = input.description.strip()
    if not desc:
        return ShotBreakdown(shots=[], total_shots=0, estimated_screen_time="0 秒", summary="場景描述為空。")

    shots = build_shots(desc, input.mood)
    total = len(shots)

    # 預估銀幕時間（每顆鏡頭平均 3-5 秒）
    min_sec = total * 3
    max_sec = total * 5
    screen_time = f"{min_sec}–{max_sec} 秒（約 {round(max_sec/60, 1)} 分鐘）" if max_sec >= 60 else f"{min_sec}–{max_sec} 秒"

    detected_mood = detect_mood(desc, input.mood)
    summary = (
        f"建議 {total} 顆鏡頭，情緒基調為「{detected_mood}」，"
        f"預估銀幕時間 {screen_time}。"
        f"包含：{', '.join(set(s.shot_type for s in shots))}。"
    )

    return ShotBreakdown(
        shots=shots,
        total_shots=total,
        estimated_screen_time=screen_time,
        summary=summary
    )


# ──────────────────────────────────────────
# 健康檢查
# ──────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "Shot Description Generator API",
        "version": "1.0.0",
        "usage": "POST /predict with JSON: {\"description\": \"...\", \"mood\": \"...\"}",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
