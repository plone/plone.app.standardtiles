# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


version = '1.0a1.dev0'

setup(name='plone.app.standardtiles',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rob Gietema',
      author_email='rob@fourdigits.nl',
      url='http://plone.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'lxml',
          'plone.app.dexterity[grok,relations]',
#         'plone.app.deco',
          'plone.app.tiles',
          'plone.app.discussion',
          'plone.app.contentlisting',
#         'plone.app.imagetile',
#         'plone.app.mediarepository',
          'plone.formwidget.contenttree',
          'plone.formwidget.querystring',
          'plone.formwidget.multifile',
          'plone.directives.form',
          'plone.directives.tiles',
          'plone.app.intid',
          'plone.app.registry',
          'z3c.relationfield',
          'z3c.form',
          'five.grok',
      ],
      extras_require={
          'test': [
              'interlude',
              'plone.app.blocks',
              'plone.app.testing',
              'plone.app.dexterity',
              ],
          },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
