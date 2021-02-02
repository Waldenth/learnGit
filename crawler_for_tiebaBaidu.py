# 百度贴吧贴子爬取
# Author: Aaron(Waldenth)
# 2021-02-02
# Attention: 正则表达式可能需要随百度贴吧页面升级而更新,不保证长期有效
# fix bug :  使用贴吧数据库的楼层作为楼层标准

import requests
import re
import time

# html清洗处理类
class Tool:
    #去除img标签
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #换行的标签转义\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #制表符<td>转义\t
    replaceTD= re.compile('<td>')
    #段落开头-> "\n  "
    replacePara = re.compile('<p.*?>')
    #换行符或双换行符转义\n
    replaceBR = re.compile('<br><br>|<br>')
    #剔除其余标签
    removeExtraTag = re.compile('<.*?>')

    #贴子标题
    titleStr='title="百度贴吧" /><title>(.*?)</title>' 
    #贴子页数
    pageNumStr='<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>'
    #贴子内容
    postContentStr='<div id="post_content_.*?>(.*?)</div>'
    #贴子作者
    postAuthorStr='<li class="d_name" data-field=.*?>(.*?)</li>'
    #贴子在贴吧数据库中的楼层
    floorStr='class="tail-info">([0-9]{1,8}楼)</span><span'

    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        #strip()将前后多余内容删除
        return x.strip()

    def filter(self,reStr,page,isReturnList):
        pattern=re.compile(reStr,re.S)
        if isReturnList==0:
            result = re.search(pattern,page)
        else:
            result=re.findall(pattern,page)
        return result



# 百度贴吧帖页爬虫类
class CrawlerBDTB:
    
    # 类初始化
    def __init__(self,baseURL,onlySeeLZ,floorTag): 
        # onlySeeLZ:是否只看楼主;0关闭,1开启; floorTag :是否写入楼分隔符;0关闭,1开启
        
        #目标贴链接地址
        self.baseURL = baseURL
        #是否只看楼主
        self.seeLZ = '?see_lz='+str(onlySeeLZ)
        #HTML标签剔除工具类对象
        self.tool = Tool()
        #全局file变量，文件写入操作对象
        self.file = None
        #楼层标号，初始为1 (作废:百度抽楼,这是按照爬到的现存的贴子数计算楼层)
        self.floor = 1
        #默认的标题
        self.defaultTitle = "DataSet"
        #是否写入楼分隔符的标记
        self.floorTag = floorTag
        # headers: 请求头,绕过简单反爬机制
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        }

    # 获取目标贴标题
    def getTitle(self,page):
        
        #获取标题
        result=self.tool.filter(self.tool.titleStr,page,0)
        if result:
            #如果存在,则返回标题
            return result.group(1).strip()
        else:
            print("Log: Failed to get title, the default title <"+self.defaultTitle+ "> will be used.")
            return None
   
   # 设置导出文件标题
    def setFileTitle(self,title):
        #如果标题不是为None，即成功获取到标题
        if title is not None:
            self.file = open(title + ".csv","w+")
        else:
            self.file = open(self.defaultTitle + ".csv","w+")

    # 获取目标贴指定页数据
    def getPageData(self,pageIndex): 
        # pageIndex : 页索引号
        
        try:
            url = self.baseURL+ self.seeLZ + '&pn=' + str(pageIndex)
            responseData=requests.get(url,headers=self.headers,timeout=5)
            return responseData.text
        except:
            print("Error: Get Page Data Error")
            return None

    # 获取目标贴总页数
    def getPageNum(self,page):
        #page: 页面

        #帖子页数的正则表达式
        result=self.tool.filter(self.tool.pageNumStr,page,0)
        if result:
            return result.group(1).strip()
        else:
            print("Error: Failed to get the number of pages")
            return None
    
    # 获取页面每一层楼所需内容
    def getContent(self,page,needMainText):
        # needMainText: 获取贴子主体信息;0只获取作者,1额外获取贴子内容
        if needMainText==0:
            items=self.tool.filter(self.tool.postAuthorStr,page,1)
            floors=self.tool.filter(self.tool.floorStr,page,1)
            length=len(items)
            if len(items)!=len(floors):
                print("Warning: floor and text is not matched, it's very likely that something went wrong!")
                length=(len(items) if len(items)<=len(floors) else len(floors))
            contents=[]
            for i in range(0,length):
                content = "\n"+self.tool.replace(floors[i])+"\n"+self.tool.replace(items[i])+"\n"
                contents.append(content.encode('utf-8'))
            return contents
        else:
            authorItems=self.tool.filter(self.tool.postAuthorStr,page,1)
            floors=self.tool.filter(self.tool.floorStr,page,1)
            mainTextItems=self.tool.filter(self.tool.postContentStr,page,1)
            length=len(authorItems)
            if len(authorItems)!=len(mainTextItems) or len(authorItems)!=len(floors) or len(mainTextItems)!=len(floors):
                print("Warning: floor and text and author-info is not matched, it's very likely that something went wrong!")
                length=min(len(authorItems),min(len(mainTextItems),len(floors)))
            print("Log: length is "+str(length))
            contents=[]
            for i in range(0,length):
                content = "\n"+self.tool.replace(floors[i])+"\n"+self.tool.replace(authorItems[i])+"\n"+self.tool.replace(mainTextItems[i])+"\n"
                contents.append(content.encode('utf-8'))
            return contents
    
    def writeData(self,contents):
        #向文件写入每一楼的信息
        for item in contents:
            if self.floorTag == '1':
                #楼之间的分隔符
                floorLine = "\n" + str(self.floor) + "L:"
                self.file.write(floorLine)
            try:  
                self.file.write(str(item,encoding = "utf-8"))
            except:
                print("encoding error!")
            self.floor += 1

    def start(self):
        firstPage=self.getPageData(1)
        pageNum = self.getPageNum(firstPage)
        title = self.getTitle(firstPage)
        self.setFileTitle(title)
        if pageNum == None:
            print ("URL is invalid")
            return
        try:
            print ("This post has " + str(pageNum) + "page(s)")
            for i in range(1,int(pageNum)+1):
                print ("Now writing the data of page[" + str(i)+"]" )
                page = self.getPageData(i)

                # needMainText=0,不开启获取贴子主体信息
                contents = self.getContent(page,0)
                self.writeData(contents)
        #出现写入异常
        except IOError:
            print ("IO Error" )
        finally:
            time.sleep(3)
            self.file.close()
            print ("success!")


if __name__ == "__main__":
    print("Please input the url of the WebPage [tieba.baidu.com]")
    baseURL=input()
    baseURL=str(baseURL)
    print("Please confirm the url : "+baseURL)
    seeLZ = '0' # 关闭只看楼主
    floorTag = '0' # 楼层分隔符,由于采用贴吧数据库楼层信息,作废
    crawler = CrawlerBDTB(baseURL,seeLZ,floorTag)
    crawler.start()