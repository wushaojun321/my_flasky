#encoding:utf8

import re
import requests
def get_page():
	r = requests.get('http://jandan.net/ooxx')
	html = r.text.encode('utf-8')
	re_rule_page = r'<a href="http://jandan.net/ooxx/page-(.+?)#comment-'
	page = re.findall(re_rule_page, html)
	if len(page) != 0:
		if page[0].isdigit():
			i = int(page[0])
			L = [str(i), str(i-1), str(i-2)]
			return L	
	result = {'code':11,'message':'re error!'}
	return result

def get_pic_url():
	page = get_page()
	if type(page) == list and len(page) != 0:
		L = []
		re_rule = r'<p><a href="(.+?\.jpg)" target="_blank" class="view_img_link">\[查看原图\]'
		for i in page:
			url = 'http://jandan.net/ooxx/page-'+i
			r = requests.get(url)
			r = r.text.encode('utf-8')
			pic_url = re.findall(re_rule, r)
			L = L + pic_url
		return L
	return page