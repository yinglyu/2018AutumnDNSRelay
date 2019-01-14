# -*- coding: UTF-8 -*-
#record.py

#域名记录模块

#1.读取本地记录域名的文本文件并存储为程序的持久化文件
#2.将持久化文件转换为数据字典
#3.更新数据字典
#4.程序运行中通过线程IO更新持久化文件

#由于dnsrelay.txt windows格式的问题在读文件时通过 \r\m分割

import pickle
import os
import threading


d_web_ip = {}
d_ip_web = {}
update_dic = {}


def init_dic(args): #将初始化部分封装成init_dic 便于传参
    if args.detail == 4:
        print args.input_file
    data = open(args.input_file)  # 相当于一调用当前python 就自动读取原始dns的txt
    for each_line in data:

        try:
            (ip, sitecopy) = each_line.split(' ', 1)
            (site, nothing) = str(sitecopy).split('\r\n', 1)  # 相当于删掉每一行的换行符 原始为\n mac 用\r\n才能成功 windows 或许不同
            d_web_ip[site] = [ip, 1]  # 记录site的ip和频次
            d_ip_web[ip] = site  # 通过ip 找site
            if args.detail == 4:
                print "input_file line:"
                print each_line
                print "d_web_ip:"
                print site, d_web_ip[site]
                print "d_ip_web:"
                print ip,d_ip_web[ip]
        except:
            if args.detail == 4:
                print 'Input file finish.'

    data.close()

    try:
        with open('newdnsrelay.pickle', 'wb') as newdnsrelay_file:
            pickle.dump(d_web_ip, newdnsrelay_file)  # site 找ip的数组持久化
    except IOError as err:
        print 'File error:' + str(err)
    except pickle.PickleError as perr:
        print 'Pickling error:' + str(perr)


def get_web_ip():#从dnsrelay文件里面读取已经存在的记录
    with open('newdnsrelay.pickle', 'rb') as f:
        global update_dic
        update_dic = pickle.load(f)#pickle 数据字典持久化数据
        return update_dic.copy()
    return (None)


def update(web_site, args, add=None):#更新分为 已有记录 和 新记录
    global update_dic
    if (update_dic.get(web_site) != None):
        add_frequen = update_dic[web_site]
        add_frequen[1] = add_frequen[1] + 1
        if args.detail == 2:

            print web_site + ' frequence incrase 1,with ip ' + add_frequen[0]
        return add_frequen[1]
    else:
        update_dic[web_site] = [add, 1]
        if args.detail == 2:
            print 'record for a new site'
        return 1


def update_cache(args):#更新.pickle文件 调用my_thread函数
    global update_dic
    m = update_dic.copy()
    t = threading.Thread(target=my_thread, kwargs=m)
    if args.detail == 2:
        print 'ready to update local cache'
    t.start()
    t.join()


def my_thread(*argu, **arg):#按照frequence的排序更新存储 最终只增加非0.0.0.0的前30条记录 不够30条就有多少记多少
    frequence = []
    remain_dic = {}
    for each_key in arg:
        tmp = arg[each_key]
        if (tmp[1] not in frequence):
            frequence.append(tmp[1])
        if (tmp[0] == '0.0.0.0'):
            remain_dic[each_key] = '0.0.0.0'

    print 'various frequence:'
    for each in frequence:
        print 'have ' + str(each)
    for each_key in remain_dic:
        arg.pop(each_key)  # enimilate ban

    i = 0
    while (i < 30):
        max_frequence = max(frequence)
        for each_key in arg:
            tmp = arg[each_key]
            if (tmp[1] == max_frequence):
                remain_dic[each_key] = tmp[0]
                i = i + 1
            if (i == 30):
                break;
        frequence.remove(max_frequence)
        if (not frequence):  ###no more
            break;

    update_file(remain_dic)


def update_file(new_dic):#将.pickle文件提到dnsrelay.txt里面
    f = open('dnsrelaycopy.txt', 'w')
    for each_key in new_dic:
        word = str(new_dic[each_key]) + ' ' + str(each_key)
        f.write(word)
        f.write('\n')
        new_dic[each_key] = [new_dic[each_key], 0]

    try:
        with open('newdnsrelay.pickle', 'wb') as newdnsrelay_file:
            pickle.dump(new_dic, newdnsrelay_file)
    except IOError as err:
        print 'File error:' + str(err)
    except pickle.PickleError as perr:
        print 'Pickling error:' + str(perr)

