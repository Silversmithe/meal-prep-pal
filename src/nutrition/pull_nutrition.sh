#!/bin/bash

## References
# https://www.sciencedirect.com/science/article/pii/S0002916522001794?via%3Dihub
# https://fdc.nal.usda.gov/index.html

## Download the database
# https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip
wget https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip

## Unzip the file
unzip FoodData_Central_sr_legacy_food_json_2018-04.zip

## Remove the zip file
rm FoodData_Central_sr_legacy_food_json_2018-04.zip

## Complete
