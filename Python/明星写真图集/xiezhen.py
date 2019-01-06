import requests
import re,os
from threading import Thread
from queue import Queue
import time
import random


# 明星地址队列FIFO
soriQ = Queue(0)

# 获取图片地址类
class RosiUrl:
  # 初始化
  def __init__(self):
    self.baseUrl = "http://www.5442.com/mingxingtuku/"


  # 获取某一页明星列表页面的代码
  def getPage(self,url):
    response = requests.get(url)
    response.encoding = 'gbk'
    return response.text


  #　解析getPage返回的代码并放入队列中
  def getAllInfo(self,page):
    pattern1 = re.compile(r'<div class="imgList2">(.*?)</div>',re.S)
    itemsMain = re.findall(pattern1,page)
    pattern = re.compile(r'<li.*?<a href="(.*?)".*?title="(.*?)".*?<img.*?</a>',re.S)
    items = re.findall(pattern,itemsMain[0])
    for item in items:
      global soriQ
      # item[0]地址，item[1]标题
      soriQ.put([item[0],item[1]])


  # 爬取前n页的列表
  def start(self,n):
    for i in range(n):
      url = self.baseUrl + "list_9_" + str(i+1) + ".html"
      page = self.getPage(url)
      self.getAllInfo(page)



# 下载图片类
class DownloadImg:
  def __init__(self):
    self.urls = []


  # 获取展示页面的代码
  def getPage(self,url):
    response = requests.get('https:' + url)
    response.encoding = 'gbk'
    return response.text


  # 获取所有展示页面中img的url
  def getAllUrls(self,url):
    # 第一页的url
    page = self.getPage(url)
    self.getImgUrls(page)

    # 下一页的url
    nextPage = page
    pageBaseUrl = url[:-10:1]
    # 这里没有写下一页，不会被正常解析，原因可能是编码不一致
    pattern = re.compile(r"<li><a href='(.*?)'>.*?</a></li>",re.S)

    item = re.findall(pattern,nextPage)
    while True:
      item = re.findall(pattern,nextPage)
      # 获取下一页的地址
      nextUrl = item[len(item)-1]
      if nextUrl == "#":
        return None
      else:
        nextPage = self.getPage(pageBaseUrl + nextUrl)
        self.getImgUrls(nextPage)


  # 获取展示页面中img的url
  def getImgUrls(self,page):
    # 前面页面是下一页，最后一页是下一篇
    pattern = re.compile(r"<a.*?title='点击图片进入下一.*?<img src='(.*?)'",re.S)
    urls = re.findall(pattern,page)
    for url in urls:
      self.urls.append(url)


  # 获取图片类型
  def getImgType(self,url):
    arr = url.split('.')
    l = len(arr)
    return arr[l-1]


  # 保存图片,folder为文件夹
  def saveImg(self,folder):
    i = 1
    for url in self.urls:
      ir = requests.get(url,stream=True)
      # ir：<Response [403]>，通过proxys和headers解决
      if ir.status_code == 200:
        imgType = self.getImgType(url) 
        with open('%s/%d.%s' % (folder,i,imgType), 'wb') as f:
          f.write(ir.content)
          f.flush()
        i +=1
    # 一个图片下载任务完成后清空
    self.urls = []

  # 创建文件夹
  def mkdir(self,path):
    path = path.strip()
    # 判断路径是否存在
    isExists=os.path.exists(path)
    if not isExists:
      # 如果不存在则创建目录
      os.makedirs(path)
      return True
    else:
      # 如果目录存在则不创建，并提示目录已存在
      return False


  def start(self):
    # 多个进程公用一个队列
    global soriQ
    while not soriQ.empty():
      item = soriQ.get()
      # 创建文件夹
      self.mkdir(item[1])
      # 获取图片地址
      self.getAllUrls(item[0])
      # 下载图片
      self.saveImg(item[1])
      # 完成一项任务
      soriQ.task_done()
      # 休眠，time.sleep是对当前线程的sleep
      time.sleep(10 + random.randint(0,10))



if __name__ == '__main__':
  ru = RosiUrl()
  ru.start(5)

  for i in range(5):#新建5个线程 等待队列
    di = DownloadImg()
    t = Thread(target=di.start)
    # 父线程为守护进程
    t.setDaemon(True)
    t.start()

  # 阻塞调用线程，直到队列中的所有任务被处理掉。
  # 当未完成的任务数降到0，join()解除阻塞。
  soriQ.join()