Changelog
=========

2.0.0 (unreleased)
------------------

- use safe html transform for raw tile output
  [vangheem]

- Handle unicode error when applying filters on raw tile
  [vangheem]

- When calling ``@@plone.app.standardtiles.contentlisting`` directly without having it configured via a form, get the ``query`` and ``sort_on`` values from it's default factories.
  [thet]

- Move tile registrations from ``media.zcml`` to more appropriate places:
  - ``existingcontent``, ``rss`` and ``rawhtml`` tiles into ``content.zcml``,
  - ``navigation`` and ``sitemap`` tiles in to ``layout.zcml``.
  [thet]

- Take permissions and visibility of viewlets in tiles into account.
  [jensens]

- Drop Plone 4 fallback for language selector
  [jensens]

- Housekeeping and minor cleanup.
  [jensens]

- Moved KeywordTile and TableOfContentsTile to common.py.
  [jensens]

- Simplify basic viewlet proxy tiles.
  [jensens]

- Removed support for Plone 4.3. For Plone 4.3 support, please use
  plone.app.standardtiles < 2.0.
  [datakurre, jensens, thet]

- Enable coveralls and code analysis.
  [gforcada]

- Adapt travis to all other mosaic realted packages.
  [gforcada]

1.0 (2016-04-11)
----------------

- Nothing changed.


1.0b5 (2016-04-06)
------------------

- Add registry configuration to specify additional content listing views
  [vangheem]

- Add limit to contentlisting
  [martior]

- Fix embed tile to ram.cache oembed code by URL
  [datakurre]

- Fix permission definitions to not use public permissions for add
  [vangheem]

- Fix Event to work with summary_view content listing tile
  [vangheem]

- Fix listings not including /view on urls
  [vangheem]

- Add better error handling in summary_view
  [vangheem]

- Fix getting lead image
  [vangheem]

- Fix to not transform rawhtml output if rendered within mosaic layouteditor
  [vangheem]


1.0b4 (2015-10-04)
------------------

- Change navigation tile to not use deprecated defaults from portal_properties
  [datakurre]

- Add socialtags tile
  [vangheem]

- Fix sitemap tile to read correct setting on Plone 5
  [datakurre]


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
