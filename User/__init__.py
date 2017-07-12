# -*- coding: utf-8 -*-
# @Time  : 2017/3/26 10:29
# @Author: FSOL
# @File  : __init__.py.py

"""
__init__.py
==========================
Will count all user and write it into globalvar.user_list.
"""
import Work.globalvar as gv
import Function
from Work.log import Logger
import os
import sys
import importlib
logger = Logger('User', 'DEBUG')


def default_entry(self):
    pass


def default_receive(self, message):
    order = gv.order_handler(message)
    try:
        response = Function.function_act(order)
    except Exception as e:
        logger.error(logger.traceback())
        response = ''
    finally:
        return response


def default_leave(self):
    pass

user_list = {}

if __name__ == '__main__':
    pass
else:
    temp_list = os.listdir(os.path.join(os.getcwd(), 'User'))
    file_list = []
    for m_file in temp_list:
        x = m_file.rfind('.')
        if x != -1 and m_file[x:] == '.py':
            file_list.append(m_file[:-3])
    file_list.remove('__init__')
    file_list = map(lambda x: 'User.{}'.format(x), file_list)

    for m_file in file_list:
        try:
            if m_file in sys.modules:
                cwm = reload(sys.modules[m_file])
            else:
                cwm = importlib.import_module(m_file)
            for (name, way) in cwm.Users.items():
                if name not in user_list:
                    user_list[name] = {}
                if 'entry' in way:
                    user_list[name]['entry'] = way['entry']
                else:
                    user_list[name]['entry'] = default_entry
                if 'receive' in way:
                    user_list[name]['receive'] = way['receive']
                else:
                    user_list[name]['receive'] = default_receive
                if 'leave' in way:
                    user_list[name]['leave'] = way['leave']
                else:
                    user_list[name]['leave'] = default_leave
        except Exception:
            logger.error("Failed to load user.{}:".format(m_file))
            logger.error(logger.traceback())