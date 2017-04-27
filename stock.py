# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 09:40:36 2017

@author: xk
"""

import requests
from bs4 import BeautifulSoup
import re
import traceback
 
def getHTMLText(url, code = 'utf-8'):
    try:
        r = requests.get(url, timeout = 30)
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        return ""
 
def getStockList(lst, stockURL):
    html = getHTMLText(stockURL, code = 'GB2312')
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find_all('a')
 
    #print('a length: {0}'.format(len(a)))
    for i in a:
        try:
            href = i.attrs['href']
            lst.extend(re.findall(r"[s][hz]\d{6}", href))
            #print('lst length: {0}'.format(len(lst)))
 
        except:
            continue
 
def getStockInfo(lst, stockURL, fpath):
    count = 0
 
    for stock in lst:
        url = stockURL + stock + '.html'
        html = getHTMLText(url)
        try:
            if html == "":
                continue
            infoDict = {}
            soup = BeautifulSoup(html, 'html.parser')
            stockInfo = soup.find('div', attrs = {'class':'stock-bets'})
 
            #其中存在一些页面返回的stockInfo值为None
            #若不进行判断，则会在stockInfo.find_all一行出错，跳转到except语句段
            if stockInfo is None:
                continue
 
            name = stockInfo.find_all(attrs={'class':'bets-name'})[0]
            name = name.text.split()
            #nameLst = [x for x in re.split(r'\s+|\(|\)', name) if x != '']
 
            #股票信息中增加了股票代码的信息
            infoDict.update({'股票名称':name[0], '股票代码':stock})
 
            keyList = stockInfo.find_all('dt')
            valueList = stockInfo.find_all('dd')
 
            #对于一些如国债逆回购的信息，网页中只有名称信息，而没有其他信息
            #因此对这类信息进行清洗
            if len(keyList) < 1:
                continue
 
            for i in range(len(keyList)):
                key = keyList[i].text.strip()
                value = valueList[i].text.strip()
                infoDict[key] = value
 
 
            with open(fpath, 'a', encoding = 'utf-8') as f:
                f.write(str(infoDict) + '\n')
                #f.write(url)
                count += 1
                print('\r当前速度： {:.2f}%'.format(count*100/len(lst)), end = '')
        except:
            count += 1
            print('\r当前速度： {:.2f}%'.format(count*100/len(lst)), end = '')
            traceback.print_exc()
            continue
 
 
def main():
    stock_list_url = 'http://quote.eastmoney.com/stocklist.html'
    stock_info_url = 'https://gupiao.baidu.com/stock/'
    output_file = "D:/baidustockinfo.txt"
    slist = []
    getStockList(slist, stock_list_url)
    getStockInfo(slist, stock_info_url, output_file)
 
main()