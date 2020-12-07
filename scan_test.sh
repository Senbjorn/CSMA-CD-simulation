#!/usr/bin/env bash
search_str=$1
input_dir=$2
for fname in $input_dir/*;
do
	echo $fname
	cat $fname | grep "$search_str"
done
