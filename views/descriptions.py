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

class DescriptionsView(BaseROView):
    def __init__(self, user):
        self._user = user
        title = u"%10d: wszystkie opisy" % ( user.ggnumber )
        super( DescriptionsView, self ).__init__(title)

    def fill(self):
        sql = SQL_MSG(self._user.ggnumber)
        query = 'select descr, strftime( "%Y-%m-%d %H:%M:%S", time) showtime from msg where not descr="" group by descr order by time;'
        ret = sql.execute( query )
        list = ret.fetchall()
        print query
        print list
        self._maxlines = 1
        new_list = [ ]
        for obj in list:
            self._maxlines += 1
            new_list.append( obj[1] +' '+ obj[0] )

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
        """__call__(self) -> None
        Invoke the view.
        """
        if self.fill():
            self.refresh()
            self.run()
        else:
            ROText( 1, 0, u'Nie znaleziono żadnych opisów.', u'Błąd').run()
