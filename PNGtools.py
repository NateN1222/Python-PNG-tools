# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 18:16:58 2016

@author: Nate Nichols

"""
# TODO: support adding to "keywords"
# TODO: perhaps create a way to "recompile" a PNG
# TODO: support filtering 
# TODO: switch to decompressObj and a buffer to reduce memory usage
# TODO: support interlaced and PLTE formats
# TODO: finish genXml
# TODO: allow searching for blocks/testing the image without parsing the data
import binascii
import zlib

# returns list of  nibblesPerPixel chunks broken into nibblesPerSample parts.
# zWidth is just used to remove filter bits. 
class PNGReaderObj:
    
    def __init__(self):
        self.keywords = ["IHDR","IDAT","IEND","cHRM","gAMA","iCCP","sBit",
        "sRGB","bKGD","hIST","tRNS","pHYs","sPLT","tIME","iTXt","tEXt","zTXt",
        "Title","Author","Description","Copyright","Creation Time","Software",
        "Disclaimer","Warning","Source","Comment"]
        self.foundKeywords = [] # incase you want to check what chunks it found
    
    def genXml(self,pixels):
    # search the xml document for ss:Color=" in hex.   
    # this assumes test.xml has the dimmensions of the image.  
    # WIP, do not use
      with open("test.xml","rb") as f:
            f.close()
    
    def getPixels(self,file):    
        def parse(decompImgHex,nibblesPerPixel,nibblesPerSample,zWidth): 
            def listToStr(_list):    
                t = ""
                for i in _list:
                    t = t + i
                return t        
            decompImgHex = list(binascii.hexlify(decompImgHex))
            lines = listToStr(decompImgHex)
            # ----------------------
            #print "lines: "+ lines
            #-----------------------
            nibblesPerLine = (nibblesPerPixel*zWidth)+2    
            temp = []
            for i in range(0,len(lines),nibblesPerLine):
                temp.append(lines[i+2:i+nibblesPerLine])
            #print "temp :" + listToStr(temp)
            decompImgHex = temp
            lasti = 0
            pixels = []
            decompImgHex = listToStr(decompImgHex)
            #print decompImgHex
            for i in range(nibblesPerPixel,len(decompImgHex)+1,nibblesPerPixel):        
                rpixel = decompImgHex[lasti:i]
                rpixel = listToStr(rpixel)
                #print "rpixel:" + rpixel
                pixel = []
                lastj = 0
                #print "len(rpixel) :" + str(len(rpixel))
                for j in range(nibblesPerSample,len(rpixel)+1,nibblesPerSample):
                    sample = rpixel[lastj:j]
                    #sample = listToStr(sample)
                  #  print "sample: "+ sample
                    pixel.append(sample)
                 #   print "pixel: " + listToStr(pixel)
                    lastj = j
                #print "pixel: "+ listToStr(pixel)
                pixels.append(pixel)
                lasti = i
            print "pixels:"+ str(pixels)
            return pixels    
        try:    
            fh = open(file,'rb')
            data = binascii.hexlify(fh.read())
            fh.close()
        except IOError:        
            print("could not open png file.")
            return 0
        #test for the universal PNG file signature
        if data[0:16] == "89504e470d0a1a0a":
            print("Valid PNG Signature.")  
        else:
            print("Invalid Signature. Testing anyway...")
        
        print("searching for chunks...")
        
        self.foundKeywords = []
        index = -1
        wordHex = ""   
        for i in self.keywords:
            wordHex = binascii.hexlify(i)
            index = data.find(wordHex)
            if index == -1:
                print(i+" not found...")
            else:
                print(i+" found.")
                self.foundKeywords.append([i,index,index + len(wordHex)])
                # foundkeywords format: keyword, start address, end address
        
        # figure out order of flags and then determine whether or not        
        # PNG is valid according to PNG spec    
        self.foundKeywords.sort(key=lambda x: x[1])    
        IDATindex = data.find("49444154")
        PLTEindex = data.find("504c5445")
        
        # just assume the PNG data isn't absolutely FUBAR..
        for i in self.foundKeywords:
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
        l = len(self.foundKeywords)
        chunks = {}
        for index, obj in enumerate(self.foundKeywords):
            if index < (l - 1):
                next_ = self.foundKeywords[index + 1]    
                chunks[obj[0]] = (data[obj[2]:next_[1]])
            else: 
                chunks[obj[0]] = data[obj[2]:len(data)]
                    
        # extract the actual image data between IDAT and IEND
        imgHex = chunks["IDAT"] # this should just use the dictionary..
        
        # extract IHDR block
        IHDRblock = chunks["IHDR"]
        zWidth = int(IHDRblock[0:8],16)
        zHeight = int(IHDRblock[8:16],16)
        zArea = zWidth*zHeight
        zBitDepth = int(IHDRblock[16:18],16)
        zcolorType = int(IHDRblock[19:20],16) # if this is 3, PLTE chunk exists
        zCompression = int(IHDRblock[21:22],16)
        zFilter = int(IHDRblock[23:24],16)
        zInterlace = int(IHDRblock[25:26],16)
        
        decompImgHex= (
                zlib.decompress(binascii.unhexlify(chunks["IDAT"]),
                15, 
                len(imgHex))
                )
        
        nibblesPerPixel = (zBitDepth*3)/4
        nibblesPerSample = zBitDepth/4
        
        if zcolorType == 0:
            # simple grayscale
            return parse(decompImgHex,nibblesPerPixel,nibblesPerSample,zWidth)
        #----------------------------------------------------------------------
        elif zcolorType == 2:
            # RGB
            return parse(decompImgHex,nibblesPerPixel,nibblesPerSample,zWidth)
            
        elif zcolorType == 4:
            # grayscale with alpha
            return parse(decompImgHex,nibblesPerPixel,nibblesPerSample,zWidth)
        
        elif zcolorType == 6:
            # RGBA
            return parse(decompImgHex,nibblesPerPixel,nibblesPerSample,zWidth)
            
        elif zcolorType == 3:
            print("this type of PNG not supported as of now.")
            return 0
            # 1,2,4,8
            # extract PLTE block. This one works differently than the others.
            # number of bits per sample is bitDepth. allowed: 1,2,4,8 