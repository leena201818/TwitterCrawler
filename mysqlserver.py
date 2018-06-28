# encoding=utf-8
import pymysql

class MySqlServer:
    def __init__(self,host,port,user,pwd,db):
        self.host = host    #主机名
        self.port = port
        self.user = user    #用户名
        self.pwd = pwd      #密码
        self.db = db        #数据库名

    def __GetConnect(self):
        if not self.db:
            raise(NameError,"No database information is set")
        #连接数据库
        self.conn = pymysql.connect(host=self.host,port = int(self.port),user=self.user,password=self.pwd,database=self.db,charset="utf8")
        cur = self.conn.cursor()
        if not cur:
            raise(NameError,"Unable to connect to the database")
        else:
            return cur

    def ExecQuery(self,sql):    #执行查询语句
        cur = self.__GetConnect()
        cur.execute(sql)
        data = cur.fetchall()    #一次获取全部数据
        # row=cur.fetchone()    #一次获取一行数据
        # rows = cur.fetchmany(10)    #获取10行数据

        #查询完毕后必须关闭连接
        self.conn.close()
        return data,cur.rowcount

    # def ExecNonQuery(self,sql): #执行非查询语句
    #     cur = self.__GetConnect()
    #     cur.execute(sql)
    #     self.conn.commit()
    #     self.conn.close()

    def ExecNonQuery(self,sql,params): #执行非查询语句
        cur = self.__GetConnect()
        c = cur.execute(sql,params)
        self.conn.commit()
        self.conn.close()
        return cur.rowcount

    def ExecNonQueryBatch2(self,lstsql,lstparams): #执行非查询语句
        cur = self.__GetConnect()
        ln = len(lstsql)
        for i in range(ln):
            sql = lstsql[i]
            params = lstparams[i]
            c = cur.execute(sql,params)

        self.conn.commit()
        self.conn.close()
        return cur.rowcount

    def ExecNonQueryBatch(self,sql,lstParam): #执行非查询语句
        cur = self.__GetConnect()
        for params in lstParam:
            cur.execute(sql,params)
            # print(params)
        self.conn.commit()
        self.conn.close()
        return cur.rowcount


    def test(self): #测试连接
        try:
            cur = self.__GetConnect()
            return 'Connected!'
        except  Exception as e:
            return 'Disconnected!'

if __name__ == '__main__':
    pass