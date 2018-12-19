# TwitterCrawler
【简介】
twitter crawler with a task dispatch server

mysql保存种子账号、任务调度

mongodb保存结果数据

调度器+爬虫，运行在linux操作系统

1、调取器负责读取任务表中的任务，接受爬虫请求返回任务，记录任务执行状态信息。

2、爬虫从调取器请求任务，执行信息爬取，上报采集状态，直接向mongodb保存结果信息

【配置】

调取器、mysql任务数据库、mongodb结果数据库可以分别部署在不同的服务器上

config.json
{
        "apikeys": {          
                "i0mf0rmer034": {
                        "app_key": "pgpat",
                        "app_secret": "9dzDza1olxdkMu",
                        "oauth_token": "984036Fzl",
                        "oauth_token_secret": "vxNnvyY33AL4E"
                }
        },                                                      #twitter开发者账号的key

        "serverinfo":{
                "dbIP": "192.168.8.191",                        #mysql任务数据库服务器地址
                "dbPort": "3306",                               #mysql任务数据库服务端口
                "dbUser": "test",                               #mysql任务数据库用户
                "dbPwd": "test",                                #mysql任务数据库密码 
                "dbName":"twitterdb",                           #mysql任务数据库实例名
                "serverIP": "192.168.8.191",                    #调度服务器地址
                "serverPort": "8099"},                          #调度服务器服务端口
        "mongoinfo":{                                           #结果库mogodb的配置信息
                "dbIP": "192.168.8.100",
                "dbPort": "27017",
                "dbUser": "twitter",
                "dbPwd": "twitter",
                "dbName":"twitter"
        }
}


【基本流程】

0)在mysql创建任务库：在mysql中运行create_twitterdb.sql

1）导入种子账号：importuserseed.py

2）生成任务：generateusertask.py

3)启动调度器：taskserver.py

4)启动爬虫：twuserspider.py

【代理设置】
