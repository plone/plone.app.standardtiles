from setuptools import setup, find_packages
import os

version = '0.1'

setup(
    name='plone.app.standardtiles',
    version=version,
    description="",
    long_description=open("README.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='',
    author='Rob Gietema',
    author_email='rob@fourdigits.nl',
    url='https://github.com/plone/plone.app.standardtiles',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.schema',
        'zope.component',
        'zope.i18nmessageid',
        'plone.autoform',
        'plone.supermodel',
        'plone.namedfile',
        'plone.tiles',
        'plone.app.toolbar',
        'plone.app.tiles',
      ],
      extras_require={
          'test': [
              'zope.configuration',
              'plone.app.testing',
              'robotsuite',
              'robotframework-selenium2library',
              'plone.act',
              ],
          },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
