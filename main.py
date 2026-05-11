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
lines = content.strip().split(chr(10))
title = lines[0].replace("#", "").strip()
body = chr(10).join(lines[1:]).strip()

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

driver.get("https://note.com")
time.sleep(2)
driver.add_cookie({"name": "_note_session_v5", "value": os.environ["NOTE_SESSION"], "domain": ".note.com"})
driver.add_cookie({"name": "_vid_v1", "value": os.environ["NOTE_VID"], "domain": ".note.com"})

driver.get("https://note.com/notes/new")
time.sleep(5)
print(f"URL: {driver.current_url}")
editables = driver.find_elements(By.XPATH, "//*[@contenteditable=" + chr(39) + "true" + chr(39) + "]")
print(f"editable数: {len(editables)}")
driver.quit()
