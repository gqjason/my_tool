from .capture_nowcoder import get_nowcoder
from .capture_atcoder import get_atcoder
from .capture_codeforces import get_codeforces
from datetime import datetime, timedelta, timezone

class Main:
    
    def get_all_website():
        res = []
        res += get_nowcoder.get_nc()
        res += get_codeforces.get_cf()
        res += get_atcoder.get_ac()
        
        return res
    
    def get_upcoming_contests():
        # 获取所有比赛
        res = Main.get_all_website()
        
        # 确保所有时间都是时区感知的 UTC 时间
        for contest in res:
            if contest['start_time'].tzinfo is None:
                # 如果时间没有时区信息，假设为 UTC 并添加时区
                contest['start_time'] = contest['start_time'].replace(tzinfo=timezone.utc)
        
        # 按开始时间排序
        res.sort(key=lambda x: x['start_time'])
        return res
        
    def filter_today_competition(res):
        # 获取当前 UTC 时间（时区感知）
        now_utc = datetime.now().astimezone()
    
        # 计算今天 UTC 时间的开始和结束（时区感知）
        today_start_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        today_end_utc = today_start_utc + timedelta(days=1)
        
        # 筛选今天还未开始的比赛
        upcoming_today = []
        for contest in res:
            # 确保比赛时间是时区感知的
            start_time = contest['start_time']
            #print(start_time, today_start_utc)
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            
            # 检查比赛是否在今天
            if start_time < today_start_utc or start_time >= today_end_utc:
                continue
            
            # 检查比赛是否还未开始
            if start_time > now_utc:
                # 创建副本以避免修改原始数据
                contest_copy = contest.copy()
                contest_copy['start_time'] = start_time
                upcoming_today.append(contest_copy)
        
        return upcoming_today

    def run():
        upcoming_contest = Main.get_upcoming_contests()
        today_contest = Main.filter_today_competition(upcoming_contest)
        
        # print("[OJ_Bot]")
        # if not today_contest:
        #     print("今天没有即将开始的比赛")
        # else:
        #     for i, contest in enumerate(today_contest, 1):
        #         print("-" * 60)
        #         print(f"比赛平台：{contest['platform']}")
        #         print(f"比赛标题: {contest['title']}")
        #         print(f"比赛时间: {contest['time']}")
        #         print(f"比赛时长: {contest['duration']}")
                
        # for i, contest in enumerate(upcoming_contest, 1):
        #     print("-" * 60)
        #     print(f"比赛平台：{contest['platform']}")
        #     print(f"比赛链接: {contest['link']}")
        #     print(f"比赛标题: {contest['title']}")
        #     print(f"比赛时间: {contest['time']}")
        #     print(f"比赛时长: {contest['duration']}")

    
    def return_today_upcoming_contest():
        
        upcoming_contest = Main.get_upcoming_contests()
        today_contest = Main.filter_today_competition(upcoming_contest)
        return today_contest
    
    def return_all_upcoming_contest():
        upcoming_contest = Main.get_upcoming_contests()
        return upcoming_contest

    
if __name__ == '__main__':
    Main.run()