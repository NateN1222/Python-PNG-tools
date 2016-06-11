# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 18:16:58 2016

@author: Nate Nichols

"""
import csv
import binascii



class Pixels(object):
    
    def printPixels(self):
        temp = ""
        for i in range(1,self.count):
            temp = str(i)+": "            
            for j in range(0,3):
                temp = temp + (str(self.pixels[i][j]) + " ")
            print(temp)
        print(str(self.count))
                
    
    def newPixel(self,dat):    
        self.count = self.count + 1
        r = int(dat[1:2],16)
        g = int(dat[2:3],16)
        b = int(dat[4:5],16)        
        self.pixels.append([r,g,b])
    
    def __init__(self):
        self.count = 0
        self.pixels = []






f = open("test.csv", 'rb') 
try:
    reader = csv.reader(f)
    for row in reader:   
        print row    
finally:
    f.close()      
    
    
# read image data
fh = open('test.png','rb')
data = binascii.hexlify(fh.read())
debug = fh.read()
fh.close()
# write raw hex to a textfile
fh = open('test.txt','w')
fh.write(data)
fh.close
fh.close()

#test for the universal PNG file signature
if data[0:16] == "89504e470d0a1a0a":
    print("Valid Signature.")  
else:
    print("Invalid Signature. Testing anyway...")

# critical ones will just be searched for manually because they are certain 
# to be found
keywords = ["IHDR","IDAT","IEND","cHRM","gAMA","iCCP","sBit","sRGB","bKGD",
"hIST","tRNS","pHYs","sPLT","tIME","iTXt","tEXt","zTXt","Title","Author",
"Description","Copyright","Creation Time","Software","Disclaimer","Warning",
"Source","Comment"]

print("searching for ancillary flags...")

foundKeywords = []
index = -1
wordhex = ""


for i in keywords:
    wordHex = binascii.hexlify(i)
    index = data.find(wordHex)

    if index == -1:
        print(i+" not found...")
    else:
        print(i+" found.")
        foundKeywords.append([i,index,index + len(wordHex)])
        # foundkeywords format: keyword, start address, end address

# figure out order of flags and then determine whether or not        
# PNG is valid according to PNG spec
# TODO: test for duplicates
print(type(foundKeywords))


foundKeywords.sort(key=lambda x: x[1])


IDATindex = data.find("49444154")
PLTEindex = data.find("504c5445")
#Name  Multiple  Ordering constraints
#        OK?
#   
#cHRM    No      Before PLTE and IDAT
#gAMA    No      Before PLTE and IDAT
#iCCP    No      Before PLTE and IDAT
#sBIT    No      Before PLTE and IDAT
#sRGB    No      Before PLTE and IDAT
#bKGD    No      After PLTE; before IDAT
#hIST    No      After PLTE; before IDAT
#tRNS    No      After PLTE; before IDAT
#pHYs    No      Before IDAT
#sPLT    Yes     Before IDAT
#tIME    No      None
#iTXt    Yes     None
#tEXt    Yes     None


# just assume the PNG data isn't absolutely FUBAR

for i in foundKeywords:
    if (i[0] == "cHRM")|(i[0] == "gAMA")|(i[0] == "iCCP")|(i[0] == "sBIT")|(i[0] == "sRGB"):
        if ((i[1] > PLTEindex) & (i[1] > IDATindex)):
            print("--------error 1--------")
    if (i[0] == "bKGD")|(i[0] == "hIST")|(i[0] == "tRNS"):
        if (i[1] < PLTEindex)|(i[1] > IDATindex):
            print("--------error 2--------")
    if(i[0] == "pHYs")|(i[0] == "sPLT"):
        if(i[1] > IDATindex):
            print("--------error 3--------")
# now break into chunks, store into dictionary.
# format: {Name:Chunk}

next_ = None
l = len(foundKeywords)
chunks = {}
for index, obj in enumerate(foundKeywords):
    if index < (l - 1):
        next_ = foundKeywords[index + 1]    
        chunks[obj[0]] = (data[obj[2]:next_[1]])
    else: 
        chunks[obj[0]] = data[obj[2]:len(data)]
            
# extract the actual image data between IDAT and IEND
Imghex = chunks["IDAT"] # this should just use the dictionary....

# extract IHDR block
# move this block to a DEF later?
IHDRblock = chunks["IHDR"]
Width = int(IHDRblock[0:8],16)
Height = int(IHDRblock[8:16],16)
Area = Width*Height
Depth = int(IHDRblock[16:18],16)
Colortype = int(IHDRblock[19:20],16) # if this is 3, PLTE chunk exists
hCompression = int(IHDRblock[21:22],16)
Filter = int(IHDRblock[23:24],16)
Interlace = int(IHDRblock[25:26],16)


# extract the actual image data between IDAT and IEND

# extract PLTE if it exists

#print(chunks["IDAT"])
print("\n"+"------------------------------------"+"\n")

test = "this is a test ok ladsZZZabdcefgjog"

print(test[test.find("lads")+4:test.find("abdcef")])


"""""
IDEA: rework this to just automatically break into chunks when 
it finds these keywords so they can be easily parsed



   Critical chunks (must appear in this order, except PLTE
                    is optional):
   
           Name  Multiple  Ordering constraints
                   OK?
   
           IHDR    No      Must be first
           PLTE    No      Before IDAT
           IDAT    Yes     Multiple IDATs must be consecutive
           IEND    No      Must be last

Standard keywords for text chunks:

   Title            Short (one line) title or caption for image
   Author           Name of image's creator
   Description      Description of image (possibly long)
   Copyright        Copyright notice
   Creation Time    Time of original image creation
   Software         Software used to create the image
   Disclaimer       Legal disclaimer
   Warning          Warning of nature of content
   Source           Device used to create the image
   Comment          Miscellaneous comment; conversion from
                    GIF comment

"""""
















