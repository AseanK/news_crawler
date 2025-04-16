import asyncio
import argparse
from article import NewsUpdater
from event import EventUpdater
from utils import convert_to_json

from firebase import Firebase
from gpt import ChatGPT


async def manual_update_news(title, content, date):
    gpt = ChatGPT()
    fb = Firebase()

    summary_data = await gpt.get_summary(content) ## Get summary

    summary_data = convert_to_json(summary_data)

    await fb.create_news(title, summary_data, date)


async def auto_update_news():
    gpt = ChatGPT()
    fb = Firebase()

    updater = NewsUpdater(firebase=fb, gpt=gpt)
    await updater.update_news()


async def auto_update_event():
    fb = Firebase()
    updater = EventUpdater(fb)

    await updater.update_event()


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
            await auto_update_news()
    elif args.mode == "cal":
        await auto_update_event()
        

if __name__ == "__main__":
    asyncio.run(main())
