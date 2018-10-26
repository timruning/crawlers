import json
import time

import requests
from bs4 import BeautifulSoup


def get_proxy_list():
    file = open("../proxy/proxy.txt", "r")
    lines = file.read().split("\n")
    result = []
    currenttime = time.time()
    for line in lines:
        line = line.strip()
        if "".__eq__(line):
            continue
        tmp = line.split("\t")
        ip = tmp[1]
        ht = tmp[0]
        # time_stamp = time.mktime(time.strptime(tmp[5], "%Y-%m-%d"))
        # if currenttime - time_stamp < 30 * 24 * 60 * 60:
        result.append([ht, ip, currenttime])
    file.close()
    return result


def get_proxy_index(proxy_list):
    index = 0
    while True:
        currenttime = time.time()
        if currenttime - proxy_list[index][2] > 2:
            proxy_list[index][2] = currenttime
            tmp = proxy_list[index]
            proxy_list[index] = proxy_list[len(proxy_list) - 1]
            proxy_list[len(proxy_list) - 1] = tmp
            return len(proxy_list) - 1
        index += 1
        if index == len(proxy_list):
            time.sleep(2)
            index = 0


def get_request(url, proxy_list):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Host": "www.fzyshcn.com",
        "Referer": "http://www.fzyshcn.com/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
    }
    get_proxy_index(proxy_list)
    proxy = {proxy_list[len(proxy_list) - 1][0]: proxy_list[len(proxy_list) - 1][1]}
    return requests.get(url=url, headers=headers, proxies=proxy, timeout=2)


if __name__ == '__main__':
    proxy_list = get_proxy_list()
    url = "http://www.fzyshcn.com/shehui/"

    suc = True
    menu_t = []
    index = 0
    while suc:
        try:
            req = get_request(url=url, proxy_list=proxy_list)
            text = req.content.decode("gbk")
            bf = BeautifulSoup(text)
            menu = bf.find_all("div", "menu_t")

            for v in menu:
                a = v.find_all("a")
                for i in a:
                    title = i.text
                    href = i.get("href")
                    class_ = i.get("class")
                    if class_ is None:
                        menu_t.append([title, href])
            req.close()
            suc = False
        except:
            print(index, "ERROR", url)
            index += 1

    index_url = []
    for v in menu_t:
        menu = v[0]
        url = v[1]
        suc = True
        index = 0
        while suc:
            try:
                req = get_request(url=url, proxy_list=proxy_list)
                text = req.content.decode("gbk")
                bf = BeautifulSoup(text)
                url_list = bf.find_all("div", class_="epages")
                for v1 in url_list:
                    a = v1.find_all("a")
                    hre1 = None
                    max = 1
                    for v2 in a:
                        text = v2.text
                        if str.isnumeric(text):
                            if int(text) > max:
                                max = int(text)
                        href = v2.get("href")

                        if href is not None and hre1 is None:
                            tmp = href.split("/")[:-1]
                            hre1 = "/".join(tmp)
                    index_url.append([menu, hre1 + "/index.html"])
                    for i in range(2, max + 1):
                        index_url.append([menu, hre1 + "/%d.html" % i])

                suc = False
                req.close()
            except:
                print(index, "bad req", v)
                index += 1
    host = "http://www.fzyshcn.com"

    xwt_list = []
    for v in index_url:
        menu = v[0]
        url = host + v[1]
        suc = True
        index = 0
        while suc:
            try:
                req = get_request(url=url, proxy_list=proxy_list)
                text = req.content.decode("gbk")
                bf = BeautifulSoup(text)
                xwt = bf.find_all("div", class_="xwt")
                for v1 in xwt:
                    xwt_a = v1.find_all("div", class_="xwt_a")
                    a = xwt_a[0].find_all("a")[0]
                    href = a.get("href")
                    title = a.text
                    xwt_b = v1.find_all("div", class_="xwt_b")[0].text
                    xwt_c = v1.find_all("div", class_="xwt_c")[0].text
                    xwt_list.append([menu, href, title, xwt_b, xwt_c])
                suc = False
            except:
                print(index, "error\t", v)
                index += 1

    title_file = open("../data/text/fzysh_title.txt", "w")
    for v in xwt_list:
        title_dic = {
            "menu": v[0],
            "url": v[1],
            "title": v[2],
            "abstract": v[3],
            "time": v[4][5:]
        }
        js = json.dumps(title_dic)
        title_file.write(str(js) + "\n")

    content_file = open("../data/text/fzysh_content.txt", "w")

    for v in xwt_list:
        title_dic = {
            "menu": v[0],
            "url": v[1],
            "title": v[2],
            "abstract": v[3],
            "time": v[4][5:]
        }
        suc = True
        index = 0
        while suc:
            try:
                req = get_request(title_dic["url"], proxy_list=proxy_list)
                text = req.content.decode("gbk")
                bf = BeautifulSoup(text)
                left1_d = bf.find_all("div", class_="left1_d")
                content_list = []
                for v1 in left1_d:
                    word_wrap = v1.find_all("span", id="zoom")
                    for v12 in word_wrap:
                        p = v12.find_all("p")
                        for v23 in p:
                            if not str(v23).__contains__("strong"):
                                content_list.append(v23.text)

                if len(content_list) > 0:
                    title_dic["content"] = "\u0001".join(content_list)
                    js = json.dumps(title_dic)
                    content_file.write(str(js) + "\n")
                suc = False
            except:
                print(index, v, suc)
                index += 1
