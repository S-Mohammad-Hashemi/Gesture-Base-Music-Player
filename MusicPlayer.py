
from __future__ import unicode_literals
from time import sleep

import sys
import threading
import time


import spotify
from PyQt4 import QtGui
from PyQt4.QtGui import *
import spotipy
from svmTrain import trainModel
import threading
import socket
import math
from spotify.player import PlayerState
import json
import pickle

track_uri = ''
current_milli_time = lambda: int(round(time.time() * 1000))
        
        
    


class SpotifyGUI(QtGui.QWidget):
    listWidget=None
    session=None
    clf=None
    favListFile=None
    favList=None
    def __init__(self):
        super(SpotifyGUI, self).__init__()
        self.sp = spotipy.Spotify()
        self.initUI()
        self.session = spotify.Session()
        session=self.session
        Spotify_username="" #Enter your own username
        Spotify_password="" #Enter your own password
        session.login(Spotify_username,Spotify_password)
        print session.connection.state
        session.process_events()
        print session.connection.state
        session.process_events()
        print session.connection.state
        session.process_events()
        print session.connection.state
        session.process_events()    
        print session.connection.state
        session.process_events()
        print session.connection.state
        session.process_events()
        
        print session.connection.state
        session.process_events()
        while str(session.connection.state)!='1':
            session.process_events()
            sleep(1)
        print session.user
#         album = session.get_album('spotify:album:7bmoWZCJMWHCT3qXNr9pT0')
        self.audio = spotify.AlsaSink(session)
        self.favListFile=open("favList","r")
        try:
            self.favList=pickle.load(self.favListFile)
        except:
            self.favList=[]
            print "error in reading file!"
        self.favListFile.close()
        self.session.player.startTime=current_milli_time()
        self.session.player.duration=0
        #TODO

        self.clf=trainModel()
        print "model is trained..."
        t = threading.Thread(target=self.getGestureFromNodeRed)
        t.start()
        print "here"
        
        
    def getGestureFromNodeRed(self):
        print "NETWORKING"
        TCP_IP = '127.0.0.1'
        TCP_PORT = 8887
        BUFFER_SIZE = 300  # Normally 1024, but we want fast response
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            print 'Connection address:', addr
            bb=None
            while 1:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    print "Error: Networking, no data error!!!!!"
                    bb=[[],[],[],[],[]]
                    break
                lines=data.split('\n')
                if len(lines)!=1:
                    print "error in len of lines"
                    bb=[[],[],[],[],[]]
                    continue
                if lines[0]=="end":
                    print "end"
                    if bb!=None:
                        mylist=[]
                        for line in bb:
                            for i in range(len(line)):
                                mylist.append(line[i])
                        mylist=mylist+[0]*(5*50-len(mylist))
                        y_predict=self.clf.predict([mylist])
                        ops=['play','stop','next','prev','ff','ff2','r','r2','like','unlike']
                        query=ops[y_predict[0]]
                        self.gestureCommand(query)
                        print "heyyyyy"
                    bb=[[],[],[],[],[]]
                    continue
                try:
                    sensorName,accelRaw=lines[0].split(':')
                except:
                    print "error in colon(:)"    
                    bb=[[],[],[],[],[]]
                    continue
                accelData=None
                if sensorName=="bb3":
                    accelData=accelRaw.split(' ')
                else:
                    accelData=accelRaw.split(', ')
                    for i in range(len(accelData)):
                        accelData[i]=int(math.ceil(float(accelData[i])*256))
                    
                if len(accelData)!=3:
                    print "Error02: wrong accelData"
                    bb=[[],[],[],[],[]]
                    continue
                if bb==None:
                    continue
                index=int(sensorName[-1])-1
                for i in range(len(accelData)):
                    accelData[i]=(int(accelData[i])+512)/1024.0
                bb[index].extend(accelData)
                
            conn.close()

        
    def searchMusic(self):
        self.listWidget.clear()
        sender=self.sender()
        query=str(sender.text())
        print query,type(query)
        sp=self.sp
        results = sp.search(q=query, limit=50)
        print type(results),len(results)
