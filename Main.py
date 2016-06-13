# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 18:16:58 2016

@author: Nate Nichols

"""

import binascii
import zlib
import os

def genXml(pixels):
    
# search the xml document for ss:Color=" in hex. 
    
    
    with open("test.xml","rb") as f:
        
        
        
        
        f.close()
    
# read image data
fh = open('test.png','rb')
data = binascii.hexlify(fh.read())
debug = fh.read()
fh.close()
# write raw hex to a textfile
fh = open('test.txt','w')
fh.write(data)
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
imgHex = chunks["IDAT"] # this should just use the dictionary..

# extract IHDR block
# move this block to a DEF later? perhaps all should be in a get<BLOCK> method
IHDRblock = chunks["IHDR"]
zWidth = int(IHDRblock[0:8],16)
zHeight = int(IHDRblock[8:16],16)
zArea = zWidth*zHeight
zbitDepth = int(IHDRblock[16:18],16)
zcolorType = int(IHDRblock[19:20],16) # if this is 3, PLTE chunk exists
zhCompression = int(IHDRblock[21:22],16)
zFilter = int(IHDRblock[23:24],16)
zInterlace = int(IHDRblock[25:26],16)

fh = open('test.txt','w')
decompImgHex= (
        zlib.decompress(binascii.unhexlify(chunks["IDAT"]),
        15, 
        len(imgHex))
        )
# Also might want to create a bitstream and switch to decompressObj to use 
# less memory, work with large images (megabytes)
fh.write(decompImgHex)
fh.close
fh.close()


# TODO: account for interlaced ("fade in type") rendering
pixels = []

if zcolorType == 0:
    debug = 69
    # simple grayscale
    # 1,2,4,8,16 = allowed bitdepth

elif zcolorType == 2:
    # 8 or 16 bits per sample = 24 or 48 bits per pixel = 6 or 12 nibbles per 
    # pixel
    # RGB 
    decompImgHex = list(binascii.hexlify(decompImgHex))
    
    nibblesPerPixel = (zbitDepth*3)/4 # make this dynamic
        
    for i in range(0,len(decompImgHex),nibblesPerPixel*zWidth):
        decompImgHex = decompImgHex[0:i] + decompImgHex[i+2:len(decompImgHex)]
    
    for i in range(nibblesPerPixel,
                   len(decompImgHex)+nibblesPerPixel,
                   nibblesPerPixel):        
        pixels.append([
            int(decompImgHex[i-6] + decompImgHex[i-5],16), # TODO: add 12 nibble handling
            int(decompImgHex[i-4] + decompImgHex[i-3],16),
            int(decompImgHex[i-2] + decompImgHex[i-1],16),
            ])
    
    
#00
#ff ff ff
#00 00 00 
#00 
#00 00 00
#ff ff ff

    
    
elif zcolorType == 3:
    pallette = []
    # 1,2,4,8
    # extract PLTE block
    # number of bits per sample is bitDepth. allowed: 1,2,4,8 

elif zcolorType == 4:
    debug = 9
    # 8,16
    # grayscale with alpha

elif zcolorType == 6:
    debug = 420
    # 8,16    
    # RGBA

#------------------------------------------------------------------------------
print("\n"+"------------------------------------"+"\n")

