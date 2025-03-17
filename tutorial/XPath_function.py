from lxml import etree

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>XPath函数测试</title>
</head>
<body>
<div>
    <img src="1.png" alt="png格式图片">
    <img src="2.jpg" alt="jpg格式图片">
    <img src="3.gif" alt="gif格式图片">
    <img src="4.jpg" alt="jpg格式图片">
    <img src="5.png" alt="png格式图片">
</div>
<div>
    <p>李白：抽刀断水水更流，举杯消愁愁更愁。</p>
    <p>杜甫：安得广厦千万间，大庇天下寒士俱欢颜。</p>
    <p>李白：举杯邀明月，对影成三人。</p>
    <p>杜甫：此曲只应天上有，人间能得几回闻。</p>
    <p>李白：桃花潭水深千尺，不及汪伦送我情。</p>
    <p>杜甫：星垂平野阔，月涌大江流。</p>
</div>
</body>
</html>
"""

xp = etree.HTML(html)

# 提取所有PNG图片的src列表
print(xp.xpath('//img[contains(@src, ".png")]/@src'))  # 方法一：contains函数，找到src属性中包含.png的img标签
print(xp.xpath('//img[substring(@src, string-length(@src) - 3) = ".png"]/@src'))  # 方法二：substring函数，找到src属性后四位是.png的img标签

# 提取所有五言诗
print(xp.xpath('//p[string-length(text()) = 15]/text()'))  # string-length函数，找到文本长度为15的p标签

# 提取所有杜甫的七言诗
print(xp.xpath('//p[starts-with(text(), "杜甫") and string-length(text()) = 19]/text()'))  # starts-with函数，找到文本以"杜甫"开头，长度为19的p标签


"""
这里仅仅是演示了几个基本的XPath函数，实际上XPath函数还有很多，可以根据实际需求来选择合适的函数。
"""