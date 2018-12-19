# TwitterCrawler
twitter crawler with a task dispatch server

mysql保存种子账号、任务调度
mongodb保存结果数据

调度器+爬虫，运行在linux操作系统

0)在mysql创建任务库：连接信息在config.json中

1）导入种子账号：importuserseed.py

2）生成任务：generateusertask.py

3)启动调度器：taskserver.py

4)启动爬虫：twuserspider.py

