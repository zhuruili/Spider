# Spider

![language](https://img.shields.io/badge/language-Python-blue)
![license](https://img.shields.io/badge/License-MIT-red)

This repository records the simple code snippets I coded during my learning of web crawling techniques.Some simple crawler code will be updated from time to time, I hope it can help you，good luck！

仓库记录着我在学习爬虫技术过程中留下的简单代码段。会不定时更新，希望能帮到你。

---

## 文件说明

- [**SimPrograms**](https://github.com/zhuruili/Spider/tree/main/SimPrograms)  
  记录自己学习爬虫所留下的简单程序，该文件夹下的爬虫程序的特点是'简单'，基本上都是一个Python文件直接运行即可。
- [**Spi_DataSave**](https://github.com/zhuruili/Spider/tree/main/Spi_DataSave)  
  保存部分爬取的内容，体量比较小的数据集我会同步到仓库，如有需要可以直接下载。
- [**Projects**](https://github.com/zhuruili/Spider/tree/main/Spi_DataSave)  
  可能会上传一些小项目，主要有关爬取完数据之后对数据的处理。

## 内容目录

### SimPrograms

- [urllib模拟登陆](https://github.com/zhuruili/Spider/blob/main/SimPrograms/package_urllib.py)  
  使用`urllib`简单模拟发送请求与登陆
- [NBA球员top50](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_NBA.py)  
  基于`requests`获取数据，使用`xpath`表达式提取数据
- [当当网好评榜Top200](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_dangdang.py)  
  基于`requests`获取数据，使用正则表达式（`re`）提取数据并保存到文本文件
- [经济日报全站爬虫](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_EconomicDaily.py)  
  对经济日报站点的全方位信息收集，基于`requests`与`re`，层层深入
- [b站视频信息](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_bilibili_rsc.py)  
  基于`DrissionPage`实现自动化数据抓取，仅抓取搜索视频后看到的视频信息
- [MOOC视频信息](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_MOOC_rsc.py)  
  程序与‘b站视频信息’爬取程序类似，同样是一个基于`DrissionPage`实现的简单Demo。
- [JD商品评论自动化爬取](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_JD_comments.py)  
  本爬虫项目和先前的简单例子有些区别。首先是它做了翻页的适配。其次是通过提前手动登录的方式解决登陆/验证码等问题，随后再使用代码接管浏览器，不过这需要配置浏览器所占用的端口号
- [某宝商品数据自动化采集](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_Taobao.py)  
  同样有翻页的适配，不过采取的是程序登陆，不过实测这样的效果似乎并不太好 -_-

### DataSaved

仓库中所保存的程序爬取所得到的数据集可能会随时变动，因此就不在此处列表展示了，感兴趣的话可以直接到存放数据集的文件夹下查看其具体内容。

---

> [!Important]
> 注意：仓库代码仅供学习交流使用，不可用于非法用途！
