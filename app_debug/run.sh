#!/usr/bin/env bash


pkill "ios_minicap"

UDID=`idevice_id -l` | xargs
PORT=12345
RESOLUTION="400x600"
PLATFORM="iOS"
echo $UDID
app_info=`ideviceinstaller -l | grep -i zhihu`

if [ "$UDID" == "" ]; then
    echo "没有检测到连接设备，程序退出"
    exit 1
elif [ "$app_info" == "" ]; then
    echo "连接的设备中未安装「知乎」APP，程序退出"
    exit
fi

./ios-minicap/build/ios_minicap \
    --udid $UDID \
    --port $PORT --resolution $RESOLUTION >/dev/null 2>&1 &

#python test.py -d $UDID -p $PORT -r $RESOLUTION
./ios-minicap/build/ios_minicap -u f955925d4043f9d8fbb014da293dcf6ecc58b8aa -p 12345 -r 375x600

#
#process_id=34564
#process_id=`ps -Af | grep './ios-minicap/build/ios_minicap' | awk '{print $2}' | head -n 1`
#kill $process_id

#./ios-minicap/build/ios_minicap --udid f955925d4043f9d8fbb014da293dcf6ecc58b8aa --port 12345 --resolution 400x600
#python test.py -d f955925d4043f9d8fbb014da293dcf6ecc58b8aa -p iOS
