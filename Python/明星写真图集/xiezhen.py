import requests
import sys,re,os
from threading import Thread
from queue import Queue
from time import sleep


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
    response = requests.get(url)
    response.encoding = 'gbk'
    return response.text


  # 获取所有展示页面中img的url
  def getAllUrls(self,url):
    # 第一页的url
    page = self.getPage(url)
    self.getImgUrls(page)

    # 下一页的url
    # nextPage = page
    # pageBaseUrl = url[:-10:1]
    # pattern = re.compile(r'<a href="(.*?)">下一页</a>',re.S)
    # item = re.findall(pattern,nextPage)
    # print(item)

    # while True:
    #   item = re.findall(pattern,nextPage)
    #   print(item)
    #   if newxtUrl == "#":
    #     return None
    #   else:
    #     nextPage = self.getPage(pageBaseUrl + newxtUrl)
    #     self.getImgUrls(nextPage)


  # 获取展示页面中img的url
  def getImgUrls(self,page):
    pattern = re.compile(r'<a.*?title="点击图片进入下一页".*?src="(.*?)".*?</a>',re.S)
    urls = re.findall(pattern,page)
    print(urls)
    for url in urls:
      self.urls.append(url)


  # 保存图片,folder为文件夹
  def saveImg(self,folder):
    i = 1
    for url in self.urls:
      ir = requests.get(url,stream=True)
      if ir.status_code == 200:
        imgType = self.getImgType(url) 
        with open('/%s/%d.%s' % (folder,i,imgType), 'wb') as f:
          f.write(ir.content)
          f.flush()
        i +=1


  def getImgType(self,url):
    arr = url.split('.')
    l = len(arr)
    return arr[l-1]


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


  # def start(self):
  #   global soriQ
  #   while not soriQ.empty():
  #     item = soriQ.get()
  #     # 创建文件夹
  #     self.mkdir(item[1])
  #     # 获取图片地址
  #     self.getAllUrls(item[0])
  #     print(self.urls)
  #     # 下载图片
  #     self.saveImg(item[1])
  #     # 完成一项任务
  #     soriQ.task_done()


  def start(self):
    global soriQ
    item = soriQ.get()
    # 创建文件夹
    self.mkdir(item[1])
    # 获取图片地址
    self.getAllUrls(item[0])
    # 下载图片
    self.saveImg(item[1])
    # 完成一项任务
    soriQ.task_done()
  

url = RosiUrl()
url.start(1)
img = DownloadImg()
img.start()
