from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# import chromedriver_binary
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import datetime
import requests
from sendline import Line
import pickle
import colorama
import config
import os

options = Options()
#ヘッドレスモードで実行
options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
urls = ["https://www.e-license.jp/el2/pc/p01a.action?b.studentId="+config.student_id+"&b.password="+config.password+"&method%3AdoLogin=%83%8D%83O%83C%83%93&b.wordsStudentNo=%8B%B3%8FK%90%B6%94%D4%8D%86&b.processCd=&b.kamokuCd=&b.schoolCd="+config.school_id+"&index=&server=el1",
"https://www.e-license.jp/el2/pc/p03a.action?b.schoolCd="+config.school_id+"&b.processCd=N&b.kamokuCd=0&b.lastScreenCd=&b.instructorTypeCd=0&b.dateInformationType=&b.infoPeriodNumber=&b.carModelCd=301&b.instructorCd=0&b.page=1&b.groupCd=1&b.changeInstructorFlg=1&b.nominationInstructorCd=0",
"https://www.e-license.jp/el2/pc/p03a.action?b.schoolCd="+config.school_id+"&b.processCd=N&b.kamokuCd=0&b.lastScreenCd=&b.instructorTypeCd=0&b.dateInformationType=&b.infoPeriodNumber=&b.carModelCd=301&b.instructorCd=0&b.page=2&b.groupCd=1&b.changeInstructorFlg=1&b.nominationInstructorCd=0",
"https://www.e-license.jp/el2/pc/p03a.action?b.schoolCd="+config.school_id+"&b.processCd=N&b.kamokuCd=0&b.lastScreenCd=&b.instructorTypeCd=0&b.dateInformationType=&b.infoPeriodNumber=&b.carModelCd=301&b.instructorCd=0&b.page=3&b.groupCd=1&b.changeInstructorFlg=1&b.nominationInstructorCd=0"]

avadates = []
avadatetimes =[]
f = open(os.path.join(os.path.dirname(__file__),"emptytimelist.txt"),"rb")
try:
    prelist = pickle.load(f)
except:
    prelist = []
    
notify_status = False

for url in urls:
    driver.get(url)
    html=driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    datelist = soup.find_all(class_="date")
    for date in datelist:
        emptynum = len(date.find_all(class_="status1"))
        
        # if len(date.find_all(class_="status3"))+len(date.find_all(class_="status4"))>=2: 
        #     print(date.find(class_="view").text.replace("\n","").replace("\t","")+": 済")
        if emptynum==0:
            print(date.find(class_="view").text.replace("\n","").replace("\t","")+": 満")
        else:
            print(date.find(class_="view").text.replace("\n","").replace("\t","")+": 空")
            count = 0
            emptylist = []
            for i in date.find_all("td"):
                if "status1" in str(i):
                    emptylist.append(str(count))
                    avadatetimes.append(date.find(class_="view").text.replace("\n","").replace("\t","")+" "+str(count))
                count += 1
            avadates.append(date.find(class_="view").text.replace("\n","").replace("\t","")+" "+" ".join(emptylist))
driver.quit()

for i in avadatetimes:
    if i in prelist:
        pass
    else:
        notify_status = True
        break
if len(avadates)==0:
    print("*********\n空きなし\n*********")
else:
    print("*********\n空きあり\n"+"\n".join(avadates)+"\n*********")
    message = ("技能予約可能\n\n"+"\n".join(avadates)+"\n"+urls[0])
    if notify_status:
        line = Line(config.line_token)

        try:
            result_line = line.send_message(message)
        except Exception as error:
            print('[LINE Notify] Result: Failed')
            print('[LINE Notify] ' + colorama.Fore.RED + 'Error: ' + error.args[0], end = '\n\n')
        else:
            if result_line['status'] != 200:
                # ステータスが 200 以外（失敗）
                print('[LINE Notify] Result: Failed (Code: ' + str(result_line['status']) + ')')
                print('[LINE Notify] ' + colorama.Fore.RED + 'Error: ' + result_line['message'], end = '\n\n')
            else:
                # ステータスが 200（成功）
                print('[LINE Notify] Result: Success (Code: ' + str(result_line['status']) + ')')
                print('[LINE Notify] Message: ' + result_line['message'], end = '\n\n')
f = open(os.path.join(os.path.dirname(__file__),"emptytimelist.txt"),"wb")
pickle.dump(avadatetimes,f)
