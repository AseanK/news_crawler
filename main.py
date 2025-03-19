import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys

from openai import AsyncOpenAI

import os
import requests
from lxml.html import fromstring

from firebase import Firebase

API_KEY = os.getenv("CHATGPT_API")

def get_proxies():
    url = 'https://free-proxy-list.net/anonymous-proxy.html'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:30]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

async def get_summary(article):
    client = AsyncOpenAI(
        api_key = API_KEY
    )

    response = await client.responses.create(
        model="gpt-4o-mini",
        instructions="Provide concise and comprehensive summary of the given article and list stock markets that might get affected according to the article. Explain how it'll be affected. Rate the impact it might cause out of 5 (5 = Extremly affected, 1 = least likely to get affected)",
        input=article,
    )

    return response.output_text

async def get_top_articles(headlines):
    inp = ""
    for i, headline in enumerate(headlines):
        inp += f"{i}. {headline.text}"

    client = AsyncOpenAI(
        api_key = API_KEY
    )

    response = await client.responses.create(
        model="gpt-4o-mini",
        instructions="Provide only space separated indice of following headlines that are crucial and impactful in stock market.",
        input=inp,
    )

    ## Check for duplicated headline
    return [int(x) for x in response.output_text.split()]


async def main():
    opts = Options()
    fb = Firebase()
    opts.page_load_strategy = 'eager'
    opts.add_argument('--blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome(opts)
    driver.get("https://finance.yahoo.com/topic/latest-news/")

    data = driver.find_elements(By.XPATH, "//h3[contains(@class, 'clamp')]")

    top_articles = await get_top_articles(data)
    print(top_articles)

    for i in top_articles:
        heading = data[i].text
        content = ""
        data[i].find_element(By.XPATH, "..").send_keys(Keys.COMMAND, Keys.RETURN) ## Open each article in separate tab
        driver.switch_to.window(driver.window_handles[-1]) ## Focus to article tabs

        body = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "body-wrap"))) ## Wait to load

        try: ## If read more, click it
            body.find_element(By.CLASS_NAME, "readmore-button").click()
        except Exception:
            pass

        content_list = body.find_elements(By.XPATH, "//p[contains(@class, 'yf-')]") ## Content body in a list

        for i in content_list:
            content += i.text

        summary = await get_summary(content) ## Get summary

        fb.create_data(heading, summary)
        


if __name__ == "__main__":
    asyncio.run(main())
