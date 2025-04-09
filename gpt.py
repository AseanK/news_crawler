from openai import AsyncOpenAI
import os

class ChatGPT:
    def __init__(self) -> None:
        self.API_KEY = os.getenv("CHATGPT_API")

        self.client = AsyncOpenAI(
            api_key = self.API_KEY
        )


    async def get_top_articles(self, headlines):
        inp = ""
        for i, headline in enumerate(headlines):
            inp += f"{i}. {headline.text}"

        response = await self.client.responses.create(
            model="gpt-4o-mini",
            instructions="Only provide a space separated indice of following headlines that are crucial and impactful in stock market.",
            input=inp,
        )

        ## TODO: Check for duplicated headline
        return [int(x) for x in response.output_text.split()]


    async def get_summary(self, article):
        response = await self.client.responses.create(
            model="gpt-4o-mini",
            instructions=
            """
            Provide concise and comprehensive summary of the given article and list stock markets that might get affected according to the article.
            Explain how it'll be affected. Rate the impact it might cause out of 5 (5 = Extremly affected, 1 = least likely to get affected).
            Use the following rules:
            1. Use the following JSON format and update the values
            2. Do not add or manipulate anything other than the values in the JSON
            3. "Impacts" represents the stock markets that might get affected
            4. "Impacts" should contain at least 2 stock markets but no more than 6
            5. Response should only contain JSON
            6. In summary, do not mention that the output is a summary. Write the summary as it is original
            Template:
            {
            "summary": "summary of the article",
            "impacts": [
                        [
                            "company": "company name",
                            "ticker": "ticker symbol",
                            "ticker": "ticker symbol only with alphabet characters",
                            "rating": "impact rating using only ★, do not use any other character"
                        ],
                        [
                            "company": "company name",
                            "ticker": "ticker symbol only with alphabet characters",
                            "rating": "impact rating using only ★, do not use any other character"
                            "explanation": "Explanation of the impact"
                        ],
                    ],
            }
            """,
            input=article,
        )

        return response.output_text

