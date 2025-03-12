from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType

import requests
from lxml.html import fromstring

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

def bypass_cookie(driver):
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'sp_message_container')]")))

    if element:
        driver.execute_script("""
                var element = arguments[0];
                element.parentNode.removeChild(element);
            """, element)


if __name__ == "__main__":
    running = True
    data = []

    opts = Options()
    # prefs = {}
    # prefs["webkit.webprefs.javascript_enabled"] = False
    # prefs["profile.default_content_setting_values.javascript"] = 2
    # prefs["profile.managed_default_content_settings.javascript"] = 2

    # opts.add_experimental_option("prefs", prefs)
    # opts.add_argument('--disable-javascript')
    opts.page_load_strategy = 'eager'

    # prox = Proxy()

    driver = webdriver.Chrome(opts)
    driver.get("https://finance.yahoo.com/topic/latest-news/")

    for headline in driver.find_elements(By.XPATH, "//h3[contains(@class, 'clamp')]"):
        data.append(headline)

    for i, headline in enumerate(data):
        print(f"{i}. {headline.text}")

    while running:
        content = ""
        inp = input("")

        if inp == "q":
            driver.quit()

        ## Validation needed if inp > 0 and inp < len(data)
        data[int(inp)].find_element(By.XPATH, "..").click()

        body = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "body-wrap")))
        try:
            body.find_element(By.CLASS_NAME, "readmore-button").click()
        except Exception:
            pass

        content_list = body.find_elements(By.XPATH, "//p[contains(@class, 'yf-')]")

        for i in content_list:
            content += i.text

        print(content)
