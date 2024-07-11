import pickle
import json
import sys
from pprint import pprint

if len(sys.argv) < 2:
  print("must specify user id as argument")
  sys.exit(1)

with open("bot_data.pickle", 'rb') as file:
  data = pickle.load(file)

todel = sys.argv[1]
print(f"Attempting to delete {todel} from bot_data")

try:
  del data["bot_data"][int(todel)]
except:
  print("could not delete")
  sys.exit(1)

print("re-saving pickle file")
with open("bot_data.pickle", "wb") as file:
  pickle.dump(data, file)
