import os
import anthropic
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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

driver = webdriver.Chrome(options=options)

driver.get("https://note.com/login")
time.sleep(2)

driver.find_element(By.NAME, "email").send_keys(os.environ["NOTE_EMAIL"])
driver.find_element(By.NAME, "password").send_keys(os.environ["NOTE_PASSWORD"])
driver.find_element(By.XPATH, "//button[@type='submit']").click()
time.sleep(3)

driver.get("https://note.com/notes/new")
time.sleep(2)

driver.find_element(By.XPATH, "//input[@placeholder='記事タイトル']").send_keys(title)
driver.find_element(By.XPATH, "//div[@contenteditable='true']").send_keys(body)
time.sleep(1)

driver.find_element(By.XPATH, "//button[contains(text(),'公開')]").click()
time.sleep(2)
driver.find_element(By.XPATH, "//button[contains(text(),'公開する')]").click()
time.sleep(2)

print("投稿完了")
driver.quit()
