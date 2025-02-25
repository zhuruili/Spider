import requests
import re
import os

def request_dangdang(url):
    """请求网页"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None
    
def parse_result(html):
    """解析得到的网页源代码"""
    # 如果网站源码更新，此处的正则表达式可能需要更新
    pattern = re.compile(
    r'<li.*?list_num.*?(\d+).</div>.*?<img src="(.*?)".*?class="name".*?title="(.*?)">.*?class="star">.*?class="tuijian">(.*?)</span>.*?class="publisher_info">.*?target="_blank">(.*?)</a>.*?class="biaosheng">.*?<span>(.*?)</span></div>.*?<p><span class="price_n">&yen;(.*?)</span>.*?</li>',
    re.S
    )
    items = re.findall(pattern=pattern, string=html)
    for item in items:
        yield {
            'range': item[0],
            'image': item[1],
            'title': item[2],
            'recommend': item[3],
            'author': item[4],
            'times': item[5],
            'price': item[6]
        }  # 生成器，逐个返回数据，节省内存

def write_to_file(item):
    """以文件形式保存数据"""
    directory = 'Spi_DataSave'
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(os.path.join(directory, 'dangdang.txt'), 'a', encoding='utf-8') as f:
        f.write('range: ' + item['range'] + '\n')
        f.write('image: ' + item['image'] + '\n')
        f.write('title: ' + item['title'] + '\n')
        f.write('recommend: ' + item['recommend'] + '\n')
        f.write('author: ' + item['author'] + '\n')
        f.write('times: ' + item['times'] + '\n')
        f.write('price: ' + item['price'] + '\n\n')

if __name__ == '__main__':
    page = 5  # 页数
    for i in range(page):
        print('第%d页' % (i + 1))
        url = 'http://bang.dangdang.com/books/fivestars/01.00.00.00.00.00-recent30-0-0-1-' + str(page)
        html = request_dangdang(url)
        items = parse_result(html)
        for item in items:
            write_to_file(item)
            print(item)
    print("Done!")
