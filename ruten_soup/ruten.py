import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
import argparse

# 商品分類
cateid = '000500140001' # 遊戲王
sort = 'prc%2Fac' # 價格由低到高 只找第一頁就好
headers = {'User-Agent':'GoogleBot'}
q = 'cibr-jp040'
with open('cart.txt') as f:
    lines = f.read()
shop_cart = lines.split('\n')

my_cart = defaultdict(lambda: defaultdict(lambda: 0))
for item in shop_cart:
    pid_list = []
    q,n = item.split(' ')
    print(q,n)
    n = int(n)
    search_url = 'https://rtapi.ruten.com.tw/api/search/v3/index.php/core/prod?cateid=' + cateid + '&q=' + q #+ '&sort=' + sort
    resp = requests.get(search_url, headers=headers)
    search_result = resp.text
    total_item = json.loads(search_result)["TotalRows"] # 總共有幾個商品
    pages = (total_item // 30) + 1 # 頁數
    for page in range(pages):
        offset = page * 30 + 1 # request 一頁 30 筆
        if offset != 0 : 
            search_url = 'https://rtapi.ruten.com.tw/api/search/v3/index.php/core/prod?cateid=' + cateid + '&q=' + q + '&offset=' + str(offset)
        else :
            search_url = 'https://rtapi.ruten.com.tw/api/search/v3/index.php/core/prod?cateid=' + cateid + '&q=' + q  
        resp = requests.get(search_url, headers=headers)
        search_result = resp.text        
        for pro in json.loads(search_result)['Rows']:
            pid_list.append(pro['Id'])
    for pid in pid_list:
        try : 
            product_url = 'https://www.ruten.com.tw/item/show?' + pid
            resp = requests.get(product_url, headers=headers)
            soup = BeautifulSoup(resp.text, "lxml")
            info = json.loads(soup.findAll('script',{'type':'application/ld+json'})[0].text)
            price = int(info['offers']['price'])
            if price > 9999:
                continue
            shop = info['brand']['name']
            try :
                stock = json.loads(soup.findAll('strong')[1].text)
            except : 
                stock = 0
            if stock >= n :
                #print('shop: ',shop,' price: ',int(price),' stock: ',int(stock))
                my_cart[shop]['item'] += 1
                my_cart[shop]['sum'] += price * n
                #my_cart[shop]['product'] +=  
        except :
            pass

max_sum = 600
min_sum = 100
for k, v in my_cart.items():
    if v['sum'] <= max_sum and v['sum'] >= min_sum:
        print(k,v['item'],v['sum'])
    #print(v['item'])
    #print(v['sum'])