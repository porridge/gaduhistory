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
from lib.cache import SQL
from views.log import LogView
from lib.gui.text import ROText

class YearsView(MenuView):
    def __init__(self, user ):
        self._user = user
        title = "%10d: %s - rok" % ( user.ggnumber, user.show )
        super( YearsView, self ).__init__( title )

    def __call__(self):
        sql = SQL()
        query = 'select DISTINCT strftime( "%Y", time) from gadu where ggnumber=:ggnumber'
        tab = {
            'ggnumber' : self._user.ggnumber,
        }
        ret = sql.execute( query, tab )
        self._list = []
        for obj in ret.fetchall():
            year = obj[0]
            object = MonthsView(self._user, year)
            self._list.append( MenuObject( year, object ) )
        if len( self._list ) > 0:
            super( YearsView, self).__call__()
        else:
            ROText( 1, 0, u'Nie znaleziono żadnych logów.', u'Błąd').run()

class MonthsView(MenuView):
    def __init__(self, user, year ):
        self._user = user
        title = u"%10d: %s - miesiąc" % ( user.ggnumber, user.show )
        super( MonthsView, self ).__init__(title)
        self._year = year

    def __call__(self):
        sql = SQL()
        query = 'select DISTINCT strftime( "%Y-%m", time) from gadu where ggnumber=:ggnumber and strftime( "%Y", time)=:year;'
        tab = {
            'ggnumber' : self._user.ggnumber,
            'year'      : self._year,
        }
        ret = sql.execute( query, tab )
        self._list = []
        for obj in ret.fetchall():
            time = obj[0]
            object = DaysView( self._user, time)
            self._list.append( MenuObject( time, object ) )
        super( MonthsView, self).__call__()

class DaysView(MenuView):
    def __init__(self, user, time ):
        self._user = user
        title = u"%10d: %s - dzień" % ( user.ggnumber, user.show )
        super( DaysView, self ).__init__(title)
        self._time = time

    def __call__(self):
        sql = SQL()
        query = 'select DISTINCT strftime( "%Y-%m-%d", time) as showtime, count(*) from gadu where ggnumber=:ggnumber and strftime( "%Y-%m", time) = :date group by showtime;'
        tab = {
            'ggnumber' : self._user.ggnumber,
            'date'      : self._time,
        }
        ret = sql.execute( query, tab )
        self._list = []
        for obj in ret.fetchall():
            showtime = obj[0]
            time = obj[1]
            object = LogView( self._user, showtime)
            self._list.append( MenuObject( showtime +" ("+ str(obj[1]) +")", object ) )
        super( DaysView, self).__call__()
