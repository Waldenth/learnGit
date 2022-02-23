import requests
from bs4 import BeautifulSoup
import re


class Posting:
    def __init__(self, username, floorNumber, postingContent):
        self.username = username
        self.floorNumber = floorNumber
        self.postingContent = postingContent


class tiebaCrawler:
    # 类初始化
    def __init__(self, baseURL, onlySeeLZ):
        # onlySeeLZ:是否只看楼主;0关闭,1开启; floorTag :是否写入楼分隔符;0关闭,1开启

        # 目标贴链接地址
        self.baseURL = baseURL
        # 是否只看楼主
        self.seeLZ = '?see_lz='+str(onlySeeLZ)
        # headers: 请求头,绕过简单反爬机制
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        }
        self.ignorePostingContent = True
        self.floorNumberRE = re.compile("[0-9]{1,12}楼")
        self.startPageIndex = 91
        self.endPageIndex = 200
        self.getAllReplies = False  # 如果只爬取部分页面需要设置为False
        self.isNormal = True
        self.currentPageIndex = 1

        self.postings = []

        # 全局file变量，文件写入操作对象
        self.fileName = "_fromPage"+str(self.startPageIndex)
        self.suffix = ".txt"

    def getPageData(self, pageIndex):
        if(self.isNormal is False):
            info = "\nERROR: getPageData(): The process work status is unnormal, will abort soon."
            print("\033[0;31m%s\033[0m" % info)
            return None
        try:
            self.currentPageIndex = pageIndex
            url = self.baseURL+self.seeLZ+"&pn="+str(pageIndex)
            responseData = requests.get(url, headers=self.headers, timeout=5)
            return responseData.text
        except:
            info = "\nERROR: getPageData(): Get Page [" + \
                str(pageIndex)+"] Data Error"
            print("\033[0;31m%s\033[0m" % info)
            self.isNormal = False
            return None

    def getNeededData(self, pageData):
        if(self.isNormal is False):
            info = "\nERROR: getNeededData(): The process work status is unnormal, will abort soon."
            print("\033[0;31m%s\033[0m" % info)
            return
        if(pageData != None):
            soup = BeautifulSoup(pageData, "lxml")
            floorPostings = soup.find_all(
                name="div", attrs={"class": "l_post l_post_bright j_l_post clearfix"})

            if(len(floorPostings) != 0):
                for item in floorPostings:
                    username = item.find(name="li", attrs={
                        "class": "d_name"}).text.replace('\n', '')
                    floorNumber = item.find(name="span", attrs={
                        "class": "tail-info"}, text=self.floorNumberRE).text.replace('\n', '')
                    self.postings.append(Posting(username, floorNumber, None))
                info = "Page ["+str(self.currentPageIndex)+"/"+str(self.endPageIndex) + \
                    "] has been completed, [" + \
                    str(len(floorPostings))+"] replies, total " + \
                    str(len(self.postings))+" replies."
                print(info, end='\r')
            else:
                info = "\nERROR: getNeededData(): Can not find needed data in the page. This process will abort."
                self.isNormal = False
                print("\033[0;31m%s\033[0m" % info)
        else:
            print("\033[0;31m%s\033[0m" %
                  "\nERROR: getNeededData(): The pageData is None")

    def firstPage(self):
        if(self.isNormal is False):
            return
        pageData = self.getPageData(self.startPageIndex)

        if pageData is None:
            info = "\nERROR: firstPage(): Can not get page info, your IP might be banned."
            print("\033[0;31m%s\033[0m" % info)
            self.isNormal = False
            return
        else:
            soup = BeautifulSoup(pageData, 'lxml')
            title = soup.find(name="title")

            if(title != None):
                self.fileName = title.text+self.fileName
                info = "The data will be storaged in \""+self.fileName+self.suffix+"\""
                print("\033[0;32m%s\033[0m" % info)
            else:
                info = "\nWARNING: firstPage(): Can not get title from the first page , will use default filename [" + \
                    self.fileName+self.suffix+"]."
                print("\033[0;33m%s\033[0m" % info)

            postInfo = soup.find(name="li", attrs={"class": "l_reply_num"})

            if(self.getAllReplies):
                if(postInfo is None):
                    self.isNormal = False
                    info = "\nERROR: firstPage(): Can not get post num and set end page num , your IP might be banned."
                    print("\033[0;31m%s\033[0m" % info)
                    return
                else:
                    postInfo = re.findall(r'\d+', postInfo.text)

            if(postInfo is None or len(postInfo) != 2):
                info = "\nWARNING: firstPage(): The page info maybe incorrect. The end page Index will set as " + \
                    str(self.endPageIndex)
                print("\033[0;33m%s\033[0m" % info)
            if(self.getAllReplies):
                if(len(postInfo) >= 2):
                    info = "Total replies: " + str(postInfo[0])
                    print("\033[0;32m%s\033[0m" % info)
                    info = "Total pages: "+str(postInfo[1])
                    print("\033[0;32m%s\033[0m" % info)
                    self.endPageIndex = postInfo[1]
            self.getNeededData(pageData)

    def writeData(self):
        if(len(self.postings) > 0):
            if(self.isNormal is False):
                self.fileName = self.fileName + \
                    "_toPage"+str(self.currentPageIndex)
                info = "\nATTENTION: writeDara(): The work process has encountered some errors and the task is not fully completed\nThe save file will be " + \
                    self.fileName + self.suffix
                print("\033[0;33m%s\033[0m" % info)
            with open(self.fileName+self.suffix, 'w', encoding="utf-8") as f:
                if(self.ignorePostingContent):
                    for posting in self.postings:
                        f.write(str(posting.floorNumber) +
                                "    :    "+str(posting.username)+"\n")

    def start(self):
        self.firstPage()
        for i in range(int(self.startPageIndex)+1, int(self.endPageIndex)+1):
            if(self.isNormal):
                pageData = self.getPageData(i)
                self.getNeededData(pageData)
            else:
                break
        self.writeData()
        if(self.isNormal):
            print("\033[0;32,47m%s\033[0m" % "\nSuccess!")
        else:
            print("\033[0;31;47m%s\033[0m" %
                  "\nWrite Complete! But something went wrong.")


# 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
# https://tieba.baidu.com/p/7712845390
if __name__ == "__main__":
    print("Please input the url of the WebPage [tieba.baidu.com]")
    baseURL = input()
    baseURL = str(baseURL)
    print("Please confirm the url : "+"["+baseURL+"]")
    seeLZ = '0'  # 关闭只看楼主
    crawler = tiebaCrawler(baseURL, seeLZ)
    crawler.start()
