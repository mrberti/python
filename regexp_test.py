#! /bin/python
import re

file_name = 'test.csv'

text = '';
with open(file_name,'r') as f:
    for line in f:
        new_line = line
        if re.match(r'^path,',line):
            new_line = re.sub(r'([^,/]*/)*([^,]*)',r'\2',line)
        text = text + new_line

print(text)