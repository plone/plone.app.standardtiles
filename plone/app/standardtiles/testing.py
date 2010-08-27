from zope import schema

from zope.component import adapter
from zope.interface import implementsOnly, implementer

from z3c.form import interfaces
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser import widget

from plone.directives import form


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

    textfield = schema.TextLine(
        title = u"Test text field"
    )

    intfield = schema.Int(
        title = u"Integer test field"
    )

    boolfield = schema.Bool(
        title = u"Boolean test field"
    )

    form.widget(
        funkyfield = FunkyFieldWidget
    )
    funkyfield = schema.TextLine(
        title = u"Test funky field"
    )
