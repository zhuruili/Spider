# 自动化抓取淘宝商品数据
# 如果发现代码运行不了了很正常，因为某宝经常更新，但一般稍微修改一下应该就能过关
from DrissionPage import ChromiumPage
import time
import random
import re
import json
from DataRecorder import Recorder

# 参数设置
USERNAME = "your username"  
PASSWORD = "your pwd"
SearchItem = input("请输入您想要的商品名称：")  # 搜索的商品名称
json_data = {}  # 存放数据
SaveOrNot = True  # 是否保存数据,如果不保存就填False
SAVEPATH = "Spi_DataSave"  # 数据保存路径
data_list = []  # 存放待保存数据
Pages = 5  # 爬取页数

# 功能函数
def random_sleep():
    """小睡一下"""
    time.sleep(random.randint(1, 3))  # 随机等待

def login():
    """登录"""
    cp.ele('css:# fm-login-id').clear()  # 清空用户名输入框
    random_sleep()
    cp.ele('css:# fm-login-id').input(USERNAME)  # 输入用户名
    cp.ele('css:# fm-login-password').input(PASSWORD)  # 输入密码
    random_sleep()
    try:
        cp.ele('css:.fm-button.fm-submit.password-login.ariatheme',timeout=1).click()  # 点击登录按钮
    except:
        cp.ele('css:.fm-button.fm-submit.password-login').click()
    random_sleep()

def Search(item):
    """搜索"""
    random_sleep()
    cp.ele('# q').input(SearchItem)  # 输入搜索内容
    random_sleep()
    cp.ele('css:.btn-search.tb-bg').click()  # 点击搜索按钮
    random_sleep()

def get_data(resp):
    """提取数据,返回json数据"""
    try:
        resp_re = re.findall(pattern=' mtopjsonp[a-z]+\d+\((.*)\)',string=resp)[0]  # 使用正则提取json数据
        # print(resp_re)
    except:
        print("正则第一次匹配失败，尝试第二次匹配......")
        try:
            resp_re = re.findall(pattern=' mtopjsonp\d+\((.*)\)',string=resp)[0]  # 使用正则提取json数据
            # print(resp_re) 
        except:
            print("正则第二次匹配失败，网站或已更新，请手动调整正则表达式")

    json_data = json.loads(resp_re)  # 转换json数据
    return json_data

def get_items(json_data):
    """解析json数据"""
    data_list.clear()  # 清空数据,防止重复
    itemArr = json_data['data']['itemsArray']
    for item in itemArr:
        title = item['title']
        price = item['price']
        nick = item['nick']
        sale = item['realSales']
        # 还可以增加更多数据，这里我懒得写了
        print(f'商品名称：{title}，价格：{price}，店铺：{nick},销量：{sale}')
        data_list.append([title,price,nick,sale])

def save_data(data_list,page):
    """保存数据"""
    if SaveOrNot:
        FilePath = SAVEPATH + "\\" + SearchItem + ".xlsx"  
        r = Recorder(FilePath)
        if page == 0:
            r.add_data(['商品名称','价格','店铺','销量'])
        r.add_data(data_list)
        r.record()
        print("数据已保存")
    else:
        print("数据未保存")

if __name__ == "__main__":
    cp = ChromiumPage()  # 打开浏览器

    cp.get('https://www.taobao.com/')  # 打开淘宝首页

    cp.listen.start('h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0')  # 启动监听
    Search(SearchItem)  # 搜索商品
    
    try:
        login()  # 这里我发现一个很神奇的事情是即使我之前登陆过了但有时运行这个代码淘宝还是会让我重新登陆，或许是反爬机制？
    except:
        print("账户已登陆，无需重复登陆")
    for p in range(Pages):
        print(f"------**正在爬取第{p+1}页数据**------")
        resp = cp.listen.wait()  # 等待监听响应
        # print(resp._raw_body)  # 输出响应，观察结构方便后续数据提取
        resp = resp._raw_body  
        json_data = get_data(resp)  # 提取数据
        # print(json_data)
        get_items(json_data)  # 解析数据

        save_data(data_list,p)  # 保存数据
        random_sleep()
        cp.ele('css:.next-icon.next-icon-arrow-right.next-xs.next-btn-icon.next-icon-last.next-pagination-icon-next',timeout=1).click()  # 点击下一页
        print(f"------**第{p+1}页数据爬取完毕**------")

    print("------**Spider Done**------")