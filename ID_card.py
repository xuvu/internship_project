from time import sleep
from smartcard.CardMonitoring import CardMonitor, CardObserver


# a simple card observer that prints inserted/removed cards
class PrintObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """
    def __init__(self):
        self.CardStatus = 0

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            self.CardStatus = 1

        for card in removedcards:
            self.CardStatus = 0

import binascii
import io
import os
import sys
from PIL import Image
from smartcard.System import readers
from smartcard.util import HexListToBinString, toHexString, toBytes

class CardReader:
    def __init__(self):
        # Check card
        self.SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
        self.THAI_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]

        # CID
        self.CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]

        # TH Fullname
        self.CMD_THFULLNAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64]

        # EN Fullname
        self.CMD_ENFULLNAME = [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64]

        # Date of birth
        self.CMD_BIRTH = [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08]

        # Gender
        self.CMD_GENDER = [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01]

        # Card Issuer
        self.CMD_ISSUER = [0x80, 0xb0, 0x00, 0xF6, 0x02, 0x00, 0x64]

        # Issue Date
        self.CMD_ISSUE = [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x08]

        # Expire Date
        self.CMD_EXPIRE = [0x80, 0xb0, 0x01, 0x6F, 0x02, 0x00, 0x08]

        # Address
        self.CMD_ADDRESS = [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64]

        #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓ code for card observer ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        self.cardmonitor = CardMonitor()
        self.cardobserver = PrintObserver()
        self.cardmonitor.addObserver(self.cardobserver)
        #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ code for card observer ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

    """
    def checkCard(self):
        return self.cardobserver.CardStatus
    """

    def readCard(self):
        if self.cardobserver.CardStatus:
            # Get all the available readers
            readerList = readers()

            """
            for readerIndex,readerItem in enumerate(readerList):
                print(readerIndex, readerItem)
            """
            # Select reader
            readerSelectIndex = 0

            reader = readerList[readerSelectIndex]
            #print("Using:"), reader

            self.connection = reader.createConnection()
            self.connection.connect()
            
            atr = self.connection.getATR()
            #print("ATR: " + toHexString(atr))
            if (atr[0] == 0x3B & atr[1] == 0x67):
                self.req = [0x00, 0xc0, 0x00, 0x01]
            else :
                self.req = [0x00, 0xc0, 0x00, 0x00]

            #data, sw1, sw2 = self.connection.transmit(self.SELECT + self.THAI_CARD)

            self.connection.transmit(self.SELECT + self.THAI_CARD)
            
            #print("Select Applet: %02X %02X" % (sw1, sw2))

            allInfo = {
            'CID': self.thai2unicode(self.getData(self.CMD_CID, self.req)[0]),
            'FullnameTH': self.thai2unicode(self.getData(self.CMD_THFULLNAME, self.req)[0]),
            'FullnameEN': self.thai2unicode(self.getData(self.CMD_ENFULLNAME, self.req)[0]),
            'Date of birth':self.thai2unicode(self.getData(self.CMD_BIRTH, self.req)[0]) ,
            'Gender': self.thai2unicode(self.getData(self.CMD_GENDER, self.req)[0]),
            'Card Issuer': self.thai2unicode(self.getData(self.CMD_ISSUER, self.req)[0]),
            'Issue Date': self.thai2unicode(self.getData(self.CMD_ISSUE, self.req)[0]),
            'Expire Date': self.thai2unicode(self.getData(self.CMD_EXPIRE, self.req)[0]),
            'Address': self.thai2unicode(self.getData(self.CMD_ADDRESS, self.req)[0]),
            }
            return allInfo
            
        else: 
            return 0

    # tis-620 to utf-8
    def thai2unicode(self,data):
        resp = ''
        if isinstance(data, list):
            resp = bytes(data).decode('tis-620').replace('#', ' ')
            return resp.strip()
        else :
            return data

    def getData(self,cmd, req = [0x00, 0xc0, 0x00, 0x00]):
        data, sw1, sw2 = self.connection.transmit(cmd)
        data, sw1, sw2 = self.connection.transmit(req + [cmd[-1]])
        return [data, sw1, sw2]
    
    def __del__(self):
        # don't forget to remove observer, or the
        # monitor will poll forever...
        self.cardmonitor.deleteObserver(self.cardobserver)


