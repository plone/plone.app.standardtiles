# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '1.0b4'


setup(
    name='plone.app.standardtiles',
    version=version,
    description="Standard tiles for Plone Blocks page composition",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.rst").read()),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.0',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
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
        'requests',
        'plone.app.dexterity',
        'plone.app.tiles',
        'plone.app.discussion',
        'plone.app.contentlisting',
        'plone.app.imaging',
        'plone.formwidget.querystring',
        'plone.formwidget.multifile',
        'plone.app.registry',
        'z3c.form',
    ],
    extras_require={
        'test': [
            'plone.app.blocks',
            'plone.app.testing',
            'plone.app.dexterity',
            'plone.app.widgets',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
