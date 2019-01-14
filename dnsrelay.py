# -*- coding: UTF-8 -*-
#dnsrelay.py
#主模块

#1.分析参数
#2.定义全局变量，进行初始化
#3.socket绑定端口
#4.循环监听端口
#5.通过发射多个线程处理消息

#输出时间信息
#将运行代码部分分装成run_DNSrelay函数 便于传参
#参数：1 -d 输出信息详细程度 2 -i 输入文档选择 3 -a 权威DNS选择
#增加KeyboardInterrupt 使得程序在ctrl+C 后能停下来

import time
import socket
import record
import unpack
import pack
import argparse
import threading

def run_DNSrelay(s,args,msg,client,port):


    global the_dic
    if args.detail == 4:
        print "web_ip detail:"
        print the_dic
    global client_request# 消息序列号+IP 对应序列号
    global client_request_index  # 序列号对应IP和port
    global key_record
    global client_wait # 记录等待的客户
    global time_rest


    if args.detail > 0:
        print 'running'
    if True:

        request = list(msg)  # 将元组变为列表
        requre_web, q_type_str = unpack.get_request(request[12:], args)
        website = ''.join(requre_web)
        if args.detail == 3:
            print "Message detail:"
            print request  # 查看消息具体内容
            print "Q_type:", q_type_str
        Q_type = 0
        if (q_type_str == ['\x00', '\x1c']):  # Q Type 为 28 时，DNS消息是ipv6 地址
            Q_type = 28
        if (client == args.authority_DNS and port == 53):#

            if (Q_type != 28): # ipv4 响应
                response_ip = msg[-4] + msg[-3] + msg[-2] + msg[-1] # 记录ip地址
                char_ip = socket.inet_ntoa(response_ip) #ip转为字符串格式

                fre = record.update(website, args, char_ip)#更新网站记录

                if args.detail > 0:
                    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    print "Authority > Relay   Client:"
                    print website + ' : ' + char_ip
                if args.detail == 2:
                    print 'with the frequence of ' + str(fre)
            else:
                if args.detail > 0:
                    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    print "Authority > Relay   Client: IPv6 Response"

            for each_client in client_wait: # 对于每一个用户
                if request[0] + request[1] + str(each_client) in client_request:# 查找其是否有当前序号的请求
                    my_key, birth = client_request[request[0] + request[1] + str(each_client)] # 得到请求记录 在 client_request_index中的key
                    client_request.pop(request[0] + request[1] + str(each_client)) #删除请求

                    if my_key in client_request_index:
                        s.sendto(msg, client_request_index[my_key]) #转发 answer
                        client_wait[each_client] = client_wait[each_client] - 1  # client's record count decrease
                        if args.detail == 6:
                            print each_client + " has " + str(client_wait[each_client]) + " request to be answered."
                        if client_wait[each_client] < 1:  # dielete client without request
                            client_wait.pop(each_client)
                            if args.detail == 6:
                                print "delete client:" + each_client


                    if args.detail > 0:
                        if args.detail == 2:
                            print "Response to ip and Client port"
                        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        if my_key in client_request_index:
                            print "Authority   Relay > Client",client_request_index[my_key],":"
                            client_request_index.pop(my_key) #删除 client_request_index中 my_key 对应的记录
                        else :
                            print "Authority   Relay > Client:"

                        if (Q_type != 28):
                            print website + ' : ' + char_ip
                            if args.detail == 2:
                                print 'with the frequence of ' + str(fre)
                        else:
                            print "IPv6 Response"

                    break


        else: # 收到客户请求
            if args.detail > 0:
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                print "Authority   Relay < Client",(client, port),":"
                print "Request website:" + website

            if (Q_type != 28 and the_dic.get(website) != None): # 查到了ip
                re_ip = the_dic.get(website)#site 通过找ip
                fre = record.update(website,args)


                c_frame = pack.make(re_ip[0], msg,args)
                s.sendto(c_frame, (client, port))
                if args.detail > 0:
                    if args.detail == 2:
                        print "Found in local cache."
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    print "Authority   Relay > Client", (client, port) , ":"
                    print website + " : " + re_ip[0]
                    if args.detail == 2:
                        print ' with frequence ' + str(fre)



            else:

                if args.detail > 0:
                    if args.detail == 2:
                        print "Ask authority server."
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    print "Authority < Relay   Client:"
                    print "Request website:" + website


                if args.detail == 6: # 尝试从client_request的key 值中获取 client 的 ip，成功后可以在记录删除时，对等待用户记录client_wait{}进行记录数减少和删除
                    test_key = request[0] + request[1] + str(client)
                    print test_key[2:]
                    if test_key[2:] == client:
                        print "get right client type"
                    else:
                        print "get wrong client type"
                if request[0] + request[1] + str(client) not in client_request:
                    key_record = key_record + 1
                    request_general = key_record
                    client_request[request[0] + request[1] + str(client)] = request_general, time.time()
                    client_request_index[request_general] = (client, port)

                    if client not in client_wait:
                        client_wait[client] = 1 # client has one request
                        if args.detail == 6:
                            print "record new client:" + client
                    else:
                        client_wait[client] = client_wait[client] + 1
                        if args.detail == 6:
                            print client + " has " + str(client_wait[client]) + " request to be answered."

                else:
                    request_general, birth = client_request[request[0] + request[1] + str(client)]
                    client_request[request[0] + request[1] + str(client)] = request_general, time.time()

                s.sendto(msg, (args.authority_DNS, 53))

        time_rest = time_rest + 1

        try:
            if args.detail == 3:
                print "expire check:1234567890"
            for client_request_record in client_request: # check delete old client_request
                request_general, start = client_request[client_request_record]
                age = time.time() - start
                if (args.detail == 6):
                    print str(client_request_record[2:]) +  "'s age = "+ str(age)
                    if client_request_record[2:] in client_wait:
                        print "fine"
                if (age > 3):
                    if (args.detail == 6):
                        print "Client record expire."
                    client_request_index.pop(request_general)
                    client_request.pop(client_request_record)
                    if client_request_record[2:] in client_wait:
                        client_wait[client_request_record[2:]] = client_wait[client_request_record[2:]] - 1 # client's record count decrease
                        if args.detail == 6:
                            print client_request_record[2:] + " has " + str(client_wait[client_request_record[2:]]) + " request to be answered."
                        if client_wait[client_request_record[2:]] < 1:  # delete client without request
                            client_wait.pop(client_request_record[2:])
                            if args.detail == 6:
                                print "delete client:" + client_request_record[2:]



            if (time_rest == 50):
                print 'pay attention'
                print '######################'
                record.update_cache(args)
                print '######################'
                the_dic = record.get_web_ip()
                time_rest = 0
        except:
            print ""

        if args.detail > 0:
            print '-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-'


