#!/usr/bin/env bash

python3 label_image.py \
    --graph=../training/zhihu/model/ios_zhihu_output_graph.pb \
    --labels=../training/zhihu/labels/ios_zhihu_output_labels.txt \
    --input_layer=Placeholder \
    --output_layer=final_result \
    --image=../training/zhihu/test/transition-end-000001.jpg