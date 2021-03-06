# __author__ = 'xjlin'
# -*- coding: utf-8 -*-
import os
import codecs
import csv
import time
import random 
import json

import requests
from selenium import webdriver

# from Function.crawler import Worker
from Subfunc.Crawler import USER_AGENTS
from Work.log import Logger
logger = Logger('Tmall', 'DEBUG')


class TmallWorker():
    def __init__(self):
        self.cookies = None
        self.proxies = None
        self.number = 0
        self.proxies_pool = []
        self.webdriver = webdriver.PhantomJS()

    def refresh(self):
        self.cookies = None
        self.proxies = None
        self.proxies_pool = []
        self.number = 0
        self.webdriver.delete_all_cookies()

    def __get_proxy(self):
        if len(self.proxies_pool) < 2:
            try:
                logger.debug("Asking for new proxy...")
                time.sleep(random.randint(1, 10))
                re = requests.get(
                    'http://http-webapi.zhimaruanjian.com/getip?num=10&type=2&pro=&city=0&yys=0&port=11&time=1&ts=1&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1')
                js = json.loads(re.content)
                self.proxies_pool.extend(js['data'])
            except Exception as e:
                logger.error('{}:{}'.format(e, re.content))
        self.proxies = self.proxies_pool[self.number]
        self.number = (self.number + 1) % 10
        logger.debug("Proxy switched to {}".format(self.proxies))
        url = 'http://{}:{}'.format(self.proxies['ip'], self.proxies['port'])
        proxies = {
            'http': url,
            'https': url
        }
        self.proxies = proxies
        # return {'http': 'http://36.56.47.249:8852', 'https': 'http://36.56.47.249:8852'}

    def __del_proxies(self):
        logger.debug('Deleting proxies {}'.format(self.proxies))
        try:
            self.proxies = None
        except Exception as e:
            logger.warning('delete failed. {}'.format(e))

    def __get_cookies(self):
        cookies = {}
        self.webdriver.delete_all_cookies()
        self.webdriver.get('https://login.tmall.com/')
        time.sleep(2)
        # logger.debug(browser.get_cookies())
        cookies[u'isg'] = self.webdriver.get_cookie('isg')['value']
        cookies[u'cna'] = u""
        logger.debug("Switch cookies to {}".format(cookies[u'isg']))
        self.cookies = cookies

    def __get_web(self, url):
        user_agent = random.choice(USER_AGENTS)
        headers = {
            'authority': 'list.tmall.com',
            'method': 'GET',
            'path': url,
            'scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'user-agent': user_agent,
        }
        time.sleep(0.5)
        self.__get_proxy()
        logger.debug('Trying open {} with UA:{} and proxy:{} and cookies:{}.'.format(url, headers['user-agent'], self.proxies, self.cookies))
        r = requests.get(url=url, headers=headers, proxies=self.proxies, cookies=self.cookies, timeout=(3.05, 27))
        # r = requests.get(url=url, proxies=self.proxies)
        # r = requests.get(url=url, cookies=self.cookies)
        # logger.debug('{}: {}'.format(r.status_code, r.content))
        return r

    def get_json(self, url):
        # request for the HTML
        if not self.cookies:
            self.__get_cookies()
        if not self.proxies:
            # self.__get_proxy()
            pass

        counter = 10
        while counter != 0:
            try:
                r = self.__get_web(url)
                if r.status_code == 200:
                    break
                else:
                    logger.warning(r.status_code)
                    raise requests.exceptions.ProxyError
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as e:
                logger.warning(e)
                counter -= 1
                # self.__get_proxy()

        if counter == 0:
            logger.error('{} {}'.format(url.encode('utf-8'), 'requests failed'))
            return
        else:
            logger.debug('Prase 1 passed.')

        flag = 10
        while flag != 0:
            try:
                logger.debug(r.content[:100])
                js = json.loads(r.content)
                logger.debug('Prase 2 passed.')
                return js
            except (ValueError, TypeError, requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as e:
                logger.warning(e)
                flag -= 1
                if flag >= 2:
                    # self.__get_proxy()
                    r = self.__get_web(url)
                elif flag == 1:
                    self.__get_cookies()
                    # self.__get_proxy()
                    r = self.__get_web(url)
                else:
                    break
        logger.error('{} {}'.format(url.encode('utf-8'), 'decode failed'))

tmall_handler = TmallWorker()


def get_item(json_data):
    js = json_data['item']
    data_list = []
    for i in js:
        item = {}
        try:
            item['goodsID'] = i['item_id']
        except KeyError:
            item['goodsID'] = None

        try:
            item['goodsName'] = i['title'].encode('utf8')
        except KeyError:
            item['goodsName'] = None

        try:
            item['shopID'] = i['shop_id'].encode('utf8')
        except KeyError:
            item['shopID'] = None

        try:
            item['shopName'] = i['shop_name'].encode('utf8')
        except KeyError:
            item['shopName'] = None

        try:
            item['sales'] = i['sold'].encode('utf8')
        except KeyError:
            item['sales'] = None

        try:
            item['price'] = i['price'].encode('utf8')
        except KeyError:
            item['price'] = None

        try:
            item['comments'] = i['comment_num'].encode('utf8')
        except KeyError:
            item['comments'] = None
        data_list.append(item)
    return data_list


def write_csv(data_list, page, category_name):
    PATH = os.path.join(os.getcwd())
    PRESENT_TIME = str(time.strftime('%H-%M-%S', time.localtime(time.time())))
    PRESENT_DAY = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
    if data_list is None:
        return None

    # check or create a daily dictionary
    try:
        file_dict = os.path.join(PATH, 'Data', 'TmallData', '{}{}'.format('TmallData_', PRESENT_DAY))
    except TypeError:
        file_dict = ''.join(['../TmallData_', PRESENT_DAY])
    try:
        os.makedirs(file_dict)
    except OSError, e:
        if e.errno != 17:
            raise e

    # create a file and its name for a certain page

    file_name = ''.join(
        [file_dict, '/', 'tmallPrice', '_', PRESENT_DAY, '_', PRESENT_TIME, '_', category_name,
         '_', str(page)])
    with codecs.open(file_name, 'wb') as f:
        fieldnames = ['goodsID', 'goodsName', 'shopName', 'shopID', 'sales', 'price',
                      'comments', ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            data = {key: value for key, value in data.items() if key in fieldnames}
            writer.writerow(data)

    # return indicator
    return


def parse(fake_url):
    try:
        logger.info(fake_url)
        url = fake_url.split('&*')[0]
        page = url.split('no=')[1]
        category_name = fake_url.split('*')[-1]
        json_data = tmall_handler.get_json(url)
        data_list = get_item(json_data)
        write_csv(data_list, page, category_name)
        return 0
    except Exception:
        logger.error(logger.traceback())
        return 1
    

crawler = {
    'TMALL': parse
}
