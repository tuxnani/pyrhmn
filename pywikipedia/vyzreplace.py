#!/usr/bin/python
# -*- coding: utf-8  -*-
"""this is Vyzbot.
"""
import wikipedia, pagegenerators, catlib
import sys, touch, replace, string, category, login, os

s=wikipedia.Site('te')
login.LoginManager('rhmn_288', False, s) #replace xxxxx with bot's password

reptext=[(u'మధ్యపానం', u'మద్యపానం')]
exceptions= []
acceptall = True
start='!'
namespace = None
myPagegen=pagegenerators.AllpagesPageGenerator(start, namespace)
'''
# in long comments this is another variation to get pages in a specific category
reptext=[(u'Wikipedia basic information', u'వికీపీడియా మౌళిక సమాచారము'),]
oldCatTitle=u'Wikipedia basic information'
newCatTitle=u'వికీపీడియా మౌళిక సమాచారము'
exceptions= []
acceptall = True
start='!'
namespace = u'Category'
inPlace = False
myPagegen=pagegenerators.CategorizedPageGenerator(oldCatTitle, recurse = False)
'''                                                  
vyzrep=replace.ReplaceRobot(myPagegen, reptext, exceptions,
                            acceptall)
vyzrep.run()

wikipedia.stopme()
