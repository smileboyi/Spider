import requests,codecs
from bs4 import BeautifulSoup

DOWNLOAD_URL = 'http://movie.douban.com/top250/'

# 获取html源码
def download_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/53'
    }
    return requests.get(url,headers=headers).content

# 解析html		
def parse_html(html):
    soup = BeautifulSoup(html)
    movie_items_soup = soup.find('ol',attrs={'class': 'grid_view'}).find_all('li')
    movie_name_list = []
    for movie_li in movie_items_soup:
        detail = movie_li.find('div',attrs={'class': 'hd'})
        movie_name = detail.find('span',attrs={'class':'title'}).getText()
        movie_name_list.append(movie_name)
    next_page = soup.find('span', attrs={'class': 'next'}).find('a')
    if next_page:
        return movie_name_list,DOWNLOAD_URL + next_page['href']
    return movie_name_list,None

# 批量分页请求，将数据存入movie.txt中
def main():
    url = DOWNLOAD_URL
    with codecs.open('movie.txt','wb',encoding='utf-8') as fp:
        # 直到DOWNLOAD_URL为None时不再爬取
        while url:
            html = download_page(url)
            movies, url = parse_html(html)
            fp.write(u'{movies}\n'.format(movies='\n'.join(movies)))


if __name__ == '__main__':
    main()