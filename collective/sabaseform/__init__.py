# -*- coding: utf-8 -*-

import zope.i18nmessageid

MessageFactory = zope.i18nmessageid.MessageFactory('collective.sabaseform')

from collective.sabaseform.utils import BaseListView
from collective.sabaseform.base import AddForm, EditForm, ShowForm

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
