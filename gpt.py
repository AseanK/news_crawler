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
            Use the following format, fill in the []:
            [summary of the provided article]
            ### Possible impact
            [bullet points of companies that are likely to get affected with following format]
            - **[Company name (ticker symbol)]** [rating of the impact with ★]
                - [Explanation of the impact]
            """,
            input=article,
        )

        return response.output_text

