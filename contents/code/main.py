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
    def __getattr__(self,name):
        #print 'point %s'%name
        def tryf():
            try:
                amarok = dbus.SessionBus().get_object('org.kde.amarok','/Player')
                a=getattr(amarok,name)
                return a()
            except: pass
        return tryf

class MCLabel(Plasma.Label):
    def mousePressEvent(self,event):
        self.emit(SIGNAL('clicked'),event)

class PyMCApplet(plasma.Applet):
    def __init__(self,parent,args=None):
        plasma.Applet.__init__(self,parent)

    def init(self):
        KGlobal.locale().insertCatalog("media")

        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        self.setMinimumSize(32*9,64)

        self.dialog = None
        self.player = Player()

        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.theme.setContainsMultipleImages(False)
        #self.theme.resize(self.size())

        self.timer = self.startTimer(1000)

        self.mlayout = QGraphicsLinearLayout(Qt.Horizontal)
        self.label = MCLabel()
        self.label.setText('40%')

        self.mlayout.addItem(self.label)
        self.prev_bt = MCLabel()
        self.prev_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-skip-backward.png')
        self.play_bt = MCLabel()
        self.play_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-playback-start.png')
        self.stop_bt = MCLabel()
        self.stop_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-playback-stop.png')
        self.next_bt = MCLabel()
        self.next_bt.setImage('/usr/share/icons/oxygen/32x32/actions/media-skip-forward.png')

        self.mlayout.addItem(self.prev_bt)
        self.mlayout.addItem(self.play_bt)
        self.mlayout.addItem(self.stop_bt)
        self.mlayout.addItem(self.next_bt)
        self.setLayout(self.mlayout)

        self.connect(self.prev_bt,SIGNAL('clicked'),self.Prev)
        self.connect(self.play_bt,SIGNAL('clicked'),self.Play)
        self.connect(self.stop_bt,SIGNAL('clicked'),self.Stop)
        self.connect(self.next_bt,SIGNAL('clicked'),self.Next)

        #self.connect(self.label,SIGNAL('clicked'),self.l_clicked)

    def timerEvent(self,ev):
        try:
            pos = int(self.player.PositionGet())
            len = int(self.player.GetMetadata()['mtime'])
            self.label.setText(str(pos*100/len)+'%')
        except: pass

    def Prev(self):
        self.player.Prev()

    def Play(self):
        #st = self.player.
        self.player.Play()

    def Stop(self):
        self.player.Stop()

    def Next(self):
        self.player.Next()

#    def shape(self):
#        path = QPainterPath()
#        path.addEllipse(self.boundingRect().adjusted(-2, -2, 2, 2))
#        return path
#
    def constraintsEvent(self, constraints):
        if constraints & Plasma.SizeConstraint:
            self.resize(self.size())

def CreateApplet(parent):
    return PyMCApplet(parent)
