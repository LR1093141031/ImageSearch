# ImageSearch
 SauceNao、Ascii2d、WhatsAnime 以图搜图网站的爬虫或api

最初目的为方便给QQ机器人输出。因此相比其他作者的多了很多字符串拼接等处理，和通过QQ反馈的错误描述。

能实现比较简单的搜图，并输出显示搜索结果，下载搜索结果图片。

考虑到部分网站开始使用http2协议，需求httpx、lxml、retrying、BeautifulSoup4.

范例在每个.py文件最后

——2020.12.22