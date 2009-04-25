#! /usr/bin/python                                                 

from PyQt4.QtCore import *
from PyQt4.QtGui import * 
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *  
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript as plasma
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

class MCMeter(Plasma.Meter):
    def mousePressEvent(self,event):
        self.emit(SIGNAL('clicked'),event)

    def wheelEvent(self,event):
        print event.delta()
        self.emit(SIGNAL('wheel'),event)

class MCLabel(Plasma.Label):
    def setText(self,text):
        width = QFontMetrics(self.font()).width(text)
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)
        Plasma.Label.setText(self,text)
        
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
        #self.setMaximumWidth(32*7)

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

        #self.mlayout.addItem(self.label)
        #self.mlayout.addItem(self.volume)

        self.pos_meter=MCMeter()
        self.pos_meter.setMeterType(Plasma.Meter.BarMeterVertical)
        self.vol_meter=MCMeter()
        self.vol_meter.setMeterType(Plasma.Meter.BarMeterVertical)
        self.mlayout.addItem(self.pos_meter)
        self.mlayout.addItem(self.vol_meter)
        self.pos_meter.setMaximumWidth(10)
        self.pos_meter.setMaximumHeight(32)
        self.vol_meter.setMaximumWidth(32)
        self.vol_meter.setMaximumHeight(10)
        
        btns=[('prev_bt','media-skip-backward.png',self.Prev),
            ('play_bt','media-playback-start.png',self.Play),
            ('pause_bt','media-playback-pause.png',self.Pause),
            ('stop_bt','media-playback-stop.png',self.Stop),
            ('next_bt','media-skip-forward.png',self.Next)
        ]

        for bt in btns:
            setattr(self,bt[0],MCLabel())
            but=getattr(self,bt[0])
            but.setImage('/usr/share/icons/oxygen/32x32/actions/'+bt[1])
            self.connect(but,SIGNAL('clicked'),bt[2])
            self.mlayout.addItem(but)
            but.setMinimumWidth(32)
            but.setMaximumWidth(32)
            but.setMaximumHeight(32)

        self.setLayout(self.mlayout)

        self.connect(self.pos_meter,SIGNAL('wheel'),self.change_pos)
        self.connect(self.vol_meter,SIGNAL('wheel'),self.change_vol)

        self.connect(self.label,SIGNAL('wheel'),self.change_pos)
        self.connect(self.volume,SIGNAL('wheel'),self.change_vol)

    def redraw_vol(self,vol=None):
        if not vol:
            try:
                vol = int(self.player.VolumeGet())
            except:
                vol = 0
        self.volume.setText("V:%s%%"%str(vol))
        self.vol_meter.setValue(vol)

    def redraw_pos(self,pos=None):
        if not pos:
            try:
                pos = int(self.player.PositionGet())
                len = int(self.player.GetMetadata()['mtime'])
                pos = pos*100/len
            except:
                pos=0
        self.label.setText("P:%s%%"%str(pos))
        self.pos_meter.setValue(pos)

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
