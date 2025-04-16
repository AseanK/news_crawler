from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys

class EventUpdater:
    def __init__(self, firebase) -> None:
        self.fb = firebase
        self.opts = Options()
        self.opts.page_load_strategy = 'eager'
        self.opts.add_argument('--blink-settings=imagesEnabled=false')
        self.driver = webdriver.Chrome(self.opts)


    async def get_events(self):
        res = {}
        try:
            body = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.table"))
            )

            tbody_list = body.find_elements(By.TAG_NAME, "tbody")

            for tbody in tbody_list:
                events = tbody.find_elements(By.CSS_SELECTOR, "tbody tr")
                for event in events:
                    if event.get_attribute("data-id"):
                        td = event.find_elements(By.TAG_NAME, "td")
                        date = td[0].get_attribute("class")
                        time = td[0].find_element(By.TAG_NAME, "span").text
                        if time == "":
                            time = "N/A"

                        try:
                            content = td[4].find_element(By.TAG_NAME, "a").text
                        except:
                            content = td[4].find_element(By.TAG_NAME, "span").text

                        if date not in res:
                            res[date] = {}

                        if time not in res[date]:
                            res[date][time] = []

                        res[date][time].append(content)

            return res
        except Exception as e:
            print(f"Error: {e}")
            return {}


    async def update_event(self):
        self.driver.get("https://tradingeconomics.com/united-states/calendar")

        events = await self.get_events()

        for date, event in events.items():
            await self.fb.create_events(date, event)
