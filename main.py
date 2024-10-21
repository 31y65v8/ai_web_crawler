import asyncio
from crawl4ai import AsyncWebCrawler

async def main():#定义名为main的异步函数，所有异步操作必须在async函数中运行
    '''async with：使用异步上下文管理器，确保在进入和退出上下文时正确管理资源。这里是创建一个 AsyncWebCrawler 的实例。
AsyncWebCrawler(verbose=True)：创建一个异步爬虫实例，verbose=True 表示在爬取过程中输出详细的日志信息（如请求、响应、错误等）。
as crawler：将创建的爬虫实例命名为 crawler，可以在此上下文中使用它进行网页爬取。'''
    async with AsyncWebCrawler(verbose=True,user_agent="Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3") as crawler:
        result = await crawler.arun(url="https://www.nbcnews.com/business")
        print(f"Basic crawl result: {result.markdown[:500]}")  # Print first 500 characters

   # asyncio.run(main())
        #pass#占位符，表示在这里将来会添加具体的爬虫代码。当前没有实际的爬取操作。

if __name__ == "__main__":#如果当前模块是主程序则执行以下代码块，防止模块被导入时自动执行某些代码
    asyncio.run(main())#调用 asyncio.run() 函数以执行 main 异步函数。这会启动事件循环，并在其中运行 main，直到其完成。