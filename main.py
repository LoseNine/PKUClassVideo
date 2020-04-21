import requests
from urllib.parse import quote
import os
import random
import threading
import configparser

class PKUVideo:
    def __init__(self,u,p):
        self.username=u
        self.password=p

        self.session=requests.session()
        self.setHeaders()


    def setHeaders(self):
        headers={
            'Referer':'https://portal.pku.edu.cn/portal2017/login.jsp',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
        }
        self.session.headers=headers

    def getloginPage(self):
        url='https://iaaa.pku.edu.cn/iaaa/oauth.jsp'
        params={
            'appID': 'portal2017',
            'appName': quote('北京大学校内信息门户新版'),
            'redirectUrl': 'https://portal.pku.edu.cn/portal2017/ssoLogin.do'
        }
        html=self.session.get(url,params=params)
        if html.status_code==200:
            self.doLogin()
        else:
            print('获取登录页失败！')

    def doLogin(self):
        url='https://iaaa.pku.edu.cn/iaaa/oauthlogin.do'
        data={
            'appid': 'portal2017',
            'userName': self.username,
            'password': self.password,
            'randCode': '',
            'smsCode': '',
            'otpCode': '',
            'redirUrl': 'https://portal.pku.edu.cn/portal2017/ssoLogin.do'
        }
        html=self.session.post(url,data)
        #print(html.text)
        if 'success' in html.text:
            token=html.json()['token']
            print('[SUCCESS]token:',token)
            self.stuAllpage(token)
        else:
            print('[doLogin]login token error')

    def stuAllpage(self,token):
        url='https://portal.pku.edu.cn/portal2017/ssoLogin.do'
        params={
            '_rand': random.random(),
            'token': token
        }
        html=self.session.get(url,params=params)
        #print(html.text)
        self.getCourses()


    def getCourses(self):
        #获取所有课程数据
        url='https://portal.pku.edu.cn/portal2017/util/appSysRedir.do?appId=liveclass'
        self.session.get(url)

        url='http://liveclass.pku.edu.cn/course/ctrl/course/retrCourses.do'
        json_data=self.session.post(url)
        if json_data.status_code==200:
            myClasses=json_data.json()['myCourses']
            if len(myClasses)==0:
                print('暂无直播课')
                exit(0)
            #print(myClasses)
            for c in myClasses:
                cname=c['KCMC']
                zxjhbh=c['ZXJHBH']
                jsap=c['JSAP']
                self.getClassinfo(zxjhbh)
        else:
            print('[getCourses]获取课程数据失败')


    def getClassinfo(self,zxjhbh):
        params={'zxjhbh':zxjhbh}
        url='http://liveclass.pku.edu.cn/course/ctrl/course/retrCourseHis.do'
        html=self.session.get(url,params=params).json()
        coursename=html['courseName']
        teachername=html['teacherName']
        courseid=html['courseId']
        rows=html['rows']
        print('[INFO]课程名：{}\n授课老师：{}\n课程ID：{}\n已上课程：{}节\n'.format(
            coursename,teachername,courseid,len(rows)
        ))
        for r in rows:
            skrq=r['SKRQ']
            skjc=r['SKJC']
            skzc=r['SKZC']
            skxq=r['SKXQ']
            sj=r['SJ']#时间
            skdd=r['SKDD']

            self.getCoursem3u8(skdd,skjc,skrq,zxjhbh,coursename,sj)


    def getCoursem3u8(self,skdd,skjc,skrq,zxjhbh,coursename,sj):
        """
        skdd:
        skjc:
        skrq:
        zxjhbh:
        """
        url='http://liveclass.pku.edu.cn/course/ctrl/course/redirectToCourserReplay.do'
        data={
            'skdd':skdd,
            'skjc':skjc,
            'skrq':skrq,
            'zxjhbh':zxjhbh
        }
        html=self.session.post(url,data=data)
        #print(html.text)
        if html.status_code==200:
            mu=html.json()['url']
            print('[SUCCESS]',mu)
            print('Downloadin....')
            self.downloadMU(mu,coursename,sj)
        else:
            print('[getCoursem3u8]M3U8 get error!')

    def downloadMU(self,url,coursename,sj):
        pathClass='./'+coursename
        if not os.path.exists(coursename):
            os.mkdir(pathClass)

        with open("{}.m3u8".format(pathClass+'/'+str(sj)),'w')as f:
            f.write(self.session.get(url).text)

        thread=threading.Thread(target=self.downloadVodeo,args=(pathClass+'/'+str(sj),url))
        thread.start()
        #self.downloadVodeo(pathClass+'/'+str(sj),url)
        print('下载完毕：{} {}'.format(coursename,sj))


    def downloadVodeo(self,textPath,url:str):
        #http://replay.pku.edu.cn/liveclass/09103/2020021705/v.m3u8
        #http://replay.pku.edu.cn/liveclass/09103/2020021705/v0.ts

        rurl=url.rsplit('/',1)[0]
        #print(url)

        ts=[]
        with open(textPath+'.m3u8','r',encoding='utf-8')as f:
            lines=f.readlines()
            for line in lines:
                line=line.strip().replace(' ','')
                if line.startswith('v'):
                    ts.append(line)

        for t in ts:
            turl=rurl+'/'+t
            print('downloading:'+turl)
            self.downloadts(turl,textPath)



    def downloadts(self,url,path):
        #http://replay.pku.edu.cn/liveclass/09103/v0.ts
        # if not os.path.exists(path):
        #     os.mkdir(path)
        #print(url,path)
        dirname=path+'.mp4'
        with open(dirname,'ab+')as f:
            f.write(self.session.get(url).content)

    def run(self):
        self.getloginPage()

def getConfig():
    curpath = os.path.dirname(os.path.realpath(__file__))
    cfgpath = os.path.join(curpath, "config.ini")
    #print(cfgpath)

    # 创建管理对象
    conf = configparser.ConfigParser()

    # 读ini文件
    conf.read(cfgpath, encoding="utf-8")

    # conf.read(cfgpath)  # python2

    # 获取所有的section
    sections = conf.sections()

    #print(sections)

    items = conf.items('studentInfo')
    return items[0][1],items[1][1]

if __name__ == '__main__':
    u,p=getConfig()

    pku=PKUVideo(u,p)
    pku.run()