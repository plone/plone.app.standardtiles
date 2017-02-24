# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


version = '2.1.0'


setup(
    name='plone.app.standardtiles',
    version=version,
    description='Tiles for plone.app.blocks page composition',
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 5.0',
        'Framework :: Plone :: 5.1',
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
        'plone.app.blocks',
        'plone.app.contentlisting',
        'plone.app.dexterity',
        'plone.app.discussion',
        'plone.app.registry',
        'plone.app.tiles',
        'plone.formwidget.multifile',
        'plone.formwidget.querystring',
        'plone.subrequest',
        'plone.tiles>=1.8.0.dev0',
        'Products.CMFPlone>=5.0.4',
        'requests',
        'setuptools',
        'z3c.form',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            'plone.app.dexterity',
            'plone.app.widgets',
            'lxml',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
