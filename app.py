from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from utils.scraper import scrape_topics
import calendar
import requests
import os

load_dotenv()
app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGO_URI')
mongo = PyMongo(app)

def get_device_ip():
    r = requests.get('https://api.ipify.org/')
    return r.text

def write_to_mongo_db(topics, ip, start_time_str, utc_timestamp):
    document = {
        'ip': ip,
        'start_timestamp': utc_timestamp,
        'start_time': start_time_str
    }

    for i, topic in enumerate(topics):
        document[f'nameoftrend{i+1}'] = topic

    record = mongo.db.trending.insert_one(document)
    document['_id'] = str(record.inserted_id)
    return document

def logger(log, cb=None):
    print(log)
    if cb:
        cb(log)

@app.route('/api/scrape', methods=['GET'])
def scrape():
    args = request.args
    proxy = args.get('proxy', 'false') == 'true'
    headless = args.get('headless', 'false') == 'true'
    use_profile = args.get('profile', 'false') == 'true'

    logs = []
    topics, ip, start_time = scrape_topics(proxy, headless, use_profile, lambda log: logger(log, lambda x: logs.append(x)))
    utc_timestamp = calendar.timegm(start_time.utctimetuple())
    start_time_str = start_time.strftime("%d/%m/%Y, %H:%M:%S")
    if topics is None:
        return jsonify({
            'success': False,
            'ip': ip,
            'start_time': start_time_str,
            'logs': logs
        })

    new_entry = write_to_mongo_db(topics, ip, start_time_str, utc_timestamp)
    return jsonify({
        'success': True,
        'ip': ip,
        'start_timestamp': utc_timestamp,
        'start_time': start_time_str,
        'topics': topics,
        'logs': logs,
        'entry': new_entry
    })



@app.route('/', methods=['GET'])
def index():
    device_ip = get_device_ip()
    return render_template('index.html', device_ip=device_ip)

if __name__ == '__main__':
    app.run(debug=True)