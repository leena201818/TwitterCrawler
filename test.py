# encoding=utf-8
import json

def getDispatchServerConfig():
    with open('config.json', 'r') as f:
        x = json.load(f)
        return x['serverinfo']['serverIP'], x['serverinfo']['serverPort']

if __name__ == '__main__':
    x = getDispatchServerConfig()
    print(x)
