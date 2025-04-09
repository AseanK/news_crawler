# from openai import OpenAI
# import os
#
# API_KEY = os.getenv("DEEPSEEK_API")
# client = OpenAI(
#     api_key=API_KEY,
#     base_url="https://api.deepseek.com",
# )
#
# response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {"role": "system", "content": "provide concise and significant fundamental analysis of the company" },
#         {"role": "user", "content": "Nvidia"},
#     ]
# )
#
#
# print(response.choices[0].message.content)


from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from firebase import Firebase


fb = Firebase()
opts = Options()
opts.page_load_strategy = 'eager'
opts.add_argument('--blink-settings=imagesEnabled=false')

driver = webdriver.Chrome(opts)
driver.get("https://finance.yahoo.com/topic/latest-news/")

data = driver.find_elements(By.XPATH, "//h3[contains(@class, 'clamp')]") ## HEADING ELEMENT

driver.switch_to.window(driver.window_handles[0])

data[0].find_element(By.XPATH, "..").send_keys(Keys.COMMAND, Keys.RETURN)
driver.switch_to.window(driver.window_handles[-1]) ## Focus to article tabs
timestamp = driver.find_element(By.CLASS_NAME, "article-wrap").find_element(By.XPATH, "//time").get_attribute('datetime')

if timestamp:
    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

print(timestamp)
