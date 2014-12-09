import json
from pprint import pprint
json_data= ('{"VM": ["rsinghania_175","rsinghania_174","rsinghania_176"]}')
data = json.loads(json_data)
pprint(data)
