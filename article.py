from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from utils import get_platform, convert_to_json


class NewsUpdater:
    def __init__(self, firebase, gpt) -> None:
        self.fb = firebase
        self.gpt = gpt
        self.is_not_ios = get_platform()
        self.opts = Options()
        self.opts.page_load_strategy = 'eager'
        self.opts.add_argument('--blink-settings=imagesEnabled=false')
        self.driver = webdriver.Chrome(self.opts)
    
    
    async def fetch_article_content(self, article, index):
        heading = article.text
        content = ""

        self.open_article_in_new_tab(index)
        self.driver.switch_to.window(self.driver.window_handles[-1])


        try:
            body = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "body-wrap"))
            )

            # Optionally click 'Read More'
            self.click_read_more(body)

            # Extract content from paragraphs
            content_list = body.find_elements(By.XPATH, "//p[contains(@class, 'yf-')]")
            content = " ".join([p.text for p in content_list])

            return heading, content

        except Exception as e:
            print(f"Error fetching content for article {heading}: {e}")
            return None, None

    
    def open_article_in_new_tab(self, index):
        article = self.driver.find_elements(By.XPATH, "//h3[contains(@class, 'clamp')]")[index]
        article.find_element(By.XPATH, "..").send_keys(Keys.CONTROL, Keys.RETURN) if self.is_not_ios else article.find_element(By.XPATH, "..").send_keys(Keys.COMMAND, Keys.RETURN)


    def click_read_more(self, body):
        try:
            body.find_element(By.CLASS_NAME, "readmore-button").click()
        except Exception:
            pass


    async def update_news(self):
        self.driver.get("https://finance.yahoo.com/topic/latest-news/")

        # Find the latest news headings
        data = self.driver.find_elements(By.XPATH, "//h3[contains(@class, 'clamp')]")

        top_articles = await self.gpt.get_top_articles(data)

        for idx in top_articles:
            self.driver.switch_to.window(self.driver.window_handles[0])
            heading, content = await self.fetch_article_content(data[idx], idx)

            if heading and content:
                summary_data = await self.gpt.get_summary(content)
                summary_data = convert_to_json(summary_data)

                if summary_data:
                    timestamp = self.driver.find_element(By.CLASS_NAME, "article-wrap").find_element(By.XPATH, "//time").get_attribute('datetime')
                    await self.fb.create_news(heading, summary_data, timestamp)
                    self.driver.close()

        # Quit the driver after completing the task
        self.driver.quit()
