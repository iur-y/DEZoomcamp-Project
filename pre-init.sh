#!/bin/bash

# pre-init.sh: get user input to generate a bucket name and replace the code with them

while true; do
    clear
    echo "Enter q to cancel"
    read -p "Enter any number between 0 and 9999 > " num
    if echo "$num" | grep -q -E "^[0-9]{1,4}$"; then
        if echo "$num" | grep -q -E -i "q"; then
            exit 0
        fi
        break
    else
        continue
    fi
done

while true; do
    clear
    echo "Enter q to cancel"
    read -p "Enter random lowercase letters like 'aisdufh' (5 to 15 letters) > " word
    if echo "$word" | grep -q -E "^[a-z]{5,15}$"; then
        if echo "$word" | grep -q -E -i "q"; then
            exit 0
        fi
        break
    else
        continue
    fi
done

sed -i "/BUCKET/s/api_producer_data_zoomcamp_project/&_${word}_${num}/" ./producer/producer.py
sed -i "/BUCKET/s/api_producer_data_zoomcamp_project/&_${word}_${num}/" ./app/app_utils.py
sed -i "s/api_producer_data_zoomcamp_project/&_${word}_${num}/;s/raw_parquet_data_zoomcamp_project/&_${word}_${num}/;" ./terraform/main.tf
sed -i "/word=/s/REPLACE/${word}/;/num=/s/REPLACE/${num}/" ./terraform/startup-script.sh

touch pre-init-done
