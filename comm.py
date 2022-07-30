'''
共用函式庫(教育版)
'''
import logging
import sys
import os,hashlib
import pymssql
import cursor
import random
import numpy as np
import pandas as pd
import opencc #另外一個很強的簡繁轉換obj
from opencc import OpenCC
from spiderscomm.langconv import *
import pytesseract
from PIL import Image,ImageEnhance,ImageFilter
import fnmatch
import urllib
import re,time
import socket
import win32event,win32process
import calendar
import datetime
from datetime import timedelta
from tqdm import tqdm
import requests
import string
import glob
from urllib.request import quote, unquote
from difflib import SequenceMatcher as SM
import difflib
import math
import shutil
import html
import statistics

#返回datetime格式：eg：2019-12-07 20:38:35.82816
now = datetime.datetime.now()

reposc ="\\(.*?\\)|\\{.*?\\}|\\[.*?\\]|\\【.*?\\】|\\★.*?\\★|\\☆.*?\\☆|\\《.*?\\》|\\『.*?\\』|\\「.*?\\」|\\＊.*?\\＊|\\〈.*?\\〉|\\{{.*?\\}|\\™.*?™}}"

#獲取今天日期
def nowday():
    nowday = datetime.datetime.now()
    return nowday

#獲取昨天日期
def yesterday():
    yesterday = now - timedelta(days=1)
    return yesterday

#獲取明天日期
def tomorrow ():
    tomorrow = now + timedelta(days=1)
    return tomorrow

#獲取本週第一天
def this_week_start():
    this_week_start = now - timedelta(days=now.weekday())
    return this_week_start

#獲取本週最後一天
def this_week_end():
    this_week_end  = now + timedelta(days=6-now.weekday())
    return this_week_end 

#獲取上週第一天
def last_week_start():
    last_week_start = now - timedelta(days=now.weekday()+7)
    return last_week_start

#獲取上週最後一天
def last_week_end():
    last_week_end = now - timedelta(days=now.weekday()+1)
    return last_week_end

#獲取本月第一天
def this_month_start():
    this_month_start = datetime.datetime(now.year, now.month, 1)
    return this_month_start

#獲取本月最後一天
def this_month_end():
    this_month_end = datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
    return this_month_end

#傳日當天日期;傳出本年度當月第幾周
def get_week_of_month(nowday):
    today_date = nowday
    this_year = today_date.date().year
    this_month = today_date.date().month
    this_day = today_date.date().day
    #month_info = calendar.monthrange(this_year, today_date.month) #回傳:第一個元素是上一個月的最後一天為星期幾(0-6)，星期天為0，第二個元素是這個月的天數
    #month_first_day = datetime.datetime.strptime('%s-%s-01' % (this_year, today_date.month), '%Y-%m-%d').date()
    #month_last_day = datetime.datetime.strptime('%s-%s-%s' % (this_year, today_date.month, month_info[1]), '%Y-%m-%d').date()
    #month_last_day_week = int(month_last_day.strftime('%w'))#本月有幾周
    #def get_week_of_month(year, month, day):

    begin = int(datetime.date(this_year, this_month, 1).strftime("%W"))
    end = int(datetime.date(this_year, this_month, this_day).strftime("%W"))

    return end - begin + 1


def get_ip_address():
 '''
 Source:
 http://commandline.org.uk/python/how-to-find-out-ip-address-in-python/
 '''
 s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 s.connect(('google.com', 0))
 ipaddr=s.getsockname()[0]
 return ipaddr

def getGray(image_file):
   tmpls=[]
   for h in range(0,  image_file.size[1]):#h
      for w in range(0, image_file.size[0]):#w
         tmpls.append( image_file.getpixel((w,h))  )
          
   return tmpls

def getAvg(ls):#獲取平均灰度值
   return sum(ls)/len(ls)
 
def getMH(a,b):#比較100個字元有幾個字元相同
   dist = 0;
   for i in range(0,len(a)):
      if a[i]==b[i]:
         dist=dist+1
   return dist

#平均哈希法(aHash) 算法
def getImgHash(fne):
   image_file = Image.open(fne) # 開啟
   image_file=image_file.resize((12, 12))#重置圖片大小我12px X 12px
   image_file=image_file.convert("L")#轉256灰度圖
   Grayls=getGray(image_file)#灰度集合
   avg=getAvg(Grayls)#灰度平均值
   bitls=''#接收穫取0或1
   #除去變寬1px遍歷畫素
   for h in range(1,  image_file.size[1]-1):#h
      for w in range(1, image_file.size[0]-1):#w
         if image_file.getpixel((w,h))>=avg:#畫素的值比較平均值 大於記為1 小於記為0
            bitls=bitls+'1'
         else:
            bitls=bitls+'0'
   return bitls

#過濾HTML中的標籤
#將HTML中標籤等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
        #先过滤CDATA
        re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        #re_br=re.compile('<br\s*?/?>')#處理換行
        #re_h=re.compile('</?\w+[^>]*>')#HTML標籤 : 匯過濾掉ex:<贈送><台灣旗艦店>關鍵字
        re_h=re.compile('<[^<]+[a-z]+[^>]*>') #HTML標籤

        re_comment=re.compile('<!--[^>]*-->')#HTML註解
        s=re_cdata.sub('',htmlstr)#去掉CDATA
      
        s=re_script.sub('',s) #去掉SCRIPT
        s=re_style.sub('',s)#去掉style
        #s=re_br.sub(' ',s)#</br>處理換行
        s=re_h.sub(' ',s) #去掉HTML標籤
        s=s.replace('< >','')#< >
        
        s=re_comment.sub('',s)#去掉HTML註解
        #去掉多餘的空行
        blank_line=re.compile('\n+')
        s=blank_line.sub('',s)
        #\r\n 去掉多余的空行
        re_rn = re.compile('\r+')
        s=re_rn.sub('',s)
        #re_p=re.compile('[\￿\▼\＊\％\!\^]*')
        #s=re_p.sub('',s)
    
        regex_s = re.compile("[\x02\x1f\x16\x0f\x09\x10\xa0\x0b\x0c\x0d\x0e\x0f\x16\x08]")
        s=regex_s.sub('',s)
        try:
          s = html.unescape(s) #html Entity 轉換
        except Exception as ex:
             pass

        #拿掉 s.replace("''","")
        s=s.strip('\n').replace("\n", "").lstrip().rstrip()  #濾掉斷行 
        return s

