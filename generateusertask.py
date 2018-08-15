# encoding=utf-8

from twuserhelper import  TWUserHelper
from loghelper.loghelper import logHelper

'''
种子用户生成任务
>python generateusertask.py
'''


if __name__ == '__main__':


    import os
    fro = input('Where to generate the user task?:{1:Munual Seeds 2:Scrawed Friends}'+os.linesep)
    sel = input('Input TaskType:{1:userInfo; 2:userBaseinfo; 3:userTimeline; 4:userFriends}'+os.linesep)

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

    twhelper = TWUserHelper()
    # logHelper.getLogger().info(sel)
    # logHelper.getLogger().info(tasktype)
    c = 0
    if (fro == '2'):
        # whereclause = 'where hasTasked = 0 and id < 130'
        whereclause = 'where  priority > 0 and hasTasked = 0'
        wh = input('Input tb_user_friends(id,fbid,name,Homepage,priority,crawledTime,hasTasked,taskedTime,Description) where clause:'+os.linesep+'The default is "{0}"'.format(whereclause) + os.linesep)
        if(len(wh) != 0):
            whereclause = wh
        print('The select filter is:{0}"{1}"'.format(os.linesep, whereclause))
        de = input('Are you sure? Y:yes  N:no '+os.linesep)
        if(de.upper() == 'Y'):
            c = twhelper.GenerateUserTaskFromFriends(tasktype, whereclause)
        else:
            # logging.info("no tasks have generated!")
            print("no tasks have generated!")
            exit(0)
    else:
        c = twhelper.GenerateUserTask(tasktype)

    # logHelper.getLogger().info("tasks have generated!")
    if fro == '2':
        print("{0} User Tasks from Friends has been generated!".format(c))

    else:
        print("{0} User Tasks from munual seed has been generated!".format(c))