def parse_arguments(parser):
    parser.add_argument('-d', '--detail', action="count", help="Increase output detail.")#-ddd print msg_content -dddd print dic_info -ddddd print other_test
    parser.add_argument('-i', '--input_file', type=str, default="dnsrelay.txt",
                        help="The input file used to store the record.")
    parser.add_argument('-a', '--authority_DNS', type=str, default='10.3.9.4',
                        help="The authority DNS server as you wish.")

    args = parser.parse_args()
    return args

def recv(s,args):
    seq = -1

    while True:
        try:
            msg, (client, port) = s.recvfrom(1024)  # 收到请求
            seq = seq + 1
            relay_thread = threading.Thread(target=run_DNSrelay, args=(s, args, msg, client, port,))
            relay_thread.start()
            if args.detail == 2:
                print 'thread' + str(seq)

        except KeyboardInterrupt:  # ctrl+C 结束程序
            print 'recv interruption'
            quit()
        except:
            print 'Time out! '


    s.close()

if __name__ == "__main__":

    #run_DNSrelay(args)
    #创建一个公用的socket
    parser = argparse.ArgumentParser()
    args = parse_arguments(parser)

    record.init_dic(args)

    the_dic = record.get_web_ip()
    if args.detail == 4:
        print "web_ip detail:"
        print the_dic
    client_request = {}  # 消息序列号+IP 对应序列号
    client_request_index = {}  # 序列号对应IP和port
    key_record = 0
    client_wait = {}  # 记录等待的客户
    time_rest = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 53
    s.bind(('', port))

    recv(s, args)

