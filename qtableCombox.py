#-*- coding:utf-8 -*-

'''
Created on 

@author: huzhicheng
'''


#!/usr/bin/env python
#coding=utf-8

from PyQt4.QtGui  import *
from PyQt4.QtCore import *  

class DBComboBoxDelegate(QItemDelegate):

  def __init__(self, comboModel, parent=None):
    QItemDelegate.__init__(self, parent)
    self.comboModel = comboModel

  def __createComboView(self, parent):
    view = QTableView(parent)
    view.setModel(self.comboModel)
    view.setAutoScroll(False)
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    view.setSelectionMode(QAbstractItemView.SingleSelection)
    view.setSelectionBehavior(QAbstractItemView.SelectRows)
    view.resizeColumnsToContents()
    view.resizeRowsToContents()
    view.setMinimumWidth(view.horizontalHeader().length())
    return view

  def createEditor(self, parent, option, index):
    combo = QComboBox(parent)
    #!! The important part: First set the model, then the view on the combo box
    combo.setModel(self.comboModel)
    #combo.setModelColumn(1)
    combo.setView(self.__createComboView(parent))
    return combo

  def setEditorData(self, editor, index):
    value = index.model().data(index, Qt.EditRole).toString()
    editor.setCurrentIndex(editor.findText(value))

  def setModelData(self, editor, model, index):
    if editor.currentIndex() >= 0:
      realidx = editor.model().index(editor.currentIndex(), 0) #确保取第一列的值
      value = editor.model().data(realidx)
      model.setData(index, value, Qt.EditRole)

###############################################################################

if __name__ == '__main__':
  import sys
  app = QApplication(sys.argv)

  table = QTableView()

  comboModel = QStandardItemModel(4, 2, table)
  comboModel.setHorizontalHeaderLabels(['Name', 'Description'])
  comboModel.setData(comboModel.index(0, 0, QModelIndex()), QVariant(u'树袋熊'))
  comboModel.setData(comboModel.index(0, 1, QModelIndex()), QVariant(u'生活在树上的熊'))
  comboModel.setData(comboModel.index(1, 0, QModelIndex()), QVariant(u'松鼠'))
  comboModel.setData(comboModel.index(1, 1, QModelIndex()), QVariant(u'可爱的松树精灵'))
  comboModel.setData(comboModel.index(2, 0, QModelIndex()), QVariant(u'大眼猴'))
  comboModel.setData(comboModel.index(2, 1, QModelIndex()), QVariant(u'这猴眼睛真大'))
  comboModel.setData(comboModel.index(3, 0, QModelIndex()), QVariant(u'猫头鹰'))
  comboModel.setData(comboModel.index(3, 1, QModelIndex()), QVariant(u'夜的精灵正站在树枝上'))

  model = QStandardItemModel(2, 3, table)
  model.setHorizontalHeaderLabels(['Name', 'Height', 'Weight'])
  model.setData(model.index(0, 0, QModelIndex()), QVariant(u'松鼠'))
  model.setData(model.index(0, 1, QModelIndex()), QVariant(u'80cm'))
  model.setData(model.index(0, 2, QModelIndex()), QVariant(u'12Kg'))

  table.setModel(model)
  table.setItemDelegateForColumn(0, DBComboBoxDelegate(comboModel, table))
  table.horizontalHeader().setStretchLastSection(True)
  table.setGeometry(80, 20, 400, 300)
  table.setWindowTitle('Grid + Combo Testing')
  table.show()

  sys.exit(app.exec_())
