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
fh = open('test2.png','rb')
data = binascii.hexlify(fh.read())
debug = fh.read()
fh.close()
# write raw hex to a textfile
fh = open('test2.txt','w')
fh.write(data)
fh.close
fh.close()



#test for the universal PNG file signature
if data[0:16] == "89504e470d0a1a0a":
    print("Valid Signature.")  
else:
    print("Invalid Signature. Testing anyway...")

critical = {"IHDR","PLTE","IDAT",""}
ancillary = {"cHRM","gAMA","iCCP","sBit","sRGB","bKGD","hIST","tRNS","pHYs","sPLT","tIME","iTXt","tEXt","zTXt"}
keywords = {"Title","Author","Description","Copyright","Creation Time","Software","Disclaimer","Warning","Source","Comment"}

print("searching for ancillary flags...")

foundAncillary = []
wordhex = ""
for i in range(0,len(ancillary)):
    wordHex = binascii.hexlify(ancillary[i])    
    index = data.find(wordHex) 

    if index == -1:
        print(str(ancillary[i])+" not found...")
    else:
        print(str(ancillary[i]+"found."))
        foundAncillary.push({keywords[i],index,index + len(wordHex)})
    
    
print("searching for keywords...")
    
foundKeywords = []

for i in keywords:
    wordHex = binascii.hexlify(keywords[i])        
    index = data.find(wordHex) 
    if index == -1:
        print(str(keywords[i])+" not found...")
    else:
        print(str(keywords[i]+"found."))
        foundKeywords.push({keywords[i],index,(index+len(wordHex))})
        



# extract IHDR block
IHDRindex = data.find("49484452") + 8 
IHDRend =IHDRindex + 26 # 13 bytes = 26 nibbles
IHDRblock = data[IHDRindex:IHDRend]
Width = int(IHDRblock[0:8],16)
Height = int(IHDRblock[8:16],16)
Area = Width*Height
Depth = int(IHDRblock[16:18],16)
Colortype = int(IHDRblock[19:20],16) # if this is 3, PLTE chunk exists
hCompression = int(IHDRblock[21:22],16)
Filter = int(IHDRblock[23:24],16)
Interlace = int(IHDRblock[25:26],16)
#read pHYs block
pHYsindex = data.find("704859730d0a") + 12
pHYsend = pHYsindex + 18
pHYsblock = data[pHYsindex:pHYsend]
ppuX = int(pHYsblock[0:8],16)
ppuY = int(pHYsblock[8:16],16)
unit = int(pHYsblock[16:18],16)


# extract the actual image data between IDAT and IEND
Imghex = data[data.find("49444154") + 8:data.find("49454e44")] 
print(len(Imghex))

pixels = Pixels()

Ancillary = {"cHRM","gAMA","iCCP","sBit","sRGB","bKGD","hIST","tRNS","pHYs","sPLT",
"tIME","iTXt","tEXt","zTXt"}

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
   
   Ancillary chunks (need not appear in this order):
   
           Name  Multiple  Ordering constraints
                   OK?
   
           cHRM    No      Before PLTE and IDAT
           gAMA    No      Before PLTE and IDAT
           iCCP    No      Before PLTE and IDAT
           sBIT    No      Before PLTE and IDAT
           sRGB    No      Before PLTE and IDAT
           bKGD    No      After PLTE; before IDAT
           hIST    No      After PLTE; before IDAT
           tRNS    No      After PLTE; before IDAT
           pHYs    No      Before IDAT
           sPLT    Yes     Before IDAT
           tIME    No      None
           iTXt    Yes     None
           tEXt    Yes     None
           zTXt    Yes     None

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
















