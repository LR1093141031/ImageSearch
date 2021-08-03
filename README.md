# ImageSearch

[![State-of-the-art Shitcode](https://img.shields.io/static/v1?label=State-of-the-art&message=Shitcode&color=7B5804)](https://github.com/trekhleb/state-of-the-art-shitcode)

以图搜图网站爬虫

现在支持以下网站

- [x] SauceNao 
- [x] Ascii2d
- [x] WhatsAnime
- [ ] Google
- [ ] Baidu

考虑到部分网站开始使用http2协议，需求包：httpx、lxml、BeautifulSoup4.

示例在每个文件最后

搜索结果返回为dict:{'img_url': self.img_url, 'correct_rate': self.correct_rate, 'result_title': self.result_title, 'result_content': self.result_content}



网络请求改为异步方法 更新TraceMoeapi  ----2021.8.3

