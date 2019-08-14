#!/usr/bin/env bash

python3 retrain.py \
    --image_dir ../training/zhihu/iOS_1-50 \
    --output_graph ../training/zhihu/model/ios_zhihu_output_graph.pb \
    --output_labels ../training/zhihu/labels/ios_zhihu_output_labels.txt

#2to3 label_image.py -n -w -o python3_7
#2to3 retrain.py -n -w -o python3_7
#pip3 install --ignore-installed --upgrade /Users/bughh/Downloads/tensorflow-1.13.1-cp37-cp37m-macosx_10_9_x86_64.whl

