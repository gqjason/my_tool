from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import re

class get_nowcoder:

    def get_nc():
        # 抓取网页内容
        url = "https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13"
        html = urlopen(url).read().decode('utf-8')

        # 使用BeautifulSoup解析
        soup = BeautifulSoup(html, 'html.parser')
        contests = []


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
                
                # 提取比赛链接
                contest_link = "https://ac.nowcoder.com" + title_tag['href']
                
                # 提取时间
                time_tag = item.find('li', class_='match-time-icon')
                if time_tag:
                    time_text = time_tag.get_text(strip=True).replace('比赛时间：', '')
                    # 尝试解析时间范围
                    try:
                        # 提取开始和结束时间
                        start_str, end_str = time_text.split(' 至 ')
                        start_str = start_str.strip()
                        end_str, duration = end_str.split('\n')
                        end_str = end_str.strip()
                        duration = duration[5:-1]
                        
                        start_time = datetime.datetime.strptime(start_str, '%Y-%m-%d %H:%M')
                        end_time = datetime.datetime.strptime(end_str, '%Y-%m-%d %H:%M')
                        now_time = datetime.datetime.now()

                        # 计算比赛时长
                        duration = end_time - start_time
                        total_minutes = int(duration.total_seconds() / 60)
                        hours = total_minutes // 60
                        minutes = total_minutes % 60
                        
                        # 格式化时长显示 (HH:MM)
                        duration_str = f"{hours}:{minutes:02d}:00"
                        
                        # 格式化时间显示
                        time_display = f"{start_time.strftime('%Y-%m-%d %H:%M')} 至 {end_time.strftime('%Y-%m-%d %H:%M')}"
                        
                        if start_time > now_time:
                            # 添加到比赛列表（添加了link字段）

                            contests.append({
                                'title': title,
                                'time': time_display,
                                'duration': duration_str,
                                'start_time': start_time,
                                'platform': "牛客",
                                'link': contest_link  # 添加比赛链接
                            })
                            
                        # # 添加到比赛列表（添加了link字段）
                        # contests.append({
                        #     'title': title,
                        #     'time': time_display,
                        #     'duration': duration_str,
                        #     'start_time': start_time,
                        #     'platform': "牛客",
                        #     'link': contest_link  # 添加比赛链接
                        # })

                    except Exception as e:
                        print(f"解析时间时出错: {e}")
                        continue
                else:
                    print(f"未找到比赛时间: {title}")
                    continue

        # 按开始时间排序（最近的在前）
        contests.sort(key=lambda x: x['start_time'])

        return contests

# 测试代码
if __name__ == "__main__":
    contests = get_nowcoder.get_nc()
    now = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')
    for contest in contests:
        print(f"比赛标题: {contest['title']}")
        print(f"比赛链接: {contest['link']}")
        print(f"比赛时间: {contest['time']}")
        print(f"比赛开始时间: {contest['start_time']}")

        print(f"比赛时长: {contest['duration']}")
        print("-" * 60)