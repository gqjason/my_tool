import requests
import csv
import os
import time
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import cloudscraper
import re
import json
import pytz

# 全局配置
USER_AGENT = UserAgent()
HEADERS = {
    'User-Agent': USER_AGENT.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'DNT': '1'
}
DELAY = (1, 3)  # 随机延迟范围(秒)
TIMEOUT = 15
RETRY_TIMES = 3
OUTPUT_FILE = "programming_contests.csv"
TODAY_OUTPUT_FILE = "today_contests.csv"  # 当天可参赛比赛输出文件

# 创建cloudscraper实例绕过Cloudflare
scraper = cloudscraper.create_scraper()

# 设置时区 (使用北京时间)
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

def get_page(url, use_cloudscraper=True):
    """获取页面内容，支持重试和绕过反爬"""
    for attempt in range(RETRY_TIMES):
        try:
            time.sleep(random.uniform(*DELAY))
            headers = {**HEADERS, 'User-Agent': USER_AGENT.random}
            
            if use_cloudscraper:
                response = scraper.get(url, headers=headers, timeout=TIMEOUT)
            else:
                response = requests.get(url, headers=headers, timeout=TIMEOUT)
            
            response.raise_for_status()
            
            # 检查常见反爬页面
            if 'captcha' in response.url.lower() or 'denied' in response.text.lower():
                raise Exception(f"触发反爬机制: {response.url}")
                
            return response.text
        
        except Exception as e:
            print(f"请求失败 ({attempt+1}/{RETRY_TIMES}): {type(e).__name__}, {e}")
            time.sleep(2)
    return None

def parse_duration(duration_str):
    """将持续时间字符串转换为分钟数"""
    # 处理牛客网格式 (如: "2小时30分钟")
    if "小时" in duration_str or "分钟" in duration_str:
        hours = 0
        minutes = 0
        
        hour_match = re.search(r'(\d+)\s*小时', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        minute_match = re.search(r'(\d+)\s*分钟', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))
        
        return hours * 60 + minutes
    
    # 处理AtCoder格式 (如: "01:30")
    elif ':' in duration_str:
        parts = duration_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # 包含秒数的情况
            return int(parts[0]) * 60 + int(parts[1])
    
    # 处理洛谷格式 (如: "2h30m")
    elif 'h' in duration_str or 'm' in duration_str:
        hours = 0
        minutes = 0
        
        hour_match = re.search(r'(\d+)\s*h', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        minute_match = re.search(r'(\d+)\s*m', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))
        
        return hours * 60 + minutes
    
    return 0  # 默认值

def format_duration(minutes):
    """将分钟数转换为标准格式 (HH:MM)"""
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"

