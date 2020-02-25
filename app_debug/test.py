#!/usr/bin/env python
# coding:utf-8
import json
import os
import requests
from optparse import OptionParser
import socket


def query_service(port):
    fobj = os.popen("lsof -i tcp:%d" % port)
    state = fobj.read().strip()
    if len(state) == 0:
        return False, -1
    ls = state.split("\n")

    status_list = ls[-1].split()
    status = status_list[-1]
    pid = status_list[1]
    return status == "(LISTEN)", pid

def test_socket():
    minicap_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = "127.0.0.1"
    port = 1313
    code = minicap_socket.connect_ex((ip, port))
    if code != 0:
        print("连接 minicap 套接字失败")
    else:
        print(code)

if __name__ == '__main__':
    # parser = OptionParser()
    # parser.add_option("-d", "--device_id", dest="device_id", default="7b0f49f4", help="lock device id")
    # parser.add_option("-p", "--port", dest="port", default="12345", help="port for ios-minicap")
    # parser.add_option("-r", "--resolution", dest="resolution", default="400x600")
    # (options, args) = parser.parse_args()
    #
    # if options.device_id:
    #     device_id = options.device_id
    # if options.port:
    #     port = options.port
    # if options.resolution:
    #     resolution = options.resolution
    #
    # # time.sleep(8)
    # main("ios")
    test_socket()
