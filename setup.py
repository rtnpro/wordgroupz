#!/usr/bin/env python
"""wordgroupz"""
from distutils.core import setup
#from DistUtilsExtra.command import *

doclines = __doc__.split("\n")
setup(name='wordgroupz',
      version='0.3b',
      description=doclines[0],
      long_description = "\n".join(doclines[:]),
      platforms = ["Linux"],
      author='Ratnadeep Debnath',
      author_email='rtnpro@gmail.com',
      url='http://gitorious.org/wordgroupz/wordgroupz',
      license = 'http://www.gnu.org/copyleft/gpl.html',
      data_files=[('/usr/share/applications',['wordgroupz.desktop']),
          ('/usr/bin',['wordgroupz']),
          ('/usr/share/pixmaps',['icons/wordgroupz.png']),
          ('/usr/share/wordgroupz',['wordgroupz.glade','wordgroupz.py','nltk_wordnet.py', 'games.py', 'games.glade', 'get_fields.py', 'html2text.py', 'wiktionary_header', 'espeak.py'])],

 #       cmdclass = { "build" : build_extra.build_extra,
 #                    "build_i18n" : build_i18n.build_i18n },
      )
