from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,WebDriverException
import re
from pyquery import PyQuery as pq
from pyquery import PyQuery
from config import *
from time import sleep
import pymongo

client=pymongo.MongoClient(MONGO_URL)
db=client[MONGO_DB]

browser=webdriver.PhantomJS(service_args=SERVARGS)
wait=WebDriverWait(browser, 10)
browser.set_window_size(1400,900)
def search():
    try:
        browser.get('https://www.taobao.com')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
        submit=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".btn-search")))
        input.send_keys('美食')
        submit.click()
        totol=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.total')))
        getproducts()
        return totol.text
    except TimeoutException:
        return search()

def save_to_mongo(resualt):
    try:
        if db[MONGO_TABLE].insert(resualt):
            print('存储到mongodb成功')
    except:
        print('存储失败')



def next_page(page):
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.input:nth-child(2)")))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.btn:nth-child(4)")))
        input.send_keys(page)
        submit.click()
        #wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,"#mainsrp-pager .items .active"),str(page)))
        getproducts()
        sleep(0.5)
    except (TimeoutException,WebDriverException):
        next_page(page)

def get_image(item):
     resualt=item.find('.img').attr('src')
     if resualt:
         return resualt
     else:
         return item.find('.img').attr('data-src')


def getproducts():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,"#mainsrp-itemlist .items .item")))
    html=browser.page_source
    doc=pq(html)
    items=doc("#mainsrp-itemlist .items .item").items()
    i=1
    for item in items:
        product={
            'image':get_image(item),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text()[:-3],
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)

def main():
    totol=search()
    totol=re.compile('\d+').search(totol).group(0)
    print(totol)

    for i in range(2,int(totol)+1):
        print("go to ",i,' page')
        next_page(i)

    browser.close()



if __name__ == '__main__':
    main()