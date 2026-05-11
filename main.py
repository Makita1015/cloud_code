import os
import anthropic
import requests

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "日本語で1000字程度のブログ記事を書いてください。テーマは自由です。タイトルも含めてください。"}
    ]
)

content = message.content[0].text
lines = content.strip().split('\n')
title = lines[0].replace('#', '').strip()
body = '\n'.join(lines[1:]).strip()

session = requests.Session()
login_url = "https://note.com/api/v1/sessions/sign_in"
payload = {"login": os.environ["NOTE_EMAIL"], "password": os.environ["NOTE_PASSWORD"]}
session.post(login_url, json=payload)

post_url = "https://note.com/api/v1/text_notes"
data = {"title": title, "body": body, "status": "published"}
session.post(post_url, json=data)
print("投稿完了")
