#dict = {'Name': 'Zara', 'Age': ['1','2','3'], 'Class': 'First','py':'Zara'}
#print([v for k,v in dict.items() if k=='Age'])
import re

class Tool:
    getEachFloor='([0-9]{1-8}楼)(.*?)\n'

    def filter(self,reStr,page,isReturnList):
        pattern=re.compile(reStr,re.S)
        if isReturnList==0:
            result = re.search(pattern,page)
        else:
            result=re.findall(pattern,page)
        return result

if __name__ == "__main__":
    dataFile=open("【23点开启回复】2021年蕾姆吧抢楼活动——祝可爱双子生日快乐！_蕾姆吧_百度贴吧.csv",'r',encoding='UTF-8')
    buffer1="floorIndex"
    buffer2="userName"
    buffer3="\n"
    index=0
    dict={}
    newKV={}
    while buffer1!="":
        buffer1=dataFile.readline().strip('\n')
        buffer2=dataFile.readline().strip('\n')
        buffer3=dataFile.readline()
        
        targetUserFloors=dict.get(buffer2,None)
        if targetUserFloors is None:
            newKV={buffer2:[buffer1]}
        else:
            targetUserFloors.append(buffer1)
            newKV={buffer2:targetUserFloors}
        dict.update(newKV)
        index+=1
        print(str(index)+" floor "+ "done! buffer1="+buffer1)

    print("Log : step1 analyse finish")
    
    dict=sorted(dict.items(),key=lambda x:len(x[1]),reverse=True) #dict退化为列表

    print("Log : step2 sort finish")

    outputFile=open("analyseRes.txt","w+",encoding="UTF-8")
    
    '''
    for userName,hasFloors in dict.items():
        outputFile.write(userName+" : has "+str(len(hasFloors))+" floor(s)\n")
        for item in hasFloors:
            outputFile.write("    "+item)
        outputFile.write(",\n\n")
    '''
    count=0 #每10楼换一行
    for item in dict:
        outputFile.write(item[0]+" : has "+str(len(item[1]))+" floor(s)\n")
        count=0
        for floor in item[1]:
            outputFile.write("  {:<6}".format(floor))
            count+=1
            if(count==10):
                outputFile.write("\n")
                count=0
        outputFile.write(",\n\n")

    print("Log : step3 write finish")
    print("success!")