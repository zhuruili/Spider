import sys
sys.path.append('D:\\helloworld_python\\Rookie\\Programs\\Spider\\utils')

import requests
import re
import json
import time
import pymysql
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from loguru import logger

from format_scripts import Remove_HTML


class ZhiLiangBao:
    """
    中国质量报爬虫
    示例网站：http://zgzlb.183read.cc/?y=2020&m=01&d=03
    """
    def __init__(self):
        # 存入数据库时不变的字段
        self.init_db_fields()

        # 参数设置
        self.main_url = 'http://zgzlb.183read.cc/'
        self.start_year = 2020
        self.start_month = 1
        self.start_day = 3
        self.content_url = 'http://zgzlb.183read.cc/art.html'

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
        self.web_domain = "zgzlb.183read.cc"
        self.chinese_domain = "中国质量报"
        self.level_column_2 = None
        self.attachment_url = None  # 附件链接
        self.source = "中国质量报"  #  文章来源（Part）

    def init_params(self):
        """
        初始化请求参数
        """
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 'Referer': 'http://zgzlb.183read.cc/?y=2022&m=01&d=07',
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

    def generate_date_list(self, start_year, start_month, start_day):
        """
        访问接口，获取日期集合
        :param start_year: 开始年份
        :param start_month: 开始月份
        :param start_day: 开始日期
        :return: 日期集合
        """
        # 根据起止时间生成请求表单形如{y: 2025 m: 01 d: 03}
        date_sets = []
        params = {
            'y': f"{start_year:04d}",
            'm': f"{start_month:02d}",
            'd': f"{start_day:02d}"
        }
        response = self.get_with_retry(self.main_url, params=params)
        if response is None:
            logger.error(f"Data is None for time request: {params}.")
            return []
        try:
            match = re.search(r"var dayList = JSON\.parse\('(\[.*?\])'\);", response)
            if match:
                json_data = match.group(1)
                day_list = json.loads(json_data)
                for item in day_list:
                    if "YM" in item:
                        date_sets.append(item["YM"])
        except Exception as e:
            logger.error(f"Failed to parse dates from response. Error: {e}")
            return []

        # 过滤掉日期早于指定日期的项
        date_sets = [date for date in date_sets if datetime.strptime(date, '%Y-%m-%d') >= datetime(start_year, start_month, start_day)]

        # 测试单日：2025-03-27
        # date_sets = ["2025-03-27"]

        logger.success(f"成功获取日期集合，共计{len(date_sets)}天")
        logger.debug(f"日期集合：{date_sets}")
        return date_sets

    def get_details(self, date):
        """
        根据日期集合获取每日各版面的链接
        :param date: 日期
        :return: 每日的所有详情链接列表
        """
        # 把原本的日期格式转换为接口需要的格式
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        params = {
            'y': f"{date_obj.year:04d}",
            'm': f"{date_obj.month:02d}",
            'd': f"{date_obj.day:02d}"
        }
        response = self.get_with_retry(self.main_url, params=params)
        if response is None:
            logger.error(f"Failed to retrieve details for date: {date}")
            return []

        # 使用正则表达式提取所有详情链接
        #  <a href="/art.html?id=959483&p=1390776634&mid=5821003">
        details = re.findall(r'<a href="(/art\.html\?id=\d+&p=\d+&mid=\d+)">', response)
        details = list(set(details))  # 去重
    
        logger.success(f"成功获取{date}的所有详情链接，共计{len(details)}个")
        return details

    def get_with_retry(self, url, params=None, retry=5, timeout=5):
        """
        使用GET方法获取指定url的内容，如果失败自动重试，合计请求5次
        :param url: 需要获取内容的url
        :param params: GET请求的参数
        :param retry: 重试次数
        :param timeout: 超时时间
        :return: 接口返回的内容
        """
        for i in range(retry):
            if i > 0:
                logger.warning(f"Retry {i}/{retry} times for {url}")
                time.sleep(2)
            try:
                response = self.session.get(url, params=params, timeout=timeout, verify=False)
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding  # 自动检测编码
                    return response.text
                else:
                    logger.error(f"Failed to retrieve the page via GET: {url}. Status code: {response.status_code}")
            except Exception as e:
                logger.error(f"Failed to retrieve the page via GET: {url}. Error: {e}")
        # 如果所有重试都失败，保存失败的url
        logger.error(f"Failed to retrieve the page via GET after {retry} attempts: {url}")
        with open('Logs/failed_urls.txt', 'a') as f:
            f.write(f"{url}\n")
        return None

    def get_data(self, raw_params):
        """
        获取详情页的数据
        :param raw_params: 详情页的请求参数(需要进一步处理)
        :return: 数据
        """
        # 处理参数，形如/art.html?id=969188&p=1390972946&mid=5955812，得到请求参数
        params = re.findall(r'id=(\d+)&p=(\d+)&mid=(\d+)', raw_params)
        if not params:
            logger.error(f"Failed to extract parameters from {raw_params}")
            return None
        params = {
            'id': params[0][0],
            'p': params[0][1],
            'mid': params[0][2]
        }

        response = self.get_with_retry(self.content_url, params=params)
        if response is None:
            logger.warning(f"Data is None for url: {params}.The page may be empty or pictures.")
            return None

        # 提取数据
        try:
            web_domain = self.web_domain  # 网站域名
            chinese_domain = self.chinese_domain  # 中文域名
            article_id = params['id'] + params['p'] + params['mid']  # 文章ID

            # <div class="lbox">01：头版            </div>
            # <div class="lbox">05：质量管理            </div>
            level_column_1_match = re.findall(r'<div class="lbox">\s*(\d+)：(.*?)\s*</div>', response, re.DOTALL)  # [('07', '品质&middot;消费')]
            if level_column_1_match:
                level_column_1_page = level_column_1_match[0][0]
                level_column_1 = Remove_HTML(level_column_1_match[0][1])
            else:
                level_column_1_page = None
                level_column_1 = None
                print(f"Failed to extract level_column_1 from {response}")

            level_column_2 = self.level_column_2  # 文章二级栏目
            article_url =  self.main_url + '?' + raw_params  # 文章链接
            article_title = Remove_HTML(re.findall(r'<title>(.*?)</title>', response)[0]) if re.findall(r'<title>(.*?)</title>', response) else None  # 文章标题


            # 文章内容
            # <font color = "#000000" face = "宋体"><b>　　本报讯 （记者 何可）</b>近日
            article_content = Remove_HTML(re.findall(r'<font color = "#000000" .*?>(.*?)</font.*?>', response)[0]) if re.findall(r'<font color = "#000000" .*?>(.*?)</font.*?>', response) else None  
            if article_content is None:
                # 如果第一遍匹配失败，适配另一种格式：<span style="color:#000000;font-family:宋体">
                article_content = Remove_HTML(re.findall(r'<span style="color:#000000;font-family:宋体">(.*?)</span>', response)[0]) if re.findall(r'<span style="color:#000000;font-family:宋体">(.*?)</span>', response) else None

            author_name = ''  # 作者
            # <li>2020年01月03日第6840期 星期五</li>
            publish_date =  datetime.strptime(re.findall(r'<li>.*?(\d+年\d+月\d+日).*?</li>', response)[0], '%Y年%m月%d日') if re.findall(r'<li>.*?(\d+年\d+月\d+日).*?</li>', response) else None  # 发布时间
            source = f"{self.source} {publish_date.strftime('%Y-%m-%d')} 第{level_column_1_page}版"  # 来源（拼接后的完整版）
            gettime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            attachment_url = self.attachment_url

        except Exception as e:
            logger.error(f"Failed to extract data from response. Error: {e}, URL: {article_url}")
            return None

        # 过滤内容为空的数据
        # if article_content == '':
        #     logger.warning(f"Content is empty for {article_url}, continue to the next one.")
        #     return None

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

    def check_and_log_missing_fields(self, result):
        """
        检查 result 中的特定字段是否为空或缺失，并记录日志
        :param result: 数据字典
        :return: 如果所有字段都完善，返回 True；否则返回 False
        """
        required_fields = [
            # "web_domain", 
            # "chinese_domain", 
            "article_id", 
            "level_column_1",
            "article_url", 
            "article_title", 
            # "content", 
            # "author_name",
            "source", 
            "publish_date"
        ]

        missing_fields = [field for field in required_fields if not result.get(field)]
        if missing_fields:
            # 记录日志
            logger.warning(f"数据缺失字段: {missing_fields}，文章链接: {result.get('article_url', '未知链接')}")

            # 保存到文件
            log_file_path = 'Logs/missing_fields.log'
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(f"缺失字段: {missing_fields}, 数据: {json.dumps(result, ensure_ascii=False)}\n")
            
            return False

        return True


if __name__ == '__main__':
    zlb = ZhiLiangBao()
    date_list = zlb.generate_date_list(zlb.start_year, zlb.start_month, zlb.start_day)
    for date in date_list:
        details_for_date = zlb.get_details(date)  # 获取每个日期的所有详情链接
        # 多线程处理
        with ThreadPoolExecutor(max_workers=zlb.max_workers) as executor:
            results = executor.map(zlb.get_data, details_for_date)
            try:
                for result in results:
                    # 检查数据并保存
                    if not zlb.check_and_log_missing_fields(result):
                        continue
                    # 保存数据
                    print(result)
                    # zlb.save_data(result)
            except Exception as e:
                logger.error(f"多线程出现异常: {e}")
        time.sleep(1)
            


