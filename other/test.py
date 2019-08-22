#!/usr/bin/env python
# coding:utf-8
import json
import os
import requests
from optparse import OptionParser
from app_config.config import APK_PATH
from other.ios_tester import IOSTester


def _send_report(post_data, apk_info):
    # 获取 app 大小
    fsize = os.path.getsize(APK_PATH)
    apk_size = round(fsize / float(1024 * 1024), 2)

    othor_data = {
        'device': os.environ['DEVICE'],
        'platform': 'Android',
        'size': apk_size,
        'version_name': apk_info['versionName'],
        'version_code': apk_info['versionCode'],
        'mr_id': os.environ['MR_ID'],
        'commit': os.environ['COMMIT'],
        'target_branch': os.environ['TARGET_BRANCH'],
        'mr_title': os.environ['MR_TITLE'],
    }
    post_data.update(othor_data)
    print('上传数据:\n%s' % json.dumps(post_data, indent=4))

    # 上报后端
    response = requests.post('http://ci-warehouse.dev.zhihu.com/api/auto_test/report', json=post_data)
    print('传后台数据返回状态码为：' + str(response.status_code))


def main(platform):
    # 开始录屏和启动 app
    fobj = os.popen("idevice_id -l")
    device_id = fobj.read().strip()
    port = 12345
    resolution = "375x600"
    # os.system("pkill ios_minicap")
    # cmd = "./ios-minicap/build/ios_minicap -u %s -p %d -r %s &" % (device_id, port, resolution)
    # print (cmd)
    # os.system(cmd)
    test_count = 8
    tester = IOSTester(test_count, platform, device_id, port ,resolution)
    launch, page_loading = tester.test()
    print ("APP 启动时长 %f" % launch)
    print ("APP 首页加载时长 %f" % page_loading)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--device_id", dest="device_id", default="7b0f49f4", help="lock device id")
    parser.add_option("-p", "--port", dest="port", default="12345", help="port for ios-minicap")
    parser.add_option("-r", "--resolution", dest="resolution", default="400x600")
    (options, args) = parser.parse_args()

    if options.device_id:
        device_id = options.device_id
    if options.port:
        port = options.port
    if options.resolution:
        resolution = options.resolution

    # time.sleep(8)
    main("ios")
