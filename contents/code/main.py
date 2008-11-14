#! /usr/bin/python                                                 

from PyQt4.QtCore import *
from PyQt4.QtGui import * 
from PyQt4 import QtWebKit
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *  
from PyKDE4.plasma import Plasma
import plasma                   
import dbus

class Player:
    def __init__(self,player):
        self.player = player

    def __getattr__(self,name):
        def tryf(*args,**kwargs):
            try:
                amarok = dbus.SessionBus().get_object(self.player,'/Player')
                a=getattr(amarok,name)
                return a(*args,**kwargs)
            except: pass
        return tryf

class MCLabel(Plasma.Label):
    def mousePressEvent(self,event):
        self.emit(SIGNAL('clicked'),event)
    def wheelEvent(self,event):
        print event.delta()
        self.emit(SIGNAL('wheel'),event)

class PyMCApplet(plasma.Applet):
    def __init__(self,parent,args=None):
        plasma.Applet.__init__(self,parent)

    def init(self):
        KGlobal.locale().insertCatalog("media")

        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        self.setMinimumSize(32*8,64)

        self.dialog = None
        self.player = Player('org.kde.amarok')

        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.theme.setContainsMultipleImages(False)

        self.timer = self.startTimer(1000)

        self.mlayout = QGraphicsLinearLayout(Qt.Horizontal)
        self.label = MCLabel()
        self.label.setText('P:0%')

        self.volume = MCLabel()
        self.volume.setText('V:0%')

        self.mlayout.addItem(self.label)
        self.mlayout.addItem(self.volume)
        self.prev_bt = MCLabel()
        self.prev_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-skip-backward.png')
        self.play_bt = MCLabel()
        self.play_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-playback-start.png')
        self.pause_bt = MCLabel()
        self.pause_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-playback-pause.png')
        self.stop_bt = MCLabel()
        self.stop_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-playback-stop.png')
        self.next_bt = MCLabel()
        self.next_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-skip-forward.png')

        self.mlayout.addItem(self.prev_bt)
        self.mlayout.addItem(self.play_bt)
        self.mlayout.addItem(self.pause_bt)
        self.mlayout.addItem(self.stop_bt)
        self.mlayout.addItem(self.next_bt)
        self.setLayout(self.mlayout)

        self.connect(self.prev_bt,SIGNAL('clicked'),self.Prev)
        self.connect(self.play_bt,SIGNAL('clicked'),self.Play)
        self.connect(self.pause_bt,SIGNAL('clicked'),self.Pause)
        self.connect(self.stop_bt,SIGNAL('clicked'),self.Stop)
        self.connect(self.next_bt,SIGNAL('clicked'),self.Next)

        self.connect(self.label,SIGNAL('wheel'),self.change_pos)
        self.connect(self.volume,SIGNAL('wheel'),self.change_vol)

    def redraw_vol(self,vol=None):
        if not vol:
            vol = int(self.player.VolumeGet())
        self.volume.setText("V:%s%%"%str(vol))

    def redraw_pos(self,pos=None):
        if not pos:
            try:
                pos = int(self.player.PositionGet())
                len = int(self.player.GetMetadata()['mtime'])
                pos = pos*100/len
            except:
                pos=0
        self.label.setText("P:%s%%"%str(pos))

    def timerEvent(self,ev):
        self.redraw_pos()
        self.redraw_vol()

    def change_vol(self,event):
        delta = event.delta()/120
        vol = self.player.VolumeGet()
        vol += 5*delta
        self.player.VolumeSet(vol)
        self.redraw_vol(vol=vol)

    def change_pos(self,event):
        delta = event.delta()/120
        pos = self.player.PositionGet()
        len = int(self.player.GetMetadata()['mtime'])
        pos += len/100*5*delta
        self.player.PositionSet(pos)
        self.redraw_pos(pos=pos/len)

    def Prev(self):
        self.player.Prev()

    def Play(self):
        self.player.Play()

    def Pause(self):
        self.player.Pause()

    def Stop(self):
        self.player.Stop()

    def Next(self):
        self.player.Next()

    def constraintsEvent(self, constraints):
        if constraints & Plasma.SizeConstraint:
            self.resize(self.size())

def CreateApplet(parent):
    return PyMCApplet(parent)
