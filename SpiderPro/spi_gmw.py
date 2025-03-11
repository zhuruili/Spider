import requests
import re
from datetime import datetime, timedelta
import pymysql
from loguru import logger
import time
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

class GuangMingWang:
    """
    光明网爬虫
    示例网站：https://epaper.gmw.cn/gmrb/html/2025-01/25/nbs.D110000gmrb_01.htm
    """
    def __init__(self):
        """初始化"""
        # 存入数据库时不变的字段
        self.web_domain = "epaper.gmw.cn"  # 文章主站点
        self.chinese_domain = "光明日报"  # 站点中文名称
        self.level_column_2 = None  # 文章二级栏目
        self.attachment_url = None  # 附件链接
        self.source = "光明日报"  # 文章来源

        # 参数设置
        self.start_year = 2012
        self.end_year = 2020
        self.start_month = 7
        self.end_month = 12
        self.start_day = 12
        self.end_day = 31
        self.url_prefix = "https://epaper.gmw.cn/gmrb/html/"
        self.url_suffix_default = "nbs.D110000gmrb_01.htm"

        # 多线程
        self.max_workers = 5
        logger.debug(f"Max workers: {self.max_workers}")
        self.lock = Lock()

        # 请求参数
        self.init_params()

        # 数据库连接
        self.init_db()

        # 初始化代理
        self.init_proxy()

    def init_params(self):
        """
        初始化请求参数
        """
        self.headers = {
            "YOUR_HEADERS"
        }

        self.cookies = {
            "YOUR_COOKIES"
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.cookies.update(self.cookies)

    def init_db(self):
        """
        初始化数据库连接与SQL语句
        """
        self.db = pymysql.connect(
            "YOUR_DB_CONNECTION",
        )
        self.cursor = self.db.cursor()
        self.GMW_sql = """
        INSERT INTO newspapers_relate_info (
        web_domain, chinese_domain, article_id, level_column_1, level_column_2,
        article_url, article_title, content, author_name, source,
        publish_date, gettime, attachment_url
        ) 
        VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s)
        """

    def generate_urls(self, start_year, start_month, start_day, end_year, end_month, end_day):
        """
        根据传入的起始年月日和截至年月日生成期间的所有链接
        :param start_year: 开始年份
        :param start_month: 开始月份
        :param start_day: 开始日期
        :param end_year: 结束年份
        :param end_month: 结束月份
        :param end_day: 结束日期
        :return: url列表
        url示例: https://epaper.gmw.cn/gmrb/html/2025-01/25/nbs.D110000gmrb_01.htm
        """
        urls = []
        current_date = datetime(start_year, start_month, start_day)
        end_date = datetime(end_year, end_month, end_day)

        while current_date <= end_date:
            url = f"{self.url_prefix}{current_date.strftime('%Y-%m/%d')}/{self.url_suffix_default}"
            urls.append(url)
            current_date += timedelta(days=1)

        logger.info(f"起始日期为{format_date(datetime(start_year, start_month, start_day))}, 截至日期为{format_date(datetime(end_year, end_month, end_day))}, 共计{len(urls)}天")

        return urls

    def generate_dates_in_url(self, start_year, end_year, start_month, end_month):
        """
        根据传入的起止日期生成**url**中的日期列表
        :param start_year: 开始年份
        :param end_year: 结束年份
        :param start_month: 开始月份
        :param end_month: 结束月份
        :return: 日期列表
        日期示例：2025-02
        """
        dates = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                    continue
                dates.append(f"{year}-{month:02d}")
        return dates
    
    def generate_url_for_every_day(self, dates):
        """
        根据传入的日期列表生成url列表
        :param dates: 日期列表
        :return: url列表
        url示例: https://epaper.gmw.cn/gmrb/html/2025-01/25/nbs.D110000gmrb_01.htm
        """
        urls = []
        for date in dates:
            for day in range(1, 32):  # 假设每个月最多有31天
                url = f"{self.url_prefix}{date}/{day:02d}/{self.url_suffix_default}"
                urls.append(url)
        return urls

    def check_url(self, url):
        """
        检查url是否有效
        :param url: 需要检查的url
        :return: True or False
        """
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            logger.error(f"{url} is invalid.")
            return False
        
    def get_urls_for_every_branch(self, url):
        """
        根据传入的`每日url`生成`每日各版面url`列表
        :param url: 每日url
        :return: 每日各版面url列表
        """
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve the page: {url}")
            return []

        page_content = response.text
        branch_urls = re.findall(r'<a id=pageLink href=(nbs\.D110000gmrb_\d+\.htm)>', page_content)
        full_branch_urls = [url.rsplit('/', 1)[0] + '/' + branch_url for branch_url in branch_urls]

        # 添加每日的默认版面链接
        if f"{url.rsplit('/', 1)[0]}/nbs.D110000gmrb_01.htm" not in full_branch_urls:
            full_branch_urls.insert(0, f"{url.rsplit('/', 1)[0]}/nbs.D110000gmrb_01.htm")

        return full_branch_urls
        
    def get_detailed_urls(self, url):
        """
        获取每日各版面的所有篇章的详细链接
        :param url: 每日各版面url
        :return: 该面板的所有篇章的详细链接列表
        """
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve the page: {url}")
            return []
        page_content = response.text
        detailed_urls = re.findall(r'<a href=(nw\.D110000gmrb_\d+_\d+-\d+\.htm.*?)>', page_content)
        full_detailed_urls = [url.rsplit('/', 1)[0] + '/' + detailed_url for detailed_url in detailed_urls]
        return full_detailed_urls

    def get_data(self, url):
        """
        获取每篇文章的具体数据
        :param url: 文章的url
        :return: 文章的数据
        示例url: https://epaper.gmw.cn/gmrb/html/2022-01/07/nw.D110000gmrb_20220107_3-01.htm
        """
        # 获取网页内容
        response = self.get_with_retry(url=url)
        if response is None:
            logger.error(f"Failed to retrieve the page: {url}.The url may be invalid.")
            return None
        
        # 填入数据库的字段
        web_domain = self.web_domain
        chinese_domain = self.chinese_domain
        article_id = ''.join(re.findall(r'\d+', url))
        # 提取一级栏目
        level_column_1_pattern = re.compile(r'(\d+)版:([^\s<]+)')
        level_column_1_matches = level_column_1_pattern.findall(response)
        level_column_1 = level_column_1_matches[0][1] if level_column_1_matches else None
        level_column_2 = self.level_column_2
        article_url = url  # 文章链接
        # 提取文章标题
        title_match = re.findall(r'<founder-title>(.*?)</founder-title>', response, re.DOTALL)
        article_title = title_match[0].replace('\n', '').strip() if title_match else None
        # 提取文章内容
        content_match = re.search(r'<div id="articleContent">.*?<!--enpcontent-->(.*?)<!--/enpcontent-->', response, re.S)
        article_content = content_match.group(1).strip() if content_match else None
        # 提取<p>标签中的内容并拼接
        if article_content:
            paragraphs = re.findall(r'<P>(.*?)</P>', article_content, re.S)
            article_content = ''.join(paragraph.strip() for paragraph in paragraphs)
            article_content = format_content(article_content)
        # 作者
        author_match = re.findall(r'<founder-author>(.*?)</founder-author>', response, re.DOTALL)
        author_name = author_match[0].replace('\n', '').strip() if author_match else None
        publish_date = from_url_get_date(url)
        source = f"{self.source} {format_date(publish_date)} 第{level_column_1_matches[0][0]}版"
        gettime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_time = gettime
        attachment_url = self.attachment_url

        return {
            "web_domain": web_domain,
            "chinese_domain": chinese_domain,
            "article_id": article_id,
            "level_column_1": level_column_1,
            "level_column_2": level_column_2,
            "article_url": article_url,
            "article_title": article_title,
            "content": article_content,
            "author_name": author_name,
            "source": source,
            "publish_date": publish_date,
            "gettime": gettime,
            "updatetime": update_time,
            "attachment_url": attachment_url
        }

    def save_data(self, data):
        """
        将数据存入数据库
        :param data: 需要存入的数据
        """
        with self.lock:
            try:
                params = (
                    data["web_domain"], data["chinese_domain"], data["article_id"],
                    data["level_column_1"], data["level_column_2"], data["article_url"],
                    data["article_title"], data["content"], data["author_name"],
                    data["source"], data["publish_date"], data["gettime"],
                    data["attachment_url"]
                )
                self.cursor.execute(self.GMW_sql, params)
                self.db.commit()
                logger.info(f"成功保存发布日期为{format_date(data['publish_date'])}的数据，文章链接为{data['article_url']}，文章标题为{data['article_title']}")
            except Exception as e:
                self.db.rollback()
                logger.error(f"Failed to save data: {data['article_url']}")
                logger.error(f"Error: {e}")
        
    def init_proxy(self):
        """
        初始化代理
        """
        # 把你的代理放在这里
        proxies = {}
        self.proxies = proxies
        self.session.proxies.update(self.proxies)
        requests.proxies = self.proxies
        logger.info("Proxy initialized successfully.")

    def get_with_retry(self, url, retry=3, timeout=2):
        """
        获取指定url的内容，如果失败自动重试，合计请求5次
        :param url: 需要获取内容的url
        :param retry: 重试次数
        :param timeout: 超时时间
        :return: 网页内容
        """
        for i in range(retry):
            if i > 0:
                logger.warning(f"Retry {i}/{retry} times for {url}")
                time.sleep(2)
            try:
                response = self.session.get(url, timeout=timeout)
                if response.status_code == 200 and response.text is not None:
                    response.encoding = 'utf-8'
                    return response.text
                else:
                    logger.error(f"Failed to retrieve the page: {url}")
            except Exception as e:
                print(f"Failed to retrieve the page: {url}")
                print(f"Error: {e}")
        return None


# 辅助函数

def from_url_get_date(url):
    """
    从url中获取日期
    :param url: 需要获取日期的url
    :return: 日期
    示例url：https://epaper.gmw.cn/gmrb/html/2022-01/07/nw.D110000gmrb_20220107_3-01.htm
    """
    match = re.search(r'/(\d{4}-\d{2}/\d{2})/', url)
    if match:
        date_str = match.group(1).replace('/', '-')
        return datetime.strptime(date_str, '%Y-%m-%d')
    return None
    
def format_date(date):
    """
    格式化日期
    :param date: 日期
    :return: 格式化后的日期
    """
    return date.strftime('%Y-%m-%d')

def format_content(content):
    """
    格式化文章内容,去除`&nbsp`、`<STRONG>`等内容
    :param content: 文章内容
    :return: 格式化后的文章内容
    """
    content = content.replace('&nbsp;', '')
    content = re.sub(r'<[^>]+>', '', content)
    return content

if __name__ == '__main__':
    gmw = GuangMingWang()
    every_day_urls = gmw.generate_urls(
        gmw.start_year, gmw.start_month, gmw.start_day, 
        gmw.end_year, gmw.end_month, gmw.end_day
        )
    for every_day_url in every_day_urls:
        if gmw.check_url(every_day_url):
            detail_list = []  # 存储每日各版面的详细链接
            branches = gmw.get_urls_for_every_branch(every_day_url)
            for branch in branches:
                branch_details = gmw.get_detailed_urls(branch)
                detail_list.extend(branch_details)
            # 多线程获取数据
            logger.success(f"成功生成{every_day_url}的所有详细链接，共计{len(detail_list)}篇文章")
            with ThreadPoolExecutor(max_workers=gmw.max_workers) as executor:
                results = executor.map(gmw.get_data, detail_list)
                try:
                    for result in results:
                        if result is None:
                            logger.warning(f"Data is None for a certain url in {branch_details}, continue to the next one.")
                            continue
                        print(result)
                        # gmw.save_data(result)
                except Exception as e:
                    logger.error(f"多线程出现异常: {e}")
            time.sleep(0.3)
