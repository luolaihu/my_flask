from flask import Flask
from flask import render_template
import redis 
import json
import datetime

app = Flask(__name__)

@app.route('/')
def index():
	day = datetime.datetime.now().strftime('%Y-%m-%d')
	client = redis.StrictRedis(host='127.0.0.1', port = 6379, db = 0)
	articles = client.hgetall(day)
	if articles is None:
		articles = {}
	intList = [int(i) for i in articles.keys()] 
	articleList = [ json.loads(articles[str(k)]) for k in sorted(intList , reverse = False)]
	sort = range(len(articleList))
	return render_template('index.html', day = day, sort = sort , articles = articleList )

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/hr')
def hr():
	return render_template('hr.html')

@app.route('/<day>/<did>')
def detail(day, did):	
	client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
	jsonStr = client.hget(day, did)
	html = 'No This Article'
	if jsonStr is not None:
		body = json.loads(jsonStr)
		html = body['raw_html']
	return html

if __name__ == '__main__':
	app.run()
