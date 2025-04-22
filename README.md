# Spider

![language](https://img.shields.io/badge/language-Python-blue)
![license](https://img.shields.io/badge/License-MIT-red)

This repository records the simple code snippets I coded during my learning of web crawling techniques.Some simple crawler code will be updated from time to time, I hope it can help you，good luck！

仓库记录着我在学习爬虫技术过程中留下的代码段。会不定时更新，希望能帮到你。

> [!Important]
> 警告：仓库代码仅供学习交流使用，不可用于非法用途！

---

## 文件说明

- [**SimPrograms**](https://github.com/zhuruili/Spider/tree/main/SimPrograms)  
  记录自己学习爬虫所留下的简单程序，该文件夹下的爬虫程序的特点是'简单'，基本上都是一个Python文件直接运行即可。
- [**SpiderPro**](https://github.com/zhuruili/Spider/tree/main/SpiderPro)  
  这部分内容对初学者来说会有一定难度，小白慎入。该文件夹下的爬虫程序是我在公司实习时候留下的相对简单的爬虫业务代码，基本上都是全站级别的数据采集，数据量大概在几万到几十万不等
- [**utils**](https://github.com/zhuruili/Spider/tree/main/utils)  
  做爬虫项目时可能用上的实用类工具代码
- [**tutorial**](https://github.com/zhuruili/Spider/tree/main/tutorial)  
  爬虫相关知识点的简明教程与知识补充
- [**Spi_DataSave**](https://github.com/zhuruili/Spider/tree/main/Spi_DataSave)  
  保存部分爬取的内容，体量比较小的数据集我会同步到仓库，如有需要可以直接下载。

## 内容目录

### SimPrograms

这部分的内容比较杂，相当于是借助一个个简单的案例来初步熟悉爬虫到底在干什么、它的流程一般是怎样的、基于请求的爬虫和基于自动化的爬虫大概分别是怎么做的等等

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

我在实习期留下的代码，虽然算不上很成熟，但是与我之前入门时候依葫芦画瓢写下的半吊子代码相比还是有很大的改进，比如多了很多异常处理，做了很多优化来提高代码的效率，并且在经过一个个相似的项目的训练后能够逐渐形成一套属于自己的爬虫模板，对比刚开始的我也算有了不少提高

> [!Note]
> 注意：这部分内容虽然是我在公司实习留下的代码，但是代码全程由我自己编写，并非公司向我提供，并且代码中所有有关公司的信息或者使用的资源均已被我移除，你可以放心的查看或学习其中的内容

- [光明日报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_gmw.py) | [中国教育报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_jyb.py)  
  基于`datetime`批量生成url、`requests`发送请求、`re`匹配内容、`pymysql`连接数据库并保存数据、`loguru`输出日志信息、`threading`与`ThreadPoolExecutor`控制多线程爬取、`time`控制休眠。
- [中国旅游报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_lyb.py) | [美术报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_msb.py) | [钱江晚报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_qjwb.py) | [永康日报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_ykrb.py)  
  在前两代报刊项目中发现了即使挂代理依旧存在网络错误导致数据缺失的问题。对此，本项目新增了对每日、每版次链接的访问重试，并增加了将多次重试请求依旧访问失败的链接保存到`Logs`下的日志文件的功能，方便项目跑完之后的数据校对与缺失填补
- [扬子晚报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_yzwb.py)  
  这个报纸相对于先前的报纸更新一些所以结构略有不同，但使用的代码大体仍然类似。比较特别的一点是在发送请求时你需要注意`headers`中的`if-modified-since`参数，起初由于这个参数的问题导致访问结果为`304`
- [今晚报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_jinwanbao.py)  
  在这份报纸中你并不能在最后的文章详情页界面获取所有的信息，其中的版面信息需要在使用多线程的同时传入包含版面信息的参数，这里使用`functools`中的`partial`进行参数传递，同时修改了并发逻辑，但也一定程度上降低了爬取的速率
- [中国农村信用合作报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_chinanshw.py)  
  优化了`今晚报`项目中存在的传参逻辑不当导致爬取速率降低的问题，在这版代码中函数的返回值不仅仅是个包含一系列链接的列表，而是包含多种数据的元组构成的列表，使得在上级页面获得的信息能够在不损失爬取速率的情况下传递到下级页面的爬取。并且在提取数据时综合使用了`re`和`xpath`
- [科普时报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_kpsb.py) | [中国质量报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_zlb.py)  
  针对有些报纸并不是每天都出版的问题，采用寻找出版日期接口的方式来提高访问的效率，例如有效日期可能藏在`period.xml`文件或者某段JS代码中，通过它得到具体的出刊时间，从而大幅减少无效的请求，提高效率
- [交通安全周刊](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_jtaqzk.py) | [人民公安报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_rmga.py)  
  针对某些内容链接又臭又长，不好找入口规律的问题，在这里利用了页面的重定向功能来让目标站点主动指引我们到想要的页面中，一定程度上避免在复杂的链接找规律中浪费时间
- [中国政府采购报](https://github.com/zhuruili/Spider/blob/main/SpiderPro/spi_zcb.py)  
  与之前的诸多静态网页报纸不同，政采报采用了异步加载的方式，因此在这版代码中，我们通过该报纸的各个接口找到对应的信息，并对其返回的`JSON`数据进行解析取得数据

### utils

- [请求测试](https://github.com/zhuruili/Spider/blob/main/utils/curl_test.py)  
  最原始而简单的请求代码，你可以在抓取你需要的数据包后通过复制该数据包的`Copy as cURL(bash)`到例如`Curl`或`Json`这类格式规范化网站来快速得到一个基本的请求模板，你可以通过注释来一步步检测究竟是什么参数导致了访问的失败，在本示例代码中是`if-modified-since`参数影响了访问导致返回`304`响应码
- [正则测试](https://github.com/zhuruili/Spider/blob/main/utils/re_test.py)  
  快速测试你的正则表达式能否提取到你想要的数据，而不用每修改一次正则就重新跑一遍自己的完整项目来调试，代码非常简单但是有时候真的能节省很多时间
- [数据格式化](https://github.com/zhuruili/Spider/blob/main/utils/format_scripts.py)  
  在得到原始数据后常常需要对数据进行一些常规的清洗, 有许多处理其实是共通的, 例如删除文本中的`HTML`标签或
  空白符等等, 为了避免每次写脚本都要重写这些函数, 可以将它们集中到特定的脚本中当作包来调用
- [查漏补缺](https://github.com/zhuruili/Spider/blob/main/utils/LeakFilling.py)  
  在爬取大批量的数据时，即使你挂了代理，做了请求重试等多种措施，也依旧可能有缺漏的网页没访问到或者访问失败，你可以将这部分网页的链接保存，并使用这份工具文件快速解析你所保存的失败网页，并将结果输出在新的文件中，之后你只需要在生成的新文件中查找`200`的结果即可快速找到你之前项目中访问失败的链接中哪些其实仍然是可用的

### tutorial

这并不是一个教程仓库，但是当我开始稍微系统性的接触爬虫知识的时候我发现自己在知识储备上有很多的不足并且存在一些认知盲区。以往我只是根据一些简单的爬虫案例教程来入门，这导致我对很多知识其实是一知半解的，所以我希望留下一些以知识点为导向的简单代码段作为简明教程

- [XPath函数](https://github.com/zhuruili/Spider/blob/main/tutorial/XPath_function.py)  
  我曾经天真的认为形如`//div/p/text()`就是`XPath`的全部了，但是它居然还支持各种各样的函数来达到数据灵活提取的目的

### DataSaved

仓库中所保存的程序爬取所得到的数据集可能会随时变动，因此就不在此处列表展示了，感兴趣的话可以直接到存放数据集的文件夹下查看其具体内容。

---

> [!Tip]
> 感谢你造访我的仓库，或许此时我已经不再是数据采集实习生了，但是爬虫技术在我上学和实习期间还是帮了我不少，因此我依旧会时不时更新些新内容
