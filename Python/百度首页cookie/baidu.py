import urllib.request
import http.cookiejar


if __name__ == '__main__':
  filename = 'cookie.txt'

  """第一次访问获取cookie并保存"""

  # 声明一个MozillaCookieJar对象实例来保存cookie
  cookie = http.cookiejar.MozillaCookieJar(filename)
  # 利用HTTPCookieProcessor对象来创建cookie处理器
  handler=urllib.request.HTTPCookieProcessor(cookie)
  # 利用build_opener方法创建一个opener
  opener = urllib.request.build_opener(handler)

  response = opener.open('http://www.baidu.com')
  # 保存cookie到文件
  # ignore_discard的意思是即使cookies将被丢弃也将它保存下来，
  # ignore_expires的意思是如果在该文件中cookies已经存在，则覆盖原文件写入。
  cookie.save(ignore_discard=True, ignore_expires=True)


  """第二次访问，带上cookie"""
  # 创建MozillaCookieJar实例对象
  cookie = http.cookiejar.MozillaCookieJar()
  # 从文件中读取cookie内容到变量
  cookie.load('cookie.txt', ignore_discard=True, ignore_expires=True)
  # 创建请求的request
  req = urllib.request.Request("http://www.baidu.com")
  opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
  response = opener.open(req)
  print(response.read())

