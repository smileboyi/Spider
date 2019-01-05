import requests
import http.client
import re


def get_proxy(page):
  xiciUrl = 'http://www.xicidaili.com/nn/' + str(page)
  headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
  }
  response = requests.get(xiciUrl, headers=headers)
  pattern = re.compile('<tr.*?country.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?高匿.*?<td>(.*?)</td>.*?</tr>', re.S)
  return re.findall(pattern, response.text)



def test_proxy(proxy):
  baiduUrl = "http://www.baidu.com"
  headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
  }
  ip = proxy[0]
  port = proxy[1]
  try:
    # 只要能在3秒内连接上说明代理可用
    conn = http.client.HTTPConnection(ip, port, timeout=3)
    conn.request(method='GET', url=baiduUrl, headers=headers)
    return proxy
  except:
    return None


def collect_usable_proxy(proxy):
  proxy_list = []
  for proxy in proxys:
    p = test_proxy(proxy)
    if p is not None:
      proxy_list.append(p)
  return proxy_list



if __name__ == '__main__':
  for i in range(3):
    print('获取和验证第{}页代理中。。。'.format(i+1))
    proxys = get_proxy(i+1)
    proxy_list = collect_usable_proxy(proxys)
    print('第{}页可用代理：{}'.format(i+1, proxy_list))

