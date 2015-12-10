#!/usr/bin/python

import redis
import gflags
import logging
import sys
import datetime
from goose import Goose
import json
from lxml import etree

FLAGS = gflags.FLAGS
gflags.DEFINE_string('url', '', '')

def init(argv):
	FLAGS(argv)

def setHashRedis(key = 'default', field = '1' ,value = ''):
	client = redis.StrictRedis(host = '47.88.26.190', port = 6379, db = 0)
	client.hset(key, field, value)
	client.expire(key, 604800) # 7*24*60*60

def getContent(url = 'http://47.88.26.190/'):
	import httplib2
	h = httplib2.Http('.cache')
	(resp, content) = h.request(url, 'GET')
	return content
	
def getArticle(url):
	g = Goose()
	article = g.extract(url=url)
	return article

def pipe(url):
	article = getArticle(url)
	client = redis.StrictRedis(host = '47.88.26.190', port = 6379, db = 0)
	key = datetime.datetime.now().strftime("%Y-%m-%d")
	num = client.hkeys(key)
	field = 1
	if num is not None:
		field = len(num) + 1
	setHashRedis(key = key, field = field, value = json.dumps({'title':article.title, 'cleaned_text':article.cleaned_text, 'raw_html':article.raw_html}))

def run():
	start_url = FLAGS.url
	detail_urls = []
	html = getContent(url = start_url)
	tree = etree.HTML(html)
	nodes = tree.xpath('//*[@id="page"]/div/div[2]/div/div[2]/div/div[1]/div/div/div[2]/h2/a/@href')
	for node in nodes:
		detail_urls.append(start_url + node[node.find('/',1):])

	client = redis.StrictRedis(host = '47.88.26.190', port = 6379, db = 0)
	key = datetime.datetime.now().strftime("%Y-%m-%d")
	nums = client.hkeys(key)
	for k in nums:
		client.hdel(key, k)
		
	for url in detail_urls:
		pipe(url)

if __name__ == '__main__':
	init(sys.argv)
	run()


