import requests
import re
from lxml import etree
import time
import pymysql
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from loguru import logger

class chinanshw:
    """
    中国农村信用合作报爬虫
    示例网站：http://ep.chinanshw.cn/content/2025-03/25
    """
    def __init__(self):
        # 存入数据库时不变的字段
        self.init_db_fields()

        # 参数设置
        self.start_year = 2018
        self.end_year = 2025
        self.start_month = 4
        self.end_month = 4
        self.start_day = 24
        self.end_day = 1
        self.url_prefix = "http://ep.chinanshw.cn/content/"
        
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
        self.web_domain = "ep.chinanshw.cn"
        self.chinese_domain = "中国农村信用合作报"
        self.attachment_url = None  # 附件链接
        self.source = "中国农村信用合作报"  #  文章来源（Part）

    def init_params(self):
        """
        初始化请求参数
        """
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            # 'If-Modified-Since': 'Tue, 01 Apr 2025 06:04:42 GMT',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
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
        :return: 日期链接列表
        """
        dates = []
        date_urls = []
        start_date = datetime(start_year, start_month, start_day)
        end_date = datetime(end_year, end_month, end_day)
        delta = timedelta(days=1)
        while start_date <= end_date:
            dates.append(start_date.strftime('%Y%m%d'))
            date_urls.append(f"{self.url_prefix}{start_date.strftime('%Y-%m/%d')}")
            start_date += delta
        logger.success(f"成功生成日期列表，共计{len(dates)}个")

        return date_urls

    def get_branches(self, url):
        """
        :param url: 日链接
        :return: 每日各版面url列表
        """
        response = self.get_with_retry(url)
        if len(response) == 8:
            logger.debug(f"找不到所在刊期: {url}")
            return []
        if response is None:
            logger.error(f"Data is None for url: {url}.The page may be empty or pictures.")
            return []
        # <a  href="/content/2018-04/24/1">第1版：要闻</a></span>
        pattern = re.compile(r'<span class="txt"><a  href="(.*?)">第(\d+)版：([^<]+)</a></span>', re.DOTALL)
        branches = pattern.findall(response)

        logger.success(f"成功生成{date}的所有版面链接，共计{len(branches)}个")

        return branches

    def get_detailed_urls(self, branch):
        """
        获取每日各版面的所有篇章的详细链接
        :param branch: 从版面处获得的各种参数
        :return: 该面板的所有篇章的详细链接, 版次，版名
        """
        url = f"http://{self.web_domain}/{branch[0]}"
        response = self.get_with_retry(url)
        if response is None:
            logger.error(f"Data is None for url: {url}.The page may be empty or pictures.")
            return []
        # 使用`xpath`提取：//ul[@class='scroll']/li/a/@href
        html = etree.HTML(response)
        detailed_urls = html.xpath("//ul/li/a/@href")
        column_2_count = len(detailed_urls)

        logger.success(f"成功生成{url}的所有篇章的详细链接，共计{column_2_count}篇")

        # 组织返回数据
        detaileds = [(f"http://{self.web_domain}{url}", branch[1], branch[2], column_2_count) for url in detailed_urls]

        return detaileds

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
        :param details: 包含文章链接、版次和版名和计数的元组
        :return: 文章的数据
        """
        # 获取网页内容
        response = self.get_with_retry(url=details[0])
        if response is None:
            logger.error(f"Data is None for url: {details[0]}.The page may be empty or pictures.")
            return None
        # 解析网页内容，规范化填入数据库的字段
        web_domain = self.web_domain
        chinese_domain = self.chinese_domain
        article_id = ''.join(re.findall(r'\d+', details[0]))  # 以url中的数字作为文章id
        # 提取一级栏目和版次
        level_column_1_page = details[1]  # 版次
        level_column_1 = details[2]  # 一级栏目
        level_column_2 = details[3]  # 计数
        article_url = details[0]  # 文章链接
        # 提取文章标题
        title_matches = re.findall(r'<h1>(.*?)</h1>', response, re.DOTALL)
        if title_matches:
            article_title = title_matches[0].replace('\n', '').strip()
        if article_title:  # 除去标题中的HTML标签
            article_title = re.sub(r'<[^>]+>', '', article_title).replace('&nbsp;', '').replace('&ldquo;', '').replace('&rdquo;', '')
        else:
            article_title = None
        # 提取文章内容
        content_pattern = re.compile(r'<div class="content" id="newspapercontent">(.*?)</div>', re.DOTALL)
        content_match = content_pattern.search(response)
        article_content = content_match.group(1).strip() if content_match else None
        # 除去内容中的HTML标签
        if article_content:
            article_content = re.sub(r'<[^>]+>', '', article_content)
            article_content = article_content.replace('&nbsp;', '').replace('&ldquo;', '').replace('&rdquo;', '')
        # 作者
        author_match = re.findall(r'<div class="reporter">(.*?)</div>', response, re.DOTALL)
        author_name = author_match[0].replace('\n', '').strip() if author_match else None
        # 发布日期
        # 从URL中提取发布日期
        url_date_pattern = re.compile(r'/(\d{4}-\d{2}/\d{2})/')
        url_date_match = url_date_pattern.search(details[0])
        if url_date_match:
            publish_date_str = url_date_match.group(1)
            publish_date = datetime.strptime(publish_date_str, '%Y-%m/%d')
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


if __name__ == '__main__':
    nshw = chinanshw()
    dates_url = nshw.generate_dates(nshw.start_year, nshw.start_month, nshw.start_day, nshw.end_year, nshw.end_month, nshw.end_day)
    for date in dates_url:
        detail_list = []  # 存储每日所有篇章的详细参数
        branches = nshw.get_branches(date)
        for branch in branches:
            details = nshw.get_detailed_urls(branch)
            detail_list.extend(details)
        # 多线程处理
        logger.debug(f"成功生成{date}的所有篇章的详细链接，共计{len(detail_list)}篇")
        with ThreadPoolExecutor(max_workers=nshw.max_workers) as executor:
            results = executor.map(nshw.get_data, detail_list)
            try:
                for result in results:
                    if result is None:
                        logger.warning(f"Data is None for a certain url in {detail_list}, continue to the next one.")
                        continue
                    print(result)
                    # nshw.save_data(result)
            except Exception as e:
                logger.error(f"多线程出现异常: {e}")
        time.sleep(1)
            


