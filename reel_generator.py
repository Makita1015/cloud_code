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

# ---- デザイン定数 ----
BG_COLOR   = (195, 168, 138)   # ミディアムウォームブラウン（背景）
CARD_COLOR = (255, 255, 255)   # 白（カード）
CARD_X     = 55                # カード左右マージン
CARD_Y     = 140               # カード上下マージン
CARD_W     = REEL_W - CARD_X * 2   # 970
CARD_H     = REEL_H - CARD_Y * 2   # 1640
CARD_R     = 38                # 角丸半径
PAD_X      = 70                # カード内テキスト左右余白
PAD_Y      = 80                # カード内テキスト上下余白

TEXT_DARK   = (50, 28, 10)     # 濃い茶（本文・タイトル）
TEXT_MED    = (110, 70, 35)    # 中茶（補助テキスト）
TEXT_LIGHT  = (168, 130, 88)   # 薄茶（ヒント・ドット非活性）
TEXT_RED    = (192, 50, 40)    # 赤（問題提起ラベル）
TEXT_GREEN  = (40, 135, 72)    # 緑（解決策ラベル）
DOT_ACTIVE  = (110, 70, 35)    # 進捗ドット（現在）
DOT_INACTIVE = (195, 172, 148) # 進捗ドット（他）

THEMES = [
    "新規集客を増やすホームページ活用術",
    "リピーター獲得のWeb戦略",
    "予約を増やす導線づくり",
    "Googleで上位表示される方法",
    "SNSとホームページの使い分け",
    "口コミ・レビューを増やす仕組み",
    "競合サロンと差がつくポイント",
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


def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def text_height(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]


def draw_centered(draw, text, font, y, color):
    bbox = draw.textbbox((0, 0), text, font=font)
    x = (REEL_W - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3] - bbox[1]


def draw_base(draw):
    """背景とカードを描画する"""
    draw.rectangle([(0, 0), (REEL_W, REEL_H)], fill=BG_COLOR)
    draw.rounded_rectangle(
        [(CARD_X, CARD_Y), (CARD_X + CARD_W, CARD_Y + CARD_H)],
        radius=CARD_R, fill=CARD_COLOR
    )


def draw_progress(draw, total, current):
    dr = 12
    spacing = 46
    total_w = (total - 1) * spacing + dr * 2
    sx = (REEL_W - total_w) // 2
    dy = CARD_Y + CARD_H - 62
    for i in range(total):
        ex = sx + i * spacing + dr
        col = DOT_ACTIVE if i == current else DOT_INACTIVE
        draw.ellipse([(ex - dr, dy - dr), (ex + dr, dy + dr)], fill=col)


# カード内のコンテンツ領域
CONTENT_X     = CARD_X + PAD_X       # 125
CONTENT_W     = CARD_W - PAD_X * 2   # 830
CONTENT_TOP   = CARD_Y + PAD_Y       # 220
CONTENT_BOT   = CARD_Y + CARD_H - PAD_Y - 80  # ドット領域分を残す
CONTENT_H     = CONTENT_BOT - CONTENT_TOP      # 利用可能な高さ


def vcenter_y(block_h: int) -> int:
    """コンテンツブロックの高さから垂直中央のY座標を返す"""
    return CONTENT_TOP + max(0, (CONTENT_H - block_h) // 2)


def make_hook_slide(data: dict, theme_name: str) -> np.ndarray:
    img = Image.new("RGB", (REEL_W, REEL_H))
    draw = ImageDraw.Draw(img)
    draw_base(draw)

    # ---- コンテンツブロックの高さを計算 ----
    badge_f  = get_font(46)
    title_f  = get_font(96)
    sub_f    = get_font(54)
    hint_f   = get_font(44)

    title_lines = jp_wrap(data.get("title", ""), 10)
    sub_lines   = jp_wrap(data.get("subtitle", ""), 16)

    gap = 38
    badge_h  = text_height(draw, theme_name, badge_f) + 12
    title_h  = len(title_lines) * 118
    sub_h    = len(sub_lines) * 72 if sub_lines else 0
    block_h  = badge_h + gap + title_h + (gap + sub_h if sub_lines else 0)

    ty = vcenter_y(block_h)

    # テーマバッジ（茶色テキスト、下線のみ）
    draw_centered(draw, theme_name, badge_f, ty, TEXT_MED)
    tw = text_width(draw, theme_name, badge_f)
    lx = (REEL_W - tw) // 2
    line_y = ty + badge_h + 4
    draw.rectangle([(lx, line_y), (lx + tw, line_y + 3)], fill=TEXT_LIGHT)
    ty += badge_h + gap + 10

    # メインタイトル（大・濃い茶）
    for line in title_lines:
        draw_centered(draw, line, title_f, ty, TEXT_DARK)
        ty += 118

    # サブタイトル
    if sub_lines:
        ty += gap
        for line in sub_lines:
            draw_centered(draw, line, sub_f, ty, TEXT_MED)
            ty += 72

    draw_progress(draw, 4, 0)
    return np.array(img)


def make_body_slide(data: dict, slide_type: str, dot_index: int) -> np.ndarray:
    img = Image.new("RGB", (REEL_W, REEL_H))
    draw = ImageDraw.Draw(img)
    draw_base(draw)

    label_f  = get_font(46)
    title_f  = get_font(84)

    if slide_type == "problem":
        label      = "こんな悩みありませんか？"
        bar_color  = TEXT_RED
    else:
        label      = "ホームページで解決！"
        bar_color  = TEXT_GREEN

    title_lines = jp_wrap(data.get("title", ""), 12)

    # 箇条書きは \n で分割するだけ（改行しない）
    body_lines = [l.strip() for l in data.get("body", "").split("\n") if l.strip()]

    # 最長行に合わせてフォントサイズを自動調整（最大62px）
    max_len = max(len(l) for l in body_lines) if body_lines else 1
    body_size = min(62, int(CONTENT_W / max_len * 1.05))
    body_f = get_font(body_size)
    body_line_h = int(body_size * 1.45)

    gap = 36
    label_h  = text_height(draw, label, label_f) + 14
    title_h  = len(title_lines) * 102
    div_h    = 28
    body_h   = len(body_lines) * body_line_h
    block_h  = label_h + gap + title_h + div_h + gap + body_h

    ty = vcenter_y(block_h)

    # ラベル：左に細い縦バー＋テキスト
    lbbox = draw.textbbox((0, 0), label, font=label_f)
    lw = lbbox[2] - lbbox[0]
    lh = lbbox[3] - lbbox[1]
    bar_w = 7
    lx = (REEL_W - lw - bar_w - 18) // 2
    draw.rectangle([(lx, ty), (lx + bar_w, ty + lh + 10)], fill=bar_color)
    draw.text((lx + bar_w + 18, ty + 4), label, font=label_f, fill=bar_color)
    ty += label_h + gap

    # タイトル（濃い茶）
    for line in title_lines:
        draw_centered(draw, line, title_f, ty, TEXT_DARK)
        ty += 102

    # 区切り線
    ty += 10
    line_w = 480
    draw.rectangle(
        [((REEL_W - line_w) // 2, ty), ((REEL_W + line_w) // 2, ty + 4)],
        fill=TEXT_LIGHT
    )
    ty += div_h + gap - 10

    # 本文（左寄せ、改行なし）
    bx = CONTENT_X + 20
    for line in body_lines:
        draw.text((bx, ty), line, font=body_f, fill=TEXT_MED)
        ty += body_line_h

    draw_progress(draw, 5, dot_index)
    return np.array(img)


def make_cta_slide(data: dict) -> np.ndarray:
    img = Image.new("RGB", (REEL_W, REEL_H))
    draw = ImageDraw.Draw(img)
    draw_base(draw)

    title_f = get_font(90)
    item_f  = get_font(52)

    title_lines = jp_wrap(data.get("title", "まず無料相談\nプロフのリンクから"), 11)
    cta_items = [
        "DMからお気軽にどうぞ",
        "いいね・保存で後から見返せる",
        "フォローで毎日更新をお届け",
    ]

    gap = 40
    title_h = len(title_lines) * 112
    div_h   = 28
    items_h = len(cta_items) * 80
    block_h = title_h + gap + div_h + gap + items_h

    ty = vcenter_y(block_h)

    # メインメッセージ
    for line in title_lines:
        draw_centered(draw, line, title_f, ty, TEXT_DARK)
        ty += 112

    # 区切り線
    ty += gap
    line_w = 560
    draw.rectangle(
        [((REEL_W - line_w) // 2, ty), ((REEL_W + line_w) // 2, ty + 4)],
        fill=TEXT_LIGHT
    )
    ty += div_h + gap

    # CTAアイテム（茶色テキスト、シンプル）
    for item in cta_items:
        draw_centered(draw, item, item_f, ty, TEXT_MED)
        ty += 80

    draw_progress(draw, 5, 4)
    return np.array(img)


def make_profile_slide() -> np.ndarray:
    img = Image.new("RGB", (REEL_W, REEL_H))
    draw = ImageDraw.Draw(img)
    draw_base(draw)

    main_f = get_font(80)
    sub_f  = get_font(52)

    lines   = ["詳細は", "プロフィールリンク", "からどうぞ"]
    line_h  = 105
    gap     = 50
    arrow_h = 70
    sub_h   = 65
    block_h = len(lines) * line_h + gap + arrow_h + gap + sub_h

    ty = vcenter_y(block_h)

    for line in lines:
        draw_centered(draw, line, main_f, ty, TEXT_DARK)
        ty += line_h

    ty += gap

    # 矢印（シンプルな下向き）
    arrow_f = get_font(68)
    draw_centered(draw, "↓", arrow_f, ty, TEXT_MED)
    ty += arrow_h + gap

    draw_centered(draw, "プロフのリンクをタップ", sub_f, ty, TEXT_LIGHT)

    draw_progress(draw, 5, 3)
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
    "body": "（悩み・課題を箇条書き。・で始め1行12文字以内で4〜5行。改行は\\nで）"
  }},
  "solution": {{
    "title": "（解決策のタイトル。12文字以内）",
    "body": "（解決策を箇条書き。・で始め1行12文字以内で4〜5行。改行は\\nで）"
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
        make_hook_slide(script["hook"], theme),
        make_body_slide(script["problem"], "problem", 1),
        make_body_slide(script["solution"], "solution", 2),
        make_profile_slide(),
        make_cta_slide(script["cta"]),
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
    names = ["01_hook", "02_problem", "03_solution", "04_profile", "05_cta"]
    for name, arr in zip(names, frames):
        Image.fromarray(arr).save(f"{out_dir}/{name}.png")
    print(f"\n完了! 4枚のスライド画像を保存しました")
    print(f"  フォルダ: {out_dir}/")
    return out_dir


def create_slides_from_dict(script: dict, theme: str, out_dir: str = None) -> str:
    """
    台本dictを直接渡してスライド画像を生成する。
    Claude Codeのチャットから内容を指定するときに使う。

    script の形式:
    {
        "hook":     {"title": "...", "subtitle": "..."},
        "problem":  {"title": "...", "body": "..."},
        "solution": {"title": "...", "body": "..."},
        "cta":      {"title": "..."}
    }
    """
    today = datetime.now(JST)
    date_str = today.strftime("%Y-%m-%d")
    if out_dir is None:
        slug = theme.replace("・", "_").replace("/", "_").replace(" ", "")[:20]
        out_dir = f"reels/{date_str}_{slug}"
    os.makedirs(out_dir, exist_ok=True)

    frames = [
        make_hook_slide(script["hook"], theme),
        make_body_slide(script["problem"], "problem", 1),
        make_body_slide(script["solution"], "solution", 2),
        make_profile_slide(),
        make_cta_slide(script["cta"]),
    ]
    names = ["01_hook", "02_problem", "03_solution", "04_profile", "05_cta"]
    paths = []
    for name, arr in zip(names, frames):
        path = f"{out_dir}/{name}.png"
        Image.fromarray(arr).save(path)
        paths.append(path)

    with open(f"{out_dir}/script.json", "w", encoding="utf-8") as f:
        json.dump({"theme": theme, "date": date_str, "script": script}, f, ensure_ascii=False, indent=2)

    print(f"完了! {out_dir}/")
    return out_dir


def create_reel(theme_index: int = None) -> str:
    """スライド画像 + MP4動画を生成。ローカル実行用。"""
    out_dir, frames = _setup(theme_index)
    names = ["01_hook", "02_problem", "03_solution", "04_profile", "05_cta"]
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