##替换常用HTML字符
# 使用正常的字符替换HTML中特殊的字符.
# 你可以添加新的字符到CHAR_ENTITIES中,处理更多HTML字符.
# @param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                     'lt': '<', '60': '<',
                     'gt': '>', '62': '>',
                     'amp': '&', '38': '&',
                     'quot': '"', '34': '"', }
 
    re_charEntity = re.compile(r'&#?(?P<name>\w+);')
    sz = re_charEntity.search(htmlstr)
    while sz:
        entity = sz.group()  # entity全称，如>
        key = sz.group('name')  # 去除&;后entity,如>为gt
        try:
            htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
            sz = re_charEntity.search(htmlstr)
        except KeyError:
            # 以空串代替
            htmlstr = re_charEntity.sub('', htmlstr, 1)
            sz = re_charEntity.search(htmlstr)       
    return htmlstr

#去除這些符號裡面字符包含符號,傳出 以外的字符
def set_keyword_spc(sentence):  
    sentence_seged = sentence.strip() 
    # ["()","{}","[]","【】","《》"]
    outstr = re.sub(reposc, "", sentence_seged) 
    return outstr

def cleanTrianSet(filepath):
      """
      清洗句子中空行、空格
      目前采用将所有数据读取到内存，后续思考其他高效方式
      删除空格、\u3000、 \xa0等字符
      """
      # 删除评论上面的 \n
      fileDf = pd.read_csv(filepath, keep_default_na=False)
      fileDf["rate"] = fileDf["rate"].apply(lambda x: x.replace("\n", ""))
      linelist = fileDf.values.tolist()
      filelines = [ _[0] + "," + _[-1] for _ in linelist]
      cleaned_lines = map(lambda x: x.translate({ord('\u3000'): '', ord('\r'): '', ord('\xa0'): None,ord(' '): None}), filelines[1:])  # 更加优雅的方式 在这个问题中是比较快的方式
      return cleaned_lines  # 返回一个map对象

def simple2tradition(line):  
    #將簡體轉換成繁體  
    line = Converter('zh-hant').convert(line)  
    #line = line.encode('utf-8')  
    return line 
  
def tradition2simple(line):  
    #將繁體轉換成簡體  
    line = Converter('zh-hans').convert(line)  
    #line = line.encode('utf-8')  
    return line

#只取英文字符
def set_keyword_99(sentence):  
    sentence_seged = sentence.strip() 
    #[^a-zA-Z]
    outstr = re.sub("[^a-zA-Z]", "", sentence)
    return outstr

#取出 中文 list[] ;若字串中有" "則會split
def set_keyword_chs(sentence):  
    sentence_seged = sentence.strip()   
    re_han_detail = re.compile("([\u4E00-\u9FD5]+)")#中文
    blocks = re_han_detail.split(sentence)
    list1 = []
    try:
       for blk in blocks:
           if re_han_detail.match(blk):
              if (len(blk) >=2) :
                 list1.append(blk)
       return list1
    except: 
       return ""
    
#依據實際 商品之空格 取出 斷詞
def word_split_sp(line):
    words_num = filter_pno(line) 
    re_han_detail = re.compile("([\u4E00-\u9FD5]+)")#中文

    words = line.split(" ")
    items = []
    if len(words) >=4 :
       for word in words:
          try:
            finds =""
            for i,x in enumerate(words_num):
                if (x.find(word)!=-1) :
                   finds = x
                   break;

            if (finds=="" and len(word)>=2  and (re_han_detail.match(word)  )):
               items.append(word.strip())
          except: 
           pass
    return items

#去除所有半型全型符號，只留字母，數字，中文
#會將商品全名稱濾掉空格及商品型號(abc-999)=abc999
def remove_punctuation(line):
    rule = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fa5]")
    try:
      line = rule.sub('',line)
    except:
          return ""
    return line

#去除中文只留英數的字符
def remove_ennum(line):
    rule = re.compile(r"[^a-zA-Z0-9]")
    try:
      line = rule.sub('',line)
    except:
          return ""
    return line


#去除特殊字元取內字符
def set_keyword_spt(keyword,reps):  
    sentence_seged = keyword.strip() #去除特殊字元
    if (reps==""):
       outstr = re.search("[(](.*?)[)]",sentence_seged) #def:() g_name (xyz) ==>取出 xyz
    else:
       #"[(](.*?)[)]"
       outstr = re.search(reps,sentence_seged)

    try:
       outstr = str(outstr.group(1))
       #sentence_seged = sentence_seged[1:len(outstr)-1]
    except:
          return ""
    return outstr

#去除特殊字元及"括弧"字符; 只取出 中英數 字串
def set_keyword_search_2c_en_num(sentence):  
    sentence_seged = sentence.strip() 
    try:
       items1 = ""
       for keyword in str(sentence_seged):
           keyword = remove_punctuation(keyword)
           if (keyword!=""):
              items1 += keyword

       if (len(items1)>0):
          sentence_seged =  items1
    except:
          return ""
    return sentence_seged

#去除特殊字元字元內文字,保留以外的文字20201214
def set_keyword_search(sentence):
    sentence_seged = sentence.strip() 
    outstr = re.findall(reposc,sentence_seged)
    try:
       items1 = []
       outstr = str(outstr.group(0))
       find_sint = sentence_seged.find(outstr)      
       sentence_seged = sentence_seged[0:find_sint]
    except:
          return ""
    return sentence_seged
  
