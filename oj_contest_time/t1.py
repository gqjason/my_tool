from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime

# 抓取网页内容
url = "https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13"
html = urlopen(url).read().decode('utf-8')

# 使用BeautifulSoup解析
soup = BeautifulSoup(html, 'html.parser')
contests = []

# 获取当前时间
now = datetime.datetime.now()

# 定位所有比赛模块
for section in soup.find_all('div', class_='platform-mod'):
    # 获取模块标题
    header = section.find('h2')
    if not header:
        continue
        
    section_title = header.get_text(strip=True)
    
    # 跳过"已结束"的整个模块
    if "已结束" in section_title:
        continue
    
    # 提取当前模块内的所有比赛
    for item in section.find_all('div', class_='platform-item'):
        # 精确提取标题 - 只取平台项目内容部分的第一个<a>标签
        cont_div = item.find('div', class_='platform-item-cont')
        if not cont_div:
            continue
            
        # 在平台项目内容中查找标题链接
        title_tag = cont_div.find('a', href=lambda x: x and '/acm/contest/' in x)
        if not title_tag: 
            continue
        
        # 获取纯文本标题（去除任何子标签）
        title = title_tag.get_text(strip=True)
        
        # 提取时间
        time_tag = item.find('li', class_='match-time-icon')
        if time_tag:
            time_text = time_tag.get_text(strip=True).replace('比赛时间：', '')
            # 尝试解析时间范围
            try:
                start_str, end_str = time_text.split(' 至 ')
                start_time = datetime.datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                end_time = datetime.datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
                
                # 根据时间状态添加标签
                if now < start_time:
                    status = "即将开始"
                elif now <= end_time:
                    status = "进行中"
                else:
                    status = "已结束"  # 理论上不会出现，因为已跳过整个模块
                    
                # 添加状态标签到标题
                title = f"[{status}] {title}"
            except:
                # 时间格式解析失败时保持原样
                pass
        else:
            time_text = "时间未找到"
        
        contests.append([title, time_text])

# 按开始时间排序（最近的在前）
contests.sort(key=lambda x: x[1])

# 打印结果
print(f"发现 {len(contests)} 个未结束的比赛:")
for title, time in contests:
    print("-" * 30)
    print(f"比赛标题: {title}")
    print(f"比赛时间: {time}")