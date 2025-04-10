import asyncio
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys

import platform
import json

from env import Env
from firebase import Firebase
from gpt import ChatGPT


def get_platform():
    os = platform.system()
    return (os != 'Linux' or os == 'Windows')


def convert_to_json(inp):
    if inp.startswith("```json"):
        inp = inp.strip("```json").strip().strip("```")

    try:
        json_data = json.loads(inp)
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


async def manual_update_news(title, content, date):
    print(title)
    print(content)
    print(date)


async def update_news():
    gpt = ChatGPT()
    opts = Options()
    fb = Firebase()
    is_not_ios = get_platform()
    opts.page_load_strategy = 'eager'
    opts.add_argument('--blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome(opts)
    driver.get("https://finance.yahoo.com/topic/latest-news/")

    data = driver.find_elements(By.XPATH, "//h3[contains(@class, 'clamp')]") ## HEADING ELEMENT

    top_articles = await gpt.get_top_articles(data)

    for i in top_articles:
        driver.switch_to.window(driver.window_handles[0])
        heading = data[i].text
        content = ""

        ## Open each article in separate tab
        if is_not_ios:
            data[i].find_element(By.XPATH, "..").send_keys(Keys.COMMAND, Keys.RETURN)
        else:
            data[i].find_element(By.XPATH, "..").send_keys(Keys.CONTROL, Keys.RETURN) 

        driver.switch_to.window(driver.window_handles[-1]) ## Focus to article tabs

        try:
            body = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "body-wrap"))) ## BODY ELEMENT
            timestamp = driver.find_element(By.CLASS_NAME, "article-wrap").find_element(By.XPATH, "//time").get_attribute('datetime')

            try: ## If read more, click it
                body.find_element(By.CLASS_NAME, "readmore-button").click()
            except Exception:
                pass

            content_list = body.find_elements(By.XPATH, "//p[contains(@class, 'yf-')]") ## ARTICLE CONTENT ELEMENT

            for i in content_list:
                content += i.text

            summary_data = await gpt.get_summary(content) ## Get summary

            summary_data = convert_to_json(summary_data)

            if data != None:
                fb.create_data(heading, summary_data, timestamp)

            driver.close()

        except Exception:
            continue

    driver.quit()


async def main():
    parser = argparse.ArgumentParser(usage="Web-crawler for StockPointer")

    parser.add_argument("mode", choices=["news", "cal"])

    parser.add_argument("-m", "--manual", action="store_true")
    parser.add_argument("-t", "--title", help="Title for manual mode")
    parser.add_argument("-c", "--content", help="Content for manual mode")
    parser.add_argument("-d", "--date", help="DateTime for manual mode")

    args = parser.parse_args()

    if args.mode == "news":
        if args.manual: ## Manual mode
            if not args.title or not args.content or not args.date:
                parser.error("--manual requires both --title, --content and --date.")
            else:
                await manual_update_news(args.title, args.content, args.date)
        else:
            await update_news()
    elif args.mode == "cal":
        print("Cal mode") ## TODO
        

if __name__ == "__main__":
    asyncio.run(main())