def get_codeforces_contests():
    """从Codeforces API获取竞赛数据"""
    print("获取Codeforces竞赛数据...")
    api_url = "https://codeforces.com/api/contest.list"
    
    try:
        response = requests.get(api_url, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] != 'OK':
            print(f"Codeforces API错误: {data.get('comment', '未知错误')}")
            return []
        
        contests = []
        for contest in data['result']:
            # 只获取常规竞赛（排除训练赛）
            if contest['phase'] != 'FINISHED' or contest['type'] == 'CF':
                start_time = datetime.utcfromtimestamp(contest['startTimeSeconds'])
                start_time = start_time.astimezone(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
                
                duration_minutes = contest['durationSeconds'] // 60
                duration_formatted = format_duration(duration_minutes)
                
                # 计算结束时间 (开始时间 + 持续时间)
                end_time = datetime.utcfromtimestamp(
                    contest['startTimeSeconds'] + contest['durationSeconds']
                ).astimezone(BEIJING_TZ)
                
                contests.append({
                    'platform': 'Codeforces',
                    'name': contest['name'],
                    'link': f"https://codeforces.com/contest/{contest['id']}",
                    'start_time': start_time,
                    'duration': duration_formatted,
                    'status': contest['phase'],
                    'duration_minutes': duration_minutes,
                    'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'scraped_at': datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        print(f"获取到 {len(contests)} 个Codeforces竞赛")
        return contests
    
    except Exception as e:
        print(f"获取Codeforces数据失败: {e}")
        return []

def get_nowcoder_contests():
    """爬取牛客网竞赛数据 - 修复版"""
    print("获取牛客网竞赛数据...")
    url = "https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13"
    html = get_page(url, use_cloudscraper=True)
    
    if not html:
        print("无法获取牛客网页面")
        return []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')  # 使用更通用的解析器
        contests = []
        current_time = datetime.now(BEIJING_TZ)
        
        # 查找竞赛列表 - 更健壮的选择器
        contest_list = soup.select_one('.platform-cont.js-current')
        if not contest_list:
            contest_list = soup.select_one('.platform-mod.js-current')
        if not contest_list:
            contest_list = soup.select_one('.js-container')
        
        if not contest_list:
            print("未找到牛客网竞赛列表")
            # 调试：保存HTML以便分析
            with open('nowcoder_debug.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("已保存页面到 nowcoder_debug.html")
            return []
        
        # 提取竞赛项 - 更可靠的选择器
        items = contest_list.select('.js-item, .contest-item')
        if not items:
            items = contest_list.select('.contest-item-main')
        
        print(f"找到 {len(items)} 个竞赛项")
        
        for item in items:
            try:
                # 调试：保存当前项HTML
                # with open('nowcoder_item.html', 'w', encoding='utf-8') as f:
                #     f.write(str(item))
                
                # 提取竞赛名称和链接 - 更灵活的选择器
                name_tag = item.select_one('a:has(.contest-title), .contest-name a, .contest-title')
                if not name_tag:
                    name_tag = item.select_one('h2, .title')
                
                name = name_tag.text.strip() if name_tag else "N/A"
                link = ""
                if name_tag and name_tag.get('href'):
                    link = "https://ac.nowcoder.com" + name_tag['href']
                
                # 提取时间信息 - 更健壮的选择器
                time_tag = item.select_one('.contest-time, .item-time, .time-info')
                if not time_tag:
                    # 尝试在父元素中查找
                    time_tag = item.find_parent(class_=['contest-item', 'js-item']).select_one('.contest-time')
                
                time_text = time_tag.text.strip() if time_tag else ""
                
                # 解析时间 - 处理多种格式
                start_time = ""
                end_time = ""
                if time_text:
                    # 格式1: 报名时间：2023-10-01 09:00:00 至 2023-10-15 09:00:00
                    # 格式2: 比赛时间：2023-10-01 09:00:00 至 2023-10-01 12:00:00
                    # 格式3: 2023-10-01 09:00 - 2023-10-01 12:00
                    time_match = re.search(
                        r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}(?::\d{2})?)\s*至\s*(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}(?::\d{2})?)', 
                        time_text
                    )
                    
                    if time_match:
                        start_str = time_match.group(1)
                        end_str = time_match.group(2)
                        
                        # 标准化时间格式
                        if len(start_str) == 16:  # 缺少秒数
                            start_str += ":00"
                        if len(end_str) == 16:
                            end_str += ":00"
                            
                        try:
                            start_dt = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                            start_dt = BEIJING_TZ.localize(start_dt)
                            start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                            
                            end_dt = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
                            end_dt = BEIJING_TZ.localize(end_dt)
                            end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                        except Exception as e:
                            print(f"时间解析错误: {e}, 时间字符串: {start_str} - {end_str}")
                    else:
                        # 尝试其他格式
                        single_time = re.search(r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}(?::\d{2})?)', time_text)
                        if single_time:
                            start_str = single_time.group(1)
                            if len(start_str) == 16:
                                start_str += ":00"
                            try:
                                start_dt = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                                start_dt = BEIJING_TZ.localize(start_dt)
                                start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                                # 假设默认持续2小时
                                end_dt = start_dt + timedelta(hours=2)
                                end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                            except Exception as e:
                                print(f"单时间解析错误: {e}, 时间字符串: {start_str}")
                
                # 提取持续时间 - 备用方案
                duration_minutes = 120  # 默认2小时
                duration_tag = item.select_one('.contest-duration, .duration, .item-duration')
                if duration_tag:
                    duration_text = duration_tag.text.strip()
                    duration_minutes = parse_duration(duration_text)
                
                # 如果没有提取到时间，但有了开始和结束时间，计算持续时间
                if start_time and end_time:
                    try:
                        start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                        end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
                    except:
                        pass
                
                duration_formatted = format_duration(duration_minutes)
                
                # 提取状态
                status = "未知"
                status_tag = item.select_one('.contest-status, .status, .state')
                if status_tag:
                    status = status_tag.text.strip()
                else:
                    # 根据时间判断状态
                    if start_time and end_time:
                        now = datetime.now(BEIJING_TZ)
                        start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                        end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                        
                        if now < start_dt:
                            status = "未开始"
                        elif now < end_dt:
                            status = "进行中"
                        else:
                            status = "已结束"
                
                contests.append({
                    'platform': 'Nowcoder',
                    'name': name,
                    'link': link,
                    'start_time': start_time,
                    'duration': duration_formatted,
                    'status': status,
                    'duration_minutes': duration_minutes,
                    'end_time': end_time,
                    'scraped_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # 调试输出
                print(f"  - 解析成功: {name} | 开始: {start_time} | 结束: {end_time} | 状态: {status}")
                
            except Exception as e:
                print(f"解析牛客网竞赛项失败: {e}")
                # 打印当前项的HTML以便调试
                print("问题项HTML片段:")
                print(item.prettify()[:500])  # 只打印前500字符
        
        print(f"获取到 {len(contests)} 个牛客网竞赛")
        return contests
    
    except Exception as e:
        print(f"解析牛客网数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_atcoder_contests():
    """爬取AtCoder竞赛数据"""
    print("获取AtCoder竞赛数据...")
    url = "https://atcoder.jp/contests/"
    html = get_page(url, use_cloudscraper=False)
    
    if not html:
        print("无法获取AtCoder页面")
        return []
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        contests = []
        current_time = datetime.now(BEIJING_TZ)
        
        # 查找活跃竞赛表
        active_table = soup.find('div', id='contest-table-upcoming')
        tables = [active_table] if active_table else []
        
        # 如果没有找到活跃竞赛表，尝试查找其他表
        if not tables:
            tables = soup.find_all('div', class_='table-responsive')
        
        for table in tables:
            # 提取表格行
            rows = table.find_all('tr')
            for row in rows[1:]:  # 跳过表头
                try:
                    cols = row.find_all('td')
                    if len(cols) < 4:
                        continue
                    
                    # 提取时间
                    time_tag = cols[0].find('time')
                    if not time_tag:
                        continue
                    
                    # 解析时间（带时区信息）
                    start_time_str = time_tag.text.strip()
                    start_dt = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S%z')
                    start_dt = start_dt.astimezone(BEIJING_TZ)
                    start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 提取竞赛名称和链接
                    name_tag = cols[1].find('a')
                    name = name_tag.text.strip() if name_tag else "N/A"
                    link = "https://atcoder.jp" + name_tag['href'] if name_tag else ""
                    
                    # 提取持续时间
                    duration_minutes = parse_duration(cols[2].text.strip())
                    duration_formatted = format_duration(duration_minutes)
                    
                    # 计算结束时间
                    end_dt = start_dt + timedelta(minutes=duration_minutes)
                    end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 提取评级
                    rating = cols[3].text.strip()
                    
                    contests.append({
                        'platform': 'AtCoder',
                        'name': name,
                        'link': link,
                        'start_time': start_time,
                        'duration': duration_formatted,
                        'status': rating,
                        'duration_minutes': duration_minutes,
                        'end_time': end_time,
                        'scraped_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                except Exception as e:
                    print(f"解析AtCoder竞赛行失败: {e}")
        
        print(f"获取到 {len(contests)} 个AtCoder竞赛")
        return contests
    
    except Exception as e:
        print(f"解析AtCoder数据失败: {e}")
        return []

def get_luogu_contests():
    """爬取洛谷竞赛数据"""
    print("获取洛谷竞赛数据...")
    url = "https://www.luogu.com.cn/contest/list"
    html = get_page(url, use_cloudscraper=True)
    
    if not html:
        print("无法获取洛谷页面")
        return []
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        contests = []
        current_time = datetime.now(BEIJING_TZ)
        
        # 查找竞赛列表容器
        list_container = soup.find('div', class_='am-g lg-table-container')
        if not list_container:
            print("未找到洛谷竞赛列表")
            return []
        
        # 提取竞赛项
        items = list_container.find_all('a', class_='lg-list-item')
        for item in items:
            try:
                # 提取竞赛名称
                name_tag = item.find('span', class_='lg-list-item-name')
                name = name_tag.text.strip() if name_tag else "N/A"
                
                # 提取链接
                link = "https://www.luogu.com.cn" + item['href'] if item.has_attr('href') else ""
                
                # 提取时间信息
                time_tag = item.find('span', class_='lg-list-item-time')
                time_text = time_tag.text.strip() if time_tag else ""
                
                # 解析时间 (格式: 2023-10-01 09:00 至 2023-10-01 12:00)
                start_time = ""
                end_time = ""
                if "至" in time_text:
                    time_parts = time_text.split('至')
                    if time_parts:
                        start_str = time_parts[0].strip()
                        end_str = time_parts[1].strip()
                        try:
                            # 解析开始时间
                            start_dt = datetime.strptime(start_str, '%Y-%m-%d %H:%M')
                            start_dt = BEIJING_TZ.localize(start_dt)
                            start_time = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                            
                            # 解析结束时间
                            end_dt = datetime.strptime(end_str, '%Y-%m-%d %H:%M')
                            end_dt = BEIJING_TZ.localize(end_dt)
                            end_time = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                
                # 提取持续时间
                duration_tag = item.find('span', class_='lg-list-item-duration')
                duration_minutes = parse_duration(duration_tag.text.strip()) if duration_tag else 0
                duration_formatted = format_duration(duration_minutes)
                
                # 计算持续时间（如果未提供）
                if not duration_minutes and start_time and end_time:
                    try:
                        start_dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                        end_dt = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                        duration_minutes = int((end_dt - start_dt).total_seconds() / 60)
                        duration_formatted = format_duration(duration_minutes)
                    except:
                        pass
                
                # 提取状态
                status_tag = item.find('span', class_='lg-badge')
                status = status_tag.text.strip() if status_tag else ""
                
                contests.append({
                    'platform': 'Luogu',
                    'name': name,
                    'link': link,
                    'start_time': start_time,
                    'duration': duration_formatted,
                    'status': status,
                    'duration_minutes': duration_minutes,
                    'end_time': end_time,
                    'scraped_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                print(f"解析洛谷竞赛项失败: {e}")
        
        print(f"获取到 {len(contests)} 个洛谷竞赛")
        return contests
    
    except Exception as e:
        print(f"解析洛谷数据失败: {e}")
        return []

def filter_today_contests(contests):
    """筛选当天未结束可参加的比赛"""
    current_time = datetime.now(BEIJING_TZ)
    today_contests = []
    
    for contest in contests:
        # 检查是否有有效的时间信息
        if not contest.get('start_time') or not contest.get('end_time'):
            continue
            
        try:
            # 转换为datetime对象
            start_dt = datetime.strptime(contest['start_time'], '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(contest['end_time'], '%Y-%m-%d %H:%M:%S')
            
            # 确保时间对象有时区信息
            if not start_dt.tzinfo:
                start_dt = BEIJING_TZ.localize(start_dt)
            if not end_dt.tzinfo:
                end_dt = BEIJING_TZ.localize(end_dt)
            
            # 检查是否在今天
            if start_dt.date() != current_time.date():
                continue
                
            # 检查比赛是否已结束
            if current_time < end_dt:
                contest['time_left'] = int((start_dt - current_time).total_seconds() // 60)
                contest['has_started'] = current_time > start_dt
                today_contests.append(contest)
        except Exception as e:
            print(f"解析时间失败: {contest['name']} - {e}")
            continue
    
    # 按开始时间排序
    today_contests.sort(key=lambda x: datetime.strptime(x['start_time'], '%Y-%m-%d %H:%M:%S'))
    return today_contests

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        print(f"无数据可保存到 {filename}")
        return False
    
    try:
        file_exists = os.path.isfile(filename)
        # 动态生成字段列表
        fieldnames = list(data[0].keys()) if data else []
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"数据已保存到 {filename}")
        return True
    except Exception as e:
        print(f"保存CSV文件失败: {e}")
        return False

def print_today_contests(contests):
    """打印当天可参加的竞赛"""
    if not contests:
        print("\n今天没有未结束可参加的比赛")
        return
    
    print("\n今天未结束可参加的比赛:")
    print("-" * 90)
    print(f"{'平台':<12}{'状态':<8}{'距离开始':<10}{'开始时间':<20}{'结束时间':<20}{'比赛名称'}")
    print("-" * 90)
    
    for contest in contests:
        platform = contest['platform']
        name = contest['name']
        start_time = contest['start_time'][11:16]  # 只显示时分
        end_time = contest['end_time'][11:16] if contest.get('end_time') else "未知"
        
        # 计算时间状态
        if contest['has_started']:
            status = "进行中"
            time_left = "正在进行"
        else:
            status = "未开始"
            hours_left = contest['time_left'] // 60
            minutes_left = contest['time_left'] % 60
            time_left = f"{hours_left}时{minutes_left}分"
        
        print(f"{platform:<12}{status:<8}{time_left:<10}{start_time:<20}{end_time:<20}{name}")
    
    print("-" * 90)
    print(f"共找到 {len(contests)} 场今天可参加的比赛")

def main():
    start_time = time.time()
    all_contests = []
    
    # 获取各平台数据
    print("\n" + "="*50)
    print("开始获取各平台竞赛数据...")
    print("="*50)
    all_contests.extend(get_codeforces_contests())
    all_contests.extend(get_nowcoder_contests())
    all_contests.extend(get_atcoder_contests())
    all_contests.extend(get_luogu_contests())
    
    # 保存所有竞赛数据
    if all_contests:
        save_to_csv(all_contests, OUTPUT_FILE)
        
        # 打印摘要
        platforms = set(c['platform'] for c in all_contests)
        print("\n爬取完成! 摘要:")
        print(f"总竞赛数量: {len(all_contests)}")
        for platform in platforms:
            count = sum(1 for c in all_contests if c['platform'] == platform)
            print(f"- {platform}: {count} 个竞赛")
        
        # 筛选当天未结束的比赛
        today_contests = filter_today_contests(all_contests)
        
        # 保存当天比赛数据
        if today_contests:
            save_to_csv(today_contests, TODAY_OUTPUT_FILE)
            print_today_contests(today_contests)
        else:
            print("\n今天没有未结束可参加的比赛")
    else:
        print("\n未获取到任何竞赛数据")
    
    print(f"\n总执行时间: {time.time() - start_time:.2f}秒")

if __name__ == "__main__":
    main()