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

from lib.user import Users, User
from lib.gui import MenuView, BARS
from views.user import UserView
from lib.gui.text import Text, ROText
from lib.cache import SQL
from lib.files import FileManager
from lib.application import app
import curses
from os import listdir
from lib.gui.locals import encode_string

class UserlistView(MenuView):
    class AboutDialog(object):
        def __init__(self, y, x ):
            self._text = [
                u'Program: Gadu History',
                u'Autor: Dominik "Socek" Długajczyk',
                u'Strona: http://projects.socek.org/gaduhistory/ ',
                u'Wersja: %.1f' % app._version,
            ]

            self._x = x
            self._y = y

            max = 0
            for text in self._text:
                length = len( text )
                if length > max:
                    max = length
            self._width = max + 2
            self._height = len( self._text ) + 2
            self._win = curses.newwin( self._height, self._width, self._x, self._y )

        def show(self):
            self._win.border()
            for loop in range( len( self._text ) ):
                self._win.addstr( loop + 1, 1, encode_string(self._text[loop]) )
            self._win.refresh()

        def hide(self):
            self._win.clear()
            self._win.refresh()

    #-------------------------
    def __init__(self):
        bar = BARS['userlist']
        super( UserlistView, self ).__init__(u"Lista użytkowników", bar = bar )
        self._about = self.AboutDialog( 5, 5 )
        self._old = None
        numbers = []
        for obj in Users():
            text = "%10d: %-35s" % ( obj.ggnumber, obj.show )
            self.add_menu_item( text, UserView( obj ) )
            numbers.append( obj.ggnumber )
        dir = FileManager._history_dir()
        dirs = []
        for number in listdir( dir ):
            try:
                number = int( number )
            except:
                # the file is not a GG number, so it's not a history file
                continue
            if number in numbers:
                continue
            dirs.append( number )
        dirs.sort()
        for number in dirs:
            text = "%10s: %-35s" % ( number, '' )
            self.add_menu_item( text, UserView( obj ) )
        self.refresh()

    def show_number(self, ggnumber):
        if FileManager.has_history( ggnumber ):
            sql = SQL()
            query = 'select * from users where ggnumber=:ggnumber;'
            ret = sql.execute(query, {'ggnumber' : ggnumber })
            row = ret.fetchone()
            user = User(row, ggnumber)
            view = UserView( user )
            self.clear()
            view()
        else:
            self.refresh()
            ROText(1, 0, u'Nie znaleziono histori dla podanego numeru.', u'Błąd' ).run()

    def additional_char_handler(self):
        # 108 - l
        # 115 - s
        # 109 - m
        # 265 - F1
        if self._char == 108:
            w = Text(1, 0, u'Podaj numer', only_digits = True)
            if w.text != None and len( w.text ) > 0:
                self.show_number( int( w.text ) )
            return False
        if self._char == 115:
            w = Text(1, 0, u'Podaj nazwę' )
            if w.text != None and len( w.text ) > 0:
                self.filter_show( w.text.decode( 'UTF-8' ) )
            return False
        if self._char == 109:
            if self._old != None:
                self._list = self._old
                self._old = None
                self.refresh()
            return False
        if self._char == 265:
            self._about.show()
            self._char = self._main.getch()
            self._about.hide()
        return True

    def filter_show(self, name):
        name = name.lower()
        self._old = self._list
        self._list = []
        for obj in self._old:
            if obj._fun._user.show.lower().find( name ) != -1:
                self._list.append( obj )
        self._number = 0
        self._show_number = 0
        self._up = 0
        self.refresh()
