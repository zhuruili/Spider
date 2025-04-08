import requests
import re
from lxml import etree
import time
import pymysql
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from collections import Counter

from loguru import logger

class JTAQZK:
    """
    交通安全周刊爬虫
    示例网站：https://epaper.cpd.com.cn/szb/wwwcpd_9/dzb_16465/jtaqzk/2022/2022_06_14/16479_2022_06_14_30772/
    """
    def __init__(self):
        # 存入数据库时不变的字段
        self.init_db_fields()

        # 参数设置
        self.start_year = 2022
        self.end_year = 2025
        self.start_month = 6
        self.end_month = 4
        self.start_day = 7
        self.end_day = 1
        self.url_prefix = "https://epaper.cpd.com.cn/szb/wwwcpd_9/dzb_16465/jtaqzk/"
        
        # 线程
        self.max_workers = 3
        logger.debug(f"Max workers: {self.max_workers}")
        self.lock = Lock()

        # 请求参数
        self.init_params()

        # 数据库连接
        self.init_db()

        # 初始化代理
        self.init_proxy()

    def init_db_fields(self):
        """存入数据库时不变的字段"""
        self.web_domain = "epaper.cpd.com.cn"
        self.chinese_domain = "交通安全周刊"
        self.attachment_url = None  # 附件链接
        self.source = "交通安全周刊"  #  文章来源（Part）

    def init_params(self):
        """
        初始化请求参数
        """
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            # 'if-modified-since': 'Wed, 27 Dec 2023 08:04:30 GMT',
            # 'if-none-match': '"658bda8e-15a2a"',
            # 'priority': 'u=0, i',
            # 'referer': 'https://epaper.cpd.com.cn/szb/wwwcpd_9/dzb_16465/jtaqzk/2022/2022_06_14/',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            }

        self.cookies = {
            
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.cookies.update(self.cookies)

    def init_db(self):
        """
        初始化数据库连接与SQL语句
        """
        self.db = pymysql.connect(
            
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

    def init_proxy(self):
        """初始化代理"""
        proxies = {
            
        }
        self.proxies = proxies
        self.session.proxies.update(self.proxies)
        logger.info("Proxy initialized successfully.")
        # logger.warning("Proxy is not available for this page.")

    def generate_dates(self, start_year, start_month, start_day, end_year, end_month, end_day):
        """
        根据传入的起始年月日和截至年月日生成期间的所有可用的日期列表
        :param start_year: 开始年份
        :param start_month: 开始月份
        :param start_day: 开始日期
        :param end_year: 结束年份
        :param end_month: 结束月份
        :param end_day: 结束日期
        :return: 日期列表
        """
        # 接口链接：https://epaper.cpd.com.cn/szb/wwwcpd_9/dzb_16465/jtzksy/suoyin/

        # 访问接口得到所有日期
        date_url = 'https://epaper.cpd.com.cn/szb/wwwcpd_9/dzb_16465/jtzksy/suoyin/'
        response = self.get_with_retry(date_url)
        if response is None:
            logger.error(f"Failed to retrieve dates from {date_url}")
            return []

        # 提取日期
        pattern = re.compile(r'sss1="([\d\-,]+)"')
        match = pattern.search(response)
        if match:
            date_str = match.group(1)
            dates = date_str.split(',')
        else:
            logger.error("No dates found in the response.")
            dates = []

        # 过滤日期
        start_date = datetime(start_year, start_month, start_day)
        end_date = datetime(end_year, end_month, end_day)
        filtered_dates = []
        for date in dates:
            if date != '':
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                if start_date <= date_obj <= end_date:
                    filtered_dates.append(date_obj.strftime('%Y_%m_%d'))

        logger.info(f"Filtered dates: {filtered_dates}")

        # 测试单日
        # filtered_dates = ['2025_04_01']

        return filtered_dates
        
    def get_details(self, date):
        """
        :param url: 日链接
        :return: 每日详情页url列表
        """
        # 根据日期生成url,形如https://epaper.cpd.com.cn/szb/wwwcpd_9/dzb_16465/jtaqzk/2022/2022_06_14/
        year = date.split('_')[0]  # 把年份提出来
        url = f"{self.url_prefix}{year}/{date}"
        response = self.get_with_retry(url)
        if response is None:
            logger.error(f"Data is None for url: {url}.The page may be empty or pictures.")
            return []
        
        # Response: <script>window.location.href='./16479_2022_11_15_32375/'</script>
        # 根据重定向链接调整url
        pattern = re.compile(r"window.location.href='\.(.*?)'")
        match = pattern.search(response)
        if match:
            url = f"{url}{match.group(1)}"
        else:
            logger.error("No redirection link found in the response.")
            return []
        
        logger.info(f"正在重定向到: {url}")
        response = self.get_with_retry(url)
        if response is None:
            logger.error(f"Data is None for url: {url}.The page may be empty or pictures.")
            return []
        
        # 提取详情链接
        # document.write('<li><a href="http://epaper.cpd.com.cn/szb/wwwcpd_9/dzb_16465/jtaqzk/2025/2025_04_01/16479_2025_04_01_41151/425/t_1177973.html">
        pattern = re.compile(r'document\.write\(\'<li><a href="(http://epaper.cpd.com.cn/szb/wwwcpd_9/dzb_16465/jtaqzk/.*?)">')
        matches = pattern.findall(response)
        if matches:
            logger.info(f"成功获取到日期为{date}的所有篇章的链接，共计{len(matches)}篇")
            return count_versions(matches)  # 统计每个版号的出现次数，并返回形如 [(url1, count1), (url2, count2), ...] 的结果
        else:
            logger.error("No article links found in the response.")
            return []

        
    def get_with_retry(self, url, retry=5, timeout=5):
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
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding  # 自动检测编码
                    return response.text
                elif response.status_code == 404:
                    logger.error(f"404 for page : {url}")
                    return None
                else:
                    logger.error(f"Failed to retrieve the page: {url}, status code: {response.status_code}")
            except Exception as e:
                print(f"Failed to retrieve the page: {url}")
                print(f"Error: {e}")
        return None

    def get_data(self, details):
        """
        获取每篇文章的具体数据
        :param details: 文章链接与版号计数
        :return: 文章的数据
        """
        # 获取网页内容
        response = self.get_with_retry(details[0])
        if response is None:
            logger.error(f"Data is None for url: {details[0]}.The page may be empty or pictures.")
            return None
        # 解析网页内容，规范化填入数据库的字段
        web_domain = self.web_domain
        chinese_domain = self.chinese_domain
        article_id = ''.join(re.findall(r'\d+', details[0]))  # 以url中的数字作为文章id
        article_id = article_id[-30:]  # 取最后30位数字，避免过长
        # 提取一级栏目和版次
        level_column_1_page_pattern = re.compile(r'<span id="bc"><a href="\.\./">第(\d+)版')
        level_column_1_page_match = level_column_1_page_pattern.search(response)
        level_column_1_page = level_column_1_page_match.group(1) if level_column_1_page_match else None

        level_column_1_pattern = re.compile(r'<span id="bc"><a href="\.\./">第\d+版 (.*?)</a></span>')
        level_column_1_match = level_column_1_pattern.search(response)
        level_column_1 = level_column_1_match.group(1) if level_column_1_match else None

        level_column_2 = details[1]  # 计数
        article_url = details[0]  # 文章链接
        # 提取文章标题
        title_matches = re.findall(r'<title>(.*?)</title>', response, re.DOTALL)
        if title_matches:
            article_title = title_matches[0].replace('\n', '').strip()
        if article_title:  # 除去标题中的HTML标签
            article_title = re.sub(r'<[^>]+>', '', article_title).replace('&nbsp;', '').replace('&ldquo;', '').replace('&rdquo;', '').replace('-', '')
        else:
            article_title = None
        # 提取文章内容
        # xpath: //div[@class='content_main']/div/p[@class='contentP']
        html = etree.HTML(response)
        article_content = html.xpath("//div[@class='content_main']/div/p[@class='contentP']/text()")
        # 除去内容中的HTML标签
        if article_content:
            article_content = ''.join(article_content)  # 拼接
            article_content = re.sub(r'<[^>]+>', '', article_content)
            article_content = article_content.replace('&nbsp;', '').replace('&ldquo;', '').replace('&rdquo;', '')
        else:
            article_content = None
        # 作者
        author_name = ''
        # 发布日期
        # 从URL中提取发布日期
        url_date_pattern = re.compile(r'/(\d{4}_\d{2}_\d{2})/')
        url_date_match = url_date_pattern.search(details[0])
        if url_date_match:
            publish_date_str = url_date_match.group(1)
            publish_date = datetime.strptime(publish_date_str, '%Y_%m_%d')
        else:
            publish_date = None
        # 来源（拼接后的完整版）
        source = f"{self.source} {publish_date.strftime('%Y-%m-%d')} 第{level_column_1_page}版"
        gettime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
                logger.info(f"成功保存发布日期为{data['publish_date']}的数据，文章链接为{data['article_url']}, 文章标题为{data['article_title']}")
            except Exception as e:
                self.db.rollback()
                logger.error(f"Failed to save data: {data['article_url']}")
                logger.error(f"Error: {e}")


# 辅助函数
def count_versions(urls):
    """
    统计每个版号的出现次数，并返回形如 [(url1, count1), (url2, count2), ...] 的结果
    :param urls: 包含所有链接的列表
    :return: 包含每个链接及其对应版号总数的列表
    """
    # 提取版号的正则表达式
    version_pattern = re.compile(r'/\d{5}_\d{4}_\d+_\d+_(\d{5})/')  # 匹配类似 32837 的版号
    # 提取所有版号
    versions = [version_pattern.search(url).group(1) for url in urls if version_pattern.search(url)]
    # 统计版号出现次数
    version_counts = Counter(versions)
    # 构造结果
    result = [(url, version_counts[version_pattern.search(url).group(1)]) for url in urls if version_pattern.search(url)]

    return result


if __name__ == '__main__':
    jtaqzk = JTAQZK()
    dates = jtaqzk.generate_dates(jtaqzk.start_year, jtaqzk.start_month, jtaqzk.start_day, jtaqzk.end_year, jtaqzk.end_month, jtaqzk.end_day)
    for date in dates:
        details = jtaqzk.get_details(date)
    # 多线程处理
        logger.debug(f"成功生成{date}的所有篇章的详细链接，共计{len(details)}篇")
        with ThreadPoolExecutor(max_workers=jtaqzk.max_workers) as executor:
            results = executor.map(jtaqzk.get_data, details)
            try:
                for result in results:
                    if result is None:
                        logger.warning(f"Data is None for a certain url in {details}, continue to the next one.")
                        continue
                    print(result)
                    # jtaqzk.save_data(result)
            except Exception as e:
                logger.error(f"多线程出现异常: {e}")
        time.sleep(1)
            


