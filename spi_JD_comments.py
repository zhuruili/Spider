# env: python3.10.15
# JD商品评论自动化爬取
# Author: RookieNoob
# 最后测试于2024/11/13，代码依旧可以运行
"""
\\\\\\\\\\\\\\\WARNING////////////////
1. 本程序仅供学习交流使用,请勿用于商业用途
2. 如果想要运行程序，请确保你的电脑上已经安装了Chrome浏览器
3. 请确保参数设置中的端口号为您的电脑上运行Chrome浏览器的端口号
4. 运行本代码之前请先确定您已经登陆到JD并且不要关闭浏览器
"""
from DrissionPage import ChromiumPage

import time
import random

from DataRecorder import Recorder

# 参数设置
port = 9222 # 需要接管的浏览器端口
product_id = 100007000438 # 商品ID，可以更换成任意你想要的商品id
"""
100095622615 (手机)
100091011046 (笔记本电脑)
100007000438 (相机)
100047472554 (口红)
100015163135 (跑鞋)
100085026467 (电饭煲)
"""
pages = 100 # 最大页码（经过测试JD的评论最大加载似乎就是100页）
save_or_not = True # 是否保存数据
save_path = 'Spi_DataSave'
file_path = save_path + f'\\{product_id}.xlsx'  # 文件路径

# 数据容器
batch = [] # 批次数据

# Links
JD_link = 'https://www.jd.com/' # 京东首页
comments_link = f'https://item.jd.com/{product_id}.html#comment' # 评论链接

# 实例化
cp = ChromiumPage(addr_or_opts=port)  # 接管端口位于xxx的浏览器
r = Recorder(file_path) 

# 功能函数
def launch_browser():
    """打开页面与启动监听"""
    cp.get(JD_link)  # 打开京东首页
    cp.listen.start('appid=item-v3&functionId=pc_club_productPageComments&client=pc&clientVersion=1.0.0')
    cp.get(comments_link)  # 打开商品评论页面

def get_data():
    """数据获取"""
    resp = cp.listen.wait()  # 等待监听响应
    data = dict(resp.response.body)
    data = data['comments']
    return data

def pro(data:dict):
    """数据处理"""
    batch.clear()  # 清空数据,防止重复
    reply = '' # 回复
    for item in data:
        reply = '' # 清空回复
        id = str(item['id']) # id
        content = item['content'] # 评论内容
        creationTime = item['creationTime'] # 评论时间
        score = item['score'] # 星数
        try:
            imageCount = item['imageCount'] # 图片数
        except:
            imageCount = 0
        status = item['status'] 
        try:
            for i in range(len(item['replies'])):
                reply += f'{i}. {item["replies"][i]["content"]}'
        except:
            reply = '无回复'
        batch.append([id,content,creationTime,score,imageCount,status,reply])
    return batch


# 辅助函数
def random_sleep():
    """小睡一下"""
    time.sleep(random.randint(4, 6)/10)  # 随机等待


# 主程序
if __name__ == "__main__":
    print("------**Spider Start**------")
    launch_browser()
    for page in range(pages):
        if page == 0 & save_or_not:
            r.add_data(['id','content','creationTime','score','imageCount','status','reply'])
        print(f"------**正在爬取第{page+1}页数据**------")
        data = get_data()
        batch = pro(data)
        if save_or_not:
            r.add_data(batch)
            r.record()
        random_sleep()
        cp.ele('css:a.ui-pager-next',timeout=1).click()
        print(f"------**第{page+1}页数据爬取完毕**------")
    print("------**Spider Done**------")

    