#         print results
#         for x in results['tracks']['items']:
# #             for y in x:
#             print x['name'],x['artists']
#             print ",,,"
        
        self.session.currentIndex=0
        self.session.total=len(results['tracks']['items'])
        print "total is: ",self.session.total
        for i, t in enumerate(results['tracks']['items']):
            tempName=t['name']
            tempArtist=t["artists"][0]["name"]
#             print type(tempName)
            mystr=tempName 
            mystr+=" "+tempArtist
#             print mystr
            item=QListWidgetItem(mystr)
            item.meta=t
            self.listWidget.addItem(item)
        self.playTrack(self.listWidget.item(0),0)
    def removeFromFavList(self,item):
        print self.favList
        track_uri=item.meta["uri"]
        track_name=item.text()
        index=None
        for i,item in enumerate(self.favList):
            print item["name"]
            print track_name
            print item["uri"]
            print track_uri
            if str(item["name"])==str(track_name) and str(item["uri"])==str(track_uri):
                print "yey",i
                index=i
                break
        print "herrrreeee"
        if index!=None:
            del self.favList[index]
            print "deleted"
#         self.favList.append(dict)
    def addToFavList(self,item):
#         print item,str(item.text())
        track_uri=item.meta["uri"]
        track_name=item.text()
        dict={"name":track_name,"uri":track_uri}
        for elem in self.favList:
            if elem["uri"]==track_uri:
                return
        self.favList.append(dict)
#         track = self.session.get_track(track_uri).load()
#         self.session.player.load(track)
#         self.session.player.play()
#         self.session.player.startTime=current_milli_time()
#         self.session.player.duration=0
        print "added"
        
    def playTrack(self,item,newIndex):
        self.session.currentIndex=newIndex
#         print item,str(item.text())
        track_uri=item.meta["uri"]
        track = self.session.get_track(track_uri).load()
        self.session.player.load(track)
        self.session.player.play()
        self.session.player.startTime=current_milli_time()
        self.session.player.duration=0
        print "yohooo"
    def itemClickedFunction(self,item):
        sender=self.sender()
        self.session.currentIndex=self.listWidget.currentRow()
        self.playTrack(item,self.session.currentIndex)
#         print type(sender)
        
#         for key,value in item.meta.iteritems():
#             print key,value
    def gestureCommand(self,query):
        print query
        self.session.player.duration+=current_milli_time()-self.session.player.startTime
        self.session.player.startTime=current_milli_time()
        if query=="play":
            self.session.player.play(self.session.player.state!=PlayerState.PLAYING)
        elif query=="next":
            nextItemIndex=(self.session.currentIndex+1) % self.session.total
            nextItem=self.listWidget.item(nextItemIndex)
            self.playTrack(nextItem,nextItemIndex)
        elif query=="prev":
            prevItemIndex=(self.session.currentIndex-1) % self.session.total
            prevItem=self.listWidget.item(prevItemIndex)
            self.playTrack(prevItem,prevItemIndex)
        elif query=="stop":
            self.session.player.duration=0
            self.session.player.startTime=current_milli_time()
            self.session.player.unload()
        elif query=="ff":
            self.session.player.duration+=1000*10
            self.session.player.seek(self.session.player.duration)
        elif query=="ff2":
            self.session.player.duration+=1000*20
            self.session.player.seek(self.session.player.duration)
        elif query=="ff3":
            self.session.player.duration+=1000*30
            self.session.player.seek(self.session.player.duration)
        elif query=="r":
            self.session.player.duration-=1000*10
            self.session.player.seek(self.session.player.duration)
        elif query=="r2":
            self.session.player.duration-=1000*20
            self.session.player.seek(self.session.player.duration)
        elif query=="r3":
            self.session.player.duration-=1000*30
            self.session.player.seek(self.session.player.duration)
        elif query=="like":
            ItemIndex=(self.session.currentIndex) % self.session.total
            item=self.listWidget.item(ItemIndex)
            self.addToFavList(item)
        elif query=="unlike":
            ItemIndex=(self.session.currentIndex) % self.session.total
            item=self.listWidget.item(ItemIndex)
            self.removeFromFavList(item)
        elif query=="fav":
            self.openFavList()
            
        print "duration:" , self.session.player.duration
        
    def openFavList(self):
        self.listWidget.clear()
