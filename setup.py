# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '2.4.3'


setup(
    name='plone.app.standardtiles',
    version=version,
    description='Tiles for plone.app.blocks page composition',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 5.1',
        'Framework :: Plone :: 5.2',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='tiles content plone',
    author='Rob Gietema',
    author_email='rob@fourdigits.nl',
    url='https://plone.org',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.app.blocks',
        'plone.app.contentlisting',
        'plone.app.dexterity',
        'plone.app.discussion',
        'plone.app.registry',
        'plone.app.tiles>=3.1.2',
        'plone.subrequest',
        'plone.tiles>=1.8.0',
        'plone.batching>=1.1.7',
        'Products.CMFPlone>=5.1',
        'requests',
        'setuptools',
        'six',
        'z3c.form',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.dexterity',
            'plone.app.discussion',
            'plone.app.widgets',
            'lxml',
        ],
        'attachment': [
            'plone.formwidget.multifile>=2.0',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
