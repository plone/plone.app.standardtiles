# -*- coding: utf-8 -*-
from plone.tiles import Tile


class TableOfContentsTile(Tile):
    """A Table of contents tile."""

    def __call__(self):
        return self.index()

    @property
    def available(self):
        return True
