from flask import Flask, render_template, request
import re
from bs4 import BeautifulSoup
import urllib.request, urllib.response, urllib.error
import sqlite3
import spider
washSalary = re.compile(r'(.*?)-(.*?)元/天')
washSalary2 = re.compile(r'(\d\d?)-(\d\d?)K')
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
city_pin = {
    '100010000': '全国',
    '广州':'guangzhou',
    '北京':'beijing',
    '上海':'shanghai',
    '成都':'chengdu',
    '深圳':'shenzhen',
    '杭州': 'hangzhou'
}

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():  # put application's code here
    print("测试 hello world")
    return render_template("index.html")


@app.route('/welcome1.html')
def welcome1():
    cityname = request.args['city']  # 城市
    if cityname == '':
        cityname = '100010000'
    msalary, Msalary, keylist = getBasicInfo(cityname)
    city = city_pin[cityname]
    ImgSrc = []
    for i in range(0, 8):
        src = "static/assets/img/slide/wordInfo" + str(i) + ".png"
        ImgSrc.append(src)
    AreaInfo = getAreaData()
    return render_template("welcome1.html", ImgSrc=ImgSrc, msalary=msalary, Msalary=Msalary, city=city,
                           AreaInfo=AreaInfo)


@app.route('/member-list.html')
def memberlist():
    #  cityname = request.args['city']  # 城市
    print("获取到的城市名字前一句")
    cityname = request.values.get('city')
    print("获取到的城市名字为：%s" % cityname)
    if cityname == '' or cityname == None:
        cityname = '100010000'
        city = '全国'
    else:
        city = cityname
        cityname = city_pin[cityname]
    msalary, Msalary, keylist = getBasicInfo(cityname)

    return render_template("member-list.html", msalary=msalary, Msalary=Msalary, city=city)



@app.route('/welcome.html')
def basInfo():
    jobName = request.values.get('jobName')
    if jobName == None:
        jobName = '后端开发'
    else:
        if spider.jobIsExist(jobName) == 0:
            print("该职业不存在，正在调取爬虫爬取请稍后")
            spider.main(jobName)
    AreaInfo = getAreaData(jobName)
    degree = getDegree(jobName)
    salary, degreeSal = getSalary(jobName)
    expDes, expdata = getExp(jobName)
    return render_template("welcome.html", AreaInfo=AreaInfo, degree=degree, salary=salary, expDes=expDes, expdata=expdata, degreeSal=degreeSal)


@app.route('/test')
def test():
    print('进入test')
    result = request.values.get('username')
    if result != None:
        pass  # 才进行下一步，避免没必要的执行
    print("用户名是：%s" % result)
    return render_template('jobMatch.html')


@app.route('/match', methods=['GET', 'POST'])
def match():
    print("进入match")
    area = request.values.get('province')
    degree = request.values.get('degree')
    techs = request.values.get('userTech').split(' ')
    expSal = request.values.get('salary')
    expSal = expSal.split(' ')
    searchRes = matchBest(area, degree, techs, expSal)
    print("这是获取的消息：")
    print(area, degree, techs, expSal)

    print("这是match的方法")
    print(searchRes)
    result = request.values.get('username')
    if len(searchRes) > 0:
        return render_template("matchResult.html", searchRes=searchRes)
    else:
        return render_template("error.html")
    print("用户名是：%s" % result)



def getBasicInfo(cityname="100010000"):
    if (cityname == "100010000"):
        url = "https://www.zhipin.com/?city=" + cityname + "&ka=city-sites-" + cityname
    else:
        url = "https://www.zhipin.com/" + cityname + '/'
    html = askUrl(url)
    basicJob = re.compile(r'<p class="name">(.*?)</p>')
    basicSalary = re.compile(r'<p class="salary">(\d*?-\d*.).*?</p>')
    # file = open("./templates/basicBoss.html", "rb") 测试用
    # html = file.read()  测试用

    soup = BeautifulSoup(html, "html.parser")
    jobInfo = []  # 放置不同的信息

    for item in soup.find_all('div', class_="common-tab-box merge-city-job"):
        item = str(item)
        EachInfo = []
        name = re.findall(basicJob, item)
        # print(name)
        salary = re.findall(basicSalary, item)
        # print(salary)
        for i in range(len(name)):
            if (i % 9 == 0 and i != 0):
                jobInfo.append(EachInfo)
                EachInfo = []
            job = []
            job.append(name[i])
            job.append(salary[i])
            EachInfo.append(job)
    msalary = []
    Msalary = []
    keylist = []
    for job in jobInfo:
        for Info in job:
            keylist.append(Info[0])
            money = Info[1].replace('K', '').split('-')
            msalary.append(int(money[0]))
            Msalary.append(int(money[1]))
    print('最低工资为', msalary)
    print('最高工资为', Msalary)
    return msalary, Msalary, keylist


