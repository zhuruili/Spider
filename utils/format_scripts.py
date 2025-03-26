import re

def Remove_HTML(text):
    """
    移除文本中的HTML标签、&nbsp;、&amp;等
    """
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', '', text)
    text = re.sub(r'&amp;', '', text)
    return text