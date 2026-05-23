#!/usr/bin/env python3
"""
Instagram Reel Video Generator
美容サロン向けホームページ制作アカウント用
"""

import os
import json
import numpy as np
import anthropic
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips
import moviepy.video.fx as vfx

JST = timezone(timedelta(hours=9))
REEL_W, REEL_H = 1080, 1920
SLIDE_DURATION = 5
FPS = 24

THEMES = [
    "制作実績・Before/After",
    "制作の裏側・作業工程",
    "美容サロン集客Tips",
    "料金・サービス紹介",
    "よくある失敗例",
    "成功するサロンの共通点",
    "ホームページで差がつくポイント",
]

COLOR_SCHEMES = [
    {  # 制作実績: Rose Gold
        "bg": [(248, 225, 210), (255, 195, 215)],
        "accent": (185, 95, 120),
        "text": (65, 28, 48),
        "sub": (140, 75, 95),
        "badge_bg": (185, 95, 120),
        "badge_text": (255, 255, 255),
    },
    {  # 裏側: Deep Navy
        "bg": [(18, 28, 65), (32, 60, 95)],
        "accent": (95, 215, 185),
        "text": (255, 255, 255),
        "sub": (175, 225, 210),
        "badge_bg": (55, 155, 135),
        "badge_text": (255, 255, 255),
    },
    {  # Tips: Deep Purple
        "bg": [(78, 22, 115), (185, 42, 135)],
        "accent": (255, 215, 235),
        "text": (255, 255, 255),
        "sub": (230, 185, 215),
        "badge_bg": (215, 82, 155),
        "badge_text": (255, 255, 255),
    },
    {  # 料金: Cream Gold
        "bg": [(252, 248, 240), (255, 240, 210)],
        "accent": (178, 140, 58),
        "text": (52, 36, 12),
        "sub": (115, 82, 32),
        "badge_bg": (178, 140, 58),
        "badge_text": (255, 255, 255),
    },
    {  # 失敗例: Charcoal Red
        "bg": [(35, 25, 28), (70, 30, 38)],
        "accent": (220, 80, 95),
        "text": (255, 255, 255),
        "sub": (220, 180, 185),
        "badge_bg": (180, 55, 70),
        "badge_text": (255, 255, 255),
    },
    {  # 成功共通点: Forest Green
        "bg": [(20, 55, 42), (38, 100, 78)],
        "accent": (120, 235, 175),
        "text": (255, 255, 255),
        "sub": (175, 230, 205),
        "badge_bg": (60, 165, 120),
        "badge_text": (255, 255, 255),
    },
    {  # 差がつく: Indigo Sky
        "bg": [(28, 38, 115), (68, 85, 200)],
        "accent": (210, 225, 255),
        "text": (255, 255, 255),
        "sub": (185, 200, 245),
        "badge_bg": (100, 120, 210),
        "badge_text": (255, 255, 255),
    },
]

FONT_PATHS = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def get_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def jp_wrap(text: str, max_chars: int) -> list:
    lines = []
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            continue
        while len(para) > max_chars:
            lines.append(para[:max_chars])
            para = para[max_chars:]
        if para:
            lines.append(para)
    return lines


def gradient_image(w: int, h: int, top: tuple, bot: tuple) -> Image.Image:
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def draw_centered_text(draw, text, font, y, width, color, shadow_color=None):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    if shadow_color:
        draw.text((x + 3, y + 3), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3] - bbox[1]


