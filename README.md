# ImageSearch
 SauceNao、Ascii2d、WhatsAnime 以图搜图网站的爬虫或api

最初目的为方便给QQ机器人输出。因此相比其他作者的多了很多字符串拼接等处理，效率嘛，能跑就行的程度= = 

考虑到部分网站开始使用http2协议，该库需求httpx、lxml、retrying三个额外包，其中httpx与lxml为必须，retrying为考虑到网络不好情况下的自动重试。

范例在每个.py文件最后

——2020.12.21