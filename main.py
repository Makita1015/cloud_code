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
buttons = driver.find_elements(By.TAG_NAME, "button")
buttons[3].click()
time.sleep(5)

driver.get("https://note.com/notes/new")
time.sleep(5)

# 全inputとtextareaを確認
inputs = driver.find_elements(By.TAG_NAME, "input")
print(f"input数: {len(inputs)}")
for i, inp in enumerate(inputs):
    print(f"input[{i}]: placeholder={inp.get_attribute('placeholder')}")

textareas = driver.find_elements(By.TAG_NAME, "textarea")
print(f"textarea数: {len(textareas)}")

editables = driver.find_elements(By.XPATH, "//*[@contenteditable='true']")
print(f"contenteditable数: {len(editables)}")
for i, e in enumerate(editables):
    print(f"editable[{i}]: tag={e.tag_name} class={e.get_attribute('class')[:50]}")

driver.quit()
