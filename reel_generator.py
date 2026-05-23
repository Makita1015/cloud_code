#!/usr/bin/env python3
"""
Instagram Reel Video Generator
犬のトリミングサロン集客テーマ
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
    "新規集客を増やすホームページ活用術",
    "リピーター獲得のWeb戦略",
    "予約を増やす導線づくり",
    "Googleで上位表示される方法",
    "SNSとホームページの使い分け",
    "口コミ・レビューを増やす仕組み",
    "競合サロンと差がつくポイント",
]

# 全テーマ共通：茶色ベース・白文字
COLOR_SCHEMES = [
    {  # ダークチョコレート
        "bg": [(42, 22, 10), (78, 42, 18)],
        "accent": (220, 168, 75),
        "text": (255, 255, 255),
        "sub": (225, 200, 170),
        "badge_bg": (170, 108, 45),
        "badge_text": (255, 255, 255),
    },
    {  # エスプレッソ
        "bg": [(32, 18, 8), (68, 38, 16)],
        "accent": (205, 155, 65),
        "text": (255, 255, 255),
        "sub": (215, 190, 158),
        "badge_bg": (155, 95, 38),
        "badge_text": (255, 255, 255),
    },
    {  # モカブラウン
        "bg": [(55, 30, 14), (95, 55, 25)],
        "accent": (235, 178, 85),
        "text": (255, 255, 255),
        "sub": (230, 205, 178),
        "badge_bg": (185, 118, 50),
        "badge_text": (255, 255, 255),
    },
    {  # マホガニー
        "bg": [(50, 20, 14), (88, 38, 24)],
        "accent": (218, 148, 72),
        "text": (255, 255, 255),
        "sub": (222, 195, 168),
        "badge_bg": (168, 95, 42),
        "badge_text": (255, 255, 255),
    },
    {  # ウォールナット
        "bg": [(38, 25, 12), (72, 45, 20)],
        "accent": (228, 172, 80),
        "text": (255, 255, 255),
        "sub": (218, 195, 162),
        "badge_bg": (175, 110, 45),
        "badge_text": (255, 255, 255),
    },
    {  # コーヒーブラウン
        "bg": [(45, 25, 12), (82, 48, 22)],
        "accent": (212, 160, 70),
        "text": (255, 255, 255),
        "sub": (220, 195, 165),
        "badge_bg": (162, 100, 40),
        "badge_text": (255, 255, 255),
    },
    {  # シナモン
        "bg": [(62, 35, 16), (105, 62, 28)],
        "accent": (242, 188, 92),
        "text": (255, 255, 255),
        "sub": (235, 210, 182),
        "badge_bg": (192, 128, 55),
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


def draw_centered(draw, text, font, y, color, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (REEL_W - tw) // 2
    if shadow:
        draw.text((x + 4, y + 4), text, font=font, fill=(0, 0, 0, 80))
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3] - bbox[1]


def progress_dots(draw, total, current, scheme):
    dr = 13
    dsp = 48
    dtw = (total - 1) * dsp + dr * 2
    dx = (REEL_W - dtw) // 2
    dy = REEL_H - 90
    for i in range(total):
        ex = dx + i * dsp + dr
        col = scheme["accent"] if i == current else scheme["sub"]
        draw.ellipse([(ex - dr, dy - dr), (ex + dr, dy + dr)], fill=col)


def make_hook_slide(data: dict, scheme: dict, theme_name: str) -> np.ndarray:
    img = gradient_image(REEL_W, REEL_H, scheme["bg"][0], scheme["bg"][1])
    draw = ImageDraw.Draw(img)

    # アクセントバー（上下）
    draw.rectangle([(0, 0), (REEL_W, 12)], fill=scheme["accent"])
    draw.rectangle([(0, REEL_H - 12), (REEL_W, REEL_H)], fill=scheme["accent"])

    # テーマバッジ
    bf = get_font(44)
    bbox = draw.textbbox((0, 0), theme_name, font=bf)
    bw = bbox[2] - bbox[0] + 90
    bx = (REEL_W - bw) // 2
    by = 190
    draw.rounded_rectangle([(bx, by), (bx + bw, by + 85)], radius=42, fill=scheme["badge_bg"])
    tbbox = draw.textbbox((0, 0), theme_name, font=bf)
    draw.text(
        (bx + (bw - (tbbox[2] - tbbox[0])) // 2, by + 20),
        theme_name, font=bf, fill=scheme["badge_text"]
    )

    # メインタイトル（大きく中央）
    title = data.get("title", "")
    tf = get_font(100)
    t_lines = jp_wrap(title, 10)
    line_h = 125
    total_h = len(t_lines) * line_h
    ty = (REEL_H - total_h) // 2 - 50
    for line in t_lines[:5]:
        draw_centered(draw, line, tf, ty, scheme["text"])
        ty += line_h

    # サブタイトル
    subtitle = data.get("subtitle", "")
    if subtitle:
        sf = get_font(58)
        sy = ty + 50
        for line in jp_wrap(subtitle, 15)[:3]:
            draw_centered(draw, line, sf, sy, scheme["sub"], shadow=False)
            sy += 78

    # スワイプ誘導
    hf = get_font(46)
    draw_centered(draw, "▼  続きを見る", hf, REEL_H - 210, scheme["accent"], shadow=False)

    # プログレスドット（全4枚）
    progress_dots(draw, 4, 0, scheme)

    return np.array(img)


def make_body_slide(data: dict, scheme: dict, slide_type: str, dot_index: int) -> np.ndarray:
    img = gradient_image(REEL_W, REEL_H, scheme["bg"][0], scheme["bg"][1])
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (REEL_W, 12)], fill=scheme["accent"])
    draw.rectangle([(0, REEL_H - 12), (REEL_W, REEL_H)], fill=scheme["accent"])

    if slide_type == "problem":
        label = "こんな悩みありませんか？"
        label_bg = (160, 65, 50)   # 赤みがかったブラウン
    else:
        label = "ホームページで解決！"
        label_bg = (65, 130, 90)   # 緑がかったアクセント

    # ラベルバー（上部）
    lf = get_font(50)
    lbbox = draw.textbbox((0, 0), label, font=lf)
    lw = lbbox[2] - lbbox[0] + 80
    lx = (REEL_W - lw) // 2
    draw.rounded_rectangle([(lx, 160), (lx + lw, 255)], radius=44, fill=label_bg)
    draw.text(
        (lx + (lw - (lbbox[2] - lbbox[0])) // 2, 175),
        label, font=lf, fill=(255, 255, 255)
    )

    # タイトル
    title = data.get("title", "")
    tf = get_font(86)
    ty = 300
    for line in jp_wrap(title, 12)[:3]:
        draw_centered(draw, line, tf, ty, scheme["text"])
        ty += 108
    ty += 20

    # 区切り線
    draw.rectangle([(60, ty), (REEL_W - 60, ty + 6)], fill=scheme["accent"])
    ty += 55

    # 本文（大きめフォント）
    body = data.get("body", "")
    bf = get_font(64)
    for line in jp_wrap(body, 14)[:7]:
        draw.text((60, ty), line, font=bf, fill=scheme["text"])
        ty += 88

    # プログレスドット
    progress_dots(draw, 4, dot_index, scheme)

    return np.array(img)


def make_cta_slide(data: dict, scheme: dict) -> np.ndarray:
    img = gradient_image(REEL_W, REEL_H, scheme["bg"][0], scheme["bg"][1])
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (REEL_W, 12)], fill=scheme["accent"])
    draw.rectangle([(0, REEL_H - 12), (REEL_W, REEL_H)], fill=scheme["accent"])

    # メインメッセージ
    title = data.get("title", "まずは無料相談\nプロフのリンクから")
    tf = get_font(92)
    t_lines = jp_wrap(title, 11)
    ty = REEL_H // 5
    for line in t_lines[:5]:
        draw_centered(draw, line, tf, ty, scheme["text"])
        ty += 118
    ty += 50

    # 区切り線
    draw.rectangle([(120, ty), (REEL_W - 120, ty + 5)], fill=scheme["accent"])
    ty += 60

    # CTAボタン
    cta_items = [
        "無料相談はプロフのリンクから",
        "いいね・保存で後から見返せる",
        "フォローで毎日更新をお届け",
    ]
    cbf = get_font(52)
    for item in cta_items:
        bw = 940
        bx = (REEL_W - bw) // 2
        draw.rounded_rectangle([(bx, ty - 14), (bx + bw, ty + 72)], radius=46, fill=scheme["badge_bg"])
        cbbox = draw.textbbox((0, 0), item, font=cbf)
        cw = cbbox[2] - cbbox[0]
        draw.text(((REEL_W - cw) // 2, ty + 6), item, font=cbf, fill=scheme["badge_text"])
        ty += 118

    # プログレスドット
    progress_dots(draw, 4, 3, scheme)

    return np.array(img)


def generate_reel_script(theme: str, client: anthropic.Anthropic) -> dict:
    prompt = f"""あなたはInstagramマーケターです。