def askUrl(url):
    head = {
        # 伪装用户代理，以免被人发现我们是爬虫
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"

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


def getAreaData(jobName='后端开发'):
    AreaInfo = []
    distreet = []
    conn = sqlite3.connect('jobs.db')
    cur = conn.cursor()
    sql0 = "select distinct area from jobsInfo where jobtype='" + jobName + "' group by area"
    areas = cur.execute(sql0)
    for area in areas:
        tmpdic = {'地区': area[0]}
        distreet.append(tmpdic)
    sql = "select depoloma,count(depoloma) from jobsInfo where jobtype='" + jobName + "'group by area,depoloma"  # 总体概览
    datas = cur.execute(sql)
    tmp = []
    i = 0
    k = 0
    for data in datas:
        tmp.append(data)
        i = i + 1
        if i == 4:
            dictmp = dict(tmp)
            distreet[k].update(dictmp)
            AreaInfo.append(distreet[k])
            k = k + 1
            tmp = []
            i = 0
    cur.close()
    conn.close()
    return AreaInfo


def getDegree(jobName='后端开发'):
    conn = sqlite3.connect('jobs.db')
    cur = conn.cursor()
    sql = "select count(depoloma) as value, depoloma as name from jobsInfo where jobtype='" + jobName + "' group by depoloma"
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
    cur.close()
    conn.close()
    return result



def getSalary(jobName='后端开发'):
    conn = sqlite3.connect('jobs.db')
    cur = conn.cursor()
    sql = "select salary,depoloma from jobsInfo where depoloma!='高中' and jobtype='" + jobName + "'"
    result = cur.execute(sql)
    salary = []
    d2s = {}
    i = 0
    for info in result:
        i = i + 1
        # print(info)
        fmoney = re.findall(washSalary, info[0])
        tmp = []
        if len(fmoney) == 0:
            fmoney = re.findall(washSalary2, info[0])
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
            # print("还未更改时的数据：")
            # print(fmoney)
            tmp.append((int(fmoney[0][0]) * 30) / 1000)
            tmp.append((int(fmoney[0][1]) * 30) / 1000)
            tmp.append((tmp[0]+tmp[1]) // 2)
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
    # print("以下是转化过后的列表")
    # print(slist)
    return SalaryInfo, slist

def getExp(jobName='后端开发'):
    conn = sqlite3.connect('jobs.db')
    cur = conn.cursor()
    sql = "select experience, count(experience) from jobsInfo where jobtype='" + jobName + "'group by experience"

    result = cur.execute(sql)
    descri = []
    data = []
    for item in result:
        descri.append(item[0])
        data.append(item[1])
    cur.close()
    conn.close()
    return descri, data



def matchBest(area, degree, techs, expSal):
    conn = sqlite3.connect('jobs.db')
    cur = conn.cursor()
    #  实现一个sql， 首先搜索对应地区， 实现模糊搜索 技术
    sql = "select * from jobsInfo where area='" + area + "'"
    result = cur.execute(sql)
    joblist = []
    expSallow = int(expSal[0])
    expSalhigh = int(expSal[1])
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
        if low >= expSallow and expSalhigh <= high:
            resultJobs.append(job)
    # print("resultJobs的内容是：")
    # for job in resultJobs:
    #     print(job)
    cur.close()
    conn.close()
    return resultJobs

if __name__ == '__main__':
    app.run()
    # spider.main('python')
