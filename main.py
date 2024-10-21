import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler(verbose=True, user_agent="Mozilla/5.0") as crawler:
        urls = [
            "https://www.google.com/search?q=artificial+intelligence",
           # "https://www.google.com/search?q=ai",
            "https://www.baidu.com/search?q=人工智能"
        ]

        results = []
        for url in urls:
            result = await crawler.arun(url=url)
            results.append(result)

        # 在这里分析结果
        for result in results:
            print(f"URL: {result.url}")
            print(f"更新日期: {result.last_modified}")
            print(f"来源: {result.source}")
            print(f"内容: {result.markdown[:500]}")  # 仅打印前500字

asyncio.run(main())

