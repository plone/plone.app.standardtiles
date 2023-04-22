Changelog
=========

3.0.1 (2023-04-22)
------------------

- Fix broken CMFDynamicViewFTI import.
  [thet]

- Fix byline viewlet name
  [frapell]


3.0.0 (2022-12-05)
------------------

- Added linkintegrity for html and existingcontent tile.
  Code is ported form version 2.5.0, and is only active when
  plone.app.blocks version 6.0.2 or higher is used.
  [petschki]


3.0.0b1 (2022-06-24)
--------------------

- Fix ``isDefaultPage`` import which was moved to ``plone.base.defaultpage``
  [petschki]

- Cleanup and fix ExistingContentTile in 5.2
  [gotcha, Mychae1]


3.0.0a2 (2022-04-01)
--------------------

- Fixed KeyError ``results`` in tabular view.  Should have been ``batch``.
  Fixes `issue 122 <https://github.com/plone/plone.app.standardtiles/issues/122>`_.
  [maurits]


3.0.0a1 (2022-03-23)
--------------------

- Fix showing private content while editing a tile.
  Fixes `issue 100 <https://github.com/plone/plone.app.standardtiles/issues/100>`_.
  [maurits]

- Fix tests to respect BS5 Markup of Plone 6.
  [jensens]

- Fix membertools tile
  [agitator]

- Breaking: Drop code marked as deprecated for 3.0.
  This includes ``plone.app.standardtiles.image``.
  If anyone for any reason has still these long deprecated tile around, custom upgrades are needed.
  [jensens]

- Manual code cleanup.
  [jensens]

- Breaking: Drop Support for Python 2.7 and Plone 5.
  [jensens]

- Hide uninstall profile from install view.
  [jensens]


2.4.0 (2021-03-24)
------------------

- Content listing: Allow to use collection query parameters from context.
  Content listing: Include query parameters from request.
  Content listing: Add "tile_class".
  Batching support
  Drop support for Plone 5.0.x - no get_top_request available
  [agitator]

- Upgrade tests to github actions
  [djay]

- CI with Github actions: Python 2 / Python 3 and os version
  [ksuess]

- rss tile: expose published date
  [ksuess]

- update link to plone coredev docs in readme
  [spereverde]

- coveralls and github actions workflow
  [ksuess]

2.3.2 (2019-12-05)
------------------

- Added Alt attribute to summary view, needed for accessibility
  [rnunez]

- Py3 fix for existingcontent tile
  [petschki]

- Add uninstall profile.
  [hvelarde]

- Remove installation of plone.app.widgets default profile in tests.
  In Plone 5.0/5.1 with plone.app.widgets >= 2.0, the profile is only a dummy profile for BBB.
  In Plone 5.2 it will be removed.
  [jensens]

- Show event details for all content types which provides start or end fields.
  [MrTango]

- Fix tests in Plone 5.2
  [MrTango]

- Add custom_view also in existingcontent tile.
  [cekk]

- Fix existingcontent tile form labels
  [pnicolli]


2.3.1 (2018-06-07)
------------------

- Fix tests around deprecated raw html tile and use htmltile.
  [jensens]

- Fix #87: Existing Content Tile broken when used in multilingual sites.
  Widget is now similar to related items behavior.
  [jensens]

- Fix TileCommentForm to prefix forms with just 'form' to fix compatibility
  with plone.app.discussion javascripts
  [datakurre]


2.3.0 (2018-04-13)
------------------

New features:

- Moved dependency on ``plone.formwidget.multifile`` used for deprecated Attachement-Tile to an extra ``attachment`` in ``setup.py``.
  [jensens]


Bug fixes:

- Fix tests of Boolean widget:
  Remove checks of implementation details of the widget.
  This does not belong into this tests.
  It changed between 5.0 and 5.1 after some fixes.
  [jensens]

- Fix issue #79,
  where a test failed with Plone 5.1, because a tile in a test had no ``__name__``.
  [jensens]

- Changed title of existing content tile from h1 to h2
  [agitator]

- Fix issue where image field tile template registration did not apply for
  fields on non-default fieldset
  [datakurre]

- Imports are Python3 compatible
  [b4oshany]

- Fix issue where field tile for title and description fields rendered
  with double <html><body>-wrapping
  [datakurre]

2.2.0 (2017-06-09)
------------------

New features:

- Add "show_image", "show_text", "show_comments" and "tile_class" additional
  fields to existing content tile.
  [cekk]

Bug fixes:

- Fix non ASCII HTML tile content
  [tomgross]

- Add better descriptions for tiles.
  [cguardia]

- Fix noembed endpoint url to get valid JSON response.
  [tmassman]


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
