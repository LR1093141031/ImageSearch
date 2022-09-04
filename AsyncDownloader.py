import asyncio
import re

import httpx
import os

wait_fixed = 0.2  # 出错重试等待


async def async_pic_download(async_client: httpx.AsyncClient,
                             img_url_list: list,
                             img_file_name_list: list,
                             download_path: str,
                             request_headers=None,
                             max_attempt=3) -> list:
    """
    异步图片下载
    :param async_client: httpx.AsyncClient
    :param img_url_list: 待下载图片url列表
    :param img_file_name_list: 带下载图片名称列表
    :param download_path: 全路径
    :param max_attempt: 最大出错尝试次数
    :param request_headers:
    :return: 图片全路径或None 列表（尝试下载失败)
    """

    # 输入检查
    if len(img_url_list) != len(img_file_name_list):
        raise ValueError('输入url与name列表长度不一')
    if not os.path.exists(download_path):
        raise FileNotFoundError('输入下载地址不存在')

    task_list = []
    for url, file_name in zip(img_url_list, img_file_name_list):
        task = asyncio.create_task(
            _async_pic(async_client, url, file_name, download_path, request_headers, max_attempt))
        task_list.append(task)
    results = await asyncio.gather(*task_list)
    # await async_client.aclose()
    return list(results)


async def _async_pic(async_client: httpx.AsyncClient, img_url: str, file_name: str, download_path: str,
                     request_headers=None, max_attempt=3):
    pic = None
    attempt_num = 0

    if not img_url or not file_name:
        print('无效url 或 file_name 跳过')
        return None

    file_name = img_file_name_filter(file_name)

    while attempt_num < max_attempt:
        try:
            response = await async_client.get(img_url, headers=request_headers)
            pic = response.content
        except Exception as e:
            attempt_num += 1  # 抛错则再次尝试请求下载
            print(f'图片ID {file_name}下载出错 ', attempt_num)
            await asyncio.sleep(wait_fixed)
            continue
        break

    if pic:
        with open(f'{download_path}/{file_name}', 'wb') as f:
            f.write(pic)
        print(f'图片ID {file_name}下载完成')
        return f'{download_path}/{file_name}'
    else:
        print(f'图片ID {file_name}下载失败')
        return None


def img_file_name_filter(file_name: str) -> str:
    # 尝试修整一下fileName
    for char in [" ", "[", "]", "#", "+", "-", "*", "/", "\\", "|", "(", ")", "<", ">", "?", "@", "!", "`", "~", "$",
                 "%", "^", "&", ":", ",", "{", "}"]:
        file_name = file_name.replace(char, "")

    for img_type in ['.jpg', '.png']:
        fix = re.findall(img_type, file_name)
        if fix and len(fix) > 1:
            file_name.replace(img_type, "")
            file_name += img_type

    return file_name
