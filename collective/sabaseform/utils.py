# -*- coding: utf-8 -*-

from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.globalrequest import getRequest

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
    redirect_url = url(viewname, **kw)
    request.response.redirect(redirect_url)

def vs(klass):
    return klass.__name__.lower()

class BaseListView(object):

    def show_url(self, id, vs=None):
        vs = self.view_sufix if vs is None else vs
        return url('show-'+vs, id=id)

    def add_url(self, vs=None):
        vs = self.view_sufix if vs is None else vs
        return url('add-'+vs)
