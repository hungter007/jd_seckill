# -*- coding:utf-8 -*-
import time
import requests
import json

from datetime import datetime, timedelta
from jd_logger import logger


class Timer(object):
    def __init__(self, sleep_interval=0.5):
        # '2018-09-28 22:45:50.000'
        self.buy_time = self.get_today_buy_time()
        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)
        self.sleep_interval = sleep_interval

        self.diff_time = self.local_jd_time_diff()

    def jd_time(self):
        """
        从京东服务器获取时间毫秒
        :return:
        """
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)
        return int(js["serverTime"])

    def local_time(self):
        """
        获取本地毫秒时间
        :return:
        """
        return int(round(time.time() * 1000))

    def local_jd_time_diff(self):
        """
        计算本地与京东服务器时间差
        :return:
        """
        return self.local_time() - self.jd_time()

    def start(self):
        logger.info('正在等待到达设定时间:{}，检测本地时间与京东服务器时间误差为【{}】毫秒'.format(self.buy_time, self.diff_time))
        while True:
            # 本地时间减去与京东的时间差，能够将时间误差提升到0.1秒附近
            # 具体精度依赖获取京东服务器时间的网络时间损耗
            if self.local_time() - self.diff_time >= self.buy_time_ms:
                logger.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)
                
    @staticmethod
    def get_today_buy_time() -> datetime:
        """
        获取抢购开始时间
        :return:
        """
        buy_time_str = datetime.now().strftime("%Y-%m-%d") + " 09:59:59.500"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        if buy_time_str < now_str:
            buy_time_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") + " 09:59:59.500"
        buy_time = datetime.strptime(buy_time_str, "%Y-%m-%d %H:%M:%S.%f")
        return buy_time