犬のトリミングサロン向けホームページ制作を行うフリーランスのアカウント用に、
テーマ「{theme}」でInstagramリール動画の台本を日本語で作成してください。

以下のJSON形式で返してください（コードブロックなし、純粋なJSONのみ）:

{{
  "hook": {{
    "title": "（視聴者を引きつけるキャッチコピー。10文字以内・改行は\\nで）",
    "subtitle": "（補足。20文字以内）"
  }},
  "problem": {{
    "title": "（問題提起のタイトル。12文字以内）",
    "body": "（悩み・課題を箇条書き。・で始め1行13文字以内で4〜5行。改行は\\nで）"
  }},
  "solution": {{
    "title": "（解決策のタイトル。12文字以内）",
    "body": "（解決策を箇条書き。・で始め1行13文字以内で4〜5行。改行は\\nで）"
  }},
  "cta": {{
    "title": "（締めメッセージ。10文字以内・改行あり可）"
  }}
}}

条件:
- ターゲット: 犬のトリミングサロンオーナー（個人・小規模）
- 訴求: ホームページを持つことで集客・売上が改善する
- トーン: 親しみやすく、具体的。過度な売り込みNG
- 問題と解決策は対になるよう書く
"""
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def _setup(theme_index: int):
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
    frames = [
        make_hook_slide(script["hook"], scheme, theme),
        make_body_slide(script["problem"], scheme, "problem", 1),
        make_body_slide(script["solution"], scheme, "solution", 2),
        make_cta_slide(script["cta"], scheme),
    ]

    script_path = f"{out_dir}/script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump({"theme": theme, "date": date_str, "script": script}, f, ensure_ascii=False, indent=2)

    print(f"\n--- 生成された台本 ---")
    print(f"フック    : {script['hook']['title']}")
    print(f"問題提起  : {script['problem']['title']}")
    print(f"解決策    : {script['solution']['title']}")
    print(f"CTA       : {script['cta']['title']}")

    return out_dir, frames


def create_slides(theme_index: int = None) -> str:
    """スライド画像（PNG）のみ生成。GitHub Actions用。"""
    out_dir, frames = _setup(theme_index)
    names = ["01_hook", "02_problem", "03_solution", "04_cta"]
    for name, arr in zip(names, frames):
        Image.fromarray(arr).save(f"{out_dir}/{name}.png")
    print(f"\n完了! 4枚のスライド画像を保存しました")
    print(f"  フォルダ: {out_dir}/")
    return out_dir


def create_reel(theme_index: int = None) -> str:
    """スライド画像 + MP4動画を生成。ローカル実行用。"""
    out_dir, frames = _setup(theme_index)
    names = ["01_hook", "02_problem", "03_solution", "04_cta"]
    for name, arr in zip(names, frames):
        Image.fromarray(arr).save(f"{out_dir}/{name}.png")

    clips = [ImageClip(frames[0]).with_duration(SLIDE_DURATION)]
    for frame in frames[1:]:
        clips.append(
            ImageClip(frame).with_duration(SLIDE_DURATION).with_effects([vfx.FadeIn(0.4)])
        )

    mp4_path = f"{out_dir}/reel.mp4"
    print(f"動画書き出し中: {mp4_path}")
    concatenate_videoclips(clips, method="compose").write_videofile(
        mp4_path, fps=FPS, codec="libx264", audio=False, logger=None
    )
    print(f"\n完了!\n  フォルダ: {out_dir}/\n  動画: {mp4_path}")
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
