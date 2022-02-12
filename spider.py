# -*- codeing = utf-8 -*-
# @Time : 2022/1/21 16:42
# @Author : Warren
# @File : spider.py
# @Software : PyCharm
import urllib.request, urllib.response, urllib.error
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import random
import time
import sqlite3
from matplotlib import pyplot as plt  # 绘图， 数据可视化
from wordcloud import WordCloud
from PIL import Image                 # 图片处理
import numpy as np

findsalary = re.compile(r'<span class="red">(.*?)</span>')
finddegree = re.compile(r'</em>(\D*?)</p>.*?<div class="info-publis">', re.S)  # 匹配我们的学历
findTechKW = re.compile(r'<span class="tag-item">(.*?)</span>', re.S)
findWellfare = re.compile(r'<div class="info-desc">(.*?)</div>', re.S)
findIsExperience = re.compile(r'<p>(\d.*?)<em class="vline"></em>\D*?</p>.*?<div class="info-publis">', re.S)
findarea = re.compile(r'<span class="job-area">(.*?)(·.*?)?</span>', re.S)
findCompany = re.compile(r'<div class="company-text">.*?<a .*?>(.*?)</a>', re.S)
city_code = {
    '北京': 'c101010100'
}
def main(jobName=''):
    print("你现在已经进入了spider的main方法")
    saveDB = "jobs.db"
    inisql = '''
                create table if not exists jobsInfo
                (
                id integer primary key autoincrement,
                jobtype text,
                area text,
                company text,
                salary text,
                depoloma text,
                techs varchar,
                bonus varchar,
                experience text
                )
            '''
    Ini_db(saveDB, inisql)
    if jobName == '' or jobIsExist(jobName) == 1:
        print("该职业已经存在")
    else:
        for key, value in city_code.items():
            print("正在爬取 %s 的内容" % key)
            baseUrl = "https://www.zhipin.com/" + value + "/?query=" + jobName + "&page="
            jobs = getData(baseUrl)  # 获取到了数据
            save2db(saveDB, jobs)
def askUrl(url):
    head = {
        # 伪装用户代理，以免被人发现我们是爬虫
        "User-Agent": 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12'
    }
    url = urllib.request.Request(url=url, headers=head)
    try:
        response = urllib.request.urlopen(url)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "code"):
            print(e.code)
    return html

def imitateSurf(url, driver):
    driver.get(url)
    html = driver.page_source
    return html

def getData(baseUrl):
    jobs = []
    c = 0
    driver = webdriver.Chrome()

    for i in range(1, 2):
        url = baseUrl + str(i) + "&ka=page-" + str(i)
        html = imitateSurf(url, driver)  # 模拟浏览器打开网页, 返回一个html页面
        print("爬取到第%d页" % i)
        soup = BeautifulSoup(html, "html.parser")
        print(soup.title)
        if str(soup.title) == '<title>请稍后</title>':
            print("正在处理")
            time.sleep(2)
            html = imitateSurf(url, driver)
            soup = BeautifulSoup(html, "html.parser")
            # print("处理后的title为:", soup.title)
        dic = soup.select("input[class='ipt-search']")[0].attrs
        # print("内容为", dic, type(dic))
        jobTye = str(dic.get("value"))
        for item in soup.find_all('div', class_='job-primary'):
            c = c + 1
            data = []
            data.append(jobTye)
            item = str(item)
            area = re.findall(findarea, item)[0]
            data.append(area[0])
            company = re.findall(findCompany, item)
            data.append(company[0])
            salary = re.findall(findsalary, item)
            data.append(salary[0])
            degree = re.findall(finddegree, item)
            # print("这里是spider爬取到的学历 %s" % degree[0])
            data.append(degree[0])
            # print(degree) 学历测试
            techs = re.findall(findTechKW, item)
            data.append(techs)  # 这是一个列表， 用于生成词云
            # for tech in techs:
            #     print(tech, end=' ')
            welfare = re.findall(findWellfare, item)[0]
            if len(welfare) == 0:
                data.append('暂无')
            else:
                data.append(welfare)

            ep = re.findall(findIsExperience, item)
            l = len(ep)
            if l == 0:
                # print('无需 ')
                data.append('无需经验')
            else:
                ep = ep[0]
                if len(ep) > 6:
                    tmp = ''
                    tmp = tmp + ep[-3]
                    tmp = tmp + ep[-2]
                    tmp = tmp + ep[-1]
                    # print(tmp)
                    data.append(tmp)
                else:
                    # print(ep)
                    data.append(ep)
            # print(ep)
            jobs.append(data)
        dic = soup.select("a[ka='page-next']")[0].attrs
        if len(dic.get('class')) == 2:
            break
        else:
            print("当前页不是最后一页")
        ran_time = random.randint(1, 5)
        time.sleep(ran_time)  # 休眠，防止被检测出来了
    driver.close()
    print("共获取到%d条数据" % c)
    return jobs


def save2db(saveDB, jobs):
    print('创建输出库')
    conn = sqlite3.connect(saveDB)
    cur = conn.cursor()
    for job in jobs:
        for i in range(len(job)):
            if i == 5:
                job[i] = ' '.join(job[i])
            job[i] = '"' + str(job[i]) + '"'
        sql = '''
            insert into jobsInfo
            (jobtype,area, company, salary, depoloma, techs, bonus, experience)
            values(%s)
        ''' % ",".join(job)
        cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

def Ini_db(saveDB, inisql):
    conn = sqlite3.connect(saveDB)
    cur = conn.cursor()
    cur.execute(inisql)
    conn.commit()
    conn.close()

def getPicture(keylist):
    img = Image.open(r'static/images/TechPic.jpeg')
    img_array = np.array(img)  # 将图片转化成数组
    wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path='msyh.ttc'  # 选择字体 ： C:\Windows\Fonts
    )
    wc.generate_from_text(keylist)  # 导入好我们的分词
    # 绘图
    fig = plt.figure(1)
    plt.imshow(wc)
    plt.axis('off')
    src = "static/images/TechWordPic.png"
    plt.savefig(src, dpi=500)
def picmain():
    conn = sqlite3.connect('jobs.db')
    cur = conn.cursor()
    sql = "select techs from jobsInfo limit 100"
    datas = cur.execute(sql)
    keylist = ''
    for data in datas:
        keylist = keylist + data[0]
    print(keylist)
    cur.close()
    conn.close()
    getPicture(keylist)
def jobIsExist(jobName):
    conn = sqlite3.connect('jobs.db')
    cur = conn.cursor()
    sql = "select distinct jobtype from jobsInfo where jobtype='" + jobName + "'"

    result = cur.execute(sql)
    flag = []
    for item in result:
        flag.append(item[0])
    cur.close()
    conn.close()
    if len(flag) == 0:
        return 0
    else:
        return 1
if __name__ == "__main__":
    main("")