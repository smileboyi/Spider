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
      # item[0]地址，item[1]标题
      soriQ.put([item[0],item[1]])


  # 爬取前n页的列表
  def getRangePage(self,n):
    for i in range(n):
      url = self.baseUrl + "list_9_" + str(i+1) + ".html"
      page = self.getPage(url)
      self.getAllInfo(page)
      

  # 入口
  def start(self,index):
    self.getRangePage(index)



# 下载图片类
class DownloadImg:
  def __init__(self):
    pass

  




url = RosiUrl()
url.start(3)