def make_hook_slide(data: dict, scheme: dict, theme_name: str, account: str) -> np.ndarray:
    img = gradient_image(REEL_W, REEL_H, scheme["bg"][0], scheme["bg"][1])
    draw = ImageDraw.Draw(img)

    # Accent bars
    draw.rectangle([(0, 0), (REEL_W, 10)], fill=scheme["accent"])
    draw.rectangle([(0, REEL_H - 10), (REEL_W, REEL_H)], fill=scheme["accent"])

    # Decorative corner boxes
    for coords in [[(0, 0), (120, 120)], [(REEL_W - 120, 0), (REEL_W, 120)]]:
        overlay = Image.new("RGBA", (REEL_W, REEL_H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        ac = scheme["accent"]
        od.rectangle(coords, fill=(ac[0], ac[1], ac[2], 40))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Account name
    af = get_font(36)
    draw.text((50, 30), account, font=af, fill=scheme["sub"])

    # Theme badge
    bf = get_font(38)
    btext = theme_name
    bbox = draw.textbbox((0, 0), btext, font=bf)
    bw = bbox[2] - bbox[0] + 80
    bx = (REEL_W - bw) // 2
    by = 200
    draw.rounded_rectangle([(bx, by), (bx + bw, by + 75)], radius=38, fill=scheme["badge_bg"])
    tbbox = draw.textbbox((0, 0), btext, font=bf)
    draw.text((bx + (bw - (tbbox[2] - tbbox[0])) // 2, by + 18), btext, font=bf, fill=scheme["badge_text"])

    # Main title
    title = data.get("title", "")
    tf = get_font(82)
    t_lines = jp_wrap(title, 11)
    line_h = 105
    total_h = len(t_lines) * line_h
    ty = (REEL_H - total_h) // 2 - 60
    shadow = tuple(max(0, c - 60) for c in scheme["text"]) if scheme["text"] != (255, 255, 255) else (0, 0, 0)
    for line in t_lines[:5]:
        draw_centered_text(draw, line, tf, ty, REEL_W, scheme["text"], shadow_color=(shadow[0], shadow[1], shadow[2]))
        ty += line_h

    # Subtitle
    subtitle = data.get("subtitle", "")
    if subtitle:
        sf = get_font(46)
        s_lines = jp_wrap(subtitle, 16)
        sy = ty + 40
        for line in s_lines[:3]:
            draw_centered_text(draw, line, sf, sy, REEL_W, scheme["sub"])
            sy += 65

    # Scroll hint
    hint_f = get_font(40)
    draw.text((REEL_W // 2 - 100, REEL_H - 200), "▼  スワイプして見る", font=hint_f, fill=scheme["accent"])

    return np.array(img)


def make_content_slide(data: dict, scheme: dict, num: int, total_content: int, account: str) -> np.ndarray:
    img = gradient_image(REEL_W, REEL_H, scheme["bg"][0], scheme["bg"][1])
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (REEL_W, 10)], fill=scheme["accent"])
    draw.rectangle([(0, REEL_H - 10), (REEL_W, REEL_H)], fill=scheme["accent"])

    # Account
    af = get_font(32)
    draw.text((50, 25), account, font=af, fill=scheme["sub"])

    # Number circle
    nf = get_font(62)
    cx, cy, cr = 110, 210, 72
    draw.ellipse([(cx - cr, cy - cr), (cx + cr, cy + cr)], fill=scheme["accent"])
    ns = str(num)
    nbbox = draw.textbbox((0, 0), ns, font=nf)
    nw = nbbox[2] - nbbox[0]
    nh = nbbox[3] - nbbox[1]
    draw.text((cx - nw // 2, cy - nh // 2 - 5), ns, font=nf, fill=scheme["badge_text"])

    # Title
    title = data.get("title", "")
    tf = get_font(70)
    t_lines = jp_wrap(title, 13)
    ty = 145
    for line in t_lines[:3]:
        draw.text((205, ty), line, font=tf, fill=scheme["text"])
        ty += 92
    ty += 10

    # Divider
    draw.rectangle([(55, ty), (REEL_W - 55, ty + 6)], fill=scheme["accent"])
    ty += 50

    # Body
    body = data.get("body", "")
    bf = get_font(52)
    b_lines = jp_wrap(body, 15)
    for line in b_lines[:9]:
        draw.text((60, ty), line, font=bf, fill=scheme["text"])
        ty += 72

    # Progress dots
    dot_total = total_content + 2  # hook + content + cta
    dot_idx = num  # hook=0, content starts at 1
    dr = 11
    dsp = 42
    dtw = (dot_total - 1) * dsp + dr * 2
    dx = (REEL_W - dtw) // 2
    dy = REEL_H - 85
    for i in range(dot_total):
        ex = dx + i * dsp + dr
        col = scheme["accent"] if i == dot_idx else scheme["sub"]
        draw.ellipse([(ex - dr, dy - dr), (ex + dr, dy + dr)], fill=col)

    return np.array(img)


def make_cta_slide(data: dict, scheme: dict, account: str) -> np.ndarray:
    img = gradient_image(REEL_W, REEL_H, scheme["bg"][0], scheme["bg"][1])
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (REEL_W, 10)], fill=scheme["accent"])
    draw.rectangle([(0, REEL_H - 10), (REEL_W, REEL_H)], fill=scheme["accent"])

    # Account
    af = get_font(32)
    draw.text((50, 25), account, font=af, fill=scheme["sub"])

    # Main message
    title = data.get("title", "参考になったらいいね・保存！")
    tf = get_font(72)
    t_lines = jp_wrap(title, 12)
    ty = REEL_H // 4
    for line in t_lines[:5]:
        draw_centered_text(draw, line, tf, ty, REEL_W, scheme["text"])
        ty += 95
    ty += 40

    # CTA buttons
    cta_items = [
        "いいね・保存で後から見返せる",
        "コメントで質問してね",
        "フォローで毎日更新をお届け",
    ]
    cbf = get_font(46)
    for item in cta_items:
        bw = 880
        bx = (REEL_W - bw) // 2
        draw.rounded_rectangle([(bx, ty - 12), (bx + bw, ty + 65)], radius=42, fill=scheme["badge_bg"])
        cbbox = draw.textbbox((0, 0), item, font=cbf)
        cw = cbbox[2] - cbbox[0]
        draw.text(((REEL_W - cw) // 2, ty + 5), item, font=cbf, fill=scheme["badge_text"])
        ty += 108

    # Account big
    abf = get_font(56)
    abbbox = draw.textbbox((0, 0), account, font=abf)
    aw = abbbox[2] - abbbox[0]
    draw.text(((REEL_W - aw) // 2, REEL_H - 265), account, font=abf, fill=scheme["accent"])

    # "無料相談受付中"
    cf = get_font(42)
    ctext = "無料相談・お見積もり受付中"
    cbbox2 = draw.textbbox((0, 0), ctext, font=cf)
    cw2 = cbbox2[2] - cbbox2[0]
    draw.text(((REEL_W - cw2) // 2, REEL_H - 195), ctext, font=cf, fill=scheme["sub"])

    return np.array(img)


def generate_reel_script(theme: str, client: anthropic.Anthropic) -> dict:
    prompt = f"""あなたはInstagramマーケターです。
美容サロン向けホームページ制作を行うフリーランスのアカウント用に、
テーマ「{theme}」でInstagramリール動画の台本を日本語で作成してください。

以下のJSON形式で返してください（コードブロックなし、純粋なJSONのみ）:

{{
  "hook": {{
    "title": "（視聴者を引きつける短いキャッチコピー。12文字以内で改行なし）",
    "subtitle": "（補足説明。25文字以内）"
  }},
  "slides": [
    {{
      "title": "（スライドタイトル。13文字以内）",
      "body": "（本文。1行15文字以内で3〜5行。改行は\\nで区切る）"
    }},
    {{
      "title": "（スライドタイトル）",
      "body": "（本文）"
    }},
    {{
      "title": "（スライドタイトル）",
      "body": "（本文）"
    }}
  ],
  "cta": {{
    "title": "（締めのメッセージ。12文字以内で改行あり可）"
  }}
}}

条件:
- ターゲット: 美容サロンオーナー（個人・小規模）
- 訴求: ホームページを持つことで集客・売上が変わる
- トーン: 親しみやすく、専門的。過度な売り込みNG
- slidesは必ず3つ
"""
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    # Extract JSON if wrapped in markdown
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def _setup(theme_index: int, account: str):
    today = datetime.now(JST)
    if theme_index is None:
        theme_index = today.timetuple().tm_yday % len(THEMES)
    theme = THEMES[theme_index]
    scheme = COLOR_SCHEMES[theme_index % len(COLOR_SCHEMES)]
    date_str = today.strftime("%Y-%m-%d")
    theme_slug = theme.replace("・", "_").replace("/", "_").replace(" ", "")[:20]
    out_dir = f"reels/{date_str}_{theme_slug}"
    os.makedirs(out_dir, exist_ok=True)

    print(f"テーマ: {theme}")
    print("台本生成中...")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    script = generate_reel_script(theme, client)

    print("スライド画像生成中...")
    hook_arr = make_hook_slide(script["hook"], scheme, theme, account)
    content_arrs = [
        make_content_slide(s, scheme, i, len(script["slides"]), account)
        for i, s in enumerate(script["slides"], start=1)
    ]
    cta_arr = make_cta_slide(script["cta"], scheme, account)
    all_frames = [hook_arr] + content_arrs + [cta_arr]

    script_path = f"{out_dir}/script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump({"theme": theme, "date": date_str, "script": script}, f, ensure_ascii=False, indent=2)

    print(f"\n--- 生成された台本 ---")
    print(f"フック: {script['hook']['title']}")
    for i, s in enumerate(script["slides"], 1):
        print(f"スライド{i}: {s['title']}")
    print(f"CTA: {script['cta']['title']}")

    return out_dir, all_frames, theme_slug


def create_slides(theme_index: int = None, account: str = "@makita.web") -> str:
    """スライド画像（PNG）のみ生成。GitHub Actions用。"""
    out_dir, all_frames, _ = _setup(theme_index, account)

    slide_names = ["01_hook"] + [f"{i+2:02d}_slide{i+1}" for i in range(len(all_frames) - 2)] + [f"{len(all_frames):02d}_cta"]
    saved = []
    for name, arr in zip(slide_names, all_frames):
        path = f"{out_dir}/{name}.png"
        Image.fromarray(arr).save(path)
        saved.append(path)

    print(f"\n完了! {len(saved)}枚のスライド画像を保存しました")
    print(f"  フォルダ: {out_dir}/")
    return out_dir


def create_reel(theme_index: int = None, account: str = "@makita.web") -> str:
    """スライド画像 + MP4動画を生成。ローカル実行用。"""
    out_dir, all_frames, _ = _setup(theme_index, account)

    slide_names = ["01_hook"] + [f"{i+2:02d}_slide{i+1}" for i in range(len(all_frames) - 2)] + [f"{len(all_frames):02d}_cta"]
    for name, arr in zip(slide_names, all_frames):
        Image.fromarray(arr).save(f"{out_dir}/{name}.png")

    clips = []
    for i, frame in enumerate(all_frames):
        clip = ImageClip(frame).with_duration(SLIDE_DURATION)
        if i > 0:
            clip = clip.with_effects([vfx.FadeIn(0.4)])
        clips.append(clip)

    mp4_path = f"{out_dir}/reel.mp4"
    print(f"動画書き出し中: {mp4_path}")
    concatenate_videoclips(clips, method="compose").write_videofile(
        mp4_path, fps=FPS, codec="libx264", audio=False, logger=None
    )

    print(f"\n完了!")
    print(f"  フォルダ: {out_dir}/")
    print(f"  動画: {mp4_path}")
    return mp4_path


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    video_mode = "--video" in args
    theme_idx = next((int(a) for a in args if a.isdigit()), None)

    if video_mode:
        create_reel(theme_index=theme_idx)
    else:
        create_slides(theme_index=theme_idx)
