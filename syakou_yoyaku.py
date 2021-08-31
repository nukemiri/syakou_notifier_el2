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
import config
import colorama
import os
import re
import urllib

options = Options()
#ヘッドレスモードで実行
options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
url = config.url
driver.get(url)
login_id = driver.find_element_by_id("p01aForm_b_studentId")
login_id.send_keys(config.student_id)
password = driver.find_element_by_id("p01aForm_b_password")
password.send_keys(config.password)
login_btn = driver.find_element_by_id("p01aForm_login")
login_btn.click()

f = open(os.path.join(os.path.dirname(__file__),"emptytimelist.txt"),"rb")
try:
    prelist = pickle.load(f)
except:
    prelist = []

avadates = []
avadatetimes =[]
notify_status = False

# 自動ログイン用のURL生成
version = re.findall("(?<=\/el).+?(?=\/)", url)[0]
school_id = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["abc"][0]
d={'b.studentId': config.student_id, 'b.password': config.password, 'method:doLogin': "ログイン", 'b.wordsStudentNo': '教習生番号', 'b.schoolCd': school_id, 'index': '0'}
one_tap_url = f"https://www.e-license.jp/el{version}/pc/p01a.action?{urllib.parse.urlencode(d)}"

while True:
    html=driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    datelist = soup.find_all(class_="date")
    for date in datelist:
        emptynum = len(date.find_all(class_="status1"))
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

    try:
        next_btn = driver.find_element_by_xpath("//*[@alt='次週へ']")
        next_btn.click()
    except:
        break
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
    message = ("技能予約可能\n\n"+"\n".join(avadates)+"\n"+one_tap_url)
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
