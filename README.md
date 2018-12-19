# TwitterCrawler
【简介】

twitter crawler with a task dispatch server

mysql保存种子账号、任务调度

mongodb保存结果数据

调度器+爬虫1：N模式，运行在linux操作系统，可部署在docker容器运行。

1、调取器负责读取任务表中的任务，接受爬虫请求返回任务，记录任务执行状态信息。

2、爬虫从调取器请求任务，执行信息爬取，上报采集状态，直接向mongodb保存结果信息

【基本配置】

调度器、mysql任务数据库、mongodb结果数据库可以分别部署在不同的服务器上，采用config.json文件进行配置

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

1）导入种子账号：importuserseed.py，种子文件seedfile.txt中第一列是必填项，采用screemname或twitterid均可

2）生成任务：generateusertask.py，可以从手动种子生成任务，也可以从采集出来的friends关联账号生成，一般选择userInfo任务类型表示全采集

3)启动调度器：taskserver.py，仅仅启动一个即可，当然可以通过配置启动多个调度器

4)启动爬虫：twuserspider.py，爬虫部署在不同的docker，配置信息需要和所要链接的调度器相对应

【代理设置】

基本思路：采用shadowsocks + provxy代理方式访问外网，建议在宿主机运行ss+provxy，在docker容器内设置使用宿主机的provxy，实现docker容器内访问外网

docker运行爬虫

启动docker容器，容器内安装python3.6,以及requirements.txt模块即可，假设生成的image为“python:vim”

方式1：目录映射，不需要拷贝程序文件到容器内，采用目录映射方式（run in docker container,set the work directory）

sudo docker run -it -w /root/TwitterCrawler/ python:vim python /root/TwitterCrawler/twuserspider.py

方式2：预先将程序文件制作到image,在容器内修改配置，此处的docker image为python:tw3

===1、启动容器

        sudo docker run -it python:tw3 /bin/bash

===2、在容器内设置外网访问代理，宿主机配置ss的方法详细看config文件夹内容

        export http_proxy=http://宿主机ip:8118

        export https_proxy=http://宿主机ip:8118

或者直接在terminal中运行以上两行，或者写入/etc/profile中source使之生效
       
===3、若容器内事先没有程序文件，也可以启动容器后，从宿主机拷贝，比如：
     
        sudo docker cp ~/TwitterCrawler 7345dbdcc02a:/root
        
===4、在容器内修改 TwitterCrawler/config.json，配置mysql、mongodb、调度器ip信息，以及twitter api key信息

也可以在宿主机上配置好config.json后，拷贝到docker中，具体操作如下

        在宿主机上打开一个shell

        sudo docker cp path_to_new_account.config.json 容器ID:/root/TwitterCrawler/

===5、在容器内运行爬虫

        python twuserspider.py
