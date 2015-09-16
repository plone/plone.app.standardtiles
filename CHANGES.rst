Changelog
=========

1.0b3 (2015-09-16)
------------------

- Fix to apply output filters for rawhtml tile
  [datakurre]
- Fix encoding issue when rendering existing content tile
  [datakurre]

1.0b2 (2015-09-16)
------------------

- Add ``plone.app.standardtiles.rawhtml`` tile
  [vangheem]
- Change image tile to use radio widget for image scale selection
  [datakurre]
- Fix default values for rendering the content listing tile
  [vangheem]

1.0b1 (2015-06-08)
------------------

- Fix field tile backwards compatibility with plone.app.blocks < 2.1.1
  [Asko Soukka]

1.0a4 (2015-06-06)
------------------

- Remove text, calendar and configlets tiles
  [datakurre]
- Add scripts, stylesheets and toolbar tiles for Plone 5
  [datakurre]
- Add dublincore layout tile
  [datakurre]
- Add title field for image tile
  [datakurre]
- Refactor most layout tiles to re-use viewlets' for shared codebase
  [datakurre]
- Fix issue where byline tile was broken on Plone 5
  [datakurre]
- Fix issue where field tile ignored widget directive
  [datakurre]
- Fix profile version (no upgrade step; upgrade by reinstall)
  [datakurre]

1.0a3 (2015-05-27)
------------------

- Fix import error on Plone 4 without plone.app.contenttypes
  [datakurre]

1.0a2 (2015-05-27)
------------------

- Fix image tile to only set image width to allow proportional scaling within
  smaller than width columns
  [datakurre]

1.0a1 (2015-05-25)
------------------

- First alpha release.
