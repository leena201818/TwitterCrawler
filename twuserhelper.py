# encoding=utf-8
from datetime import datetime
import common
from mysqlserver import MySqlServer

from queue import PriorityQueue
from loghelper.loghelper import logHelper


class TWUserHelper:
    def __init__(self):
        serverconfig = common.getDatabaseServerConfig()
        self.dbinstance = MySqlServer(serverconfig[0],serverconfig[1],serverconfig[2],serverconfig[3],serverconfig[4])

    def ImportTWUserSeed(self, seedtxtfile, origin):
        with open(seedtxtfile, 'r',encoding='UTF-8') as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                if line.startswith('#'):
                    continue
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                acount = line.split(',')

                fbid = acount[0].strip('\ufeff')
                name = ''
                if len(acount) > 1:
                    name = acount[1].strip()
                else:
                    name = fbid
                mail = ''
                if len(acount) > 2:
                    mail = acount[2].strip()

                sql = "insert into tb_seed_user(fbid,name,mobileoremail,origin,publishedtime,hasTasked) values(%s,%s,%s,%s,%s,0);"
                param = (fbid, name, mail,origin, now)
                self.dbinstance.ExecNonQuery(sql, param)
                logHelper.getLogger().info("insert {0}".format(line))


    def GenerateUserTask(self,tasktype):
        '''
        从种子生成任务，按照任务类型，将所有未运行种子都导入
        :param tasktype:
        :return:
        '''
        lstsql=[]
        lstparam=[]
        # sql = "insert into tb_task_user(fbid,tasktype,priority,runningstate,deep,name) select fbid,%s,100,0,0,name from tb_seed_user where hastasked = 0;update tb_seed_user set hasTasked = 1,taskedTime=sysdate() where hastasked = 0"
        sql = "insert into tb_task_user(fbid,tasktype,priority,runningstate,deep,name) select fbid,%s,100,0,0,name from tb_seed_user where hastasked = 0;"
        param = [tasktype]
        lstsql.append(sql)
        lstparam.append(param)

        sql = "update tb_seed_user set hasTasked = 1,taskedTime=sysdate() where hastasked = %s"
        param = [0]
        lstsql.append(sql)
        lstparam.append(param)

        logHelper.getLogger().debug(sql)

        print(lstsql)
        print(lstparam)
        c = self.dbinstance.ExecNonQueryBatch2(lstsql,lstparam)
        logHelper.getLogger().debug('Generate User Task From Seed is OK!')
        return c

    def LoadTopNTask(self,n,tasktype):
        que = PriorityQueue()
        query = "SELECT id,priority,fbid,originalfbid,deep,name  FROM tb_task_user  WHERE runningState=0 and Tasktype = '{0}' order by deep,priority DESC LIMIT 0,{1}".format(tasktype,n)
        rows,c = self.dbinstance.ExecQuery(query)

        for row in rows:
            originfbid = row[3]
            deep = row[4]
            name = row[5]
            if row[3] is None:
                originfbid = ''
            if row[4] is None:
                deep = '3'
            if row[5] is None:
                name = ''

            r = common.TWTask(row[0],row[1],row[2],tasktype,originfbid,int(deep),name) #def __init__(self,id,priority,fbid,tasktype,originalfbid,deep,name):
            # for i in range(5):
            #     logHelper.getLogger().debug(row[i])
            tup = (row[1],r)   #priority作为优先级
            que.put(tup)

        return que

    def SetRuningState(self,id,state):
        sql = 'UPDATE tb_task_user SET runningState = %s WHERE id=%s'
        param = (state,id)
        self.dbinstance.ExecNonQuery(sql,param)

    def SetCompleteState(self,id,runningState,desc):
        sql = "UPDATE tb_task_user SET runningState = %s,completedTime = sysdate(),Description = %s WHERE id=%s"
        param = (runningState,desc,id)
        # logHelper.getLogger().debug(sql)
        self.dbinstance.ExecNonQuery(sql,param)

    #保存朋友信息，传入一个字典
    def Save_tb_user_friends_batch(self,lstDicResult):
        # dicResult={'fbid':'111','name':'na','homepage':'','priority':'1','Description':'ddd'}
        sql = "insert ignore into tb_user_friends(Fbid,Name,Homepage,priority,crawledTime,hasTasked,deep,Description,originalfbid) VALUES\
                	    (%s,%s,%s,%s,sysdate(),0,%s,%s,%s);"
        lstParam = []
        for dicResult in lstDicResult:
            dicResult['name'] = dicResult['name'][:120]
            param = (dicResult['fbid'],dicResult['name'],dicResult['homepage'],dicResult['priority'],dicResult['deep'],dicResult['Description'],dicResult['originalfbid'])
            lstParam.append(param)
        # logHelper.getLogger().debug('lstParam count is {0}'.format(len(lstParam)))
        self.dbinstance.ExecNonQueryBatch(sql,lstParam)
        logHelper.getLogger().info("Save_tb_user_friends_batch ok.")



    def GenerateUserTaskFromFriends(self,tasktype,whereclause):
        '''
        从朋友生成任务，按照任务类型
        :param tasktype:
        :return:
        '''
        lstsql = []
        lstparam = []

        sql = "insert into tb_task_user(fbid,tasktype,priority,runningstate,deep,name,originalfbid) \
                select fbid,%s,priority,0,deep,name,originalfbid from tb_user_friends {0};".format(whereclause)
        param = [tasktype]
        lstsql.append(sql)
        lstparam.append(param)

        sql = "update tb_user_friends set hasTasked = %s,taskedTime=sysdate() {0}".format(whereclause)
        param = [1]
        lstsql.append(sql)
        lstparam.append(param)

        c = self.dbinstance.ExecNonQueryBatch2(lstsql, lstparam)
        logHelper.getLogger().debug('Generate {0} {1} Task from Friends is OK!'.format(c,tasktype))
        return c

    def DumpTaskUser(self):
        '''
        讲完成任务转出去备份保存
        '''
        sql = 'insert into tb_task_user_log select * from tb_task_user where runningstate = 2;\
              delete from tb_task_user where runningstate = %d;'
        param = (2)
        c = self.dbinstance.ExecNonQuery(sql, param)
        logHelper.getLogger().debug('Dump {0} User Task to tb_task_user_log!'.format(c))
        return c

    def UpdateTaskDispatch(self,taskid,spider = ''):
        '''
        分配任务后，填写分配时间
        :param taskid:
        :return:
        '''
        sql = "update tb_task_user set dispatchTime = sysdate(),Spider = %s where id = %s"
        # logHelper.getLogger().debug(sql)
        param = (spider,taskid)
        c = self.dbinstance.ExecNonQuery(sql,param)
        logHelper.getLogger().debug('Update User Task DispatchTime is OK!')
        return c

