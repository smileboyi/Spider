import requests
import json
import datetime
from pymongo import MongoClient
from proxies import get_proxie_dict

# 获取职位json
def get_json(url, kd, page):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/53',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6,ja;q=0.4,en;q=0.2',
        'Host': 'www.lagou.com',
        'Origin': 'https://www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_'+kd,
        'X-Requested-With': 'XMLHttpRequest'
    }
    # 需要定期修改cookies
    cookies = {
        'Cookie': 'JSESSIONID=ABAAABAACDBABJB477830E740BBFD22D693ACC2D2AFD7F6; user_trace_token=20180105135028-a118aa1b-ab84-4658-9220-3ca2b04b921f; _ga=GA1.2.1427071389.1515131415; _gid=GA1.2.1682641947.1515131415; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1515131415; LGUID=20180105135030-56ad3ff2-f1dc-11e7-a015-5254005c3644; TG-TRACK-CODE=search_code; LGSID=20180105164714-06cdee38-f1f5-11e7-a015-5254005c3644; X_HTTP_TOKEN=c41f8f03ff82ed82b944a7e671d5cc6a; _gat=1; SEARCH_ID=3e642cab3b754a0387f4ddd1ef44ac67; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1515144376; LGRID=20180105172632-8481a7d8-f1fa-11e7-bf06-525400f775ce'
    }
    data = {'first': 'false', 'pn': page, 'kd': kd}
    json = requests.post(url, headers=headers, proxies=get_proxie_dict(), cookies=cookies, data=data).json()
    
    return json['content']['positionResult']['result']


# 每页json解析完保存到数据库中		
def save_json(json, db):
    for i in range(len(json)):
        item,job = {},json[i]
        item['_id'] = job['positionId']    #岗位对应ID
        item['companyFullName'] = job['companyFullName']   #公司全名
        item['companyLabelList'] = job['companyLabelList']  #福利待遇
        item['district'] = job['district']   #工作地点
        item['education'] = job['education']  #学历要求
        item['firstType'] = job['firstType']  #工作类型
        item['formatCreateTime'] = job['formatCreateTime']   #发布时间
        item['positionName'] = job['positionName']   #职位名称
        item['salary'] = job['salary']    #薪资
        item['workYear'] = job['workYear']   #工作年限
        item['updateTime'] = datetime.datetime.now()  #更新时间
        result = db.lagou.find_one({'_id': item['_id']}) 
        # 如果存在重复职位，不添加进去
        if not result: 
            db.lagou.insert(item)
            

# 入口程序
def main(kd='python'):
    url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&isSchoolJob=0'

    # 打开数据库
    client = MongoClient('localhost',27017)
    db = client.spiderDB

    # 先清空集合
    db.lagou.remove({})
    
    # 循环获取数据
    for page in range(0,30):
        print('正在爬取第%d页数据。。。' % (page+1))

        json = get_json(url, kd, page)
        save_json(json=json, db=db)
        
    print('数据爬取完毕！')


if __name__ == '__main__':
    main()
    