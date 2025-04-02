import requests
import re
import time
import pymysql
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from loguru import logger

class KePuShiBao:
    """
    科普时报爬虫
    示例网站：https://digitalpaper.stdaily.com/http_www.kjrb.com/kjwzb/html/2025-03/21/node_131.htm
    """
    def __init__(self):
        # 存入数据库时不变的字段
        self.init_db_fields()

        # 参数设置
        self.start_year = 2017
        self.end_year = 2025
        self.start_month = 1
        self.end_month = 3
        self.url_prefix = "https://digitalpaper.stdaily.com/http_www.kjrb.com/kjwzb/html/"
        self.url_suffix_default = "node_121.htm"
        self.xml_suffix = "period.xml"
        
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
        self.web_domain = "digitalpaper.stdaily.com"
        self.chinese_domain = "科普时报"
        self.level_column_2 = None  # 文章二级栏目
        self.attachment_url = None  # 附件链接
        self.source = "科普时报"  #  文章来源（Part）

    def init_params(self):
        """
        初始化请求参数
        """
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            # 'If-Modified-Since': 'Mon, 24 Mar 2025 08:28:21 GMT',
            # 'If-None-Match': 'W/"67e117a5-37b4"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
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

    def generate_dates(self, start_year, start_month, end_year, end_month):
        """
        根据传入的起始年月日和截至年月日生成期间的所有可用的日期列表
        :param start_year: 开始年份
        :param start_month: 开始月份
        :param end_year: 结束年份
        :param end_month: 结束月份
        :return: 日期列表
        获得日期列表的示例链接：https://digitalpaper.stdaily.com/http_www.kjrb.com/kjwzb/html/2025-03/period.xml
        """
        dates = []
        # 生成形如2025-03的日期
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if year == start_year and month < start_month:
                    continue
                if year == end_year and month > end_month:
                    break
                dates.append(f"{year}-{month:02}")
        # 访问接口得到可用日期 <period_date>2025-03-07</period_date>
        available_dates = []
        for date in dates:
            url = f"{self.url_prefix}{date}/{self.xml_suffix}"
            response = self.get_with_retry(url)
            if response is None:
                logger.warning(f"Data is None for url: {url}.The page may be empty or pictures.")
                continue
            pattern = re.compile(r'<period_date>(\d{4}-\d{2}-\d{2})</period_date>')
            matches = pattern.findall(response)
            available_dates.extend(matches)
            logger.success(f"成功生成{date}的所有可用日期列表，共计{len(matches)}天")
        
        logger.debug(f"成功生成{start_year}年{start_month}月至{end_year}年{end_month}月的所有可用日期列表，共计{len(available_dates)}天")

        return available_dates

    def get_branches(self, date):
        """
        :param date: 有效日期（\d{4}-\d{2}-\d{2}）
        :return: 每日各版面url列表
        版面链接形如：https://digitalpaper.stdaily.com/http_www.kjrb.com/kjwzb/html/2025-03/21/node_121.htm
        """
        # 将date从2025-03-21转换为形如2025-03/21的形式
        transformed_date = date.rsplit('-', 1)
        transformed_date = '/'.join(transformed_date)
        url = f"{self.url_prefix}{transformed_date}/{self.url_suffix_default}"
        response = self.get_with_retry(url)
        if response is None:
            logger.error(f"Data is None for url: {url}.The page may be empty or pictures.")
            return []
        # <a id=pageLink href=node_129.htm>第09版：博物天地</a></div>
        pattern = re.compile(r'<a id=pageLink href=(node_\d+\.htm)>')
        matches = pattern.findall(response)
        branches = [f"{url.rsplit('/', 1)[0]}/{match}" for match in matches]

        # 加入默认的第一页到列表第一个
        branches.insert(0, url)

        logger.success(f"成功生成{date}的所有版面链接，共计{len(branches)}个")

        return branches

    def get_detailed_urls(self, url):
        """
        获取每日各版面的所有篇章的详细链接
        :param url: 每日各版面url
        :return: 该面板的所有篇章的详细链接列表
        详细链接形如：https://digitalpaper.stdaily.com/http_www.kjrb.com/kjwzb/html/2025-03/21/content_586280.htm?div=-1
        """
        # <a href=content_586276.htm?div= -1>
        response = self.get_with_retry(url)
        if response is None:
            logger.error(f"Data is None for url: {url}.The page may be empty or pictures.")
            return []
        pattern = re.compile(r'<a href=(content_\d+\.htm\?div=-1)>')
        matches = pattern.findall(response)
        detailed_urls = [f"{url.rsplit('/', 1)[0]}/{match}" for match in matches]

        logger.success(f"成功生成{url}的所有篇章的详细链接，共计{len(detailed_urls)}篇")

        return detailed_urls

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

    def get_data(self, url):
        """
        获取每篇文章的具体数据
        :param url: 文章的url
        :return: 文章的数据
        示例url：https://qjwb.thehour.cn/html/2006-01/01/content_480070.htm
        """
        # 获取网页内容
        response = self.get_with_retry(url=url)
        if response is None:
            logger.error(f"Data is None for url: {url}.The page may be empty or pictures.")
            return None
        # 解析网页内容，规范化填入数据库的字段
        web_domain = self.web_domain
        chinese_domain = self.chinese_domain
        article_id = ''.join(re.findall(r'\d+', url))  # 以url中的数字作为文章id
        # 提取一级栏目和版次 第07版：<STRONG>数智潮流</STRONG>
        level_column_1_pattern = re.compile(r'第(\d+)版：<STRONG>(.*?)</STRONG>', re.DOTALL)
        level_column_1_match = level_column_1_pattern.search(response)
        if level_column_1_match:
            level_column_1 = level_column_1_match.group(2).strip()
            level_column_1_page = level_column_1_match.group(1).strip()
        else:
            level_column_1 = None
            level_column_1_page = None
        level_column_2 = self.level_column_2
        article_url = url
        # 提取文章标题
        title_matches = re.findall(r'<founder-title>(.*?)</founder-title>', response, re.DOTALL)
        if title_matches:
            if title_matches[0].strip() == "钱江晚报" and len(title_matches) > 1:
                article_title = title_matches[1].replace('\n', '').strip()
            else:
                article_title = title_matches[0].replace('\n', '').strip()
            if article_title:  # 除去标题中的HTML标签
                article_title = re.sub(r'<[^>]+>', '', article_title)
        else:
            article_title = None
        # 提取文章内容
        content_pattern = re.compile(r'<!--enpcontent-->(.*?)<!--/enpcontent-->', re.DOTALL)
        content_match = content_pattern.search(response)
        article_content = content_match.group(1).strip() if content_match else None
        # 除去内容中的HTML标签
        if article_content:
            article_content = re.sub(r'<[^>]+>', '', article_content)
            article_content = article_content.replace('&nbsp;', '')
        # 作者
        author_match = re.findall(r'<founder-author>(.*?)</founder-author>', response, re.DOTALL)
        author_name = author_match[0].replace('\n', '').strip() if author_match else None
        # 发布日期
        # 从URL中提取发布日期
        url_date_pattern = re.compile(r'/(\d{4}-\d{2}/\d{2})/')
        url_date_match = url_date_pattern.search(url)
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
    kpsb = KePuShiBao()
    available_dates = kpsb.generate_dates(kpsb.start_year, kpsb.start_month, kpsb.end_year, kpsb.end_month)
    for date in available_dates:
        detail_list = []  # 存储每日所有篇章的详细链接
        branches = kpsb.get_branches(date)
        for branch in branches:
            details = kpsb.get_detailed_urls(branch)
            detail_list.extend(details)
        # 多线程处理
        logger.debug(f"成功生成{date}的所有篇章的详细链接，共计{len(detail_list)}篇")
        with ThreadPoolExecutor(max_workers=kpsb.max_workers) as executor:
            results = executor.map(kpsb.get_data, detail_list)
            try:
                for result in results:
                    if result is None:
                        logger.warning(f"Data is None for a certain url in {detail_list}, continue to the next one.")
                        continue
                    print(result)
                    # kpsb.save_data(result)
            except Exception as e:
                logger.error(f"多线程出现异常: {e}")
        time.sleep(1)
            


