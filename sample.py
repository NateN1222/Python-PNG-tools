# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 12:35:50 2016

@author: Nate Nichols
"""

import PNGtools


test = PNGtools.PNGReaderObj()

resultPixels = test.getPixels("test.png")

count = 0
for i in resultPixels:
    count = count + 1
    temp = "pixel number " + str(count) + " is: "
    for j in i:
        temp = temp + str(int(j,16)) + " "
    print temp

temp = "keywords found are: "
for i in test.foundKeywords:
    temp = temp + i[0] + " "
print temp