#!/bin/sh

for sw in 110 120 125 130 140; do
  echo $sw
  rm data_qc/aws-sw-${sw}.nc
  for file in data_qc/aws-sw-${sw}-*.nc; do
    echo $file
    ncks -m $file > temp.txt
    for var in ps hur ta ts ws dw snd; do
      if ! grep -q ${var}: temp.txt; then
        echo "Add empty variable: $var"
	ncap2 -s "${var}=0.0" $file -O $file
      fi
    done
    rm temp.txt
  done
ncrcat data_qc/aws-sw-${sw}-*.nc -o data_qc/aws-sw-${sw}.nc
done
