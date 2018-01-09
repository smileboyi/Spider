import requests
import json
import xlwt
import time
import random


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
    json = requests.post(url, headers=headers, cookies=cookies, data=data).json()

    return parse_json(json['content']['positionResult']['result'])


# 解析每页json		
def parse_json(json):
    page_data = []  #每一页的职位数据
    for i in range(len(json)):
        item,job = [],json[i]
        item.append(job['positionId']) #岗位对应ID
        item.append(job['companyFullName']) #公司全名
        item.append(','.join(job['companyLabelList'])) #福利待遇(数组转成字符串)
        item.append(job['district']) #工作地点
        item.append(job['education']) #学历要求
        item.append(job['firstType']) #工作类型
        item.append(job['formatCreateTime']) #发布时间
        item.append(job['positionName']) #职位名称
        item.append(job['salary']) #薪资
        item.append(job['workYear']) #工作年限
        page_data.append(item)

    return page_data



# 表格样式
def set_style(name, height, bold = False):
    #初始化样式    
    style = xlwt.XFStyle()
    #为样式创建字体   
    font = xlwt.Font()
    font.name = name  
    font.bold = bold  
    font.color_index = 4  
    font.height = height  
    style.font = font

    return style  


# 创建带title信息的表格
def create_excel():  
    #创建工作簿  
    workbook = xlwt.Workbook(encoding='utf-8')    
    #创建sheet  
    data_sheet = workbook.add_sheet('sheet1')    
    row0 = ['岗位id','公司全名','福利待遇','工作地点','学历要求','工作类型','发布时间','职位名称','薪资','工作年限']
      
    #生成第一行(title) 
    for i in range(len(row0)):  
        data_sheet.write(0, i, row0[i], set_style('Times New Roman', 220, True))
        if i == 1 or i == 2:
            data_sheet.col(i).width = 10240
        else:
            data_sheet.col(i).width = 5120

    return workbook,data_sheet


# 读取数据写入表格中
def write_excel(workbook, sheet, data, page):   
    # 根据分页位置算出指定行位置基准
    index_base = (page - 1) * len(data) + 1
    for i in range(len(data)):  
        job = data[i]
        for j in range(len(job)):
            sheet.write(index_base + i, j, job[j])


# 入口程序
def main(kd='python'):
    url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&isSchoolJob=0'
    # 创建表格
    workbook,data_sheet = create_excel()
    # 爬取数据写入表格中
    for page in range(0,10):
        print('正在爬取第%d页数据。。。' % (page+1))
        page_data = get_json(url, kd, page)
        write_excel(workbook,data_sheet,page_data,page+1)

        # # 一页爬取完就随机sleep(防止出现操作频繁拒绝访问的警告)
        time.sleep(25 + random.randint(0,25))
        
    # 完成后保存数据表格
    workbook.save(kd + '_job.xls')
    print(u'创建' + kd + '_job.xls文件成功')



if __name__ == '__main__':
    # main('java')
    main()
    