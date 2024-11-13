# 最后测试于2024/11/13，代码已经失效，查看网页后发现是由于MOOC网页的前端代码发生了变化
# 但是虽然程序目前无法运行，但是通过无论它前端代码怎么改，本程序爬取的流程和思路是没有问题的，只需要根据新的前端代码修改定位元素的选择器代码就又可以运行了

from DrissionPage import WebPage
from DrissionPage import ChromiumOptions
import json

# 参数设置
json_data = {}  # 存放最终生成的json数据
data = {}  # 存放最终生成的字典

#功能函数
def search(wp,item):
    """搜索"""
    wp.ele('css:.j-textarea.inputtxt').input(item)  # 输入搜索内容
    #wp.wait.load_start()  # 等待页面加载完成
    wp.ele('css:.u-icon-search2.j-searchBtn').click()  # 点击搜索按钮

def get_data(json_data,data,links):
    """提取数据"""
    # 在课程数据包中并未发现课程链接数据，故需另外获取
    names = []  # 课程名称
    contents = []  # 课程简介
    universities = []  # 开课学校
    teachers = []  # 授课教师
    enrolls = []  # 参与人数
    pics = []  # 课程图片

    ClassLists = json_data['result']['list']
    for mooc in ClassLists:
        highlightName = mooc['highlightName']
        highlightContent = mooc['highlightContent']
        highlightUniversity = mooc['highlightUniversity']
        highlightTeacherNames = mooc['highlightTeacherNames']

        try:  # 经测试发现某些课程参与人数数据包路径不同，故需加入异常处理
            enrollCount = mooc['mocCourseCard']['enrollCount']
        except:
            try:
                enrollCount = mooc['mocCoursePackageKyCardBaseInfoDto']['enrollNum']
            except:
                enrollCount = "0"

        try:  # 经测试发现某些课程图片数据包路径不同，故需加入异常处理
            pic_src = mooc['mocCourseCard']['mocCourseCardDto']['imgUrl']
        except:
            try:
                pic_src = mooc['mocCoursePackageKyCardBaseInfoDto']['coverPhoto']
            except:
                pic_src = "None"
        # 去除课程名称和课程描述中的多余字符（#、{、}）
        highlightName = highlightName.replace('#', '').replace('{', '').replace('}', '')
        highlightContent = highlightContent.replace('#', '').replace('{', '').replace('}', '')
        
        names.append(highlightName)
        contents.append(highlightContent)
        universities.append(highlightUniversity)
        teachers.append(highlightTeacherNames)
        enrolls.append(enrollCount)
        pics.append(pic_src)
        
    # 数据检测
    assert len(names) == len(contents) == len(universities) == len(teachers) == len(enrolls) == len(pics) == len(links), '数据长度不一致！'
    # 格式转换：list->dict
    data = {
            'list': [
                {
                    'name': name,
                    'pic': pic,
                    'university': university,
                    'link': link,
                    'enroll': enroll,
                    'content': content,
                    'teacher': teacher
                }
                for name, content, university, teacher, enroll, pic, link in zip(names[:18], contents[:18], universities[:18], teachers[:18], enrolls[:18], pics[:18], links[:18])
            ]
    }

    return data

def get_ClassUrls(wp,length):
    """获取课程链接"""
    Links = []
    linkInfos = wp.eles('@href:icourse163.org/course/')
    for linkInfo in linkInfos:
        Links.append(linkInfo.link)
    # 去掉含terms的链接
    Links = [link for link in Links if 'terms' not in link]
    # 去重
    Links = remove_duplicates(Links)
    # 由于MOOC课程存在广告推荐，导致课程链接数与课程数不一致，故需手动补充
    while len(Links) < length:
        Links.append('None')
    return Links

# 辅助函数
def remove_duplicates(lst):
    """对列表去重，保持原有顺序"""
    result = []
    for item in lst:
        if item not in result:
            result.append(item)
    return result

# API
def API(item):
    """API"""
    wp_mooc = WebPage()

    wp_mooc.get("https://www.icourse163.org/")

    wp_mooc.listen.start('web/j/mocSearchBean.searchCourse.rpc')  #启动监听

    search(wp=wp_mooc,item=item)

    resp = wp_mooc.listen.wait()  #等待监听到数据
    resp = resp._raw_body
    json_data = json.loads(resp)  #转换json数据

    lenth = len(json_data['result']['list'])

    Links = get_ClassUrls(wp=wp_mooc,length=lenth)

    global data
    data = get_data(json_data=json_data,data=data,links=Links)

    wp_mooc.close()

    return data  # 返回给主程序的字典数据
    

if __name__ == "__main__":
    item = input('请输入视频名称：')
    API(item=item)