from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import re

class get_atcoder:

    def get_ac():
        # 抓取 AtCoder 比赛页面
        url = "https://atcoder.jp/contests/"
        try:
            html = urlopen(url).read().decode('utf-8')
        except Exception as e:
            print(f"访问 AtCoder 失败: {e}")
            return []
        
        # 使用 BeautifulSoup 解析
        soup = BeautifulSoup(html, 'html.parser')
        contests = []
        
        # 获取当前时间（UTC）
        now_utc = datetime.datetime.utcnow()
        # 转换为北京时间（UTC+8）
        beijing_offset = datetime.timedelta(hours=8)
        now_beijing = now_utc + beijing_offset
        
        # 查找所有比赛表
        contest_tables = soup.find_all('div', id=re.compile(r'contest-table-'))
        
        for table_div in contest_tables:
            # 确定比赛状态
            table_id = table_div.get('id', '')
            if 'active' in table_id:
                status = "进行中"
            elif 'upcoming' in table_id:
                status = "即将开始"
            else:
                # 跳过过去比赛
                continue
                
            # 查找比赛表格
            table = table_div.find('table', class_='table')
            if not table:
                continue
                
            # 遍历所有比赛行
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4:
                    continue
                    
                # 提取比赛时间信息
                time_td = cols[0]
                time_str = time_td.find('time').text.strip()
                
                # 提取持续时间
                duration_str = cols[2].text.strip()
                
                # 提取比赛标题
                title_td = cols[1]
                title_link = title_td.find('a')
                if not title_link:
                    continue
                title = title_link.text.strip()
                contest_url = "https://atcoder.jp" + title_link['href']
                
                # 解析比赛时间
                try:
                    # AtCoder 时间格式: "2024-06-30 10:00:00+0900"
                    # 提取 UTC 时间部分
                    time_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\+(\d{4})', time_str)
                    if not time_match:
                        continue
                    
                    # 解析原始时间
                    naive_time = datetime.datetime.strptime(time_match.group(1), '%Y-%m-%d %H:%M:%S')
                    
                    # 解析时区偏移（小时）
                    offset_hours = int(time_match.group(2)[:2])
                    
                    # 转换为UTC时间（减去原始时区偏移）
                    start_time_utc = naive_time - datetime.timedelta(hours=offset_hours)
                    
                    # 转换为北京时间（UTC+8）
                    start_time_beijing = start_time_utc + datetime.timedelta(hours=8)
                    
                    # 解析持续时间
                    if ':' in duration_str:
                        # 格式为 "HH:MM"
                        hours, minutes = duration_str.split(':')
                        duration = datetime.timedelta(hours=int(hours), minutes=int(minutes))
                    elif '分' in duration_str:
                        # 格式为 "XX 分"
                        minutes = int(duration_str.replace('分', '').strip())
                        duration = datetime.timedelta(minutes=minutes)
                    else:
                        # 其他格式暂时不支持
                        continue
                    
                    # 计算结束时间（北京时间）
                    end_time_beijing = start_time_beijing + duration
                    
                    # 格式化时间显示（北京时间）
                    time_display = f"{start_time_beijing.strftime('%Y-%m-%d %H:%M')} 至 {end_time_beijing.strftime('%Y-%m-%d %H:%M')}"
                    
                    # 格式化持续时间
                    total_seconds = duration.total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    duration_display = f"{hours}:{minutes:02d}:00"
                    
                    # 添加到比赛列表
                    contests.append({
                        'title': title,
                        'time': time_display,
                        'duration': duration_display,
                        'start_time': start_time_utc,  # 用于排序
                        'platform': "AtCoder"
                    })
                    
                except Exception as e:
                    print(f"解析比赛时间失败: {e}")
                    continue
        
        # 按开始时间排序
        contests.sort(key=lambda x: x['start_time'])
        
        # 打印结果
        # print(f"发现 {len(contests)} 个 AtCoder 比赛:")
        # for i, contest in enumerate(contests, 1):
        #     print("-" * 60)
        #     print(f"比赛平台: {contest['platform']}")
        #     print(f"比赛标题: {contest['title']}")
        #     print(f"比赛时间: {contest['time']}")
        #     print(f"比赛时长: {contest['duration']}")

            
        return contests

# 测试代码
if __name__ == "__main__":
    get_atcoder.get_ac()