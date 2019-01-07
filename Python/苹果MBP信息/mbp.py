from selenium import webdriver
# 页面加载（初始化是需要一定时间）
from selenium.webdriver.support.wait import WebDriverWait
# 按照XX状态等待DOM节点加载
from selenium.webdriver.support import expected_conditions as EC
# 按照XX方式查找DOM节点
from selenium.webdriver.common.by import By
from selenium.webdriver.common.utils import free_port
from pyquery import PyQuery as pq
from pymongo import MongoClient



# 数据配置
# http://phantomjs.org/download.html
EXECUTABLE_PATH=r'D:\Program Files\phantomjs-2.1.1\bin\phantomjs.exe'
SERVICE_ARGS = [ 
  # 高匿代理,如果代理失效将会拉取空页面：<html><head></head><body></body></html>
  # '--proxy=121.226.3.35:9999',
  '--proxy-type=https',
  '--load-images=false',
  '--ignore-ssl-errors=true',
  '--ssl-protocol=TLSv1',
  '--disk-cache=true',
]

MONGO_URL = 'localhost'
MONGO_DB = 'jd_apple'
MONGO_COLLECTION = 'mbp'
KEYWORD = 'Apple'

# 高版本selenium不再支持PhantomJS：Selenium support for PhantomJS has been deprecated, please use headless
driver = webdriver.PhantomJS(executable_path=EXECUTABLE_PATH, service_args=SERVICE_ARGS, port=free_port())
driver.set_window_size(1920, 1080)
page = WebDriverWait(driver, 10, 1)
client = MongoClient(MONGO_URL)
db = client[MONGO_DB]


# 搜索品牌，进入店铺，进入商品详情页，获取商品信息
def search_apple_goods():
  driver.get('https://www.jd.com/')
  try:
    print('搜索{}店铺'.format(KEYWORD))
    input_search = page.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#key")))
    btn_search = page.until(EC.element_to_be_clickable((By.XPATH, "//button[@clstag='h|keycount|head|search_c']")))
    input_search.send_keys(KEYWORD)
    btn_search.click()
    print('进入{}店铺'.format(KEYWORD))
    # 点击a标签是新开一个窗口
    shop_enter_btn = page.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".shop-enter")))
    shop_enter_btn.click()
    driver.switch_to_window(driver.window_handles[1])
    print('进入{}详情页'.format(MONGO_COLLECTION))
    mac_item = driver.find_element_by_css_selector('div.user-nav ul li:nth-child(2)')
    js="var div=document.querySelector('div.user-nav ul li :nth-child(2)');div.style.display='block';"
    # 设置节点可见才能点击
    driver.execute_script(js)
    mbp_link = mac_item.find_element_by_css_selector('div.user-navding ul li:nth-child(2) a')
    mbp_link.click()
    driver.switch_to_window(driver.window_handles[2])
    save_goods_info(driver.page_source)
  except Exception as e:
    print("重新开始爬取")
    driver.save_screenshot('screenshot.png')
    search_apple_goods()



# 保存商品信息
def save_goods_info(html):
  print("爬取数据并保存。。。")
  doc = pq(html)
  ul = doc(".parameter2.p-parameter-list")
  lis = ul.children()
  info_list = []
  for li in lis:
    key,val = li.text.split('：')
    info_list.append({key:val})

  try:
    db[MONGO_COLLECTION].insert({'infos': info_list})
    print("商品信息已保存到本地mongo中")
  except Exception as e:
    print('Fail to save, {}'.format(e))



if __name__ == '__main__':
  search_apple_goods()