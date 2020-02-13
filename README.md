# python-manga-download

2020/02/13 属于python爬虫学习项目，仅供学习交流 使用python3 requests。 图片爬虫目标：某科学的超电子炮漫画 ，漫画目录URL：'http://m.kukudm.com/comiclist/527'

参考了https://github.com/CatAndCoffee/playground/tree/master/%E8%B6%85%E7%82%AE%E4%B8%8B%E8%BD%BD 项目，全面重写，做了V2版 目前到122话，下载后总大小大约500M，单线程，有点慢，网不好可以挂代理。

相比于之前提到的原始项目：

1.用函数定义各个模块，方便维护

2.添加了下载进度条

3.添加了进度提示

4.添加了requests的超时或异常后的重连

5.增加了各种异常的捕获处理，尤其是对requests下载时的 socket error：socket timeout错误的处理（使用"except socket.error:"接收）

踩坑记录：

1.网页用gbk编码，图片URL有汉字（艹），正则匹配，字符串转码时要注意

2.有几集（28,65,66）的图片404，需要考虑到图片url报错404的问题

3.会出现"Max retries exceeded with url"问题，解决方法是在requests.get 的参数headers里添加'Connection': 'close' headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36','Connection': 'close'}

4.会出现 socket error：socket timeout和 socket error：read timeout 错误，使用' except socket.timeout:'无法捕获这些异常。结果是使用' except socket.error:'捕获的异常