#來源字符:取出 特殊字元 (*) [*]裡面的字符 
def set_keyword_findall_spc(sentence):  
    sentence_seged = sentence.strip() 
    #整個字串搜尋
    outstr = re.findall(reposc,sentence_seged)
    try:
       items1 = []
       for keyword in outstr:
           #去掉多餘的空行
           blank_line=re.compile('\n+')
           re_br=re.compile('<br\s*?/?>')#處理換行
           re_h=re.compile('<[^<]+[a-z]+[^>]*>')#HTML標籤
           re_comment=re.compile('<!--[^>]*-->')#HTML注釋
           s=re_br.sub(' ',keyword)#去掉<br
           s=re_h.sub(' ',s) #去掉HTML標籤
           s=re_comment.sub('',s)#去掉HTML注釋
           s=blank_line.sub('',s)
           try:
              outstr_sub = re.search(reposc,s)
              outstr_str = str(outstr_sub.group(0))
              sentence_seged1 = s[1:len(outstr_str)-1]
              if (sentence_seged1!=""):
                 #keyword_spc = remove_punctuation(sentence_seged1)
                 keyword_spc = sentence_seged1
                 if (len(keyword_spc) >=2) :
                    items1.append(keyword_spc.strip().rstrip())
           except:
              pass
           #items1.append(s)
       if (len(items1)>0):
          return items1#str(outstr.group(0))
       else:
          return ""
    except:
          return ""



#分詞字典vint:def 128維度:將訓練文本數據轉換成embedding矩陣
def embedding_lookup(voc, embDict,vint):
    embedding = embDict.get(voc, [random.uniform(-0.5, 0.5) for i in range(vint)])
    return embedding

def is_number(uchar):
    """判斷是否為數字,整數,浮點數"""
    chkvalue = False
    try: 
       if (uchar.isdigit()):
          chkvalue =True
    except ValueError:
          chkvalue =False

    if chkvalue == False:
      try: 
         if (float(uchar)):
            chkvalue =True
      except ValueError:
            chkvalue= False

    if chkvalue == False:
      try: 
         if (int(uchar)):
            chkvalue= True
      except ValueError:
            chkvalue= False

    return chkvalue

#將字串轉為utf-8
def strdecode(sentence):
    if not isinstance(sentence, text_type):
        try:
            sentence = sentence.decode('utf-8')
        except UnicodeDecodeError:
            sentence = sentence.decode('gbk', 'ignore')
    return sentence

def filter_eng_num(str,len_str):
    re_ban0=re.findall(r'[A-Za-z0-9]*',blk)
    items1 = []
    for keyword_0 in re_ban0:
        if (len(keyword_0) >=len_str):
           items1.append(keyword_0.strip()) 

    if (len(items1)>0) :
       list2 = list(set(items1))  #消除重複的元素
       return list2
    else:
       return ""

#取出型號規則(含-)
#去除中文只留英數的字符並保留型號規則 abc-123 ...
def filter_pno(str):
    #去掉多餘的空行
    blank_line=re.compile('\n+')
    re_br=re.compile('<br\s*?/?>')#處理換行
    re_h=re.compile('<[^<]+[a-z]+[^>]*>')#HTML標籤
    re_comment=re.compile('<!--[^>]*-->')#HTML注釋
    s=re_br.sub(' ',str)#去掉<br
    s=re_h.sub(' ',s) #去掉HTML標籤
    s=re_comment.sub('',s)#去掉HTML注釋
    s=blank_line.sub('',s)
    #取出ex: abc-123
    re_ban0=re.findall(r'[A-Za-z0-9]+-[A-Za-z0-9]+-?[A-Za-z0-9]*',s)
    #取出型號規則(不含-)ex: def789ghi or def456
    #3m or 4PQWER
    #QA82Q900RBWXZW
    #re_ban1=re.findall(r'[A-Za-z]+[0-9]+?[A-Za-z0-9]*|[0-9]+[A-Za-z]+?[A-Za-z0-9]*|[A-Za-z]+[0-9]+[A-Za-z]+|[A-Za-z]+[0-9]*|[a-zA-Z]+',s)

    #re_ban2=re.findall(r'[0-9]+[\u4E00-\u9FD5]*',s)

    items1 = []
    #ipjone 13,128g
    re_ban1_1 =re.findall(r'[0-9]+[a-zA-Z]|[a-zA-Z]+\s+[0-9]+|[a-zA-Z]+\s+[0-9]*',s)
    for keyword_1 in re_ban1_1:
            finds =""
            for i,x in enumerate(items1):
                if (keyword_1.find(x)!=-1) or ((x.find(keyword_1)!=-1) and (len(x)>(len(keyword_1)))):
                   finds = x
                   break;
            if (finds=="") and (len(keyword_1) >=2) :
               items1.append(keyword_1.strip())

    #step1.取型號 abc-123 12-abc abc-123-cdf
    for keyword_0 in re_ban0:
        if (len(keyword_0) >=2):
           items1.append(keyword_0.strip()) 
           #s=s.replace(keyword_0.strip(),'') #這樣濾掉會產生出多餘的詞出來
    #step2.取英文品牌 SONY ABC01 Dyson ...
    re_ban1=re.findall(r'[A-Za-z]+[0-9]+?[A-Za-z0-9]*|[0-9]+[A-Za-z]+?[A-Za-z0-9]*|[A-Za-z]+[0-9]+[A-Za-z]+|[A-Za-z]+[0-9]*|[a-zA-Z]+',s)
    for keyword_1 in re_ban1:
            finds =""
            for i,x in enumerate(items1):
                if (keyword_1.find(x)!=-1) or ((x.find(keyword_1)!=-1) and (len(x)>(len(keyword_1)))):
                   finds = x
                   break;
            if (finds=="") and (len(keyword_1) >=2):
               items1.append(keyword_1.strip())
               #s=s.replace(keyword_1.strip(),'') #這樣濾掉會產生出多餘的詞出來
    #step3.ABC01 ...
    re_ban2=re.findall(r'[0-9]+[\u4E00-\u9FD5]*',s)  
    #這裡應該要將上列的組合,將str取代掉避免錯誤的字串 
    #ex:Dyson 三合一涼暖空氣清淨機HP04白 ==> 04白 錯誤
    #只取英數
    for keyword_2 in re_ban2:
            finds =""
            outstrenEng = re.sub("[^a-zA-Z]", "", keyword_2)#判斷是否有英文
            outstrCht = re.sub("[^\u4E00-\u9FD5]", "", keyword_2)#判斷是否有中文 
            if (outstrenEng!='' and outstrCht==''):  
               for i,x in enumerate(items1):
                   if (keyword_2.find(x)!=-1) or ((x.find(keyword_2)!=-1) and (len(x)>(len(keyword_2)))):
                      finds = x
                      break;
               if (finds=="") and (len(keyword_2) >=2):
                  items1.append(keyword_2.strip())
    #取出特定符號 en&en
    re_ban3=re.findall(r'[a-zA-Z]+[0-9]+[A-Za-z]*|[a-zA-Z]+&[A-Za-z0-9]*',s)
    for keyword_3 in re_ban3:
        finds =""
        for i,x in enumerate(items1):
            if (keyword_3.find(x)!=-1) or ((x.find(keyword_3)!=-1) and (len(x)>(len(keyword_3)))):
               finds = x
               break;
        if (finds=="") and (len(keyword_3) >=2):
           items1.append(keyword_3.strip())

    if (len(items1)>0) :
       list2 = list(set(items1))  #消除重複的元素
       return list2
    else:
       return ""

