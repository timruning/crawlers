import requests
from bs4 import BeautifulSoup

if __name__ == '__main__':
    url = "http://www.fzyshcn.com/shyf/2018-10-25/59769.html"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Host": "www.fzyshcn.com",
        "Referer": "http://www.fzyshcn.com/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
    }
    req = requests.get(url=url, headers=headers)
    text = req.content.decode("gbk")
    bf = BeautifulSoup(text)
    left1_d = bf.find_all("div", class_="left1_d")
    p_list=[]
    for v in left1_d:
        print(v)
        print()
        print()
        word_wrap = v.find_all("span", id="zoom")
        for v1 in word_wrap:
            p = v1.find_all("p")
            for v2 in p :
                if not str(v2).__contains__("strong"):
                    p_list.append(v2.text)
    for v in p_list:
        print(v)
