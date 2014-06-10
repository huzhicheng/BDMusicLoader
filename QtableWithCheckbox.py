#!/usr/bin/env python
#-*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore
from downloadPushbutton import *

class MyButton(QtGui.QPushButton):
    def __init__(self, _id, *args, **kwargs):
        self._id = _id
        QtGui.QPushButton.__init__(self, *args, **kwargs)
        self.setStyleSheet('''QPushButton{background-image:url(./img/downloads.png);width:32px;height:32px;}''')

        self.connect(self, QtCore.SIGNAL("clicked()"), self.emitClicked)

    def emitClicked(self):
        self.emit(QtCore.SIGNAL("myclicked(int)"), self._id)
        



app = QtGui.QApplication([])

w = QtGui.QWidget()

def showMsg(_id):
    QtGui.QMessageBox.information(w, u"信息", u"查看 %d" % _id)
def emitClickedTest():
    w.emit(QtCore.SIGNAL("myclicked(int)"),1)

btn = MyButton(1, u"查看1", w)
w.connect(btn, QtCore.SIGNAL("myclicked(int)"), showMsg)

btn2 = MyButton(2, u"查看2", w)
btn2.move(0, 30)
w.connect(btn2, QtCore.SIGNAL("myclicked(int)"), showMsg)

btn3 = fzDownloadButton(parent=w)
btn3.setText('hahha')
#btn3.move(0,70)

btns = QtGui.QPushButton('HHH')
btns.resize(QtCore.QSize(32,32))
btns.setStyleSheet('''QPushButton{background-image:url(./img/downloads.png);width:32px;height:32px;}''')
btns.move(0,60)
btns.show()
w.show()

app.exec_()