#傳入list[]過濾有數字字符傳出英數字串
#去掉只有數字的詞
def filter_numtocht(keywords):
   #去掉只有數字的詞
   keyitems=[]
   for i in range(len(keywords)):
      if re.findall(r'^[^\d]\w+', keywords[i]):
         keyitems.append(re.findall(r'^\w+$', keywords[i])[0])

   return keyitems

#取字串中數字
def filter_num(keywords):
   rule = re.compile(r"[^0-9]")
   str2num = rule.sub('',keywords)
   return str2num

#去頭尾字串只留數字 字符
def StartEndStrTrun2Num(Rstr,Startstr,Endstr,defpage):
    begint = Rstr.find(Startstr)
    endint = Rstr.find(Endstr)
    try :
      gCntTotal_Str = remove_ennum(Rstr[begint:endint])
      gCntTotal_Str = filter_num (gCntTotal_Str)
    except:
      gCntTotal_Str =defpage
    return  str(gCntTotal_Str)

#頭尾切字串
def StartEndStrTrun(Rstr,Startstr,Endstr):
        begint = Rstr.find(Startstr)
        endint = Rstr.find(Endstr)
        if begint <0 :
           begint =0
        if endint <0 : #20220126 當找不到時則取至尾
            endint = len(Rstr)             
        return  str(Rstr[begint:endint].replace(Startstr,''))

#頭尾切字串
def StartEndStrTrun2(Rstr,Startstr,Endstr):
        lastStr = Rstr
        begint = Rstr.find(Startstr)
        if begint <0 :
           begint =0
        if begint >0 : #當有找的前面字串時,則由前字元開始尋找並切斷找到目的字元
            lastStr = Rstr[begint:len(Rstr)].replace(Startstr, '')
            endint = lastStr.find(Endstr)
        else :
            lastStr = Rstr[begint:len(Rstr)].replace(Startstr, '')
            endint =len(lastStr)

        return  str(lastStr[0:endint])

def CommitTable(strSQL,sqlserverIP):
    try:
        goods_conn1 = pymssql.connect(server=str(sqlserverIP), user='XX', password='XX', database='XXX', timeout=2400, login_timeout=600,autocommit=True)
        cursor1 = goods_conn1.cursor()
        cursor1.execute(strSQL)
        goods_conn1.commit()
        goods_conn1.close()
        return 1
    except ValueError:
        return 0
        goods_conn1.close()

def CommitApiTempTable(strSQL,sqlserverIP):
       try:
           goodsbid_conn1 = pymssql.connect(server=str(sqlserverIP), user='XX', password='XX', database='XX', timeout=2400, login_timeout=600,autocommit=True)
           cursor1 = goodsbid_conn1.cursor()
           cursor1.execute(strSQL)
           goodsbid_conn1.commit()
           goodsbid_conn1.close()
           return 1
       except ValueError:
           return 0
           goodsbid_conn1.close() 

def getFildValue(strSQL,sqlserverIP,fieldName,databasename):
        goodsapi_conntemp = pymssql.connect(server=str(sqlserverIP), user='XX', password='XXX', database=databasename, timeout=2400, login_timeout=2400,autocommit=True)
        cursor = goodsapi_conntemp.cursor()
        cursor.execute(strSQL)
        rowselect = cursor.fetchone()
        if (rowselect):
           return  str(rowselect[fieldName])
        else : 
           return ""

def CommitTable_dbname(strSQL,sqlserverIP,_database):
       try:
           goodsapi_conn1 = pymssql.connect(server=str(sqlserverIP), user='XX', password='XXX', database=_database , timeout=2400, login_timeout=2400,autocommit=True)
           cursor1 = goodsapi_conn1.cursor()
           cursor1.execute(strSQL)
           goodsapi_conn1.commit()
           goodsapi_conn1.close()
           return 1
       except ValueError:
           return 0
           goodsapi_conn1.close()

