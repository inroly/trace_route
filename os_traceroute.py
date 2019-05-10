#coding=utf-8
#python2
#linux系统
#需要安装GeoLite2-City_20190226库，文件在包里，路径需要修改，在前端开启前需要运行py文件
import os
import subprocess
import re
import geoip2.database
from flask import Flask,jsonify,render_template,request
import json

app = Flask(__name__)#实例化app对象
location = {}
iplist=[]

@app.after_request
def after_request(response):
	# 这里不能使用add方法，否则会出现 The 'Access-Control-Allow-Origin' header contains multiple values 的问题
	response.headers['Access-Control-Allow-Origin'] = '*'
	return response

@app.route('/')
def get_domain():
	target_domain = request.args.get('domain', '')#输入跟踪域名
	get_TraceRoute_ip(target_domain)
	
	return json.dumps(location)
#	return "1"


def get_TraceRoute_ip(target_domain):
	
	target_domain = request.args.get('domain', '')#输入跟踪域名
	cmd = 'traceroute -q 1 -m 15 '+ target_domain
	print target_domain
	iplist=[]
	r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) #使用pipe持续后的
	for line in iter(r.stdout.readline, b''): #比特形式迭代
		line = line.strip('\r\n')
		iplist.append(line) #添加行信息
		print line
	print "ip seek done"
	doneip = []
	p = re.compile(r'[(](.*?)[)]', re.S)#最小匹配，正则表达式，匹配括号内内容
	for ip_index in range(0,len(iplist)):
		if iplist[ip_index].find('*') != -1:
			continue
		else:
			doneip.append(re.findall(p, iplist[ip_index])[0])
	get_position(doneip)
	


def get_position(iplist):
	data_x = []
	data_y = []
	data_city = []
	data_country = []
	data_ip = []
#	iplist=["10.168.1.1", "192.20.122.1", '58.20.127.97', '119.39.32.150', '58.20.46.196']
	reader = geoip2.database.Reader('/Users/matthew/Desktop/GeoLite2-City_20190226/GeoLite2-City.mmdb')
	for each_ip in iplist:
#		print type(each_ip)
		if re.match("10.",each_ip)!=None or re.match("192.",each_ip)!=None:
			continue
		response = reader.city(each_ip)
		print each_ip
#		print each_ip
#		#print "??"
#		print response.country.iso_code
		data_country.append(response.country.name)
		data_ip.append(each_ip)
#		print response.country.names['zh-CN']
#		print response.subdivisions.most_specific.name
#		print response.subdivisions.most_specific.iso_code
		data_city.append(response.city.name)
#		print response.postal.code
#		print response.location.latitude
#		print response.location.longitude
		data_x.append(response.location.longitude)
		data_y.append(response.location.latitude)
#		#print "!!!!"
	location['x'] = data_x
	location['y'] = data_y
	location['city'] = data_city
	location['country'] = data_country
	location['ip'] = iplist
	reader.close()
	
	


if __name__ == "__main__":
	app.run(host='0.0.0.0',#任何ip都可以访问
				port=7777,#端口
				debug=True
				)
	#get_TraceRoute_ip()
	