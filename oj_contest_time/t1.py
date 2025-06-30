from urllib.request import urlopen
import re
from bs4 import BeautifulSoup
mu = "https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13"
res = urlopen(mu)


with open("res.txt", "wb") as f:
    f.write(res.read())
res = open('res.txt', 'r', encoding='utf-8')
res = res.readlines()

def contest_title(s):
    t = ""
    able = False
    for i in s:
        if i == '>' and not able:
            able = True
            continue
        if i == '<' and able:
            able = False
            break
        if able:
            t += i
    return t

def contest_time(s):
    t = ""
    s.strip(' ')
    t = s
    return t

#print(res)
res = [[]]
for s in res:
    if "/acm/contest" in s and "target=\"_blank\"" in s and "img" not in s:
        res.append([])
        
        res[-1].append(contest_title(s))
    if "比赛时间" in s:
        res[-1].append(contest_time(s))

for r in res:
    print("-"*20)
    for e in r:
        print(e)