def CommitTable_dbnameTimeout(strSQL,sqlserverIP,_database,_timeout):
       try:
           goodsapi_conn1 = pymssql.connect(server=str(sqlserverIP), user='XX', password='XXX', database=_database , timeout=_timeout, login_timeout=2400,autocommit=True)
           cursor1 = goodsapi_conn1.cursor()
           cursor1.execute(strSQL)
           goodsapi_conn1.commit()
           goodsapi_conn1.close()
           return 1
       except ValueError:
           return 0
           goodsapi_conn1.close()

#傳入檔案路徑;創建停用詞list  
def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]  
    return stopwords

#呼叫win 路徑下檔案
def GotoPressExe(exePath,_paramStr):
    # 建立程序獲得控制代碼
    print('呼叫' + str(exePath))
    #exePath = "C:\\FP_GOODS\\GetGoods_batch4.exe"
    param = exePath + " " + str(_paramStr) # '/input='+str(m_id)
    handle = win32process.CreateProcess(exePath,param,None,None,0,win32process. CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())
    #等待程序結束
    win32event.WaitForSingleObject(handle[0], -1)# 程序結束的返回值

#取得url檔案下載實際的檔名
def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def downloadUrlFile(url,filename):   
    downok = False
    _useragent = UAT.process_request(__name__)
    headersItems = {
                     'Content-Type' : 'text/html;charset=UTF-8',
                     'user-agent':  _useragent 
    } 
    resp = requests.get(url, stream=True,headers=headersItems,timeout=10000)
    if str(resp.status_code) == '200': 
      with open(filename, 'wb') as f:
        filename_down = get_filename_from_cd(resp.headers.get('content-disposition'))
    
        print ('成功登錄到 %s' %(url))
        #print ('開始處裡檔案內容 %s' %(filename_down))
        for data in tqdm(resp.iter_content(1024)):
            try:
               if data:
                 f.write(data)
            except:
                 pass
        downok = True

    return downok

#傳入requests.get = status_code =200;傳出檔案下載進度條並下載成功!!
def downloadUrlFile2resp(url,resp,filename):   
    downok = False
    if str(resp.status_code) == '200':
      resp.encoding = 'utf-8'       
      with open(filename, 'wb') as f:
        filename_down = get_filename_from_cd(resp.headers.get('content-disposition'))
     
        print ('成功登錄到 %s' %(url))
        print ('開始處裡檔案內容 %s' %(filename_down))
        for data in tqdm(resp.iter_content(chunk_size=1024)):
            f.write(data)
        downok = True


    return downok

#來源chklist1 list [] 將 replist2  list []排除
#取出結果 list [] (兩list過濾)
def filter2listForRepeat(chklist1,replist2):
   items5=[]

   if len(replist2)>0:
     for keyword_c in chklist1:
         finds =""
         for i,x in enumerate(replist2):
           if (x.find(keyword_c)!=-1):
              finds = x
              break;

         if (finds==""):
           items5.append(keyword_c.strip())
     if (len(items5)>0):
           ords_filtered_cut = ','.join(items5)
           keywords_str_cut = ords_filtered_cut.replace("N'",'').replace("'",'')
           return str(keywords_str_cut)
     else: #兩個list全部都相同
        ords_filtered_cut = ','.join(chklist1)
        keywords_str_cut = ords_filtered_cut.replace("N'",'').replace("'",'')
        return str(keywords_str_cut)

#去除中文只留英數的字符並保留型號規則 abc-123 ...
#消除重複的元素 string aaa,bbb,ccc,ddd
def get_gname_filter_pno(g_name):
        items = []
        gname_kw_sp_rech = filter_pno(g_name)#去除中文只留英數的字符並保留型號規則 abc-123 ...
        for keyword_kw_sp_rech in gname_kw_sp_rech:
            items.append(keyword_kw_sp_rech.strip())

        items = list(set(items))  #消除重複的元素
        if (len(items)>0):
           ords_filtered_cut = ','.join(items)
           keywords_str_cut = ords_filtered_cut.replace("N'",'').replace("'",'')
           return str(keywords_str_cut)
        else:
           return ""

def get_gname_filter_pno2list(g_name):
        items = []
        gname_kw_sp_rech = filter_pno(g_name)#去除中文只留英數的字符並保留型號規則 abc-123 ...
        for keyword_kw_sp_rech in gname_kw_sp_rech:
            items.append(keyword_kw_sp_rech.strip())

        items = list(set(items))  #消除重複的元素
        if (len(items)>0):
           return items
        else:
           return ""


#星期一傳回 1 星期日傳回  ex:today2weekday(datetime.date.today())
def today2weekday(nowdatetime):
    return datetime.date.isoweekday(nowdatetime)

#過濾list[]中取得符合find_str字串的list集合
def filter2list(lists,find_str):
    lists = sorted(lists) #排序字母順序
    file_filter=list(filter(lambda fil: str(fil).find(str(find_str))>=0, lists))
    return file_filter

#傳入搜尋路徑及萬用字元檔案 搜尋 傳出list檔案列表 ==>c:\aaa\bbb\files1.xml    
#path='c:\aaa\bbb'  seachfiles = r'\*.xml'
def seachpathallfiles(path,seachfiles):
    return glob.glob(path + seachfiles)

#取得檔案名稱
def getfilename(filepath):
   return os.path.basename(filepath) 

#檔案是否存在
def isfileExists(filepath):
   return os.path.isfile(filepath)

#目錄否存在
def isdirExists(dirpath):
   return os.path.isdir(dirpath)

#把檔案名稱改名
def rename2filename(sou_pathfiles,des_pathfiles):
   return os.rename(sou_pathfiles,des_pathfiles)

#將url有中文部分URL編碼解碼
def urldecode(g_link):
   _url = quote(g_link, safe=";/?:@&=+$,", encoding="utf-8")
   return _url

