#!/bin/bash
# AC_awk.sh created by illuz at 2015-03-25 13:10:51

awk '/^[0-9][0-9][0-9]\-[0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]$/ || /^\([0-9][0-9][0-9]\) [0-9][0-9][0-9]\-[0-9][0-9][0-9][0-9]$/ {print}' file.txt
