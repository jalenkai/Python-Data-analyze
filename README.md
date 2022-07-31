# Python 資料處裡與分析

## 重點複習

> 函數物件化(共用函式、處理字串函數、圖像函數)
- 共用函式庫建立
- 資料庫函式庫建立
- 圖像函式庫建立

> 類別,字典dict,list
- class object
  
> 模組與套件
- import pandas、numpy、scipy、matplotlib
- import os,sys,time,datatime
- 爬蟲,圖表
- 模組(自訂)分詞,簡繁轉換
  
> 特定符號分隔的文字檔案
> JSON,XML,CSV
> 資料庫表格
> 試算表

## 資料處裡與分析
```
1.Python大數據分析最重要的四個模組
Python資料分析最重要的四個模組：pandas、numpy、scipy、matplotlib。
```
> pandas
- pandas，類似於Excel試算表，pandas在Python資料分析及建模上有不錯的效果，它結合NumPy（Numerical Python的簡稱）的特性，以及試算表和關連式資料庫（SQL）的資料操作能力，可以用來對資料進行重構、切割、聚合及選擇子集合等操作。有時候，使用pandas時會和數值與科學運算有關的SciPy以前面提過的NumPy，與統計分析有關的StatsModels，與機器學習有關的 scikit-learn，與資料視學化有關的 matplotlib 及 seaborn 等等。pandas是資料科學分析工具前階段的工具。

- 在pandas裡面，最重要的兩個基本資料結構就屬Series(序列)與DataFrame，序列（Series）是一個像是一維陣列資料所組成的物件。可以利用python的串列（list）建立一個序列（Series）：
``` 
import pandas as pd
s = pd.Series([1, 2, 3, 4])
print(s.values)
array([1,2,3,4])
#第一行為索引，第二行為Series資料。輸出的每一個row由index標籤（label）及其對應的值所組成。如果在建立Series資料的時候沒有#指定index的話，pandas會自動產生從0開始的整數索引標籤。
#我們可以透過index與values屬性，分別取得Series的index陣列與值。
#透過[]運算子取值 `print(s[2])  等於3`
```
- 可以透過字典的方式建立Series
```
zip_codes ={
"100":"中正區","103":"大同區","104":"中山區","105":"松山區","106":"大安區","108":"萬華區","110":"信義區","111":"士林區","112":"北投區","114":"內湖區","115":"南港區","116":"文山區
"}
print(pd.Series(zip_codes))
```


## 資料處裡
> 文字
> N維陣列
> NumPy 函數
> Pandas  
> Pandas 單維度(Series)與二維度(DataFrame)的資料處理

## 探索資料

## 資料分析

## 數據資料視覺化

## 儲存應用