#編輯距離算法 int =0完全相似
def levenshtein(first, second):
        if len(first) > len(second):
            first, second = second, first
        if len(first) == 0:
            return len(second)
        if len(second) == 0:
            return len(first)
        first_length = len(first) + 1
        second_length = len(second) + 1
        distance_matrix = [list(range(second_length)) for x in range(first_length)]
        # print distance_matrix
        for i in range(1, first_length):
            for j in range(1, second_length):
                deletion = distance_matrix[i - 1][j] + 1
                insertion = distance_matrix[i][j - 1] + 1
                substitution = distance_matrix[i - 1][j - 1]
                if first[i - 1] != second[j - 1]:
                    substitution += 1
                distance_matrix[i][j] = min(insertion, deletion, substitution)
                # print distance_matrix
        return distance_matrix[first_length - 1][second_length - 1]

# 兩詞 list 餘弦相似度
def compute_cosine(text_a, text_b):
    # 找單詞及詞頻
    words1 = text_a.split(',')
    words2 = text_b.split(',')
    
    words1_dict = {}
    words2_dict = {}
    for word in words1:
        # word = word.strip(",.?!;")
        #word = re.sub('[^a-zA-Z]', '', word)
        word = word.lower()
        # print(word)
        if word != '' and word in words1_dict: 
            num = words1_dict[word]
            words1_dict[word] = num + 1
        elif word != '':
            words1_dict[word] = 1
        else:
            continue
    for word in words2:
        # word = word.strip(",.?!;")
        #word = re.sub('[^a-zA-Z]', '', word)
        word = word.lower()
        if word != '' and word in words2_dict:
            num = words2_dict[word]
            words2_dict[word] = num + 1
        elif word != '':
            words2_dict[word] = 1
        else:
            continue
    #print(words1_dict)
    #print(words2_dict)

    # 排序
    dic1 = sorted(words1_dict.items(), key=lambda asd: asd[1], reverse=True)
    dic2 = sorted(words2_dict.items(), key=lambda asd: asd[1], reverse=True)
    #print(dic1)
    #print(dic2)

    # 得到詞向量
    words_key = []
    for i in range(len(dic1)):
        words_key.append(dic1[i][0])  # 向數列組中添加元素
    for i in range(len(dic2)):
        if dic2[i][0] in words_key:
            # print 'has_key', dic2[i][0]
            pass
        else:  # 合併
            words_key.append(dic2[i][0])
    # print(words_key)
    vect1 = []
    vect2 = []
    for word in words_key:
        if word in words1_dict:
            vect1.append(words1_dict[word])
        else:
            vect1.append(0)
        if word in words2_dict:
            vect2.append(words2_dict[word])
        else:
            vect2.append(0)
    #print(vect1)
    #print(vect2)

    #計算餘弦相似度
    sum = 0
    sq1 = 0
    sq2 = 0
    for i in range(len(vect1)):
        sum += vect1[i] * vect2[i]
        sq1 += pow(vect1[i], 2)
        sq2 += pow(vect2[i], 2)
    try:
        result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
    except ZeroDivisionError:
        result = 0.0
    return result

def strQ2B(ustring):
    """把字串全形轉半形"""
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全形空格直接轉換
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # 全形字元（除空格）根據關係轉化
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)

def strB2Q(ustring):
    """把字串全形轉半形"""
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 32:  # 全形空格直接轉換
                inside_code = 12288
            elif (inside_code >= 33 and inside_code <= 126):  # 全形字元（除空格）根據關係轉化
                inside_code += 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)

#比較字串相似度
def string_similar(s1, s2):
    seq = SM(None, s1, s2)
    return seq.quick_ratio()

# get_close_matches返回一个相似列表，并按照相似度排列，最佳匹配
def list_similar(word,list,n=10,cutoff=0.6):
    seq = difflib.get_close_matches_sort(str(word), list, n=n, cutoff=cutoff)
    unique_set = list(set(seq))
    return unique_set


def DB2txt(dbtablename,fieldname,wheresql,SavefilePacth,sqlserverIP,databasename):
    strSQL = str('select cnt=count(*) from ' + dbtablename + '  with(nolock) where ' + str(wheresql))
    cntdoflag = getFildValue(strSQL,sqlserverIP,0,databasename)
    if (cntdoflag!="0"):

       logfile = open(SavefilePacth, 'w',encoding='utf-8') #a覆蓋

       strSQL = str('select '+ fieldname + ' from ' + dbtablename + '  with(nolock) ') 

       goods_conn = pymssql.connect(server=str(sqlserverIP), user='xx', password='xxx', database=databasename, timeout=2400, login_timeout=2400,autocommit=True)  #
       #df = pandas.read_sql(strSQL,goods_conn)
       #df.to_csv(SavefilePacth,index=False,header=0) #不保存行索引,不保存列名
       cursor = goods_conn.cursor()
       cursor.execute(strSQL)
       row = cursor.fetchone()

       #把結果寫到txt裡面
       while row:
          if str(row[0])!="" :
             logfile.write(str(row[0]).replace("'","").replace('"',"") + '\n')  
          #下一個row 
          row = cursor.fetchone()

       print('匯出 %s 檔案完成!!' % (str(SavefilePacth)))
       cursor.close()                            
       logfile.close() 

def copysfile2dfile(sourefilePatch,desfilePatch):
    if os.path.exists(sourefilePatch):
       shutil.copyfile(sourefilePatch, desfilePatch)

def IsConnectionFailed(url):
    """
         檢查連線是否失敗。
    """
    try:
        ret = urllib.request.urlopen(url=url, timeout=1)
    except:
        return False
    return True

#刪除路逕下的特定檔案(zFilesName = '.affiliate.xml')
def chkPatchDelFiles(Patch,zFilesName):
    for file_name in os.listdir(Patch):
       if file_name.endswith(zFilesName):
           try:
             os.remove(Patch + "\\" + file_name)
           except OSError as e:
              print(e)
           else:
              print("File is deleted successfully")

