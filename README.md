# ImageSearch
以图搜图的爬虫

现在支持以下网站

- [x] SauceNao
- [x] Ascii2d
- [x] WhatsAnime
- [ ] Google
- [ ] Baidu

考虑到部分网站开始使用http2协议，需求包：httpx、lxml、retrying、BeautifulSoup4.

范例在每个.py文件最后

搜索结果返回为dict:{'img_url': self.img_url, 'correct_rate': self.correct_rate, 'result_title': self.result_title, 'result_content': self.result_content}



写的太屎了，一旦有时间马上重构。-2021.3.1

