#!/usr/bin/env python
# coding: utf-8

import cv2
import os
import sys
import shutil

def new_dir(_new_dir):
    """
    新建一个存放图片的路径
    :param _new_dir: 新路径
    :return:
    """
    # 判断目录是否存在
    if os.path.exists(_new_dir):
        # 删除原有目录
        shutil.rmtree(_new_dir)
        # 创建一个新目录
        os.makedirs(_new_dir)
    else:
        # 创建一个新目录
        os.makedirs(_new_dir)
        print(_new_dir + ' has been created')


def print_video_info(vid_cap):
    print('Width of the frames in the video stream: ', vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH), ' pixel')
    print('Height of the frames in the video stream:', vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT), ' pixel')
    print('Frame rate:                              ', vid_cap.get(cv2.CAP_PROP_FPS), '/second')
    print('Total number of frames in the video file:', vid_cap.get(cv2.CAP_PROP_FRAME_COUNT), ' frames')


def video2pic(vid_cap, pic_path, video_name, offset_start=0.0, offset_end=0.0):
    print('offset时间为浮点数，单位s，例如offset_start= 3.5表示从3.5秒开始，offset_end=3.5表示距离原视频结束3.5秒停止截取')
    flag = True
    current_frame = 0

    # 判断视频打开是否有问题
    if vid_cap.isOpened() is not True:
        print("Error 01: Failed to open!")
        exit()
    else:
        print("Success to open the file/camera!")
        # 新建目录地址
        new_dir(os.path.join(pic_path, str(video_name)))
    # 获取视频的总帧数
    totalFrameNumber = vid_cap.get(cv2.CAP_PROP_FRAME_COUNT)
    # 获取视频的FPS
    rateFrameNumber = vid_cap.get(cv2.CAP_PROP_FPS)
    # 起始帧
    offset_start_frame = int(offset_start * rateFrameNumber)
    # 结束帧
    offset_end_frame = totalFrameNumber - int(offset_end * rateFrameNumber)
    print('Total frame number =  ' + str(totalFrameNumber))

    while (flag):
        # 读取每一帧
        success, image = vid_cap.read()  # c++里面是vidcap.read(image),image为临时变量，用于承载每帧的图像
        current_frame = current_frame + 1
        if current_frame >= offset_start_frame and current_frame <= offset_end_frame:
            print("Saving number " + str(current_frame) + "th frame...")
            cv2.imwrite(os.path.join(pic_path, str(video_name), 'img' + str(current_frame) + '.jpg'), image)
            if current_frame > totalFrameNumber:
                flag = False

if __name__ == '__main__':
    # 填写视频的路径
    video_format = '.mp4'
    video_name = 'iphone'
    video_path = '/Users/bughh/Desktop'
    path = os.path.join(video_path, video_name + video_format)
    print(path)
    vidcap = cv2.VideoCapture(path)
    # 打印视频文件信息
    # print_video_info(vidcap)
    # 判断是否需要截取部分视频
    # is_offset = input('Do you need to intercept video clips (y/n) ?')
    # print (is_offset)
    # if is_offset is 'y':
        # offset_time_start = input('截取帧起始时间（默认从0开始）：')
        # offset_time_end = input('截取帧结束时间（默认为视频结束）：')
        # video2pic(vidcap, float(offset_time_start), float(offset_time_end))
    # else:
    video2pic(vidcap, video_path, video_name)

