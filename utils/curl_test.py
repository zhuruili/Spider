"""
# 说明
- 用于测试请求过程中究竟是哪个参数导致了请求失败
"""

import requests

cookies = {
    "YOUR_COOKIE": "",
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    # 'if-modified-since': 'Mon, 20 Nov 2023 06:26:03 GMT',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

response = requests.get('https://epaper.yzwb.net/pc/layout/202101/02/node_A01.html', cookies=cookies, headers=headers)

# 自动解码
response.encoding = response.apparent_encoding
print(response.text)
print(response.status_code)