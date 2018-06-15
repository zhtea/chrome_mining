#coding=utf-8
"""
author:omzsl
"""
import time
import datetime 
from decimal import Decimal

#chrome timestamp to normal time
def date_from_chrome(chrome_timestamp):
    return datetime.datetime(1601,1,1) + datetime.timedelta(microseconds=int(chrome_timestamp))

#chrome timestamp diff
#input two time return duration in seconds
def chrome_time_diff(time1,time2=0):
    return str((time1 - time2)//60000000)