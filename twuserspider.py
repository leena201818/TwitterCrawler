# encoding=utf-8
import time
import xmlrpc.client
import logging

from loghelper.loghelper import logHelper
from twuserhelper import TWUserHelper

import socket

import common
import twusercrawler

#远程服务代理
serverconfig = common.getDispatchServerConfig()  # 3
serProxy = xmlrpc.client.ServerProxy('http://{0}:{1}'.format(serverconfig[0], serverconfig[1]))

def getTWUserTask(tasktype):
   return serProxy.getATaskUser(tasktype)
def reportTWTaskUserComplete(taskid,runningState,completeDescription):
   return serProxy.reportTWTaskUserComplete(taskid,runningState,completeDescription)


def main(spiderType):
    # spiderType = 'Twitter.userTimeline'

    twuserhelper = TWUserHelper()

    logName = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    myargs = {'fName': logName, 'fLevel': logging.DEBUG}
    logger = logHelper.getLogger('myLog', logging.INFO, **myargs)
    #
    logger.info("============================================================")

    hn = socket.gethostname()
    ip = socket.gethostbyname(hn)
    spidername = '[{}]/{}'.format(ip,hn)

    while True:
        try:
            if common.testDispatchServer() == 'Disconnected!':
                logHelper.getLogger().info('Dispatch server is disconnected!')
                time.sleep(5)
                continue
            logHelper.getLogger().info('Dispatch server is connected!')

            logHelper.getLogger().debug('connecting database server ...')
            if common.testDispatchServer() == 'Disconnected!':
                logHelper.getLogger().info('Database server is disconnected!,trying again later.')
                time.sleep(5)
                continue
            print('Database server is connected!')

            task = getTWUserTask(spiderType)

            taskid = task['id']
            if int(taskid) == -1:
                logHelper.getLogger().info('No task to do,sleep a while.')
                time.sleep(5)
                continue

            fbid = task['fbid']
            originalfbid = task['originalfbid']
            deep = int(task['deep'])
            name = task['name']
            priority = task['priority']

            # logHelper.getLogger().debug(task)
            logHelper.getLogger().info('Spider [{0}] have got a task:TASKID:{1}/TWID:{2}/PID:{3}. spider is working...'.format(spiderType,taskid,fbid,originalfbid))
            time.sleep(1)
            ######################################################################################################
            try:

                twuserhelper.UpdateTaskDispatch(int(taskid),spider = spidername[:50])

                # Do the job here.
                resCrawled = twusercrawler.dospider(task)

                if resCrawled == 1:

                    print('Spider have done the job,save the results,and reporting to dispatch server.')
                    k = reportTWTaskUserComplete(taskid, 2, 'completed normally.')
                    print('TASK id:{0},fbid:{1} has reported the job status.'.format(taskid,fbid))

                elif resCrawled == 0:
                    logHelper.getLogger().warning('network error or unknown error! wait and try...')
                    print('network error or unknown error! wait and try...')
                    k = reportTWTaskUserComplete(taskid, 3, 'completed abnormally.Reason:network error or unknown error!')
                    time.sleep(50)

            except Exception as e1:
                logHelper.getLogger().error('Scrawling error!',e1)
                reportTWTaskUserComplete(taskid, 3, 'completed abnormally.Error:{0}'.format(e1))
                raise  e1

            time.sleep(1)
        except Exception as e:
            logHelper.getLogger().error(e)
            logHelper.getLogger().error('the main loop error,restart it!')
            time.sleep(50)

if __name__ == '__main__':

    import os
    sel = input('What type of the spider?{1:userInfo; 2:userBaseinfo; 3:userTimeline; 4:userFriends}' + os.linesep)

    tasktype = 'Facebook.userInfo'
    if sel == '1':
        tasktype = 'Twitter.userInfo'
    elif sel == '2':
        tasktype = 'Twitter.userBaseinfo'
    elif sel == '3':
        tasktype = 'Twitter.userTimeline'
    elif sel == '4':
        tasktype = 'Twitter.userFriends'
    else:
        tasktype = 'Twitter.userInfo'

    main(tasktype)



