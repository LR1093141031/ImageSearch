import httpx
import json
import os
import re
import asyncio
from AsyncDownloader import async_pic_download

agency = None  # 使用代理的话就修改为代理地址


class TraceMoe:
    def __init__(self):
        self.agency = agency
        self.state = 200
        self.numres = 5  # 预定返回结果数
        self.tracemoe_url = "https://api.trace.moe/search?cutBorders&anilistInfo"

        self.async_tracemoe = httpx.AsyncClient(http2=False, verify=False, timeout=20, proxies=self.agency)

        self.img_url = []  # 匹配图片url
        self.img_name = []  # 匹配图片文件名
        self.correct_rate = []  # 准确率
        self.result_title = []  # 结果标题
        self.result_content = []  # 搜索结果副标题
        self.download_report = []  # 匹配图片下载确认，成功则为全路径 失败为False

    async def async_search(self, img_file_full_path=None):
        file_name = os.path.basename(img_file_full_path)
        print(f'搜索图片名称:{file_name}')
        files = {"image": ('anime.png', open(img_file_full_path, 'rb'))}
        try:
            response = await self.async_tracemoe.post(url=self.tracemoe_url, files=files)
            response_json = json.loads(response.text)
            print(f"TraceMoe搜索状态码{response.status_code}")
        except Exception as e:
            print(f"TraceMoe网络请求出错", e)
            self.state = 'TraceMoe网络请求出错'
            return False

        search_num = len(response_json['result'])     # 搜索结果数
        if search_num == 0:
            print("TraceMoe无搜索结果")
            self.state = 'TraceMoe无搜索结果'
            return False
        return self._parser(response_json)

    def _parser(self, response_json):
        results_num = len(response_json['result'])
        if results_num == 0:
            self.state = 'TraceMoe无搜索结果'
            print('TraceMoe无搜索结果')
            return False
        else:
            print(f'TraceMoe搜索到{results_num}个结果')

        response_json['result'] = response_json['result'][: min(results_num, self.numres)]  # 限制搜索结果数量

        for i in response_json['result']:
            # 搜索结果标题与副标题
            anilist_info_dict = i['anilist']['title']
            title = '' + anilist_info_dict['native'] if anilist_info_dict['native'] else ''
            title += anilist_info_dict['romaji'] if anilist_info_dict['romaji'] else ''
            self.result_title.append(title)
            # 搜索结果匹配位置
            episode = str(i['episode'])
            at = str(int(i['to'] // 60)) + '分' + str(int(i['to'] % 60)) + '秒'
            self.result_content.append(f"匹配位置 第{episode}集 {at}")
            # 准确率
            similarity = str(round(i['similarity'], 2) * 100)   #百分比化
            self.correct_rate.append(similarity + '%')
            # 结果图片url
            url = i['image']

            if 'isAdult' in i['anilist'] and i['anilist']['isAdult']:  # 临时 防r18图  ===========================
                url = None

            self.img_url.append(url)
            # 结果图片名
            file_name = re.sub(r'[\[\]()\'<>=:`,!?\-@#$%^&*]', '', i['filename']) + '.jpg'
            self.img_name.append(file_name)

        results = {'img_url': self.img_url, 'correct_rate': self.correct_rate,
                   'result_title': self.result_title, 'result_content': self.result_content}
        return results

    async def async_pic_download(self, download_path: str) -> list:
        report = await async_pic_download(self.async_tracemoe, self.img_url, self.img_name, download_path)
        if not self.async_tracemoe.is_closed:
            await self.async_tracemoe.aclose()
        return report


async def main5():
    a = TraceMoe()
    result = await a.async_search(r'C:\Users\MSI-PC\Desktop\bmss\20210803195528.png')
    print(result)
    if result:
        pic_list = await a.async_pic_download(download_path=r'C:\Users\MSI-PC\Desktop\bmss')
        print(pic_list)
    else:
        print(a.state)


if __name__ == '__main__':  # 测试例子
    asyncio.run(main5())

