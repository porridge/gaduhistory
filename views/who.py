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

from lib.gui import BaseROView
from lib.cache import SQL_MSG
import curses
from lib.gui.text import ROText

class WhoView(BaseROView):
    def __init__(self, user):
        self._user = user
        title = u"%10d: wszystkie zapisane nazwy użytkownika" % ( user.ggnumber )
        super( WhoView, self ).__init__(title)

    def fill(self):
        sql = SQL_MSG(self._user.ggnumber)
        query = 'select nick from msg where not nick="" group by nick;'
        ret = sql.execute( query)
        list = ret.fetchall()
        self._maxlines = 1
        new_list = [ ]
        for obj in list:
            self._maxlines += 1 + obj[0].count('\n')
            new_list.append( obj[0] )

        loop = -1
        self._main = curses.newpad( self._maxlines, 255 )
        for obj in new_list:
            loop += 1
            self._main.addstr( loop, 0, obj.strip().encode( 'UTF-8' ) )
        if loop == -1:
            return False
        else:
            return True

    def __call__(self):
        if self.fill():
            self.refresh()
            self.run()
        else:
            ROText( 1, 0, u'Nie znaleziono żadnych nazw.', u'Błąd').run()
