from zope import schema
from plone.directives import form


class ITestType1(form.Schema):

    textfield = schema.TextLine(
        title = u"Test text field"
    )

    intfield = schema.Int(
        title = u"Integer test field"
    )

    boolfield = schema.Bool(
        title = u"Boolean test field"
    )
