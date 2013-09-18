# -*- coding: utf-8  -*-

__version__ = '$Id: incubator_family.py 11124 2013-02-25 12:13:51Z xqt $'

import family

# The Wikimedia Incubator family

class Family(family.WikimediaFamily):
    def __init__(self):
        super(Family, self).__init__()
        self.name = 'incubator'
        self.langs = {
            'incubator': 'incubator.wikimedia.org',
        }
        self.namespaces[4] = {
            '_default': [u'Incubator', u'I', self.namespaces[4]['_default']],
        }
        self.namespaces[5] = {
            '_default': [u'Incubator talk', self.namespaces[5]['_default']],
        }
        self.namespaces[1198] = {
            '_default': u'Translations',
        }
        self.namespaces[1199] = {
            '_default': u'Translations talk',
        }
        self.interwiki_forward = 'wikipedia'
