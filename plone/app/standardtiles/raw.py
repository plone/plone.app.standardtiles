# -*- coding: utf-8 -*-
from plone.app.standardtiles.html import IHTMLTile, HTMLTile
from zope.deprecation import deprecated

IRawHTMLTile = IHTMLTile
deprecated(IRawHTMLTile, 'Use IHTMLTile instead of IRawHTMLTile')
RawHTMLTile = HTMLTile
deprecated(RawHTMLTile, 'Use HTMLTile instead of RawHTMLTile')
