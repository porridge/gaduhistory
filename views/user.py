#-*- coding: utf-8 -*-
#
#copyright 2010 Dominik "Socek" Długajczyk
#
#This file is part of Gadu History.
#
#Gadu History is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
#
#Gadu History is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Gadu History; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from lib.gui import MenuView, MenuObject
from lib import cache
from views.dates import YearsView
from views.who import WhoView
from views.descriptions import DescriptionsView

class UserView(MenuView):
    def __init__(self, user ):
        self._user = user
        title = "%10d: %s" % ( user.ggnumber, user.show )
        super( UserView, self ).__init__(title)
        self._dates = YearsView(self._user)
        self._list = [
            MenuObject( u"Pokaż datami", self._dates ),
            MenuObject( u"Pokaż wszystkie zapisane nazwy użytkownika", WhoView( self._user ) ),
            MenuObject( u"Pokaż wszystkie opisy", DescriptionsView( self._user ) ),
        ]

    def __call__(self):
        if cache.is_cache_needed( self._user.ggnumber ):
            self.cache()
        super( UserView, self ).__call__()

    def cache(self):
        self.clear()
        win = self.please_wait()
        cache.cache_history( self._user.ggnumber )
        win.clear()
        win.refresh()
        self.clear()
