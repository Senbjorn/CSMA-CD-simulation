#!/usr/bin/env bash
port=$1
n_stations=$2
station_time=$3
output_dir=$4

bus_time=$((station_time+10))
echo $bus_time
echo $station_time


bus_file=$output_dir/bus.txt
echo $bus_file
python bus.py $port 0.052 $bus_time > $bus_file &
sleep 5s
for ((i = 1 ; i < n_stations+1 ; i++)); do
  station_file=$output_dir/station_$i.txt
  echo $station_file
  python station.py $port $station_time "Hi from station $i" > $station_file &
done
