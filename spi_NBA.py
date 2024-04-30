#This program is designed to get the top50 NBA players'data
#结构非常简单的爬虫程序，适合新手学习
#可以用来复习xpath的使用

import requests
from lxml import etree

#fake headers
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

#target url
url = 'https://nba.hupu.com/stats/players'  #几乎没有反爬措施，对新手很友好

#send requests
resp = requests.get(url,headers=headers)

#data processing with xpath
e = etree.HTML(resp.text)
nums = e.xpath('//table[@class="players_table"]//tr/td[1]/text()')
names = e.xpath('//table[@class="players_table"]//tr/td[2]/a/text()')
teams = e.xpath('//table[@class="players_table"]//tr/td[3]/a/text()')
scores = e.xpath('//table[@class="players_table"]//tr/td[4]/text()')

#save data
print('Spider process for NBA data successfully completed!\nPlease go and check your file!')
with open('Novice\spider\Spi_DataSave\spi_NBA.text','w+',encoding='utf-8') as f:
    for num,name,team,score in zip(nums[1:],names,teams,scores[1:]):
        f.write(f'top{num}: {name} form {team} score:{score}\n')
print('File writting completed\nfilename:spi_NBA')
