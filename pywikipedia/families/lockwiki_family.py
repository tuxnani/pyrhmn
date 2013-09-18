# -*- coding: utf-8  -*-

__version__ = '$Id: lockwiki_family.py 10828 2012-12-23 20:59:00Z drtrigon $'

import family

# The locksmithwiki family

class Family(family.Family):
    def __init__(self):
        family.Family.__init__(self)
        self.name = 'lockwiki'
        self.langs = {
            'en': 'www.locksmithwiki.com',
        }
        self.namespaces[4] = {
            '_default': [u'Locksmith Wiki Knowledge Base',
                self.namespaces[4]['_default']], # REQUIRED
        }
        self.namespaces[4] = {
            '_default': [u'Locksmith Wiki Knowledge Base talk',
                self.namespaces[5]['_default']], # REQUIRED
        }

    def scriptpath(self, code):
        return '/lockwiki'

    def version(self, code):
        return '1.15.1'

    def nicepath(self, code):
        return "%s/" % self.path(self, code)
