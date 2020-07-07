#echo $LD_LIBRARY_PATH
#$LD_LIBRARY_PATH=/usr/local/lib
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/my_library/
export LD_LIBRARY_PATH
cannelloni -I vcan0 -R 192.168.137.212 -r 20000 -l 20000 -t 10000
