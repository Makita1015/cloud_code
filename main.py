import os
import anthropic
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

wait = WebDriverWait(driver, 15)

driver.get("https://note.com/login")
time.sleep(5)

inputs = driver.find_elements(By.TAG_NAME, "input")
inputs[0].send_keys(os.environ["NOTE_EMAIL"])
inputs[1].send_keys(os.environ["NOTE_PASSWORD"])
inputs[1].send_keys(Keys.RETURN)
time.sleep(8)

print(f"ログイン後URL: {driver.current_url}")

if "login" not in driver.current_url:
    driver.get("https://note.com/notes/new")
    time.sleep(8)
    print(f"記事作成ページURL: {driver.current_url}")
    editables = driver.find_elements(By.XPATH, "//*[@contenteditable='true']")
    print(f"editable数: {len(editables)}")
else:
    print("ログイン失敗")

driver.quit()
