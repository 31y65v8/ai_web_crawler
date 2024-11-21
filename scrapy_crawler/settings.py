'''coded by 王栩麓'''
BOT_NAME = "scrapy_crawler"

SPIDER_MODULES = ["scrapy_crawler.spiders"]
NEWSPIDER_MODULE = "scrapy_crawler.spiders"

REDIRECT_ENABLED = True#跳转到重定向后的url

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "scrapy_crawler1 (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "scrapy_crawler1.middlewares.ScrapyCrawlerSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "scrapy_crawler1.middlewares.ScrapyCrawlerDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "scrapy_crawler1.pipelines.ScrapyCrawlerPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# 自定义随机User-Agent
DOWNLOADER_MIDDLEWARES = {
    'scrapy_crawler.middlewares.RandomUserAgentMiddleware': 543,  # 中间件的优先级
}

DEFAULT_REQUEST_HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com'
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 禁用默认的 User-Agent 中间件
}
#启用pipelines，将爬取到的Google数据存入数据库
#ITEM_PIPELINES = {
 #   'scrapy_crawler.pipelines.GoogleResultPipeline': 1,
  #  'scrapy_crawler.pipelines.BaiduResultPipeline': 2,
#}

#添加动态网页处理（搜索结果页）
#SPLASH_URL = 'http://localhost:8050  'http://localhost:8052','
# 定义多个 Splash 实例的地址
SPLASH_URLS = [
    'http://localhost:8050',
    'http://localhost:8051',

]

DOWNLOAD_TIMEOUT = 300
DOWNLOADER_MIDDLEWARES = {
    'scrapy_crawler.middlewares.SplashProxyMiddleware':722,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'#使用splash的去重过滤器

CONCURRENT_REQUESTS_PER_DOMAIN = 5
SPLASH_MAX_TIMEOUT = 60  # Splash 的超时时间
# 设置下载延迟，避免对 Splash 服务器产生过多负载
DOWNLOAD_DELAY = 2  # 每个请求之间的延迟，单位是秒
DOWNLOAD_TIMEOUT = 60  # 下载超时时间
# 使用 Splash 缓存，减少重复请求并减轻 Splash 服务器压力
HTTPCACHE_ENABLED = False  # 禁用 HTTP 缓存
HTTPCACHE_EXPIRATION_SECS = 86400  # 缓存有效期设置为 24 小时
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'  # 使用 Splash 的缓存存储
# 自定义 Splash 的参数以减少资源消耗，例如禁用图片加载
SPLASH_ARGS = {
    'wait': 8,  # 等待页面加载的时间，单位为秒
    'images': 0,  # 禁用图片加载，减少 Splash 的渲染压力
    'resource_timeout': 10  # 对加载资源设置超时，单位为秒
}