#         sender=self.sender()
#         query=str(sender.text())
#         print query,type(query)
#         sp=self.sp
#         results = sp.search(q=query, limit=50)
#         print type(results),len(results)
#         print results
#         for x in results['tracks']['items']:
# #             for y in x:
#             print x['name'],x['artists']
#             print ",,,"
        
        self.session.currentIndex=0
        self.session.total=len(self.favList)
        print "total is: ",self.session.total
        for i, t in enumerate(self.favList):
            tempName=t['name']
#             tempArtist=t["artists"][0]["name"]
#             print type(tempName)
            mystr=tempName 
#             mystr+=" "+tempArtist
#             print mystr
            item=QListWidgetItem(mystr)
            item.meta=t
            self.listWidget.addItem(item)
        self.playTrack(self.listWidget.item(0),0)    
    def runCommand(self):
        sender=self.sender()
        query=str(sender.text())
        sender.clear()
        #play,pause,stop,ff,rewind,specific genre, fav playlist
        print query
        self.session.player.duration+=current_milli_time()-self.session.player.startTime
        self.session.player.startTime=current_milli_time()
        if query=="play":
#             self.session.player.play()
            self.session.player.play(self.session.player.state!=PlayerState.PLAYING)
        elif query=="pause":
            self.session.player.pause()
        elif query=="next":
            nextItemIndex=(self.session.currentIndex+1) % self.session.total
            nextItem=self.listWidget.item(nextItemIndex)
            self.playTrack(nextItem,nextItemIndex)
        elif query=="prev":
            prevItemIndex=(self.session.currentIndex-1) % self.session.total
            prevItem=self.listWidget.item(prevItemIndex)
            self.playTrack(prevItem,prevItemIndex)
            
        elif query=="stop":
            self.session.player.duration=0
            self.session.player.startTime=current_milli_time()
            self.session.player.unload()
        elif query=="ff":
            self.session.player.duration+=1000*10
            self.session.player.seek(self.session.player.duration)
        elif query=="ff2":
            self.session.player.duration+=1000*20
            self.session.player.seek(self.session.player.duration)
        elif query=="ff3":
            self.session.player.duration+=1000*30
            self.session.player.seek(self.session.player.duration)
        elif query=="r":
            self.session.player.duration-=1000*10
            self.session.player.seek(self.session.player.duration)
        elif query=="r2":
            self.session.player.duration-=1000*20
            self.session.player.seek(self.session.player.duration)
        elif query=="r3":
            self.session.player.duration-=1000*30
            self.session.player.seek(self.session.player.duration)
        elif query=="like":
            ItemIndex=(self.session.currentIndex) % self.session.total
            item=self.listWidget.item(ItemIndex)
            self.addToFavList(item)
        elif query=="unlike":
            ItemIndex=(self.session.currentIndex) % self.session.total
            item=self.listWidget.item(ItemIndex)
            self.removeFromFavList(item)
        elif query=="fav":
            self.openFavList()
            
        print "duration:" , self.session.player.duration
        
    def closeEvent(self, *args, **kwargs):
        print "we are done!"
        self.favListFile=open("favList","w")
        pickle.dump(self.favList, self.favListFile)
        self.favListFile.close()
        return QtGui.QWidget.closeEvent(self, *args, **kwargs)
        
    def initUI(self):
        
        search = QtGui.QLabel('Search')
        searchEdit = QtGui.QLineEdit()
        searchEdit.returnPressed.connect(self.searchMusic)
        command = QtGui.QLabel("Command")
        commandEdit=QtGui.QLineEdit()
        commandEdit.returnPressed.connect(self.runCommand)

        self.listWidget = QListWidget()
        self.listWidget.itemActivated.connect(self.itemClickedFunction)
        for i in range(20):
            item = QListWidgetItem("Item %i" % i)
            self.listWidget.addItem(item)

        grid = QtGui.QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(search, 1, 0)
        grid.addWidget(searchEdit, 1, 1)

        grid.addWidget(self.listWidget,2,1)
        grid.addWidget(command,3,0)
        grid.addWidget(commandEdit,3,1)

        self.setLayout(grid) 
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Gesture Based Music Player')    
        
        self.show()
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = SpotifyGUI()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
