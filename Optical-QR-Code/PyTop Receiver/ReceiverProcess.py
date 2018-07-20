import QRCodeScanner
import time
import multiprocessing

TB = 0
LID = 1
FID = 2
SID = 3

class Receiver:
    def __init__(self, linkID):
        self.linkID = linkID
        self.manager = multiprocessing.Manager()
        self.queue = self.manager.list(["X"])
        self.scanner = QRCodeScanner.QRCodeScanner(self.queue)
        self.scanner.start()
        self.currentID = None
        self.currentFrame = ''
        self.terminalFlag = False
        self.lastSeg = ''
        self.timeStart = 0
        self.timeEnd = 0
        self.nextSegNum = 0
        print("Receiver Built")

    def receive(self):
        while True:
            try:
##                segment = self.scanner.getCurrentSegment()
                segment = self.queue[0]
                
                if (segment != "X"):  ##prevent frames with no QR from being processed
                    
                    if (segment != self.lastSeg):  ##prevent duplicate QRs from being processed
                        self.lastSeg = segment
                        
                        headerMetrics = self.processHeader(segment)

                        tB = headerMetrics[TB]
                        lID = headerMetrics[LID]
                        fID = headerMetrics[FID]
                        sID = headerMetrics[SID]
                        
                        if lID != self.linkID:
                            pass

                        else:
                            print("Recevier: ", segment)
                            
                            validFrame = self.checkFrame(fID, sID)
                            if validFrame == True:
                                
                                self.currentFrame += segment[6:].strip('Z')
                                self.nextSegNum += 1
                                if self.checkTerminal(tB) == True:
                                    self.serialForward()
##                            else:
##                                self.newFrame()
                                                                    
                
            except:
                pass

            time.sleep(.08)

    def serialForward(self):
        print("Packet Received: ", self.currentFrame)
        self.timeEnd = time.time()
        self.calcSpeed()
        

    def calcSpeed(self):
        time = self.timeEnd - self.timeStart
        print(time)
        speed = (len(self.currentFrame) / 2) / time
        print("Receive Speed (Bps): ", speed)

    def newFrame(self):
        print("Reset")
        self.nextSegNum = 0
        self.currentFrame = ''
        self.nextSeg = 0
        #self.lastSeg = ''
        self.timeStart = time.time()
        self.terminalFlag = False

    def processHeader(self, segment):        
        header = segment[:6]
        linkByte = header[:2]
        frameByte = header[2:4]
        segByte = header[4:]
        (terminalBit, linkNum) = self.processLinkByte(linkByte)        
        frameNum = int(frameByte,16)
        segNum = int(segByte,16)
        return (terminalBit, linkNum, frameNum, segNum)


    def processLinkByte(self, linkByte):
        binary = (bin(int(linkByte,16))[2:]).zfill(8)
        terminalBit = binary[0]        
        linkBin = binary[1:]        
        linkNum = int(linkBin,2)        
        return (terminalBit, linkNum)


    def checkFrame(self, frameID, segID):

        if self.currentID == None:
            self.currentID = frameID
        
        if self.terminalFlag == True:
            self.newFrame()
            self.currentID = frameID
        
        if (frameID == self.currentID):
            if self.nextSegNum == segID:
##                print("VALID") 
                return True
            else:
##                print("NOT VALID")
                return False
        else:
##            print("NEW VALID")
            self.newFrame()
            self.currentID = frameID
            
            return True

    def checkTerminal(self, terminalBit):
        
        if terminalBit == '1':
            self.terminalFlag = True
            return True
        elif terminalBit == '0':
            return False





receiver = Receiver(69)
receiver.receive()


