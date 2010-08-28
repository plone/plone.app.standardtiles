from zope import schema

from zope.component import adapter
from zope.interface import implementsOnly, implementer

from z3c.form import interfaces
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser import widget

from plone.directives import form, dexterity


class IFunkyWidget(interfaces.IWidget):
    """Funky, useless widget for testing
    """


class FunkyWidget(widget.HTMLTextInputWidget, Widget):
    """Funky widget implementation.
    """
    implementsOnly(IFunkyWidget)

    klass = u'funky-widget'
    value = u''

    def update(self):
        super(FunkyWidget, self).update()
        widget.addFieldClass(self)


@adapter(schema.interfaces.IField, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def FunkyFieldWidget(field, request):
    """IFieldWidget factory for FunkyWidget.
    """
    return FieldWidget(field, FunkyWidget(request))


class ITestType1(form.Schema):

    test_text = schema.TextLine(
        title = u"Test text field"
    )

    test_int = schema.Int(
        title = u"Integer test field"
    )

    test_bool = schema.Bool(
        title = u"Boolean test field"
    )

    form.widget(
        funky = FunkyFieldWidget
    )
    funky = schema.TextLine(
        title = u"Test funky field"
    )

    dexterity.read_permission(topsecret='cmf.ModifyPortalContent')
    dexterity.write_permission(topsecret='cmf.ManagePortal')
    topsecret =  schema.TextLine(
        title = u"Top secret field"
    )
