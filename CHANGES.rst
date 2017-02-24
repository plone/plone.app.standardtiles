Changelog
=========

2.1.0 (2017-02-24)
------------------

New features:

- Added title and description fields content listing tile,
  will show up on tile if filled in.
  [agitator]

- Add plone.app.standardtiles.leadimage for rendering lead image from
  lead image behavior directly (without viewlet indirection)
  [datakurre]

Bug fixes:

- Fix setup dependencies: do not depend on plone.app.imaging, it is not needed.
  This removes an transient dependency on Archetypes.
  [jensens]

- Fix issues where tiles didn't properly render when traversed from a view context
  [datakurre]

- Minor cleanup in contentlisting and existingcontent.
  [jensens]

- Fix byline tile to base on respective Plone 5 viewlet
  (but note that it only renders for anonymous users when they are allowed
  to view it)
  [datakurre]

- Fix issue where viewletmanagers were rendered in parent context instead of
  object context
  [datakurre]

- Fix viewletmanager and portlet tiles to render like on default views on ESI
  when rendered directly against contentish context (ESI doesn't have
  knowledge of parent request like subrequest based composition has)
  [datakurre]

- Fix discussion tile to properly post to tile URL and redirect to context URL;
  Add explicit CSRF-protection to support rendering as ESI tile
  [datakurre]


2.0.0 (2016-12-13)
------------------

Breaking changes:

- Removed support for Plone 4.3. For Plone 4.3 support, please use
  plone.app.standardtiles < 2.0.
  [datakurre, jensens, thet]

- Rename rawhtml to html, deprecate rawhtml tile and make it normal
  tile (not persisted into annotation)
  [vangheem]

- Mark `plone.app.standardtiles.image` and `plone.app.standardtiles.attachment`
  as deprecated.
  [vangheem]

- Remove deprecated skip-links tile, because there's no such viewlet feature on
  Plone 5
  [datakurre]

- Drop Plone 4 fallback for language selector
  [jensens]

New features:

- Added a new raw embed tile
  [agitator]

- Use safe html transform for html (was raw) tile output
  [vangheem]

- Be able to show/hide title/description with existing content tile
  [vangheem]

Bug fixes:

- Fix existing content tile to work with collections.
  This fixes https://github.com/plone/plone.app.mosaic/issues/202
  [vangheem]

- Validate selected content for existing content is not the current context
  the tile is being rendered against.
  [vangheem]

- Fix batching urls on existing content tiles
  [vangheem]

- When calling ``@@plone.app.standardtiles.contentlisting`` directly without
  having it configured via a form, get the ``query`` and ``sort_on`` values
  from it's default factories.
  [thet]

- Change initial limit for listing tile to 100 instead of 1000
  [vangheem]

- Handle unicode error when applying filters on html (was raw) tile
  [vangheem]

- Take permissions and visibility of viewlets in tiles into account.
  [jensens]

- Replace misleading warnings on missing viewlet tiles with silent
  debug level logging
  [datakurre]

- Fix issue where layout tiles failed on portlet manager context
  [datakurre, agitator]

- Fix lockinfo to not log Unauthorized-errors by protecting its registration
  only with zope2.View, but render it empty without cmf.ModifyPortalContent
  [datakurre]

- Fix portlet tile (broken by regression)
  [datakurre]

- Fix issue where existing content did not render on edit form and
  logged error when target content object was deleted
  [datakurre]

- Fix recursion loop in existingcontent tile (#48)
  [tomgross]

Refactoring:

- Move tile registrations from ``media.zcml`` to more appropriate places:
  - ``existingcontent``, ``rss`` and ``rawhtml`` tiles into ``content.zcml``,
  - ``navigation`` and ``sitemap`` tiles in to ``layout.zcml``.
  [thet]

- Housekeeping and minor cleanup.
  [jensens]

- Moved KeywordTile and TableOfContentsTile to common.py.
  [jensens]

- Simplify basic viewlet proxy tiles.
  [jensens]

- Enable coveralls and code analysis.
  [gforcada]

- Adapt travis to all other mosaic realted packages.
  [gforcada]

- Remove unused function.
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
  [datakurre]

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
