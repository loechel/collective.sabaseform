# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

from collective.saversioning import VersionedMeta, VersionedListener

from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.globalrequest import getRequest

from five import grok
from z3c.form import button
from plone.directives import form
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.statusmessages.interfaces import IStatusMessage

import zope.i18nmessageid
MessageFactory = zope.i18nmessageid.MessageFactory('collective.sabaseform')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

BaseORM = declarative_base()

VersionedBaseORM = declarative_base(metaclass=VersionedMeta)

def url(viewname, **kw):
    site = getSite()
    urltool = getToolByName(site, 'portal_url')
    urlbase = urltool.getPortalObject().absolute_url()
    url = urlbase + '/@@' + viewname
    if kw:
        params = "&".join(["%s=%s" % (k, str(v)) for k, v in kw.items()])
        url += "?" + params
    return url

def go(viewname, **kw):
    request = getRequest()
    u = url(viewname, **kw)
    request.response.redirect(u)


class BaseORMListView(object):

    def show_url(self, id, vs=None):
        vs = self.view_sufix if vs is None else vs
        return url('show-'+vs, id=id)

    def add_url(self, vs=None):
        vs = self.view_sufix if vs is None else vs
        return url('add-'+vs)

def vs(klass):
    return klass.__name__.lower()

class AddForm(form.SchemaForm):
    """Add Form
    """

    grok.context(INavigationRoot)

    ignoreContext = True

    def createAndAdd(self, data):
        raise NotImplementedError

    def nextURL(self):
        go('list-'+vs(self.klass))

    def cancelURL(self):
        self.nextURL()

    @button.buttonAndHandler(_(u'Cadastrar'), name='cadastrar')
    def handleCadastrar(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        status = IStatusMessage(self.request)
        try:
            obj = self.createAndAdd(data)
            session = Session()
            session.flush()
        except IntegrityError, e:
            msg = _(u'Falha de integridade relacional: ' + str(e))
            status.add(msg, 'error')
            raise
        else:
            status.add(_(u'Cadastro efetuado com sucesso.'), 'info')
            self.nextURL()

    @button.buttonAndHandler(_(u'Cancelar'), name='cancelar')
    def handleCancelar(self, action):
        self.cancelURL()

    def updateActions(self):
        self.request.set('disable_border', True)
        super(AddForm, self).updateActions()
        self.actions["cadastrar"].addClass("context")
        self.actions["cancelar"].addClass("standalone")


class EditForm(form.SchemaForm):
    """Edit Form
    """

    grok.context(INavigationRoot)

    def getContent(self):
        session = Session()
        return session.query(self.klass).get(self.rec_id())

    def applyChanges(self, data):
        content = self.getContent()
        if content:
            for k, v in data.items():
                setattr(content, k, v)

    def nextURL(self):
        go('show-'+vs(self.klass), id=self.rec_id())

    def rec_id(self):
        return self.request.get('id', self.request.get('form.widgets.id', None))

    @button.buttonAndHandler(_(u'Salvar'), name='salvar')
    def handleSalvar(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        status = IStatusMessage(self.request)
        try:
            self.applyChanges(data)
            session = Session()
            session.flush()
        except IntegrityError, e:
            msg = _(u'Falha de integridade relacional: ' + str(e))
            status.add(msg, 'error')
            raise
        else:
            status.add(_(u"Alteraçs efetuadas"), "info")
            self.nextURL()

    @button.buttonAndHandler(_(u'Cancelar'), name='cancelar')
    def handleCancelar(self, action):
        self.nextURL()

    def updateActions(self):
        self.request.set('disable_border', True)
        super(EditForm, self).updateActions()
        self.actions["salvar"].addClass("context")
        self.actions["cancelar"].addClass("standalone")


class ShowForm(form.SchemaForm):
    """Show Form
    """

    grok.context(INavigationRoot)

    mode = 'display'

    def removeItem(self):
        content = self.getContent()
        status = IStatusMessage(self.request)
        try:
            session = Session()
            session.delete(content)
            session.flush()
        except AssertionError, e:
            msg = _(u'Falha de integridade relacional: ' + str(e))
            status.add(msg, 'error')
            raise
        else:
            status.add(_(u'Registro removido.'), 'info')
            self.nextURL()

    def getContent(self):
        session = Session()
        return session.query(self.klass).get(self.rec_id())

    def nextURL(self):
        go('list-'+vs(self.klass))

    def editURL(self):
        go('edit-'+vs(self.klass), id=self.rec_id())

    def rec_id(self):
        return self.request.get('id', self.request.get('form.widgets.id', None))

    @button.buttonAndHandler(_(u'Editar'), name='editar')
    def handleEditar(self, action):
        self.editURL()

    @button.buttonAndHandler(_(u'Excluir'), name='excluir')
    def handleExcluir(self, action):
        self.removeItem()

    @button.buttonAndHandler(_(u'Voltar'), name='voltar')
    def handleVoltar(self, action):
        self.nextURL()

    def updateActions(self):
        self.request.set('disable_border', True)
        super(ShowForm, self).updateActions()
        self.actions["editar"].addClass("context")
        self.actions["excluir"].addClass("context")
        self.actions["voltar"].addClass("standalone")
