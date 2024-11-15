# Spider

![language](https://img.shields.io/badge/language-Python-blue)
![license](https://img.shields.io/badge/License-MIT-red)
![package](https://img.shields.io/badge/package-requests|DrissionPage-orange)

This repository records the simple code snippets I coded during my learning of web crawling techniques.Some simple crawler code will be updated from time to time, I hope it can help you，good luck！

仓库记录着我在学习爬虫技术过程中留下的简单代码段。会不定时更新，希望能帮到你。

---

## 相关文件说明

- [**SimPrograms**](https://github.com/zhuruili/Spider/tree/main/SimPrograms)  
  记录自己学习爬虫所留下的简单程序，该文件夹下的爬虫程序的特点是'简单'，基本上都是一个Python文件直接运行即可。
- [**Spi_DataSave**](https://github.com/zhuruili/Spider/tree/main/Spi_DataSave)  
  保存部分爬取的内容，体量比较小的数据集我会同步到仓库，如有需要可以直接下载。

## 内容目录

### SimPrograms

- [NBA球员top50](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_NBA.py)  
  NBA 球员top50数据--文件：spi_NBA.py。基于requests获取数据，使用xpath表达式提取数据。代码结构很清晰也比较短，适合新手学习。
- [b站视频信息](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_bilibili_rsc.py)  
  哔哩哔哩视频信息自动化爬取--文件：spi_bilibili_rsc.py。基于DrissionPage实现自动化数据抓取，只是一个很简单的Demo抓取的内容也只是搜索视频后看到的推送内容。
- [MOOC视频信息](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_MOOC_rsc.py)  
  MOOC视频信息爬取--文件：spi_MOOC_rsc.py。程序与‘b站视频信息’爬取程序类似，同样是一个基于DrissionPage实现的简单Demo。
- [JD商品评论自动化爬取](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_JD_comments.py)  
  JD商品评论自动化爬取--文件：spi_JD_comments.py。本爬虫项目和先前的简单例子有些区别。首先是它做了翻页的适配，实测JD商品评论最大加载量是100页，本程序几乎能够从头翻到尾。其次是通过提前手动登录的方式解决登陆/验证码等问题，随后再使用代码接管浏览器，不过这需要配置浏览器所占用的端口号。
- [某宝商品数据自动化采集](https://github.com/zhuruili/Spider/blob/main/SimPrograms/spi_Taobao.py)  
  某宝商品数据自动化采集--文件：spi_Taobao.py。同样有翻页的适配，不过采取的是程序登陆，不过实测这样的效果似乎并不太好-_-。

### DataSaved

仓库中所保存的程序爬取所得到的数据集可能会随时变动，因此就不在此处列表展示了，感兴趣的话可以直接到存放数据集的文件夹下查看其具体内容。

---

> [!Important]
> 注意：仓库代码仅供学习交流使用，不可用于非法用途！
