# danawa.py
# PPT에는 hkDB / 코드는 작성자 이름대로 sbgDB로 수정

import time
import re
import pymongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
from selenium import webdriver # selenium은 webdriver api를 통해 브라우저를 제어함
from selenium.webdriver.common.by import By #https://www.seleniumhq.org/docs/03_webdriver.jsp#locating-ui-elements-webelements
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


conn = MongoClient('localhost', 27017)
db = conn['sbgDB']
collection = db['sbg']
collection.drop()


main_url = 'http://www.danawa.com/'
keyword =input("검색할 전자제품명을 입력하세요! : ")
driver=webdriver.Chrome("C:/0.ITstudy/chromedriver.exe")
driver.get(main_url)
driver.implicitly_wait(10)


search=driver.find_element_by_id("AKCSearch")
search.clear()
search.send_keys(keyword)


# 검색 버튼 클릭
btn_search = driver.find_element_by_css_selector("button.btn_search_submit")
btn_search.click()


elem=driver.find_element_by_css_selector("#opinionDESC")
elem.click()


# 최소 가격 설정
minVal=int(input("최소 시작가격을 설정해주세요 : "))
maxVal=int(input("최대 한도가격을 설정해주세요 : "))
time.sleep(1)
minPrice=driver.find_element_by_id("priceRangeMinPrice")
minPrice.clear()
minPrice.send_keys(minVal)
time.sleep(3)


# 최대 가격 설정
maxPrice=driver.find_element_by_id("priceRangeMaxPrice")
maxPrice.clear()
maxPrice.send_keys(maxVal)


price_search = driver.find_element_by_css_selector("button.btn_search")
price_search.click()


try:
    print("\n**************************************")
    print(" 상품의견이 많은 순으로 검색되었습니다!!\n 한 페이지당 30개의 제품을 표시합니다.")
    print("**************************************\n")
    lastPage=int(input(" 몇번째 페이지까지 검색하시겠습니까? : "))
    for page in range(1, lastPage+1):
        driver.execute_script("getPage(%s); return false;" % page)
        time.sleep(3)

        print("\n************%s 페이지로 이동!!!************\n" % page)

        soup = BeautifulSoup(driver.page_source, "lxml" ) 
        pItems = soup.select(".product_list > .prod_item > .prod_main_info")

        electronics=[]
        electronicTag = []
        cnt=0
        for prod_item in pItems:
            proTitle = prod_item.find("img")['alt']
            proTitle=re.sub('\[.*\]','',proTitle)
            proHref = prod_item.find('a',{'href' : True} )['href']
            proCon = prod_item.find_all('a',{'class' : "view_dic"} )
            proPrice = prod_item.select("p strong")[0].text

            print("\n==============================================================================")
            print(' 제품명 : ', proTitle)
            print(" URL : ", proHref)
            print(" 제품가격 : ", proPrice)
            print(" -제품 스펙- ")

            for i in proCon:
                print(i.text, end='/')
                electronicTag.append(i.text)
                
            electronicTag2 = electronicTag.copy()  ## dic 에 list 를 집어 넣으면 주소값이 들어가기 때문에 copy()를 써야된다.
            collection.insert({'title':proTitle, "url":proHref,"price":proPrice, "spec":electronicTag2})
            electronicTag.clear()
    print("\n ***몽고DB 연동!!!***")
    for i in collection.find({},{"title":1}):
        print(i, end="\n\n")
       

except Exception as e:
    print("---페이지 파싱 에러", e)


finally:
    time.sleep(3)
    driver.close()