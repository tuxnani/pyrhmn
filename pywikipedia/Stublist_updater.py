#!/usr/bin/python
# -*- coding: utf-8  -*-
#Scipt to update the list in వికీపీడియా:మొలకల జాబితా
 
import wikipedia, pagegenerators, catlib, config, codecs
 
# Replace the contents in the page 'pageTitle' with data 'pageData' 
logstublist.write(u'{{మొలకల జాబితా శీర్షిక}}\r\n') 
# and add the comment 'comment'
def writeData(pageTitle, pageData, comment):
  page = wikipedia.Page(wikipedia.getSite(), pageTitle)
  try:
    # Load the page's text from the wiki
    data = page.get()
  except wikipedia.NoPage:
    data = u''
  data = pageData
  try:
    page.put(data, comment = comment)
  except wikipedia.EditConflict:
    wikipedia.output(u'Skipping %s because of edit conflict' % (page.title()))
  except wikipedia.SpamfilterError, url:
    wikipedia.output(u'Cannot change %s because of blacklist entry %s' % (page.title(), url))
 
 
 
comment = u'బాటు: మొలకల జాబితా తాజకరించా'
disambig = u"{{అయోమయ నివృత్తి}}"
stublistPageTitle = u"వికీపీడియా:మొలకల జాబితా"
 
#opening stublist log and writing header
logstublist = codecs.open('stublist.log', encoding='utf-8', mode='wb') 
logstublist.write(u'{{మొలకల జాబితా శీర్షిక}}\r\n') 
 
#opening stublist wikipage and generating linked page links
stublistPage = wikipedia.Page(wikipedia.getSite(), stublistPageTitle)
gen = pagegenerators.LinkedPageGenerator(stublistPage)
preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 500)
 
for page in preloadingGen:
    try:
      # Load the page's text from the wiki
      pageData = page.get()
      if not page.canBeEdited():
         wikipedia.output(u'Skipping locked page %s' % page.title())
         continue
    except wikipedia.NoPage:
       wikipedia.output(u'Page %s not found' % page.title())
       continue
    except wikipedia.IsRedirectPage:
       wikipedia.output(u'Page %s is redirect page' % page.title())
       continue
    # check for disambig template and skip the page if it is disambig page
    if pageData.find(disambig) >= 0: 
       wikipedia.output(u'Page %s is Disambiguation Page' % page.title())
       continue
 
    # checking the page length and write to log if it is stub
    if len(pageData) < 2048:
           logstublist.write(u'# [[' + page.title() + u']]' + u'\r\n')
 
 
# close stublist log handle
logstublist.close()
 
 
# upload the stublist to tewiki
logfilestublist = codecs.open('stublist.log', encoding='utf-8', mode='rb')
writeData(u'వికీపీడియా:మొలకల జాబితా', logfilestublist.read(), comment)
logfilestublist.close()
