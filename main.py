import os
import anthropic
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://note.com/login")
time.sleep(5)

inputs = driver.find_elements(By.TAG_NAME, "input")
inputs[0].send_keys(os.environ["NOTE_EMAIL"])
inputs[1].send_keys(os.environ["NOTE_PASSWORD"])

# 全ボタンのテキストを入力後に再確認
buttons = driver.find_elements(By.TAG_NAME, "button")
print(f"ボタン数: {len(buttons)}")
for i, btn in enumerate(buttons):
    print(f"button[{i}]: text='{btn.text}' visible={btn.is_displayed()}")

driver.quit()
