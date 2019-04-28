#!/bin/bash
input=$1
output=${input%.*}
grep  "^\[Black " $1 |sed 's/\[Black //g'|sed 's/\]//g'|sed "s/\"//g" > Blacks
grep  "^\[White " $1 |sed 's/\[White //g'|sed 's/\]//g'|sed "s/\"//g" > Whites
sort -u Blacks > SortedBlacks
sort -u Whites > SortedWhites
cat SortedBlacks SortedWhites > profiles
uniq profiles > $output

