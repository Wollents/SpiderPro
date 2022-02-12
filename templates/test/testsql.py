# -*- codeing = utf-8 -*-
# @Time : 2022/1/22 14:46
# @Author : Warren
# @File : testsql.py
# @Software : PyCharm



import sqlite3
import re

washSalary = re.compile(r'(.*?)-(.*?)元/天')
washSalary2 = re.compile(r'(\d\d?)-(\d\d?)K')
def getAreaData():
    AreaInfo = []
    distreet = []
    conn = sqlite3.connect('../../jobs.db')
    cur = conn.cursor()
    sql0 = "select distinct area from jobsInfo group by area"
    areas = cur.execute(sql0)
    for area in areas:
        tmpdic ={'地区':area[0]}
        distreet.append(tmpdic)
    # print(distreet)
    sql = "select depoloma,count(depoloma) from jobsInfo group by area,depoloma"  # 总体概览
    datas = cur.execute(sql)
    tmp = []
    i = 0
    k = 0
    for data in datas:
        tmp.append(list(data))
        i = i + 1
        if i == 4:
            if tmp[3][0] != '硕士':
                tmp[3][0] = '硕士'
                tmp[1][1] = tmp[1][1] + tmp[3][1]
                tmp[3][1] = 0
            dictmp = dict(tmp)
            distreet[k].update(dictmp)
            AreaInfo.append(distreet[k])
            k = k + 1
            tmp = []
            i = 0
    for info in AreaInfo:
        print(info)
    cur.close()
    conn.close()

    return AreaInfo

def getCount():
    conn = sqlite3.connect('../../jobs.db')
    cur = conn.cursor()
    sql = 'select count(depoloma) as value, depoloma as name from jobsInfo group by depoloma'
    infos = cur.execute(sql)
    tmp = []
    result = []
    dit = {}
    print(infos.description)
    for info in infos:
        tmp1 = ['value']
        tmp1.append(info[0])
        tmp.append(tmp1)
        tmp1 = ['name']
        tmp1.append(info[1])
        tmp.append(tmp1)
        dit = dict(tmp)
        result.append(dit)
    print(result)
def getSalary():
    conn = sqlite3.connect('../../jobs.db')
    cur = conn.cursor()
    sql = 'select salary,depoloma from jobsInfo where depoloma!="高中"'
    result = cur.execute(sql)
    salary = []
    d2s = {}
    i = 0
    for info in result:
        i = i + 1
        # print(info)
        fmoney = re.findall(washSalary, info[0])  # 多少钱一天
        tmp = []
        if len(fmoney) == 0:
            fmoney = re.findall(washSalary2, info[0])
            # print("这里是多少K", fmoney)
            tmp.append(int(fmoney[0][0]))
            tmp.append(int(fmoney[0][1]))
            tmp.append((tmp[0] + tmp[1]) // 2)
            dtmp= {}
            dtmp[info[1]] = tmp
            if d2s.get(info[1]) == None:
                dtmp[info[1]].append(1)
                d2s.update(dtmp)
            else:
                d2s[info[1]][3] = d2s[info[1]][3] + 1
                if tmp[0] < d2s[info[1]][0]:
                    d2s[info[1]][0] = tmp[0]
                if tmp[1] > d2s[info[1]][1]:
                    d2s[info[1]][1] = tmp[1]
                d2s[info[1]][2] = d2s[info[1]][2] + tmp[2]
            salary.append(tmp)
        else:
            # print("还未更改时的数据（d多少钱一天）：")
            # print(fmoney)
            tmp.append((int(fmoney[0][0]) * 30) / 1000)
            tmp.append((int(fmoney[0][1]) * 30) / 1000)
            tmp.append((tmp[0]+tmp[1]) // 2)
            if tmp[0] == 0.3:
                print("还未更改时的数据（d多少钱一天）：")
                print(fmoney)
                print("多少钱一天更改之后的数据")
                print(tmp)
                print("这是该工作的相关信息:  ", info)
            dtmp = {}
            dtmp[info[1]] = tmp
            if d2s.get(info[1]) == None:
                dtmp[info[1]].append(1)
                d2s.update(dtmp)
            else:
                d2s[info[1]][3] = d2s[info[1]][3] + 1
                if tmp[0] < d2s[info[1]][0]:
                    d2s[info[1]][0] = tmp[0]
                if tmp[1] > d2s[info[1]][1]:
                    d2s[info[1]][1] = tmp[1]
                d2s[info[1]][2] = d2s[info[1]][2] + tmp[2]
            salary.append(tmp)
            salary.append(tmp)
    # print(salary)
    for key in d2s.keys():
        d2s[key][2] = d2s[key][2] // d2s[key][3]
    # print("所获得得字典是：")
    # print(d2s)
    # print("总共条数是：%d" %i)
    Smin = 10000
    Smax = -1
    Savr = 0
    for i in range(len(salary)):
        if salary[i][0] < Smin:
            Smin = salary[i][0]
        if salary[i][1] > Smax:
            Smax = salary[i][1]
        Savr = Savr + salary[i][2]
    Savr = Savr // len(salary)
    # print("最大值为：%d   最小值为 %d     平均值为：%d" % (Smax, Smin, Savr))
    SalaryInfo = []
    SalaryInfo.append(len(salary))
    SalaryInfo.append(Smin)
    SalaryInfo.append(Smax)
    SalaryInfo.append(Savr)
    cur.close()
    conn.close()
    # print("以下是测试")
    slist = [['学历水平', '最低工资', '最高工资', '平均工资']]
    for item in d2s.items():
        sltmp = []
        sltmp.append(item[0])
        item[1].pop()
        sltmp.extend(item[1])
        slist.append(sltmp)
    print("以下是转化过后的列表")
    print(slist)
    return SalaryInfo, d2s


def getExp():
    conn = sqlite3.connect('../../jobs.db')
    cur = conn.cursor()
    sql = 'select experience, count(experience) from jobsInfo group by experience'

    result = cur.execute(sql)
    descri = []
    data = []
    for item in result:
        descri.append(item[0])
        data.append(item[1])
    cur.close()
    conn.close()
    return descri, data

def testMatch():
    conn = sqlite3.connect('../../jobs.db')
    cur = conn.cursor()
    sql = '''
        select * from jobsInfo where area='北京' limit 100
    '''
    techs = 'Java Python'.split(' ')
    print(techs)
    result = cur.execute(sql)
    joblist = []
    degree = '本科'
    exp = 14
    for item in result:
        techflag = item[6]
        for tech in techs:
            if tech in techflag and item[5] == degree:
                joblist.append(item)
                break
    resultJobs = []
    for job in joblist:
        money = job[4]
        salary = re.findall(washSalary, money)
        low = high = -1
        if len(salary) == 0:
            salary = re.findall(washSalary2, money)
            low = int(salary[0][0])
            high = int(salary[0][1])
        else:
            low = (int(salary[0][0]) * 30) // 1000
            high = (int(salary[0][1]) * 30) // 1000
        if low < exp and exp < high:
            resultJobs.append(job)
    print("resultJobs的内容是：")
    for job in resultJobs:
         print(job)
    return resultJobs
testMatch()