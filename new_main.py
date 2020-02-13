# -*- coding:UTF-8 -*-
# requests版 第二版
# By haozeguanger 2020/02/13
import requests
import os
import time
import sys
import re
import socket
from bs4 import BeautifulSoup

# 主目录地址
linkPath = 'http://m.kukudm.com/comiclist/527'
basePath = 'http://m.kukudm.com'
pic_server = 'https://s1.kukudm.com/'
savePath = 'E:\\pythonWorkSpace'
chapterPath = ''
contentsModel = re.compile("<a href=\'([\S|\w|\d]+.htm)\'>([\S]+)</a></li>")
# reModel = re.compile(b"document.write\(\"<a\shref=\'([\S]*?.htm)\'><IMG\sSRC=\'\"[\S]*?\+\"([\S|\s]*?)\'></a>")
reModel2 = re.compile("document.write\(\"<a\shref=\'([\S]*?.htm)\'><IMG\sSRC=\'\"[\S]*?\+\"([\S|\s]*?)\'></a>")
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
           'Connection': 'close'}

socket.setdefaulttimeout(20)  # 这里对整个socket层设置超时时间。后续文件中如果再使用到socket，不必再设置


def mkdir(path):
    """
    检查是否存在目录，若没有则创建目录
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.mkdir(path)
        print('build dir: [%s]' % path)
    else:
        print('dir [%s] already exist' % path)


def delete_file(path):
    """
    检查是否存在文件，若有则删除文件
    :param path:
    :return:
    """
    if os.path.exists(path):
        os.remove(path)
        print('delete file: [%s]' % path)
    else:
        print('no such file to delete: [%s]' % path)


def downloader(path, url):
    """
    通过requests库，下载文件保存到本地，并显示文件大小和下载进度
    :param path:
    :param url:
    :return:
    """
    if not os.path.exists(path):
        print('now downloading %s as %s' % (url, path))
        start = time.time()  # 开始时间
        ERROR_FLAG2 = False
        for i in range(1, 10):
            try:
                # res = requests.get(url, headers=headers, timeout=5)
                # if res.status_code == 200:
                #     with open(path, 'wb') as f:
                #         f.write(res.content)
                #         f.close()
                #         res.close()
                #         print('已下载：%s' % path)
                #         break
                size = 0
                response = requests.get(url, stream=True, headers=headers, timeout=15)  # stream属性 分段下载
                chunk_size = 10240  # 每次下载数据块的大小
                content_size = int(response.headers['content-length'])  # 总大小
                if response.status_code == 200:
                    print('[file size]:%0.2f MB' % (content_size / 1024 / 1024))
                    with open(path, 'wb') as file:
                        for data in response.iter_content(chunk_size=chunk_size):
                            file.write(data)
                            size += len(data)  # 已下载文件大小
                            # '\r' 回车符 指定第一个字符开始，搭配end属性完成覆盖进度条
                            print('\r' + '[downloading]:%s%.2f%%' % ('['+'>' * int(size / content_size * 50)+' '*(50-int(size / content_size * 50))+']', float(size / content_size * 100)), end='')
                        end = time.time()  # 结束时间
                        print('\n' + 'download successful  %.2fs used; %s' % ((end - start), path))
                        break
            except socket.timeout:
                print('下载第%d次 socket timeout,' % i)
                delete_file(path)
                # time.sleep(1)
            except socket.error:
                print('下载第%d次 socket.error，重试中' % i)
                delete_file(path)
                # time.sleep(1)
            except socket.gaierror:
                print('下载第%d次 socket.gaierror' % i)
                delete_file(path)
                # time.sleep(1)
            except requests.exceptions.Timeout:
                print('下载第%d次连接超时' % i)
                delete_file(path)
                # time.sleep(1)
            if i == 9:
                ERROR_FLAG2 = True
        if ERROR_FLAG2:
            print('\n' + 'download %s failed' % url)
    else:
        print('\n' + 'file [%s] already exists' % path)


def save_pic(path, url):
    """
    :param path:
    :param url:
    :return:
    通过requests库 将抓取到的图片保存到本地
    """
    content = requests.get(url).content
    with open(path, 'wb') as f:
        f.write(content)
        print('已下载：%s' % path)


def test_html(url):
    res = requests.get(url, headers=headers)  # 获取网页内容
    res.encoding = 'gbk'  # 防止出现乱码有时候可以gbk换着用
    soup = BeautifulSoup(res.content, "lxml")  # 通过bs4对网页进行解析
    print(soup.prettify())


def find_chapter(index_url):
    """
    获取漫画目录中的每一章节的url
    返回一个字典类型
    :return:
    """
    chapter_dic = {}
    # 连接目录页面，超时重试10次
    for i in range(1, 20):
        try:
            res = requests.get(index_url, headers=headers, timeout=5)  # 获取url内容
            if res.status_code == 200:
                break
        except socket.timeout:
            print('第%d次 socket.timeout' % i)
            # time.sleep(1)
        except socket.error:
            print('第%d次 socket.error' % i)
            # time.sleep(1)
        except requests.exceptions.Timeout:
            print('第%d次连接超时' % i)
            # time.sleep(1)

        if i == 9:
            print('目录页面连接失败，程序退出')
            sys.exit()

    res.encoding = 'gbk'  # utf-8/gbk
    res.close()
    soup = BeautifulSoup(res.content, "lxml")  # 通过bs4对网页进行解析
    # print(soup.prettify())

    # 找到标题 并创建目录
    title = soup.title.string.split('-')[0]
    print('find name: %s' % title)
    mkdir(savePath + '\\' + title)
    global chapterPath
    chapterPath = savePath + '\\' + title
    print('chapterPath: %s' % chapterPath)

    # 查找所有章节链接
    all_a = soup.find(class_='classopen', id='list').find_all('a')
    # print(all_a)
    for a in all_a:
        chapter_dic[a.text] = basePath + a.get('href')
        print('find chapter: %s, url:%s' % (a.text, basePath + a.get('href')))

    print(chapter_dic)
    return chapter_dic


def get_pic(dic):
    """
    打开字典中每个章节的url
    找到目标图片，下载并保存到本地
    :param dic:
    :return:
    """

    for index in list(dic.keys()):
        print(index)
        print(dic[index])
        ERROR_FLAG = False
        for i in range(1, 20):
            try:
                res = requests.get(dic[index], headers=headers, timeout=5)  # 获取url内容
                if res.status_code == 200:
                    break
            except socket.timeout:
                print('第%d次socket.timeout' % i)
                # time.sleep(1)
            except socket.error:
                print('第%d次 socket.error' % i)
                # time.sleep(1)
            except requests.exceptions.Timeout:
                print('第%d次连接超时' % i)
                # time.sleep(1)
            if i == 9:
                print('%s连接失败，执行下一个下载' % index)
                ERROR_FLAG = True
        if ERROR_FLAG:
            continue

        res.encoding = 'gbk'  # utf-8/gbk
        soup = BeautifulSoup(res.content, "lxml")  # 通过bs4对网页进行解析

        # 获取本章节的总页数
        page_number = soup.find_all('ul', class_='subNav')[1].find_all('li')[1].text.split('/')[1]
        print('%s page number : %s' % (index, page_number))
        global chapterPath
        mkdir(chapterPath+'\\'+index)

        current_page = 1
        while current_page <= int(page_number):
            # 示例： document.write("<a href='/comiclist/527/8459/4.htm'><IMG SRC='" + m2007 + "kuku4comic4/mkxdcdcp/Vol_01/kkdm003XX0.jpg'></a>");
            # 从匹配正则表达式的字符串中提取出有效信息 res1输出示例[(b'/comiclist/527/8459/2.htm', b'kuku4comic4/mkxdcdcp/Vol_01/kkdm001Y9C.jpg')]
            res2 = reModel2.findall(res.content.decode('gbk', 'ignore'))
            # print(res2)
            # print(chapterPath+'\\'+index+'\\'+str(current_page) + '.' + res2[0][1].split('.')[1])
            # print(pic_server + res2[0][1])
            res.close()
            downloader(chapterPath+'\\'+index+'\\'+str(current_page) + '.' + res2[0][1].split('.')[-1], pic_server + res2[0][1])

            # time.sleep(0.25)
            current_page = current_page + 1
            for i in range(1, 20):
                try:
                    res = requests.get(basePath+res2[0][0], headers=headers, timeout=5)  # 获取url内容
                    if res.status_code == 200:
                        break
                except socket.timeout:
                    print('第%d次socket.timeout' % i)
                    # time.sleep(1)
                except socket.error:
                    print('第%d次 socket.error' % i)
                    # time.sleep(1)
                except requests.exceptions.Timeout:
                    print('第%d次连接超时' % i)
                    # time.sleep(1)

                if i == 9:
                    print('%s 第%d页连接失败，执行下一个下载' % (index, current_page))
                    ERROR_FLAG = True
            if ERROR_FLAG:
                continue
            res.encoding = 'gbk'  # utf-8/gbk


def main():
    """
    main program
    :return:
    """
    # test_html(linkPath)
    chapter_dic = find_chapter(linkPath)
    get_pic(chapter_dic)
    # get_pic({'某科学的超电磁炮_Vol_1': "http://m.kukudm.com/comiclist/527/8459/1.htm"})
    print('program shutdown')
    sys.exit()


if __name__ == '__main__':
    main()
