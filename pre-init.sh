#!/bin/bash

# pre-init.sh: get user input to generate a bucket name and replace the code with them

# check if project id and principal were replaced
# extract project_id from variables.tf
project_id=$(sed -n "/variable \"project_id\"/{:begin;n;s/.*default[^\"]*\"\(.*\)\".*/\1/p;t;b begin}" terraform/variables.tf)

if echo "$project_id" | grep -q -E "REPLACE"; then
    echo "Please uncomment and replace the project_id default value in ./terraform/variables.tf" 2>&1;
    exit 1
fi
# extract principal e-mail from variables.tf
principal=$(sed -n "/variable \"service_account_principal\"/{:begin;n;s/.*default[^\"]*\"\(.*\)\".*/\1/p;t;b begin}" terraform/variables.tf)

if echo "$principal" | grep -q -E "REPLACE"; then
    echo "Please uncomment and replace the service_account_principal default value in ./terraform/variables.tf" 2>&1;
    exit 1
fi

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
