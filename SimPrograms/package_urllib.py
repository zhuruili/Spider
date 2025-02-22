import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import ssl

ssl._create_default_https_context = ssl._create_unverified_context  # 全局取消证书验证

def test_get():
    """向百度发送请求，获取网页源代码"""
    url_baidu = 'http://www.baidu.com'
    response = urllib.request.urlopen(url_baidu)
    print(response.read().decode('utf-8'))

def test_post():
    """模拟登录`ChinaUnix`论坛"""
    url = 'http://account.chinaunix.net/login/login'
    data = {
        'username': 'YOUR_USERNAME',
        'password': 'YOUR_PASSWORD',
    }
    postdata = urllib.parse.urlencode(data).encode('utf-8')  # 将字典转换为url编码的字符串，并转换为bytes类型
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
    }

    request = urllib.request.Request(url=url, data=postdata, headers=headers)
    cjar = http.cookiejar.CookieJar()  # 创建cookie容器, 用于存放cookie
    cookie = urllib.request.HTTPCookieProcessor(cjar)  # 创建cookie处理器
    opener = urllib.request.build_opener(cookie)  # 创建opener
    urllib.request.install_opener(opener)  # 安装opener，全局生效，后续使用`urllib.request.urlopen`发送请求时，会自动携带cookie

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.reason)

    fhandle = open('./test.html', 'wb')
    fhandle.write(response.read())
    fhandle.close()


if __name__ == '__main__':
    test_get()
    test_post()