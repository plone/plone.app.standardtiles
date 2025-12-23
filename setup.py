from setuptools import setup


version = "4.0.0a1"


setup(
    name="plone.app.standardtiles",
    version=version,
    description="Tiles for plone.app.blocks page composition",
    long_description=(open("README.rst").read() + "\n" + open("CHANGES.rst").read()),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.2",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="tiles content plone",
    author="Rob Gietema",
    author_email="rob@fourdigits.nl",
    url="https://github.com/plone/plone.app.standardtiles",
    license="GPL",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "plone.api>=2.3.0",
        "plone.app.blocks",
        "plone.app.tiles>=4.0.0",
        "plone.base",
        "plone.subrequest",
        "plone.tiles>=1.8.0",
        "requests",
        "setuptools",
        "Zope",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.app.dexterity",
            "plone.app.discussion",
            "lxml",
        ],
        "attachment": [
            "plone.formwidget.multifile>=2.0",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
