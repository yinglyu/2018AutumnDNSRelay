# -*- coding: UTF-8 -*-
#unpack.py
#解包模块
#从收到的报文中提取网址和QTYPE信息

#提取出报文中的url
#读取网页格式的操作最后通过pop删除一个.会出现程序终止
#可能是收到错误格式报文的缘故
#增加了判断len(new_list)，程序不会终止

def get_request(your_list,args):#list 是一个字符串数组
    my_list = []
    new_list = []
    my_list.extend(your_list)


    thelen = ord(my_list[0])#格式：第一个字符存第一段字符串长度
    if args.detail == 5:
        print "my_list:"
        print my_list
        print "the len:"
        print thelen
    try:
        while thelen != 0: #ying读到最后一个字符串
            new_list = new_list + my_list[1:thelen+1]
            my_list[0:thelen+1] = [] #删除第一段字符串
            thelen = ord(my_list[0]) #读下一段字符串长度
            new_list.append('.') #用.连接
    except IndexError:
        print "bao wen ge shi bu dui"


    if len(new_list) > 0:
        list_pop =  new_list.pop()
    else:
        if args.detail == 2:
            print "empty request."

    return new_list, my_list[1:3]

