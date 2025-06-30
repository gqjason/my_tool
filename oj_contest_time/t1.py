from urllib.request import urlopen
mu = "https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13"
res = urlopen(mu)


with open("res.txt", "wb") as f:
    f.write(res.read())
res = open("res.txt", "rb")
print(res.read().decode("utf-8"))