import requests
from lxml.html import etree
from getFreeIPS.config import parserList
#用于检测编码格式
import chardet
import random
import os
# sqlchemy config

from getFreeIPS import config
from getFreeIPS.model import engine, session, IP

import gevent
from getFreeIPS.config import MAX_CHECK_CONCURRENT_PER_PROCESS, MINNUM, MAX_DOWNLOAD_CONCURRENT


#统计 ip 数目
global g_count
g_count = 0

#check the ip address is available or not

def check_ip(ip):
    returnValue = os.system('ping -c 1 %s' % ip)
    if returnValue:
        return False
    else:
        return True



def XpathPraser(response, parser):
    '''
    针对xpath方式进行解析
    :param response:
    :param parser:
    :return:
    '''
    # proxylist = []
    root = etree.HTML(response)
    proxys = root.xpath(parser['pattern'])

    spawns = []
    for proxy in proxys:
        try:
            ip = proxy.xpath(parser['position']['ip'])[0].text
            port = proxy.xpath(parser['position']['port'])[0].text
            type = 0
            protocol = 0

        except Exception as e:
            continue

        check_and_store_ValidIP(ip, port, type, protocol)




def check_and_store_ValidIP(ip,port,type,protocol):
    if check_ip(ip):
        print("ip: %s port: %s type: %d protocol: %d" % (ip, port, type, protocol))
        proxy = IP(id=session.query(IP).count() + 1, ip=ip, port=port, types=int(type), protocol=int(protocol))
        session.add(proxy)
        try:
            session.commit()
        except Exception:
            session.rollback()




def download(url):
    try:
        r = requests.get(url=url, headers=config.get_header(), timeout=config.TIMEOUT)
        r.encoding = chardet.detect(r.content)['encoding']
        if (not r.ok) or len(r.content) < 500:
            raise ConnectionError
        else:
            return r.text

    except Exception:
        count = 0  # 重试次数

        start = random.choice([num for num in range(1, 100)])
        allIPS = session.query(IP).count()
        start_index = start * allIPS / 100
        end_index = start_index + 30
        if end_index > allIPS:
            end_index = allIPS

        proxylist = session.query(IP).all()[start_index:end_index]

        if not proxylist:
            return None

        while count < config.RETRY_TIME:
            try:
                proxy = random.choice(proxylist)
                ip = proxy.ip
                port = proxy.port
                proxies = {"http": "http://%s:%s" % (ip, port), "https": "http://%s:%s" % (ip, port)}

                r = requests.get(url=url, headers=config.get_header(), timeout=config.TIMEOUT, proxies=proxies)
                r.encoding = chardet.detect(r.content)['encoding']
                if (not r.ok) or len(r.content) < 500:
                    raise ConnectionError
                else:
                    return r.text
            except Exception:
                g_count += 1

import threading as td

def threadTask(parser, url):
    html_text = download(url=url)
    XpathPraser(html_text, parser)

def crawl(parser):
    if parser['type'] == 'xpath':
        for url in parser['urls']:
            t = td.Thread(target=threadTask, args=(parser, url))
            t.setDaemon(True)
            t.start()
            t.join()


from multiprocessing import Process

def startCrawl():
    for p in parserList:
        process = Process(target=crawl, args=(p,))
        process.start()
        process.join()



if __name__ == "__main__":
    import time
    start_time = time.time()
    startCrawl()
    end_time = time.time()
    print("all complete! spend %d seconds" % (end_time - start_time))

