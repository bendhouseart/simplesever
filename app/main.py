import flask
import requests
import psutil
import math
import time
import lorem
import random
from prometheus_flask_exporter import PrometheusMetrics

app = flask.Flask(__name__)
#app.config["DEBUG"] = True
metrics = PrometheusMetrics(app)

metrics.info('app_info', 'Application info', version='0.0.0')


@app.route('/')
def home():
    return "<h1>Welcome to a simple flask app to fulfill server requests needed for Insight's " \
           "DevOps Challenge Problem</h1>"


@app.route('/cpu', methods=['GET'])
def cpu_intensive():
    n1, n2 = 0, 1
    count = 0
    nterms = 1000
    cpu_log = []
    while count < nterms:
        cpu = psutil.cpu_percent()
        cpu_log.append(cpu)

        nth = n1 + n2
        n1 = n2
        n2 = nth
        if count > 100:
            avg_cpu_use = math.fsum(cpu_log[-5:])/5
            print(avg_cpu_use)
            if cpu > 90.0:
                message = f"Maxed cpu usage stopping fib sequence at count: {count}, number: {nth}"
                count += 1
                return message
            else:
                count -= 1
        else:
            count += 1
        print(f"cpu %{str(cpu)}, fib num: {nth}")
        message = f"Reached count: {count}, number:{nth}"

    return message


@app.route('/memory', methods=['GET', 'POST'])
def mem_intensive():
    if flask.request.method == 'POST':
        print(flask.request.method)
    else:
        mem = psutil.virtual_memory()
        mem_hog = []
        long_wiki_entry = requests.get('https://en.wikipedia.org/wiki/List_of_Private_Passions_episodes')

        if mem.percent > 90.0:
            low_memory = True
        elif long_wiki_entry.status_code != 200:
            low_memory = True
            print("Failed GET request from URL")
        else:
            low_memory = False

        while not low_memory:
            mem = psutil.virtual_memory()
            time.sleep(0.01)
            if mem.percent > 90:
                low_memory = True
                mem_hog = []
            else:
                mem_hog.append(long_wiki_entry.text)
        return "Kicking off memory intensive task"


@app.route('/disk', methods=['GET'])
def disk_intensive():
    try:
        path = '/var/tmp/garbage_file_' + str(random.randint(0, 999999999999999)) + '.txt'
        with open(path, 'w') as outfile:
            for i in range(100):
                paragraph = lorem.paragraph()
                print(paragraph, file=outfile)
    except FileNotFoundError:
        pass
    return "Writing lorem to disk"


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=80)
    except PermissionError:
        app.run()
