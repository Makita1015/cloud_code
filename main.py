import os
import textwrap
import anthropic
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont

JST = timezone(timedelta(hours=9))
today = datetime.now(JST).strftime("%Y-%m-%d")
filename = f"articles/{today}-ai-news.md"
thumbnail_path = f"articles/images/{today}.png"

# --- 記事生成 ---
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": (
            "今日のAI・機械学習分野のニュースや注目トピックを日本語で1000字程度にまとめた記事を書いてください。\n"
            "構成：\n"
            "1. 冒頭の一言：AIにちなんだ短いギャグやダジャレを1文だけ入れてください（例：「AIの進化が止まらない…まるで学習率が高すぎるみたいだ。」のような感じ）\n"
            "2. 本日のハイライト（2〜3トピック）\n"
            "3. 各トピックの概要と背景\n"
            "4. まとめと今後の展望\n"
            "タイトルは「今日のAIニュースまとめ（YYYY年MM月DD日）」の形式にしてください。\n"
            "本文中に # や ## などのマークダウン見出し記号は使わないでください。段落の区切りは空行で表現してください。"
        )
    }]
)

content = message.content[0].text.strip()
lines = content.split("\n")
title = f"今日のAIニュースまとめ（{datetime.now(JST).strftime('%Y年%m月%d日')}）"
body = "\n".join(lines[1:]).strip()


# --- サムネイル生成 ---
def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJKjp-Bold.otf" if bold else "/usr/share/fonts/truetype/noto/NotoSansCJKjp-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def create_thumbnail(title_text: str, date_str: str, out_path: str) -> None:
    W, H = 1280, 670
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # グラデーション背景（濃い青→紫）
    c_start = (8, 12, 70)
    c_end = (80, 8, 110)
    for y in range(H):
        t = y / H
        r = int(c_start[0] + (c_end[0] - c_start[0]) * t)
        g = int(c_start[1] + (c_end[1] - c_start[1]) * t)
        b = int(c_start[2] + (c_end[2] - c_start[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # 装飾ライン
    draw.rectangle([(0, H - 6), (W, H)], fill=(130, 80, 255))

    # AI NEWS バッジ（左上）
    badge_font = load_font(28, bold=True)
    bx, by = 36, 36
    draw.rounded_rectangle([(bx, by), (bx + 160, by + 52)], radius=10, fill=(100, 60, 240))
    draw.text((bx + 18, by + 10), "AI NEWS", font=badge_font, fill=(255, 255, 255))

    # タイトル（中央）
    title_font = load_font(58, bold=True)
    max_chars = 18
    wrapped = textwrap.wrap(title_text, width=max_chars)[:3]  # 最大3行
    line_h = 72
    total_h = len(wrapped) * line_h
    start_y = (H - total_h) // 2 - 10

    for i, line in enumerate(wrapped):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = start_y + i * line_h
        # テキストシャドウ
        draw.text((x + 3, y + 3), line, font=title_font, fill=(0, 0, 0, 120))
        draw.text((x, y), line, font=title_font, fill=(255, 255, 255))

    # 日付（右下）
    date_font = load_font(30)
    date_display = datetime.now(JST).strftime("%Y.%m.%d")
    bbox = draw.textbbox((0, 0), date_display, font=date_font)
    dw = bbox[2] - bbox[0]
    draw.text((W - dw - 36, H - 52), date_display, font=date_font, fill=(200, 180, 255))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    print(f"サムネイル作成完了: {out_path}")


create_thumbnail(title, today, thumbnail_path)

# --- Markdown 保存 ---
frontmatter = f"""---
title: "{title}"
emoji: "🤖"
type: "idea"
topics: ["ai"]
published: true
---

"""

os.makedirs("articles", exist_ok=True)
with open(filename, "w", encoding="utf-8") as f:
    f.write(frontmatter + body + "\n")

print(f"記事作成完了: {filename}")
