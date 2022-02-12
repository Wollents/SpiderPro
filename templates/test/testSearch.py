# -*- codeing = utf-8 -*-
# @Time : 2022/1/21 16:51
# @Author : Warren
# @File : testSearch.py
# @Software : PyCharm
from bs4 import BeautifulSoup
import re
import sqlite3
findsalary = re.compile(r'<span class="red">(.*?)</span>')
finddegree = re.compile(r'</em>(\D*?)</p>.*?<div class="info-publis">', re.S)  # 匹配我们的学历
findTechKW = re.compile(r'<span class="tag-item">(.*?)</span>', re.S)
findWellfare = re.compile(r'<div class="info-desc">(.*?)</div>', re.S)
findIsExperience = re.compile(r'<p>(\d.*?)<em class="vline"></em>\D*?</p>.*?<div class="info-publis">', re.S)
findarea = re.compile(r'<span class="job-area">(.*?)(·.*?)?</span>', re.S)  # 只要第一个
findCompany = re.compile(r'<div class="company-text">.*?<a .*?>(.*?)</a>', re.S)
city_code = {
    '北京': 'c101010100',
    '上海': 'c101020100',
    '广州': 'c101280100',
    '深圳': 'c101280600',
    '杭州': 'c101210100',
    '西安': 'c101110100',
    '武汉': 'c101200100',
    '成都': 'c101270100',
    '南京': 'c101190100'
}
def main():
    jobs = getBasicInfo()
    print("主函数")
    # for job in jobs:
    #    print(job)
    saveDB = "jobstest.db"
    inisql = '''
        create table if not exists jobsInfo
        (
        id integer primary key autoincrement,
        jobType text,
        company text,
        area text,
        salary text,
        depoloma text,
        techs varchar,
        bonus varchar,
        experience text
        )
    '''
   #  baseUrl = "https://www.zhipin.com/c101010100/?query=后端开发&page="
    save2db(saveDB, jobs, inisql)



def getBasicInfo():

    file = open("../test/boss.html", "rb") # 测试用
    html = file.read()  # 测试用
    soup = BeautifulSoup(html, "html.parser")

    jobs = []  # 放置不同的信息
    jobTye = ''
    dic = soup.select("input[class='ipt-search']")[0].attrs
    jobTye = dic.get("value")
    print("职业类型是")
    print(jobTye)
    for item in soup.find_all('div', class_="job-primary"):
        data = []
        data.append(jobTye)
        item = str(item)
        company = re.findall(findCompany, item)
        # print("找到的工资名称为：", company)
        data.append(company[0])
        area = re.findall(findarea, item)[0]
        data.append(area[0])

        salary = re.findall(findsalary, item)
        data.append(salary[0])
        degree = re.findall(finddegree, item)
        data.append(degree[0])

        print("爬取到的的学历为：%s" % degree[0])  # 学历测试
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
    if dic.get('class') == 'next disabled':
        print("最后一页啦！宝贝")
    else:
        print("不是最后一页")
    for job in jobs:
        print(job)
    return jobs
def save2db(saveDB, jobs, inisql):
    print('创建输出库')
    Ini_db(saveDB, inisql)
    conn = sqlite3.connect(saveDB)
    cur = conn.cursor()
    for job in jobs:
        for i in range(len(job)):
            if i == 2:
                job[i] = ' '.join(job[i])
            job[i] = '"' + str(job[i]) + '"'
        sql = '''
            insert into jobsInfo
            (jobtype, company, salary, depoloma, techs, bonus, experience,area)
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

def test():
    for key,value in city_code.items():
        print("正在爬取 %s 的内容" % key)
        baseUrl = "https://www.zhipin.com/" + value + "/?query=后端开发&page="
        print(baseUrl)

if __name__ == '__main__':
    main()