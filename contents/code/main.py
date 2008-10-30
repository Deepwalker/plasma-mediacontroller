#! /usr/bin/python                                                 

from PyQt4.QtCore import *
from PyQt4.QtGui import * 
from PyQt4 import QtWebKit
from PyKDE4.kdecore import *
from PyKDE4.kdeui import *  
from PyKDE4.plasma import Plasma
import plasma                   
import dbus

class PyMCApplet(plasma.Applet):
    def __init__(self,parent,args=None):
        plasma.Applet.__init__(self,parent)

    def init(self):
        KGlobal.locale().insertCatalog("media")

        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)

        self.dialog = None

        self.bus = dbus.SessionBus()
        self.amarok = self.bus.get_object('org.kde.amarok','/Player')

        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.theme.setContainsMultipleImages(False)
        #self.theme.resize(self.size())

        self.mlayout = QGraphicsLinearLayout(Qt.Horizontal)
        #self.eline = Plasma.LineEdit()
        #self.mlayout.addItem(self.eline)
        self.prev_bt = Plasma.PushButton()
        self.prev_bt.setText('<-')
        self.play_bt = Plasma.PushButton()
        self.play_bt.setText('>')
        self.stop_bt = Plasma.PushButton()
        self.stop_bt.setText('-')
        self.next_bt = Plasma.PushButton()
        self.next_bt.setText('->')

        self.mlayout.addItem(self.prev_bt)
        self.mlayout.addItem(self.play_bt)
        self.mlayout.addItem(self.stop_bt)
        self.mlayout.addItem(self.next_bt)
        self.setLayout(self.mlayout)

        self.connect(self.prev_bt,SIGNAL('clicked()'),self.Prev)
        self.connect(self.play_bt,SIGNAL('clicked()'),self.Play)
        self.connect(self.stop_bt,SIGNAL('clicked()'),self.Stop)
        self.connect(self.next_bt,SIGNAL('clicked()'),self.Next)


    def Prev(self):
        print "Prev it!"
        self.amarok.Prev()

    def Play(self):
        print "Play it!"
        self.amarok.Play()

    def Stop(self):
        print "Stop it!"
        self.amarok.Stop()

    def Next(self):
        print "Next it!"
        self.amarok.Next()

    def shape(self):
        if self.theme.hasElement("hint-square-clock"):
            return plasma.Applet.shape(self)
        path = QPainterPath()
        path.addEllipse(self.boundingRect().adjusted(-2, -2, 2, 2))
        return path


    def constraintsEvent(self, constraints):
        if constraints & Plasma.SizeConstraint:
            self.resize(self.size())

def CreateApplet(parent):
    return PyMCApplet(parent)