#刪除路逕下的,包含zFilesName全部檔案(zFilesName = '*.xml')
def chkPatchDelFilesAll(Patch,zFilesName):
    fileslist = seachpathallfiles(Patch,r"\\"+zFilesName)

    for file_name in fileslist:
           try:
               if file_name.endswith(file_name):
                   os.remove(file_name)
           except OSError as e:
              print(e)
           else:
              print("File is deleted successfully")

#加入 addstrT:前字串 ; addstrE:後字串
def get_gname_filter_pno_setok(g_name,keyword_oth,addstrT,addstrE):
        
        items = []
        gname_kw_sp_rech = filter_pno(g_name)#去除中文只留英數的字符並保留型號規則 abc-123 ...
        for keyword_kw_sp_rech in gname_kw_sp_rech:
            #在搜尋字串中沒有此字串
            #若有型號別 'abc-def' 則取出
            #ex['3C', 'InSightTM', 'Honeywell', 'HPA5250WTW'] 
            chkenu= remove_ennum(keyword_kw_sp_rech) #只留英數字符
            if (len(chkenu)>1):
               if (keyword_kw_sp_rech.find('-')>0):
                  items.append(keyword_kw_sp_rech.lower())
               elif(keyword_oth.find(keyword_kw_sp_rech.lower())<0 and chkenu!=''): #與keyword_oth不重複
                  items.append(chkenu.lower().strip())#只取 英數 
               elif (keyword_oth.find(keyword_kw_sp_rech.lower())<0):
                  items.append(addstrT + keyword_kw_sp_rech.lower().strip() + addstrE)
        
        gname_kc_rech = resp_wordslist(g_name)#自訂規格 類型 2個....
        if (len(gname_kc_rech)>0): [items.append(keyword)  for keyword in gname_kc_rech] 
        
        items = list(set(items))  #消除重複的元素
        if (len(items)>0):
           ords_filtered_cut = ','.join(items)
           keywords_str_cut = ords_filtered_cut.replace("N'",'').replace("'",'')
           return str(keywords_str_cut)
        else:
           return ""



#20210901
#四捨五入 gtype:0(無條件進位):取到小數第幾位;1(四捨五入):取到小數第幾位
def getFloat45(gtype,number,n=0):
    rVlaue = 0.0
    if (gtype==0):
       rVlaue=math.ceil(float(number))
    else:
       rVlaue=round(float(number) , n)

    return float(rVlaue)

#傳出自訂規格 
def resp_wordslist(resp_words):
   str0 = re.findall(r"[\u4E00-\u9FD5]+折",resp_words)
   str01 = re.findall(r"[0-9]+折",resp_words)
   str1 = re.findall(r"[0-9]+入",resp_words)
   str2 = re.findall(r"[0-9]+人",resp_words)
   str3 = re.findall(r"[0-9]+個",resp_words)
   str4 = re.findall(r"[0-9]+隻",resp_words)
   str5 = re.findall(r"[0-9]+對",resp_words)
   str6 = re.findall(r"[0-9]+套",resp_words)
   str7 = re.findall(r"[0-9]+元",resp_words)
   str8 = re.findall(r"[0-9]+%",resp_words)
   str9 = re.findall(r"[0-9]+％",resp_words)
   str10 = re.findall(r"[0-9]+代",resp_words)
   str11 = re.findall(r"[一\二\三\四\五\六\七\八\九\十]+代",resp_words)
   str12 = re.findall(r"[0-9]+瓶",resp_words)
   str13 = re.findall(r"[一\二\三\四\五\六\七\八\九\十]+瓶",resp_words)

   items1 = []
   list1 = []
   re_ban = []
   if ((len(str0)>0) or (len(str01)>0) or (len(str1)>0) or (len(str2)>0) or (len(str3)>0) 
      or (len(str4)>0) or (len(str5)>0) or (len(str6)>0) or (len(str7)>0) or (len(str8)>0) or (len(str9)>0) or (len(str10)>0) or (len(str11)>0) or (len(str12)>0) or (len(str13)>0)):
      
      if (len(str0)>0): [ list1.append(keyword)  for keyword in str0] 
      if (len(str1)>0): [ list1.append(keyword)  for keyword in str1]
      if (len(str2)>0): [ list1.append(keyword)  for keyword in str2] 
      if (len(str3)>0): [ list1.append(keyword)  for keyword in str3] 
      if (len(str4)>0): [ list1.append(keyword)  for keyword in str4] 
      if (len(str5)>0): [ list1.append(keyword)  for keyword in str5] 
      if (len(str6)>0): [ list1.append(keyword)  for keyword in str6] 
      if (len(str7)>0): [ list1.append(keyword)  for keyword in str7]
      if (len(str8)>0): [ list1.append(keyword)  for keyword in str8] 
      if (len(str9)>0): [ list1.append(keyword)  for keyword in str9] 
      if (len(str10)>0): [ list1.append(keyword)  for keyword in str10] 
      if (len(str11)>0): [ list1.append(keyword)  for keyword in str11]  
      if (len(str12)>0): [ list1.append(keyword)  for keyword in str12 ] 
      if (len(str13)>0): [ list1.append(keyword)  for keyword in str13 ] 

      if (len(list1)>0): items1=list1

      #for keyword in re_ban:
      #  if (len(keyword) >=2):
      #     items1.append(keyword.strip())

      if (len(items1)>0) :
         list1 = list(set(items1))  #消除重複的元素

   return list1

#keyword : 'aaa,bbb,ccc'
def SetStrKeyword2SQLcontains(keyword):
    contains_list = keyword.split(",")
    contains_list = list(set(contains_list)) 
    items=[]
    if (len(contains_list)>0): [items.append(str('"' + keyword + '"'))  for keyword in contains_list] 
    
    return items

