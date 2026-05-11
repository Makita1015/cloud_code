import os
import anthropic
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
today = datetime.now(JST).strftime("%Y-%m-%d")
filename = f"articles/{today}-ai-news.md"

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": (
            "今日のAI・機械学習分野のニュースや注目トピックを日本語で1000字程度にまとめた記事を書いてください。\n"
            "構成：\n"
            "1. 本日のハイライト（2〜3トピック）\n"
            "2. 各トピックの概要と背景\n"
            "3. まとめと今後の展望\n"
            "タイトルは「今日のAIニュースまとめ（YYYY年MM月DD日）」の形式にしてください。"
        )
    }]
)

content = message.content[0].text.strip()
lines = content.split("\n")
title = lines[0].replace("#", "").strip()
body = "\n".join(lines[1:]).strip()

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

print(f"作成完了: {filename}")
