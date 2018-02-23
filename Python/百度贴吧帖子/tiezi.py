import re
import urllib.request

# 处理页面标签类
class Tool:
	# 去除img标签,7位长空格
	removeImg = re.compile('<img.*?>| {7}|')
	# 删除超链接标签
	removeAddr = re.compile('<a.*?>|</a>')
	# 把换行的标签换为\n
	replaceLine = re.compile('<tr>|<div>|</div>|</p>')
	# 将表格制表<td>替换为\t
	replaceTD= re.compile('<td>')
	# 把段落开头换为\n加空两格
	replacePara = re.compile('<p.*?>')
	# 将换行符或双换行符替换为\n
	replaceBR = re.compile('<br><br>|<br>')
	# 将其余标签剔除
	removeExtraTag = re.compile('<.*?>')
	def replace(self,x):
		x = re.sub(self.removeImg,"",x)
		x = re.sub(self.removeAddr,"",x)
		x = re.sub(self.replaceLine,"\n",x)
		x = re.sub(self.replaceTD,"\t",x)
		x = re.sub(self.replacePara,"\n    ",x)
		x = re.sub(self.replaceBR,"\n",x)
		x = re.sub(self.removeExtraTag,"",x)
		# strip()将前后多余内容删除
		return x.strip()
			


# 百度贴吧爬虫类
class BDTB:
 
	# 初始化，传入基地址，see_lz是否只看楼主，pn页数
	def __init__(self,baseUrl,seeLZ):
		self.baseURL = baseUrl
		self.seeLZ = '?see_lz='+str(seeLZ)
		# 获取一个工具处理实例
		self.tool = Tool()

	# 传入页码，获取该页帖子的代码
	def getPageContent(self,pageNum):
		try:
			url = self.baseURL+ self.seeLZ + '&pn=' + str(pageNum)
			request = urllib.request.Request(url)
			# py3的urlopen返回的不是string是bytes。
			response = urllib.request.urlopen(request)
			return response.read().decode('utf-8') 
		except urllib.request.URLError as e:
			if hasattr(e,"reason"):
				print(u"连接百度贴吧失败,错误原因",e.reason)
				return None

	
	# 获取标题
	def getTitle(self):
		content = self.getPageContent(1)
		pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
		result = re.search(pattern,content)
		if result:
			return result.group(1).strip()
		else:
			return "百度贴吧"


	# 获取页数
	def getPageNum(self):
		content = self.getPageContent(1)
		pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>',re.S)
		result = re.search(pattern,content)
		if result:
			return int(result.group(1))
		else:
			return None


	# 获取帖子内容
	def getContent(self,content):
		pattern = re.compile('<div id="post_content_.*?>(.*?)</div>',re.S)
		return re.findall(pattern,content)


	# 启动程序，拉取帖子
	def start(self):
		pageNum = self.getPageNum()
		if pageNum == None:
			print("URL已失效，请重试")
			return

		# 创建一个文件
		file = open(self.getTitle() + ".txt", "w+", encoding="utf-8")
		floor = 1
		try:
			print("该帖子共有" + str(pageNum) + "页")
			for page in range(pageNum):
				print("正在写入第" + str(page+1) + "页数据")
				items = self.getContent(self.getPageContent(page+1))
				for item in items:
					file.write("-----------------楼层：" + str(floor) + "------------------\n")
					file.write("\n" + self.tool.replace(item) + "\n")
					floor += 1
		except IOError as e:
			print("写入异常，原因" + e.message)
		finally:
			print("写入任务完成")



if __name__ == "__main__":
	baseURL = 'http://tieba.baidu.com/p/3138733512'
	bdtb = BDTB(baseURL,1)
	bdtb.start()

