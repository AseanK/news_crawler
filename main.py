import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys

import platform

from firebase import Firebase
from gpt import ChatGPT


def get_platform():
    return platform.system != 'Linux' or 'Windows'


async def main():
    gpt = ChatGPT()
    opts = Options()
    fb = Firebase()
    is_mac_os = get_platform()
    opts.page_load_strategy = 'eager'
    opts.add_argument('--blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome(opts)
    driver.get("https://finance.yahoo.com/topic/latest-news/")

    data = driver.find_elements(By.XPATH, "//h3[contains(@class, 'clamp')]")

    top_articles = await gpt.get_top_articles(data)

    for i in top_articles:
        driver.switch_to.window(driver.window_handles[0])
        heading = data[i].text
        content = ""

        ## Open each article in separate tab
        if is_mac_os:
            data[i].find_element(By.XPATH, "..").send_keys(Keys.COMMAND, Keys.RETURN)
        else:
            data[i].find_element(By.XPATH, "..").send_keys(Keys.CONTROL, Keys.RETURN) 

        driver.switch_to.window(driver.window_handles[-1]) ## Focus to article tabs

        try:
            body = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "body-wrap"))) ## Wait to load

            try: ## If read more, click it
                body.find_element(By.CLASS_NAME, "readmore-button").click()
            except Exception:
                pass

            content_list = body.find_elements(By.XPATH, "//p[contains(@class, 'yf-')]") ## Content body in a list

            for i in content_list:
                content += i.text

            summary = await gpt.get_summary(content) ## Get summary

            fb.create_data(heading, summary)

        except Exception:
            continue

    driver.quit()
        

if __name__ == "__main__":
    asyncio.run(main())
