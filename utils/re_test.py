import re

html_content = """
<li>
    <h3><a href="../../../con/202101/01/content_873968.html" >毫不放松抓好常态化疫情防控</a></h3>
</li>
<li>
    <h3><a href="../../../con/202101/01/content_873969.html" >我国新冠病毒疫苗上市，全民免费</a></h3>
</li>
<li>
    <h3><a href="../../../con/202101/01/content_873970.html" >这些新规元旦起实施 给你我带来哪些新变化？</a></h3>
</li>
<li>
    <h3><a href="../../../con/202101/01/content_873971.html" >江苏工会准备了1.5亿元“两节”大礼包</a></h3>
</li>
"""

pattern = re.compile(r'<a href="\.\./\.\./\.\./con/\d{6}/\d{2}/(content_\d+\.html)"', re.DOTALL)
matches = pattern.findall(html_content)
print(matches)