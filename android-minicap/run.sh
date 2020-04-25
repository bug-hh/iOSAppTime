ABI=$(adb shell getprop ro.product.cpu.abi | tr -d '\r')
echo "CPU 架构: $ABI"
adb push libs/$ABI/minicap /data/local/tmp/

SDK=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
echo "Android SDK 版本: $SDK"
adb push jni/android-$SDK/$ABI/minicap.so /data/local/tmp/


screen_size=$(adb shell dumpsys window | grep -Eo 'init=[0-9]+x[0-9]+' | head -1 | cut -d= -f 2)
if [ "$screen_size" = "" ]; then
    w=$(adb shell dumpsys window | grep -Eo 'DisplayWidth=[0-9]+' | head -1 | cut -d= -f 2)
    h=$(adb shell dumpsys window | grep -Eo 'DisplayHeight=[0-9]+' | head -1 | cut -d= -f 2)
    screen_size="${w}x${h}"
fi
echo $screen_size

adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P "$screen_size"@"$screen_size"/0 &

echo "创建本地端口 1313 连接 minicap"
adb forward tcp:1313 localabstract:minicap