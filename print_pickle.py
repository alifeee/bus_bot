import pickle
import json
from pprint import pprint

with open("bot_data.pickle", 'rb') as file:
  data = pickle.load(file)

print(json.dumps(data))
