# 最后测试于2024/11/12，代码依旧能奏效，只不过b站的页面结构发生了一定变化导致每个数据项的内容量不相等了

from DrissionPage import WebPage
from DrissionPage import ChromiumOptions

# 数据容器
data = {}  # 存放最终生成的字典
json_data = {}  # 存放最终生成的json数据

# 功能函数
def search(item, wp):
    """搜索"""
    wp.ele('css:.nav-search-input').input(item)  # 输入搜索内容
    #wp.wait.load_start()  # 等待页面加载完成
    wp.ele('css:.nav-search-btn').click()  # 点击搜索按钮

def mode_switch(wp):
    """切换模式"""
    wp.change_mode()

def get_data(data,wp,SearchItem):
    """
    1.提取数据
    2.填充数据
    3.数据检测
    4.格式转换
    5.数据返回
    """
    wp.get(f'https://search.bilibili.com/all?keyword={SearchItem}&from_source=webtop_search&spm_id_from=333.1007&search_source=3')
    # 数据共有项
    titles_B = wp.eles('x://div/div[@class="bili-video-card__info--right"]/a//attribute::title')
    links_B = wp.eles('x://div[@class="bili-video-card__info--right"]/a/@href')
    authors_B = wp.eles('x://div[@class="bili-video-card__info--right"]/p/a/span[@class="bili-video-card__info--author"]/text()')
    pics_B = wp.eles('x://div[@class="bili-video-card__image--wrap"]/picture//@src')
    views_B = wp.eles('x://div[@class="bili-video-card__stats--left"]/span[1]/span/text()')
    # 可能缺失项
    dates_B = wp.eles('x://div[@class="bili-video-card__info--right"]/p/a/span[@class="bili-video-card__info--date"]/text()')
    durations_B = wp.eles('x://span[@class="bili-video-card__stats__duration"]/text()')

    print(f'Bilibili->数据规模--标题数：{len(titles_B)}，图片数：{len(pics_B)}，作者数：{len(authors_B)}，播放量数：{len(views_B)}，日期数：{len(dates_B)}，时长数：{len(durations_B)}，链接数：{len(links_B)}')
    # 经过测试发现bilibili课程数据存在广告，而广告数据存在数据项缺失的情况，因此需要手动补充

    # 缺省数据填充
    if len(dates_B) < len(titles_B):
        dates_B += [''] * (len(titles_B) - len(dates_B))
    if len(durations_B) < len(titles_B):
        durations_B += [''] * (len(titles_B) - len(durations_B))

    # 数据检测
    # assert len(titles_B) == len(pics_B) == len(authors_B) == len(views_B) == len(dates_B) == len(durations_B) == len(links_B), '数据长度不一致！'

    # 格式转换：list->dict
    data = {
            'list':[
                {
                'title':tiele,
                'pic':pic,
                'author':author,
                'link':link,
                'view':view,
                'date':date,
                'duration':duration
                }
                for tiele,pic,author,link,view,date,duration in zip(titles_B[:18],pics_B[:18],authors_B[:18],links_B[:18],views_B[:18],dates_B[:18],durations_B[:18])
            ]
    }
    # 数据返回
    return data

# API
def API(item):
    """API"""
    wp_bilibili = WebPage()
    global data,json_data

    wp_bilibili.get("https://www.bilibili.com/")

    search(item=item,wp=wp_bilibili)

    mode_switch(wp=wp_bilibili)

    data = get_data(data=data,wp=wp_bilibili,SearchItem=item)
    # print(data)  # 打印字典数据

    wp_bilibili.close()

    return data # 返回给主程序的字典数据

if __name__ == "__main__":
    item = input('请输入视频名称：')
    print(API(item=item))


    