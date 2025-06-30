import requests
from datetime import datetime, timedelta
import pytz

class get_codeforces:

    def get_cf():
        # Codeforces API端点
        API_URL = "https://codeforces.com/api/contest.list"
        
        try:
            # 发送GET请求到API
            response = requests.get(API_URL, timeout=10)
            
            # 检查响应状态
            if response.status_code != 200:
                print(f"API请求失败，状态码: {response.status_code}")
                return []
            
            # 解析JSON响应
            data = response.json()
            
            # 检查API响应状态
            if data.get('status') != 'OK':
                print(f"API返回错误: {data.get('comment', '未知错误')}")
                return []
                
            contests = data.get('result', [])
            
        except Exception as e:
            print(f"请求API时出错: {e}")
            return []
        
        # 获取当前UTC时间
        now_utc = datetime.utcnow()
        
        # 过滤和格式化比赛信息
        filtered_contests = []
        
        for contest in contests:
            # 只关注未结束的比赛
            if contest['phase'] not in ['BEFORE', 'CODING']:
                continue
                
            # 提取基本信息
            contest_id = contest['id']
            title = contest['name']
            duration_seconds = contest['durationSeconds']
            
            # 转换持续时间
            duration = timedelta(seconds=duration_seconds)
            duration_str = str(duration)
            # 简化显示：去除秒数和小数部分
            if '.' in duration_str:
                duration_str = duration_str.split('.')[0]
            
            # 处理开始时间
            if 'startTimeSeconds' in contest:
                start_time_utc = datetime.utcfromtimestamp(contest['startTimeSeconds'])
            else:
                # 如果未提供开始时间，跳过该比赛
                continue
                
            # 计算结束时间
            end_time_utc = start_time_utc + duration
            
            # 确定比赛状态
            if contest['phase'] == 'BEFORE':
                status = "即将开始"
            else:  # CODING
                status = "进行中"
            
            # 转换为MSK时区（UTC+3）
            msk_tz = pytz.timezone('Europe/Moscow')
            start_time_msk = start_time_utc.replace(tzinfo=pytz.utc).astimezone(msk_tz)
            end_time_msk = end_time_utc.replace(tzinfo=pytz.utc).astimezone(msk_tz)
            
            # 格式化时间显示
            time_display = f"{start_time_msk.strftime('%Y-%m-%d %H:%M')} 至 {end_time_msk.strftime('%Y-%m-%d %H:%M')}"
            
            # 添加到结果列表
            filtered_contests.append({
                'title': title,
                'time': time_display,
                'duration': duration_str,
                'start_time': start_time_utc,
                'platform':"Codeforces"
            })
        
        # 按开始时间排序（最近的在前）
        filtered_contests.sort(key=lambda x: x['start_time'])
        
        # 打印结果
        # print(f"发现 {len(filtered_contests)} 个未结束的比赛:")
        # for i, contest in enumerate(filtered_contests, 1):
        #     print("-" * 60)
        #     print(f"比赛平台：{contest['platform']}")
        #     print(f"比赛标题: {contest['title']}")
        #     print(f"比赛时间: {contest['time']}")
        #     print(f"比赛时长: {contest['duration']}")

        return filtered_contests

# 测试代码
if __name__ == "__main__":
    get_codeforces.get_cf()