#傳入list傳出裡面最大值 (integer)
def SetLists2max_value(lists):
    max_value = None
    for num in lists:
       if (max_value is None or num > max_value):
           max_value = num
    return max_value

#items = [6, 1, 8, 2, 3]==>3
def GetList2median(items):
   if len(items)>0:    
      return statistics.median(items)
   else:
      return 0

#中文字含有單雙引號去除 
def getbrief(gname):
   gname = filter_tags(gname)
   gname = gname.replace("'","&apos;").replace('"',"&quot;")
   return gname

#數字價格,(小數點第一位四捨五入)取至整數 :ex:4.5=5 ; 4.4=4 ; by 20211103
def getprice(gprice):
   if (is_number(gprice))==True:
      gprice = int(getFloat45(1,gprice,0))
   else:
      gprice = filter_num(gprice)

   return gprice

'''
#傳入 關鍵字 "ABC.CDE,EFG" 由神經網路 模型中取出相似詞 list組
#row_key_name: 關鍵字 "ABC.CDE,EFG" string ; model:神經網路 模型 ;
# maxtopn:取出相似詞數量 ; maxsimtoken:相似度0.1~1 ; maxcnt 最多取多少數組
'''
def getModel2similar(g_name,row_key_name,model, maxtopn=3,maxsimtoken=0.7,maxcnt=10):

    keywords_similar_list = []
    china_keywords = set_keyword_chs(row_key_name)#只取中文
    if (len(china_keywords)>0):
       for key_row in china_keywords:
          try:
            if (len(china_keywords)<=3):
               indexes = model.similar_by_word(key_row.replace("'",""), topn=maxtopn)
            elif (len(china_keywords)<=8):
               indexes = model.similar_by_word(key_row.replace("'",""), topn=(maxtopn-1))

            if (len(china_keywords)>8):
               indexes = model.similar_by_word(key_row.replace("'",""), topn=(maxtopn-1))
               simtoken=(maxsimtoken+0.1)

            for index in indexes:
               if (index[1]>=maxsimtoken):#由 model 取出 相似詞
                   keywords_similar_list.append(str(index[0].replace("'","")))

            if (len(keywords_similar_list)>=maxcnt):#大於10組就跳離
                break
          except Exception as e:
             pass
    else:
          try:
            china_keywords = set_keyword_chs(g_name)#只取中文
            if (len(china_keywords)>0):
               indexes = model.similar_by_word(g_name.replace("'",""), topn=maxtopn)  
               for index in indexes:
                  if (index[1] >=maxsimtoken):#由 model 取出 相似詞
                      keywords_similar_list.append(str(index[0].replace("'",""))) 
          except Exception as e:
             pass

    if len(keywords_similar_list)>0:
        keywords_similar_list= list(set(keywords_similar_list))  #消除重複的元素
    
    return keywords_similar_list
###################db


def chkintodbgoodsDB(g_link,g_name,g_price,g_image):
    if (g_link.find("http")>=0 and g_image.find("http")>=0 and g_link!="" and g_name != '' and g_price != "0" and g_image != '' and g_name.find('勿下標') < 0 and g_name.find('缺貨') < 0
            and g_name.find('備貨') < 0 and g_name.find('補貨') < 0 and g_name.find('售完') < 0 and g_name.find('代購') < 0
            and g_name.find('退貨專區') < 0 and g_name.find('專用賣場') < 0):
        return True  # INSERT INTO  or  Update
    else:
        return False


def getdb_merchantDataDict(m_id):
   db_conn = {
        'host': 'xxx.xxx.xxx.xxx',
        'db'  : 'xxx',
        'user': 'xx',
        'pwd' :'xxx'
        }

   strSQL="xxx"
    

   ms_conn = db_mssql(host=db_conn['host'],db=db_conn['db'],user=db_conn['user'],pwd=db58_conn['pwd'])
   cur = ms_conn.select(strSQL)
   if (len(list(cur.get('data')))>0):
      datalist = list(cur.get('data'))
      merchant = dict()
      merchant['m_name'] = getbrief(datalist[0][0]).replace('"', "&quot;").replace('"', "&apos;")
      merchant['m_link'] = datalist[0][1]
      merchant['companyno'] = datalist[0][2]
      merchant['lastmodify'] = datalist[0][3]
      merchant['sitemapurl'] = datalist[0][4]
      merchant['gettype'] = datalist[0][5]
      merchant['price_level'] = datalist[0][6]
      merchant['tracecode'] = datalist[0][7]
      merchant['collaborationtype'] = datalist[0][8]
      return merchant
   else:
      return ''

class db_mssql:
#顯示欄位名稱,資料 資料庫 物件化
    def __init__(self, host, db, user, pwd):
        self.host = host
        self.db = db
        self.user = user
        self.pwd = pwd
        #self.port = port
        self._conn = self._connect()
        self._cursor = self._conn.cursor()

    def _connect(self):         
        return pymssql.connect(
            database=self.db,
            user=self.user,
            password=self.pwd,
            server=self.host,
            timeout=2400, 
            login_timeout=600) 

    def select(self, sqlCode):
        self.common(sqlCode)
        col_names = []
        result = {}
        
        column_count = len(self._cursor.description)
        for i in range(column_count):
            desc = self._cursor.description[i]
            col_names.append(desc[0])
        data = self._cursor.fetchall()
        result['head'] = col_names
        result['data'] = data
        return result

    def close(self):
        try:
           self._cursor.close()
           self._conn.close()
        except Exception as e:
             pass

    def common(self, sqlCode):
        try:
            self._cursor.execute(sqlCode)
        except Exception as e:
            print(e)
            self._conn.rollback()
            #self._cursor.execute(sqlCode)
        #self._conn.commit() #pymssql no open

    def __del__(self):
        self.close()


