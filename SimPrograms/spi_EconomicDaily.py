import requests
import re

class EconomicDaily:
    def __init__(self):
        self.JournalName = "经济日报"

        self.start_year = 2021
        self.end_year = 2024
        self.start_month = 1
        self.end_month = 2
        self.url_prefix = "http://paper.ce.cn/pc/layout/"
        self.url_suffix_default = "node_01.html"

    def generate_dates_in_url(self, start_year, end_year, start_month, end_month):
        """
        根据传入的起止日期生成**url**中的日期列表
        :param start_year: 开始年份
        :param end_year: 结束年份
        :param start_month: 开始月份
        :param end_month: 结束月份
        :return: 日期列表
        日期示例：202502
        """
        dates = []
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                if (year == start_year and month < start_month) or (year == end_year and month > end_month):
                    continue
                dates.append(f"{year}{month:02d}")
        return dates

    def generate_url(self, dates):
        """
        根据传入的日期列表生成url列表
        :param dates: 日期列表
        :return: url列表
        url示例: http://paper.ce.cn/pc/layout/202502/20/node_01.html
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
            return False

    def get_kind_count(self, url):
        """
        获取每天的特定页面中的版面名称数量
        :param url: 特定页面的url
        :return: 版面名称数量
        """
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            pattern = re.compile(r'<li class="posRelative">\s*<a href="node_\d+\.html">.*?</a>\s*<input type="hidden" value=".*?\.pdf">\s*</li>', re.S)
            matches = pattern.findall(html)
            return len(matches)
        else:
            return 0

    def generate_urls_for_each_kind(self, url, kind_count):
        """
        根据默认的`url`与面板数量获取每个面板的url
        :param url: 默认的url
        :param kind_count: 版面数量
        :return: 每个面板的url列表
        """
        urls = []
        for i in range(1, kind_count + 1):
            url_with_unique_kind = url.replace("node_01", f"node_{i:02d}")
            urls.append(url_with_unique_kind)
        return urls

    def generate_urls_for_each_content(self, url):
        """
        根据每个版面的url获取每个版面的内容url列表
        :param url: 版面的url
        :return: 版面的内容url列表
        """
        response = requests.get(url)
        if response.status_code == 200:
            html = response.text
            pattern = re.compile(r'<li class="clearfix"><img src=".*?" /><a href="(.*?)">.*?</a></li>', re.S)
            matches = pattern.findall(html)
            content_urls = [f"http://paper.ce.cn/pc{match[8:]}" for match in matches]  # 拼接完整的内容URL
            #http://paper.ce.cn/pc/content/202101/12/content_218894.html
            return content_urls
        else:
            return []

    def get_data(self, url):
        """在这里自定义你想要的数据"""
        response = requests.get(url)
        response.encoding = 'utf-8'  # 设置编码格式为utf-8
        data = response.text

        return data




if __name__ == '__main__':
    economic_daily = EconomicDaily()
    dates = economic_daily.generate_dates_in_url(economic_daily.start_year, 
                                                 economic_daily.end_year,
                                                 economic_daily.start_month, 
                                                 economic_daily.end_month
                                                 )
    urls = economic_daily.generate_url(dates)
    for url in urls:
        if economic_daily.check_url(url):
            kind_count = economic_daily.get_kind_count(url)
            urls_for_each_kind = economic_daily.generate_urls_for_each_kind(url, kind_count)
            for url_for_each_kind in urls_for_each_kind:
                urls_for_each_content = economic_daily.generate_urls_for_each_content(url_for_each_kind)
                for url_for_each_content in urls_for_each_content:
                    html_body = economic_daily.get_data(url_for_each_content)
                    print(html_body)
                    pass
        else:
            print(f"{url} is invalid.")
