import os
import anthropic
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
wait = WebDriverWait(driver, 15)

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

title_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'タイトル')]")))
title_input.send_keys(title)

body_input = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
body_input.send_keys(body)
time.sleep(1)

driver.find_element(By.XPATH, "//button[contains(text(),'公開')]").click()
time.sleep(2)
driver.find_element(By.XPATH, "//button[contains(text(),'公開する')]").click()
time.sleep(2)

print("投稿完了")
driver.quit()
