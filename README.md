# Spider

![language](https://img.shields.io/badge/language-Python-blue)
![license](https://img.shields.io/badge/License-MIT-red)

This repository records the simple code snippets I coded during my learning of web crawling techniques.Some simple crawler code will be updated from time to time, I hope it can help you，good luck！

仓库记录着我在学习爬虫技术过程中留下的简单代码段。会不定时更新，希望能帮到你。

---

## 文件说明

- [**SimPrograms**](https://github.com/zhuruili/Spider/tree/main/SimPrograms)  
  记录自己学习爬虫所留下的简单程序，该文件夹下的爬虫程序的特点是'简单'，基本上都是一个Python文件直接运行即可。
- [**SpiderPro**](https://github.com/zhuruili/Spider/tree/main/SpiderPro)  
  这部分内容对初学者来说会有一定难度，小白慎入。该文件夹下的爬虫程序是我在公司实习时候留下的相对简单的爬虫业务代码，基本上都是全站级别的数据采集，数据量大概在几万到几十万不等
- [**utils**](https://github.com/zhuruili/Spider/tree/main/utils)  
  做爬虫项目时可能用上的实用类工具代码
- [**Spi_DataSave**](https://github.com/zhuruili/Spider/tree/main/Spi_DataSave)  
  保存部分爬取的内容，体量比较小的数据集我会同步到仓库，如有需要可以直接下载。

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

### SpiderPro

- [光明日报全站采集](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_gmw.py)  
  基于`datetime`批量生成url、`requests`发送请求、`re`匹配内容、`pymysql`连接数据库并保存数据、`loguru`输出日志信息、`threading`与`ThreadPoolExecutor`控制多线程爬取、`time`控制休眠。本代码成功爬取了目标站点从2010年到2025年3月的全部内容，合计约36w条记录
- [中国教育报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_jyb.py)  
  中国教育报信息采集，整体上与`光明日报`项目类似，优化了部分代码细节
- [中国旅游报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_lyb.py)  
  在前两代报刊项目中发现了即使挂代理依旧存在网络错误导致数据缺失的问题。对此，本项目新增了对每日、每版次链接的访问重试，并增加了将多次重试请求依旧访问失败的链接保存到`Logs`下的日志文件的功能，方便项目跑完之后的数据校对与缺失填补
- [美术报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_msb.py)  
  和`中国旅游报`项目大体类似

> [!Note]
> 注意：这部分内容虽然是我在公司实习留下的代码，但是代码全程由我自己编写，并非公司向我提供，并且代码中所有有关公司的信息或者使用的资源均已被我移除，你可以放心的查看或学习其中的内容

### utils

- [请求测试](https://github.com/zhuruili/Spider/blob/main/utils/curl_test.py)  
  最原始而简单的请求代码，你可以在抓取你需要的数据包后通过复制该数据包的`Copy as cURL(bash)`到例如`Curl`或`Json`这类格式规范化网站来快速得到一个基本的请求模板，你可以通过注释来一步步检测究竟是什么参数导致了访问的失败，在本示例代码中是`if-modified-since`参数影响了访问导致返回`304`响应码
- [查漏补缺](https://github.com/zhuruili/Spider/blob/main/utils/LeakFilling.py)  
  在爬取大批量的数据时，即使你挂了代理，做了请求重试等多种措施，也依旧可能有缺漏的网页没访问到或者访问失败，你可以将这部分网页的链接保存，并使用这份工具文件快速解析你所保存的失败网页，并将结果输出在新的文件中，之后你只需要在生成的新文件中查找`200`的结果即可快速找到你之前项目中访问失败的链接中哪些其实仍然是可用的

### DataSaved

仓库中所保存的程序爬取所得到的数据集可能会随时变动，因此就不在此处列表展示了，感兴趣的话可以直接到存放数据集的文件夹下查看其具体内容。

---

> [!Important]
> 警告：仓库代码仅供学习交流使用，不可用于非法用途！
