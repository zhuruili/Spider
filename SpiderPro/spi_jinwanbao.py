import requests
import re
import time
import pymysql
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from datetime import datetime, timedelta

from loguru import logger

class JinWanBao:
    """
    今晚报爬虫
    示例网站：http://jinwanbaoepaper.enorth.com.cn/jwb/html/2024-09/20/node_1.htm?v=1
    """
    def __init__(self):
        # 存入数据库时不变的字段
        self.init_db_fields()

        # 参数设置
        self.start_year = 2023
        self.end_year = 2025
        self.start_month = 6
        self.end_month = 3
        self.start_day = 1
        self.end_day = 19
        self.url_prefix = "http://jinwanbaoepaper.enorth.com.cn/jwb/html/"
        self.url_suffix_default = "node_1.htm?v=1"
        
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
        self.web_domain = "jinwanbaoepaper.enorth.com.cn"
        self.chinese_domain = "今晚报"
        self.level_column_2 = None  # 文章二级栏目
        self.attachment_url = None  # 附件链接
        self.source = "今晚报"  #  文章来源（Part）

    def init_params(self):
        """
        初始化请求参数
        """
        self.headers = {
            
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
        url示例：https://msb.zjol.com.cn/html/2025-03/08/node_199.htm
        """
        urls = []
        current_date = datetime(start_year, start_month, start_day)
        end_date = datetime(end_year, end_month, end_day)

        while current_date <= end_date:
            url = f"{self.url_prefix}{current_date.strftime('%Y-%m/%d')}/{self.url_suffix_default}"
            urls.append(url)
            current_date += timedelta(days=1)

        logger.info(f"起始日期：{start_year}-{start_month}-{start_day}，结束日期：{end_year}-{end_month}-{end_day}，共计{len(urls)}天")

        return urls
        
    def check_url(self, url, retry=3, timeout=2):
        """
        检查url是否有效，如果失败自动重试
        :param url: 需要检查的url
        :param retry: 重试次数
        :param timeout: 超时时间
        :return: True or False
        """
        for attempt in range(retry):
            try:
                response = self.session.get(url, timeout=timeout)
                if response.status_code == 200:
                    return True
                elif response.status_code == 404:
                    logger.debug(f"{url} is not found. Status code: {response.status_code}")
                    return False
                else:
                    logger.error(f"{url} is invalid. Status code: {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}. Error: {e}")
                time.sleep(2)  # 等待2秒后重试
        # 如果所有尝试都失败，将URL保存到文件
        with open('Logs/failed_day_urls.txt', 'a') as f:
            f.write(f"{url}\n")
        logger.debug(f"All attempts failed for {url}. URL saved to failed_urls.txt")
        return False

    def get_urls_for_every_branch(self, url, retry=3, timeout=2):
        """
        根据传入的`每日url`生成`每日各版面url`列表
        :param url: 每日url
        :param retry: 重试次数
        :param timeout: 超时时间
        :return: 每日各版面url列表
        版面链接形如：https://qjwb.thehour.cn/html/2009-01/02/node_79.htm
        """
        for attempt in range(retry):
            try:
                response = self.session.get(url, timeout=timeout)
                if response.status_code == 200:
                    response.encoding = "utf-8"
                    page_content = response.text
                    pattern = re.compile(r'<a class="rigth_bmdh_href" href="(node_\d+\.htm)">', re.DOTALL)
                    matches = pattern.findall(page_content)
                    # 构造匹配得到的的版面链接
                    full_branch_urls = [url.rsplit('/', 1)[0] + '/' + match for match in matches]

                    # 添加第一版面链接
                    # full_branch_urls.insert(0, url)

                    logger.success(f"成功生成{url}的所有版面链接，共计{len(full_branch_urls)}个")
                    return full_branch_urls
                else:
                    logger.error(f"Failed to get branches from {url}. Status code: {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}. Error: {e}")
                time.sleep(2)  # 等待2秒后重试

        # 如果所有尝试都失败，将URL保存到文件
        with open('Logs/failed_branch_urls.txt', 'a') as f:
            f.write(f"{url}\n")
        logger.error(f"All attempts failed for {url}. URL saved to failed_branch_urls.txt")
        return []

    def get_detailed_urls(self, url, retry=3, timeout=2):
        """
        获取每日各版面的所有篇章的详细链接
        :param url: 每日各版面url
        :param retry: 重试次数
        :param timeout: 超时时间
        :return: 该面板的所有篇章的详细链接列表
        详细链接形如：https://qjwb.thehour.cn/html/2009-01/02/content_4299704.htm
        """
        for attempt in range(retry):
            try:
                response = self.session.get(url, timeout=timeout)
                if response.status_code == 200:
                    response.encoding = "utf-8"
                    page_content = response.text
                    pattern = re.compile(r'<td class="default" valign="top".*?<a href="(content_\d+_\d+\.htm)"', re.DOTALL)
                    matches = pattern.findall(page_content)
                    
                    full_detailed_urls = [f"{url.rsplit('/', 1)[0]}/{match}" for match in matches]

                    # 得到当前的版面名称<span id="NewsEditionName">城事</span>
                    edition_name_pattern = re.compile(r'<span id="NewsEditionName">(.*?)</span>', re.DOTALL)
                    edition_name_match = edition_name_pattern.search(page_content)
                    if edition_name_match:
                        edition_name = edition_name_match.group(1).strip()
                    else:
                        edition_name = None

                    logger.success(f"成功生成{url}的所有篇章的详细链接，共计{len(full_detailed_urls)}篇")
                    return full_detailed_urls, edition_name
                else:
                    logger.error(f"Failed to get detailed urls from {url}. Status code: {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}. Error: {e}")
                time.sleep(2)  # 等待2秒后重试

        # 如果所有尝试都失败，将URL保存到文件
        with open('Logs/failed_detailed_urls.txt', 'a') as f:
            f.write(f"{url}\n")
        logger.error(f"All attempts failed for {url}. URL saved to failed_detailed_urls.txt")
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
                else:
                    logger.error(f"Failed to retrieve the page: {url}")
            except Exception as e:
                print(f"Failed to retrieve the page: {url}")
                print(f"Error: {e}")
        return None

    def get_data(self, url, branch_name=None):
        """
        获取每篇文章的具体数据
        :param url: 文章的url
        :return: 文章的数据
        示例url：http://jinwanbaoepaper.enorth.com.cn/jwb/html/2025-03/19/content_87647_1969088.htm
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
        # 一、二级栏目
        level_column_1 = branch_name
        level_column_2 = self.level_column_2
        # 版次当前版： 04版
        level_column_1_page = re.findall(r'当前版.*?(\d+)版', response, re.DOTALL)[0] if re.findall(r'当前版.*?(\d+)版', response, re.DOTALL) else None
        article_url = url
        # 提取文章标题
        title_matches = re.findall(r'<!--<npm:article-title>-->(.*?)<!--</npm:article-title>-->', response, re.DOTALL)
        article_title = title_matches[0].replace('\n', '').strip() if title_matches else None
        # 去除标题中的HTML标签
        if article_title:
            article_title = re.sub(r'<[^>]+>', '', article_title)
        # 提取文章内容
        content_pattern = re.compile(r'<!--<npm:article-content>-->(.*?)<!--</npm:article-content>-->', re.DOTALL)
        content_match = content_pattern.search(response)
        article_content = content_match.group(1).strip() if content_match else None
        # 除去内容中的HTML标签
        if article_content:
            article_content = re.sub(r'<[^>]+>', '', article_content)
            article_content = article_content.replace('&nbsp;', '')
        # 作者
        author_match = re.findall(r'<!--<npm:article-author>-->(.*?)<!--</npm:article-author>-->', response, re.DOTALL)
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
    jwb = JinWanBao()
    every_day_urls = jwb.generate_urls(
        jwb.start_year, jwb.start_month, jwb.start_day, 
        jwb.end_year, jwb.end_month, jwb.end_day
        )
    for every_day_url in every_day_urls:
        if jwb.check_url(every_day_url):
            branches = jwb.get_urls_for_every_branch(every_day_url)
            for branch in branches:
                detail_list = set()  # 存储每版面所有篇章的详细链接
                details, branch_name = jwb.get_detailed_urls(branch)
                detail_list.update(details)
                # 多线程处理
                logger.debug(f"成功生成{branch}的所有篇章的详细链接，共计{len(detail_list)}篇")
                with ThreadPoolExecutor(max_workers=jwb.max_workers) as executor:
                    results = executor.map(partial(jwb.get_data, branch_name=branch_name), detail_list)
                    try:
                        for result in results:
                            if result is None:
                                logger.warning(f"Data is None for a certain url in {detail_list}, continue to the next one.")
                                continue
                            print(result)
                            # jwb.save_data(result)
                    except Exception as e:
                        logger.error(f"多线程出现异常: {e}")
                time.sleep(1)
            


