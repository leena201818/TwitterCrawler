# encoding=utf-8
import json
import xmlrpc.client

from loghelper.loghelper import logHelper

from mysqlserver import MySqlServer

def getDispatchServerConfig():
    with open('config.json', 'r') as f:
        x = json.load(f)
        return x['serverinfo']['serverIP'], x['serverinfo']['serverPort']


def getDatabaseServerConfig():
    with open('config.json', 'r') as f:
        x = json.load(f)
        return x['serverinfo']['dbIP'], x['serverinfo']['dbPort'], x['serverinfo']['dbUser'], x['serverinfo']['dbPwd'], x['serverinfo']['dbName']

def testDispatchServer():
    '''
    判断是否连接上调度服务器：
    :return:'Connected!' or "Disconnected!"
    '''
    serverconfig = getDispatchServerConfig()
    try:
        s = xmlrpc.client.ServerProxy('http://{0}:{1}'.format(serverconfig[0], serverconfig[1]))
        logHelper.getLogger().debug('connecting to the dispatch server http://{0}:{1}'.format(serverconfig[0], serverconfig[1]))
        return s.test()
    except Exception as e:
        logHelper.getLogger().error(e)
        return 'Disconnected!'

def testDatabaseServer():
    '''
    判断是否连接上数据库服务器：
    :return: 'Connected!' or "Disconnected!"
    '''
    try:
        serverconfig = getDatabaseServerConfig()
        logHelper.getLogger().debug('connecting to the database server {0}:{1}'.format(serverconfig[0],serverconfig[3]))
        s = MySqlServer(host=serverconfig[0],port = 3306,user=serverconfig[2], pwd=serverconfig[3], db=serverconfig[4])
        return s.test()
    except Exception as e:
        logHelper.getLogger().error(e)
        return 'Disconnected!'

'''
    relationship：
    {
        following
        follower
    }
'''
'''
任务基本属性
taskType：
{
    Twitter.userInfo:人物信息，包括基本、动态、好友
        Twitter.userBaseinfo:仅人物基本信息
        Twitter.userTimeline: 仅人物动态信息
        Twitter.userFriends: 仅人物好友列表
        Twitter.userRelations:仅粉丝
}
'''
class TWTask():
    '''
    网络上传输的人员爬取任务对象
    通过RPC调用变成字典访问:item['fbid']
    '''
    def __init__(self,id,priority,fbid,tasktype,originalfbid,deep,name):
        self.id = id
        self.priority = priority
        self.fbid = fbid
        self.tasktype = tasktype
        self.originalfbid = originalfbid
        self.deep = deep
        self.name = name

    def __lt__(self, other):
        if self.priority < other.priority:
            return 1
        elif self.priority == other.priority:
            return 0
        else:
            return -1


if __name__ == '__main__':
    x = testDatabaseServer()
    print(x)
