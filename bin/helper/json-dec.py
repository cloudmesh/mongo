import json
from pprint import pprint

json_data= ('{"VM": ["rsinghania_175","rsinghania_174","rsinghania_176"]}')
data = json.loads(json_data)
pprint(data)


txt = '''{
    "16448a63-59c7-4016-b791-a21873faac58": {
        "floating": "149.165.158.104",
        "fixed": "10.39.1.146",
        "name": "rsinghania_205"
    },
    "64e2f361-616a-4e2e-81dc-9eb7db88430c": {
        "floating": "149.165.158.105",
        "fixed": "10.39.1.149",
        "name": "rsinghania_206"
    },
    "b4f02e1a-a9ec-447c-bc23-abbfec044032": {
        "floating": "149.165.158.110",
        "fixed": "10.39.1.140",
        "name": "rsinghania_204"
    }
}'''

json_data= (txt)
data = json.loads(json_data)
for i in data:
        print (data[i]["floating"])
        




