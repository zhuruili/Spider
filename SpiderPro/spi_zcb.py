import sys
sys.path.append('D:\\helloworld_python\\Rookie\\Programs\\Spider\\utils')

import requests
import json
import time
import pymysql
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from loguru import logger

from format_scripts import Remove_HTML

class ZhengCaiBao:
    """
    中国政府采购报爬虫
    示例网站：http://114.118.9.73:81/zcb/epaper/
    """
    def __init__(self):
        # 存入数据库时不变的字段
        self.init_db_fields()

        # 参数设置
        self.main_url = 'http://114.118.9.73:81/zcb/epaper/'
        self.getDate_link = 'http://114.118.9.73:81/reader/layout/getSZBDate.do'  # 日级接口
        self.findBm_link = 'http://114.118.9.73:81/reader/layout/findBmMenu.do'  # 版面接口
        self.getDetail_link = 'http://114.118.9.73:81/reader/layout/getBmDetail.do'  # 详情接口
        self.Data_link = 'http://114.118.9.73:81/reader/layout/detailData.do'  # 数据接口
        self.start_year = 2019
        self.start_month = 4
        self.end_year = 2025
        self.end_month = 2
        self.url_pre = 'http://114.118.9.73:81/zcb/epaper/index.html?'

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
        self.web_domain = "114.118.9.73:81/zcb/epaper/"
        self.chinese_domain = "中国政府采购报"
        self.level_column_1 = None
        self.level_column_2 = None  # 文章二级栏目
        self.attachment_url = None  # 附件链接
        self.source = "中国政府采购报"  #  文章来源（Part）

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

    def generate_date_list(self, start_year, start_month, end_year, end_month):
        """
        访问日级接口，获取日期集合
        :param start_year: 开始年份
        :param start_month: 开始月份
        :param end_year: 结束年份
        :param end_month: 结束月份
        :return: 日期集合
        """
        # 根据起止时间生成请求表单中的日期参数`sj`对应的值，形如`2025-3`
        sj_list = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if year == start_year and month < start_month:
                    continue
                if year == end_year and month > end_month:
                    break
                sj_list.append(f"{year}-{month}")
        # 请求接口，获取日期列表
        date_sets = []
        for sj in sj_list:
            data = {
                'sj': sj
            }
            response = self.post_with_retry(self.getDate_link, data=data)
            json_response = json.loads(response)
            if response is None:
                logger.error(f"Data is None for sj: {sj}.")
                continue
            date_sets.extend(json_response)
            logger.success(f"成功获取日期集合，当前日期为{sj}，共计{len(json.loads(response))}天")
        # 输出日期信息并返回
        logger.debug(f"日期合计：{len(date_sets)}")
        return date_sets

    def get_branches(self, date):
        """
        根据日期集合获取每日各版面的链接
        :param date: 日期
        :return: 每日各版面的链接列表
        """
        # 把原本的日期格式转换为接口需要的格式
        date = date.replace('/', '')
        branches = []
        data = {
            'docPubTime': date
        }
        response = self.post_with_retry(self.findBm_link, data=data)
        json_response = json.loads(response)
        if response is None:
            logger.error(f"Data is None for date: {date}.")
            return []
        for item in json_response:
            branch = item['BC']
            branches.append(branch)

        logger.success(f"成功获取{date}的所有版面链接，共计{len(branches)}个")
        return branches

    def get_details(self, date, branch):
        """
        获取每个版面的详情列表
        :param date: 日期
        :param branch: 版面
        :return: 详情列表
        """
        data = {
            'bc': branch,
            'docpubtime': date
        }
        response = self.post_with_retry(self.getDetail_link, data=data)
        if response is None or not response.strip():
            logger.error(f"Data is None or empty for date: {date}, branch: {branch}.")
            return []
        try:
            json_response = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON for date: {date}, branch: {branch}. Error: {e}")
            return []
        details = []
        for item in json_response:
            detail = item['ZB_GUID']
            details.append(detail)

        logger.success(f"成功获取{date}的{branch}版面的所有文章链接，共计{len(details)}篇")
        return details

    def post_with_retry(self, url, data=None, retry=5, timeout=5):
        """
        使用POST方法获取指定url的内容，如果失败自动重试，合计请求5次
        :param url: 需要获取内容的url
        :param data: POST请求的表单数据
        :param retry: 重试次数
        :param timeout: 超时时间
        :return: 接口返回的内容
        """
        for i in range(retry):
            if i > 0:
                logger.warning(f"Retry {i}/{retry} times for {url}")
                time.sleep(2)
            try:
                response = self.session.post(url, data=data, timeout=timeout)
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding  # 自动检测编码
                    return response.text
                else:
                    logger.error(f"Failed to retrieve the page via POST: {url}. Status code: {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to retrieve the page via POST: {url}. Error: {e}")
        return None

    def get_data(self, guid):
        """
        获取详情页的数据
        :param guid: 详情页的guid
        :return: 数据
        """
        data = {
            'guid': guid
        }
        response = self.post_with_retry(self.Data_link, data=data)
        if response is None:
            logger.error(f"Data is None for url: {data}.The page may be empty or pictures.")
            return None
        json_response = json.loads(response)

        # 提取数据
        web_domain = self.web_domain  # 网站域名
        chinese_domain = self.chinese_domain  # 中文域名
        article_id = guid  # 文章ID
        level_column_1 = json_response['bm']  # 文章一级栏目
        level_column_1_page = json_response['bc']   # 文章一级栏目(编号)
        level_column_2 = self.level_column_2  # 文章二级栏目
        article_url = self.url_pre + f'guid={guid}'  # 文章链接
        article_title = Remove_HTML(json_response['docTitle'])  # 文章标题
        article_content = Remove_HTML(json_response['content'])  # 文章内容
        author_name = Remove_HTML(json_response['docAuthor'])  # 作者
        publish_date = datetime.strptime(json_response['docPubTime'], '%Y/%m/%d %H:%M:%S')  # 发布日期
        source = f"{self.source} {publish_date.strftime('%Y-%m-%d')} 第{level_column_1_page}版"  # 来源（拼接后的完整版）
        gettime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        attachment_url = self.attachment_url

        # 过滤内容为空的数据
        if article_content == '':
            logger.warning(f"Content is empty for {article_url}, continue to the next one.")
            return None

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
    zcb = ZhengCaiBao()
    date_list = zcb.generate_date_list(zcb.start_year, zcb.start_month, zcb.end_year, zcb.end_month)
    for date in date_list:
        details_for_date = []  # 每日所有篇章的详细链接
        branches = zcb.get_branches(date)
        for branch in branches:
            detail_list = zcb.get_details(date, branch)
            details_for_date.extend(detail_list)
        logger.debug(f"成功生成{date}的所有篇章的详细链接，共计{len(details_for_date)}篇")
        # 多线程处理
        with ThreadPoolExecutor(max_workers=zcb.max_workers) as executor:
            results = executor.map(zcb.get_data, details_for_date)
            try:
                for result in results:
                    if result is None:
                        continue
                    print(result)
                    # zcb.save_data(result)
            except Exception as e:
                logger.error(f"多线程出现异常: {e}")
        time.sleep(1)
            


