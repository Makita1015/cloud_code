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
    messages=[{"role": "user", "content": "日本語で1000字程度のブログ記事を書いてください。テーマは自由です。タイトルも含めてください。"}]
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
options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

driver.get("https://note.com")
time.sleep(2)
print(f"現在のURL: {driver.current_url}")
print(f"NOTE_SESSION: {os.environ.get('NOTE_SESSION', 'なし')[:10]}...")
print(f"NOTE_VID: {os.environ.get('NOTE_VID', 'なし')[:10]}...")
cookie_str = os.environ["NOTE_SESSION"]
driver.execute_script(f"document.cookie='_note_session_v5={cookie_str}; domain=.note.com; path=/'")
vid_str = os.environ["NOTE_VID"]
driver.execute_script(f"document.cookie='_vid_v1={vid_str}; domain=.note.com; path=/'")
driver.get("https://note.com/notes/new")
time.sleep(6)

editables = driver.find_elements(By.XPATH, "//*[@contenteditable='true']")
print(f"editable数: {len(editables)}")

if len(editables) >= 1:
    editables[0].send_keys(title)
    time.sleep(1)

editables = driver.find_elements(By.XPATH, "//*[@contenteditable='true']")
if len(editables) >= 2:
    editables[1].send_keys(body)
elif len(editables) == 1:
    from selenium.webdriver.common.keys import Keys
    editables[0].send_keys(Keys.RETURN)
    editables[0].send_keys(body)
time.sleep(2)

buttons = driver.find_elements(By.TAG_NAME, "button")
for btn in buttons:
    if "公開" in btn.text and btn.is_displayed():
        btn.click()
        time.sleep(3)
        break

buttons = driver.find_elements(By.TAG_NAME, "button")
for btn in buttons:
    if "公開する" in btn.text and btn.is_displayed():
        btn.click()
        time.sleep(3)
        break

print("投稿完了")
driver.quit()
