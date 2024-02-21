import datetime
import pickle
import json
from pprint import pprint
from pybars import Compiler

with open("bot_data.pickle", 'rb') as file:
  data = pickle.load(file)

with open("feed.hbs", 'r') as file:
  template = file.read()

data_json = json.loads(json.dumps(data))

compiler = Compiler()
template = compiler.compile(template)

def _print(this, item):
  return json.dumps(item)
def now(this):
  return datetime.datetime.now().isoformat() + 'Z'
def _len(this, item):
  return len(item)

helpers = {'print': _print, 'now': now, 'len': _len}

output = template(data_json, helpers=helpers)

print(output)
