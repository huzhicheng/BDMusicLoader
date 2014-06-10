# -*- coding:utf-8 -*-
'''
Created on 2014��3��6��

@author: huzhicheng
'''
from distutils.core import setup
import py2exe
import sys 

 
#this allows to run it with a simple double click.
sys.argv.append('py2exe')
 
py2exe_options = {
        "includes": ["sip"],
        "dll_excludes": ["MSVCP90.dll",],
        "compressed": 1,
        "optimize": 2,
        "ascii": 0,
        "bundle_files": 1,
        }
 
setup(
      name = 'baidumusicdownloader',
      version = '1.0',
      windows=[{  
        'script': 'baidumusicdownloader.py', 
        "icon_resources": [(1, 'Musicico.ico')  ]}],
      zipfile = None,
      options = {'py2exe': py2exe_options}
      )