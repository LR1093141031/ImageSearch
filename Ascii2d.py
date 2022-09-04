import httpx
from bs4 import BeautifulSoup
import re
import asyncio

import os
import sys
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
from AsyncDownloader import async_pic_download

agency = None  # 使用代理的话就修改为代理地址


class Ascii2d:
    def __init__(self):
        self.agency = agency
        self.state = 200
        self.numres = 1  # 预定返回结果数
        self.ascii2d_url = "https://ascii2d.net/search/multi"
        self.img_url_prefix = 'https://ascii2d.net/'

        # 开启重定向，适配网站修改
        self.async_ascii2d = httpx.AsyncClient(http2=False, verify=False, timeout=20
                                               , proxies=self.agency, follow_redirects=True)

        self.img_url = []  # 匹配图片url
        self.img_name = []  # 匹配图片文件名
        self.correct_rate = []  # 准确率，Ascii2d没有准确率
        self.result_title = []  # 结果标题
        self.result_content = []  # 搜索结果副标题
        self.download_report = []  # 匹配图片下载确认，成功则为全路径 失败为False
        self.herf = []  # 所有匹配结果对应超链接，不返回，需要自行访问

        self.button_word = ['色合検索', '特徴検索', '詳細登録']

    async def async_search(self, img_file_full_path: str):
        file_name = os.path.basename(img_file_full_path)
        print(f'Ascii2d搜索图片名称:{file_name}')
        files = {'file': ("image.png", open(img_file_full_path, 'rb'))}
        try:
            response = await self.async_ascii2d.post(url=self.ascii2d_url, files=files)
            print('Ascii2d搜索状态码:', response.status_code)
        except Exception as e:
            self.state = 'Ascii2d网络请求出错'
            print('Ascii2d网络请求出错', e)
            return False

        return self._parser(response)

    def _parser(self, response):
        soup = BeautifulSoup(response, 'html.parser', from_encoding='utf-8')
        items = soup.find_all(class_='row item-box')
        results_num = len(items)

        if results_num <= 1:
            self.state = 'Ascii2d无搜索结果'
            print('Ascii2d无搜索结果')
            return False
        else:
            print(f'Ascii2d搜索到{results_num-1}个结果')

        items = items[1: min(results_num, self.numres+1)]  # 限制搜索结果数量，第一个为无效结果

        for item in items:
            # 匹配图片url
            url = self.img_url_prefix + item.find('img')['src']  # 获取页面全部结果图url
            self.img_url.append(url)
            # 匹配图片文件名
            self.img_name.append(self._image_url2name(url))
            # 匹配图片标题
            detail_a = item.find_all('a')
            title = detail_a[0].string
            self.result_title.append(title)
            # 匹配图片副标题
            content = detail_a[1].string
            self.result_content.append(content)
            # 匹配图片置信率
            self.correct_rate.append(None)
            # 匹配图片超链接
            herf = ''
            herf += detail_a[0]['herf'] if (detail_a[0].string not in self.button_word) and (
                        'herf' in detail_a[0]) else ''
            herf += ' ' + detail_a[1]['herf'] if (detail_a[1].string not in self.button_word) and (
                        'herf' in detail_a[0]) else ''
            self.herf.append(herf)

        results = {'img_url': self.img_url, 'correct_rate': self.correct_rate,
                   'result_title': self.result_title, 'result_content': self.result_content}

        return results

    @staticmethod
    def _image_url2name(img_url: str) -> str:
        """
        从url获得图片文件名
        :param img_url_list: 搜索结果图片url
        :return img_name: 搜索结果图片名称
        """
        try:  # 有时会遇到不包含文件名的url
            file_name = re.findall(r".*/(.*?\.jpg)", img_url)[0]
            file_name = re.sub(r'[\[\](),!?\-@#$%^&*]', '', file_name)
        except Exception as e:
            file_name = re.findall(r"\d{5,15}", img_url)[0] + r'.jpg'
        return file_name

    async def async_pic_download(self, download_path: str) -> list:
        results = await async_pic_download(self.async_ascii2d, self.img_url, self.img_name, download_path)
        if not self.async_ascii2d.is_closed:
            await self.async_ascii2d.aclose()
        return results

