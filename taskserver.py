# encoding=utf-8
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import socketserver,time,logging
from queue import PriorityQueue
from loghelper.loghelper import logHelper

import  common,twuserhelper
import threading

logName = time.strftime('%Y-%m-%d', time.localtime(time.time()))
myargs = {'fName': logName, 'fLevel': logging.DEBUG}
logger = logHelper.getLogger('serverlog', logging.INFO, **myargs)

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

mutex = threading.Lock()
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
class TaskServer:
    def __init__(self):
        self.userInfoQueue      = PriorityQueue()
        self.userBaseinfoQueue  = PriorityQueue()
        self.userTimelineQueue  = PriorityQueue()
        self.userFriendsQueue   = PriorityQueue()

        self.serverconfig = common.getDispatchServerConfig()
        self.__serverIP = self.serverconfig[0]
        self.__serverPort = int(self.serverconfig[1])
        self.__twuserhelper = twuserhelper.TWUserHelper()

    #####################################ExecQuery##################用户信息###################################################################
    def getATaskUser(self,taskType):
        '''
        根据任务类型，从人员任务列表中提取分配一个任务给爬虫
        :param taskType:任务类型
        :return:common.TWTaskUser，TWTaskUser.id=-1，表明没有任务
        '''
        mutex.acquire()
        try:
            # return common.TWTask(-1, 0, '919761698961', '0', '','3','name')
            if taskType == 'Twitter.userInfo':
                t,self.userInfoQueue = self._retrieveATaskuser(self.userInfoQueue,taskType)
                return t
            if taskType == 'Twitter.userBaseinfo':
                t,self.userBaseinfoQueue = self._retrieveATaskuser(self.userBaseinfoQueue,taskType)
                return t
            if taskType == 'Twitter.userTimeline':
                t, self.userTimelineQueue = self._retrieveATaskuser(self.userTimelineQueue, taskType)
                return t
            if taskType == 'Twitter.userFriends':
                t, self.userFriendsQueue = self._retrieveATaskuser(self.userFriendsQueue, taskType)
                return t

            return common.TWTask(-1, 0, 'noneid', '0', '0', '3','name')  # def __init__(self,id,priority,fbid,tasktype,originalfbid,deep,name):
        except Exception as exc:
            time.sleep(10)
            logger.error("exception: %s; when getATaskUser"%(exc))
            exit(1)
        finally:
            mutex.release()
    '''
    可变数据类型与不可变数据类型
            在python中哪些是可变数据类型，哪些是不可变数据类型。
            可变数据类型：列表list和字典dict；
            不可变数据类型：整型int、浮点型float、字符串型string和元组tuple。
            python中的不可变数据类型，不允许变量的值发生变化，如果改变了变量的值，相当于是新建了一个对象，
            而对于相同的值的对象，在内存中则只有一个对象，内部会有一个引用计数来记录有多少个变量引用这个对象；
            可变数据类型，允许变量的值发生变化，即如果对变量进行append、+=等这种操作后，只是改变了变量的值，而不会新建一个对象，
            变量引用的对象的地址也不会变化，不过对于相同的值的不同对象，在内存中则会存在不同的对象，即每个对象都有自己的地址，
            相当于内存中对于同值的对象保存了多份，这里不存在引用计数，是实实在在的对象。
    '''
    def _retrieveATaskuser(self,taskQueue,taskType):
        # import copy
        # taskQueue = copy.deepcopy(taskQueueS)
        # taskQueue = taskQueueS
        if taskQueue.empty():
            taskQueue = self.__twuserhelper.LoadTopNTask(10, taskType)
            print('reload {0} {1} task.'.format(taskQueue.qsize(), taskType))

        logger.info('{0} queue has left {1} tasks.'.format(taskType, taskQueue.qsize()))

        if not taskQueue.empty():
            task = taskQueue.get()[1]
            # XMLRPC传输的long必须改变成string
            task2 = common.TWTask(str(task.id), int(task.priority), str(task.fbid), task.tasktype, task.originalfbid,
                                  str(task.deep), task.name)

            logger.info(
                'dispatch TWTaskuser seed:taskid:{0}/priority:{1}/twid:{2}/name:{3}'.format(task.id, task.priority,
                                                                                            task.fbid, task.name))
            # set the running state to 1 running
            self.__twuserhelper.SetRuningState(task.id, 1)
            return task2,taskQueue
        else:
            return common.TWTask(-1, 0, 'noneid', '0', '0', '3','name'),taskQueue
            # def __init__(self,id,priority,fbid,tasktype,originalfbid,deep,name):


    def reportTWTaskUserComplete(self,taskid,runningState,completeDescription):
        '''
        报告完成情况
        :param completeDescription:
        :return:
        '''
        mutex.acquire()
        try:
            logger.info('{0},{1},{2}'.format(taskid,runningState,completeDescription))

            self.__twuserhelper.SetCompleteState(taskid,runningState,completeDescription)
            return 'OK'
        finally:
            mutex.release()

##########################################################################################################################
# Create server
#多线程实现
class RPCThreading(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
    pass

serverconfig = common.getDispatchServerConfig()  # 3
serverIP = serverconfig[0]
serverPort = int(serverconfig[1])

server = RPCThreading((serverIP,serverPort),requestHandler=RequestHandler)
# with RPCThreading(("localhost", 8089),requestHandler=RequestHandler) as server:
#Register my function
# server.register_function(getATask)

server.register_instance(TaskServer())

def test():
    return 'Connected!'
server.register_function(test)

# Register a function under a different name
def adder_function(x,y):
    return x + y
server.register_function(adder_function, 'add')

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'mul').
class MyFuncs:
    def mul(self, x, y):
        return x * y

#server.register_instance(MyFuncs())    #只能注册一个对象

print('listening on ip {0} / port {1}'.format(serverIP, serverPort))
logger.info('listening on ip {0} / port {1}'.format(serverIP, serverPort))

# Run the server's main loop
server.serve_forever()


