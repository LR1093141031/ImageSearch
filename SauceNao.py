import json
import re
from lxml import etree
import httpx
import asyncio

import os
import sys
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
from AsyncDownloader import async_pic_download

agency = None  # 使用代理的话就修改为代理地址

api_key = ''

# agency 代理地址 api_key 为Saucenao网站的api许可，注册一个点账号信息就有了，也可以留空，100次访问/ip日


class SauceNao:
    """
    SauceNao 以图搜图 api
    """

    def __init__(self):
        self.state = 200
        self.api_key = api_key
        self.agency = agency

        self.async_saucenao = httpx.AsyncClient(http2=False, verify=False, timeout=20, proxies=self.agency)
        # http1模式 调用SauceNao api

        self.saucenao_url = 'https://saucenao.com/search.php'
        self.api_mode = 2  # 0 =普通html, 1 = xml api（未实现）, 2 = json api
        self.minsim = '80!'  # 决定图片边缘细节
        self.numres = 2  # 预定返回结果数
        self.dbmask = 999  # 999为类型全开
        # forcing minsim to 80 is generally safe for complex images, but may miss some edge cases. If images being
        # checked are primarily low detail, such as simple sketches on white paper, increase this to cut down on false
        # positives.

        self.search_url = f'{self.saucenao_url}?output_type={self.api_mode}&numres={self.numres}&minsim= \
                            {self.minsim}&dbmask={999}&api_key={self.api_key}'

        self.result_img_download_headers = {}  # 可以自定headers,目前api不需要

        self.img_url = []  # 匹配图片url
        self.img_name = []  # 匹配图片文件名
        self.correct_rate = []  # 准确率
        self.result_title = []  # 结果标题
        self.result_content = []  # 搜索结果副标题
        self.download_report = []  # 匹配图片下载确认，成功则为全路径 失败为False

    async def async_search(self, img_file_full_path: str):
        """
        异步搜索请求
        :param img_file_full_path: 搜索图片全路径（本地）
        :return: 搜索结果
        """
        print(f'Saucenao搜索图片名称:{os.path.basename(img_file_full_path)}')

        files = {'file': ("image.png", open(img_file_full_path, 'rb'))}
        try:
            response = await self.async_saucenao.post(url=self.search_url, files=files)
            print('SauceNao搜索状态码:', response.status_code)
        except Exception as e:
            self.state = 'Saucenao网络请求出错'
            print('Saucenao网络请求出错', e)
            return False
        return self._parser(response)

    def _parser(self, response):
        """
        搜索结果解析
        :param response: 网页请求返回结果（未解码）
        :return:搜索结果 字典形式
        """
        search_html = response.content.decode('utf-8')  # 解码
        search_json = json.loads(search_html)
        result_json = search_json['results']
        # 判断下有几个结果
        match_json = [i for i in result_json if i['header']['hidden'] == 0]
        suspect_json = [i for i in result_json if i['header']['hidden'] == 1]
        match_num = len(match_json)
        suspect_num = len(suspect_json)
        print(f'SauceNao搜索到{match_num}个高置信结果，{suspect_num}个低置信结果')

        # 用于防止某些极端情况下，网页标签结果问题导致的错误
        if match_num == 0:
            self.state = 'SauceNao无搜索结果'
            print('SauceNao无搜索结果')
            return False

        for item in match_json:
            self.img_url.append(item['header']['thumbnail'])
            self.correct_rate.append(item['header']['similarity'])
            self.img_name.append(item['header']['index_name'] + ".jpg")

            result_title = "无法获取title"
            result_content = ""
            title_flag = True

            for content in item['data'].values():
                content = str(content)
                # 跳过链接
                if "http" in content:
                    continue
                # 仅设置一次title 取第一个值
                if title_flag:
                    result_title = content
                    title_flag = False
                    continue
                # 其余的全搞成content
                result_content += content
            self.result_title.append(result_title)
            self.result_content.append(result_content)

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
        """
        异步图片下载 自动下载所有预定搜索结果图(经self.numres参数限制后的)
        :param download_path: 下载位置全路径
        :return: 下载结果(完成则为图片文件全路径，失败则为None)
        """
        report = await async_pic_download(self.async_saucenao, self.img_url, self.img_name, download_path)
        if not self.async_saucenao.is_closed:
            await self.async_saucenao.aclose()
        return report
