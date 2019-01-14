# -*- coding: UTF-8 -*-
#pack.py
#将本地域名记录封装成DNS响应报文
# tmp_list[2] = '\x81' 设置QR = 1
#对屏蔽的网站分类讨论，改变了#RCODE = 3
import socket

def make(re_ip,msg,args):


    tmp_list = []

    for ch in msg:#收到 client 的请求中 头部QDCOUNT=1,ANCOUNT=0,NSCOUNT=0,ARCOUNT=0
        tmp_list.append(ch) #响应包的question部分不变
    tmp_list[2] = '\x81'
    # QR = 1
    if re_ip != "0.0.0.0":
        if args == 2:
            print "safe website"

        tmp_list[4:12] = ['\x00', '\x01', '\x00', '\x01', '\x00', '\x00', '\x00', '\x00']

        tmp_list = tmp_list + ['\xc0', '\x0c', '\x00', '\x01', '\x00',
                               '\x01', '\x00', '\x00', '\x02', '\x58', '\x00', '\x04']

        dive_ip = socket.inet_aton(re_ip)
        ch_ip = []
        for each_ch in dive_ip:
            ch_ip.append(each_ch)
        tmp_list = tmp_list + ch_ip

    else:
        if args == 2:
            print "dangerous website"

        #QR = 1
        tmp_list[3:12] = ['\x03','\x00', '\x01', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00']
        #RCODE = 3
    if args == 3:
        print tmp_list

    re_msg = ''.join(tmp_list)
    return re_msg
