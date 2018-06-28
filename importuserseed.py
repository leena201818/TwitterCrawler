# encoding=utf-8
import logging,sys
from twuserhelper import  TWUserHelper
from loghelper.loghelper import logHelper

if __name__ == '__main__':
    if sys.argv.__len__() != 3:
        print('usage:python importUserSeed.py filepath origin')
        exit(1)
    logHelper.getLogger().info(sys.argv[1])
    logHelper.getLogger().info(sys.argv[2])



    seedfile = sys.argv[1]
    origin = sys.argv[2]


    twhelper = TWUserHelper()
    twhelper.ImportTWUserSeed(seedfile,origin)
    logHelper.getLogger().info("seed import completed!")


