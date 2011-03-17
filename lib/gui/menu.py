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
from time import sleep
from main import Colors, get_stdscr, BARS
from base import BaseView
import curses

class MenuObject(object):
    """An object within a menu.
    """

    def __init__(self, name, fun):
        self._name = name
        self._fun = fun

    def _get_name(self):
        """Name/label of the menu element."""
        return self._name

    def _set_name(self, value):
        self._name = value

    name = property( _get_name, _set_name )

    @property
    def fun(self):
        """Function called when the menu element is activated."""
        return self._fun

class MenuView(BaseView):
    """Basic menu view."""

    def __init__(self, title = None, bar = BARS['standard']):
        super( MenuView, self ).__init__( title, bar )
        self._list = []
        self._number = 0
        self._running = True
        self._show_number = 0
        self._up = 0
        self._exit_txt = " => Exit <=                                    "

    def add_menu_item(self, title, fun ):
        """add_menu_item(self, title, fun ) -> MenuObject
        Add a new object to the menu.
        """
        object = MenuObject( title, fun )
        self._list.append( object )
        return object

    def text(self, obj):
        """text(self, obj) -> str
        Zamiana tekstu, na tekst "writable".
        TODO: what does it mean?
        """
        return obj.name.encode( 'utf-8' )

    def getmaxyx(self):
        """getmaxyx(self) -> (int, int)
        Returns the maximum height and width at the current menu object list
        state.
        """
        (maxy,maxx) = get_stdscr().getmaxyx()
        maxy = len( self._list ) + 1
        return (maxy,maxx)

    def _get_main_size(self):
        """_get_main_size(self) -> (int, int)
        Height and width of the bottom window.
        """
        (maxy,maxx) = get_stdscr().getmaxyx()
        if self._title != None:
            maxy -= 1
        if self._bar_info:
            maxy -= self._bar_info['lines']
        return (maxy, maxx)

    def fill(self):
        """fill(self) -> None
        Fill the bottom window with data.
        """
        (w_maxy,w_maxx) = self.getmaxyx()
        (s_maxy,s_maxx) = get_stdscr().getmaxyx()
        if w_maxy >= s_maxy:
            maxy = w_maxy
        else:
            maxy = s_maxy
        maxx = s_maxx
        self._main = curses.newpad( maxy, maxx )
        loop = -1
        for obj in self._list:
            loop += 1
            if loop == self._number:
                flags = curses.color_pair(Colors.hover)
            else:
                flags = curses.color_pair(Colors.normal)
            self._main.addstr( loop, 0, self.text(obj), flags )
        loop += 1
        if loop == self._number:
            flags = curses.color_pair(Colors.hover)
        else:
            flags = curses.color_pair(Colors.normal)
        self._main.addstr( loop, 0, self._exit_txt, flags )

    def go_down(self):
        """go_down(self) -> None
        Move the cursor one position down.
        """
        self._number += 1
        if self._number > len( self._list ):
            self._number = len( self._list )
            return
        self._show_number += 1

        (maxy,maxx) = self._get_main_size()

        if self._show_number >= maxy:
            self._up += 1
            self._show_number = maxy - 1

    def go_up(self):
        """go_up(self) -> None
        Move the cursor one position up.
        """
        self._number -= 1
        if self._number < 0:
            self._number = 0
            return
        self._show_number -= 1
        if self._show_number < 0:
            self._up -= 1
            self._show_number = 0

    def go_home(self):
        """go_home(self) -> None
        Move the cursor to the top.
        """
        self._number = 0
        self._show_number = 0
        self._up = 0

    def go_end(self):
        """go_end(self) -> None
        Move the cursor to the bottom.
        """
        (maxy,maxx) = self._get_main_size()
        self._number = len( self._list )
        self._show_number = maxy - 1
        self._up = self._number - maxy + 1

    def go_page_down(self):
        """go_page_down(self) -> None
        Move the cursor one page down.
        """
        (maxy,maxx) = self._get_main_size()
        self._up += maxy - 1
        if len( self._list ) - self._up < maxy:
            self.go_end()
        else:
            self._show_number = 0
            self._number = self._up

    def go_page_up(self):
        """go_page_up(self) -> None
        Move the cursor one page up.
        """
        (maxy,maxx) = self._get_main_size()
        self._up -= maxy - 1
        if self._up < 0:
            self.go_home()
        else:
            self._show_number = maxy - 1
            self._number = self._up + maxy - 1

    def run_item(self):
        """run_item(self) -> None
        Call the object currently selected with the cursor.
        """
        self.clear()
        if len( self._list ) <= self._number:
            self._running = False
        else:
            self._list[self._number].fun()
            self.refresh()

    def additional_char_handler(self):
        return True

    def __call__(self):
        """__call__(self) -> None
        Invocation of the current menu view.
        """
        self.refresh()
        self._running = True
        while self._running:
            # 113 - q
            # 259 - up
            # 258 - down
            # 262 - Home
            # 360 - End
            # 338 - PageDown
            # 339 - PageUp
            # 10 - enter
            self._main.keypad(1)
            self._char = self._main.getch()
            if self.additional_char_handler():
                if self._char == 259:
                    self.go_up()
                elif self._char == 258:
                    self.go_down()
                elif self._char == 10:
                    self.run_item()
                elif self._char == 360:
                    self.go_end()
                elif self._char == 262:
                    self.go_home()
                elif self._char == 113:
                    self._running = False
                elif self._char == 338:
                    self.go_page_down()
                elif self._char == 339:
                    self.go_page_up()
            self.refresh()
            sleep( 0.01)
        self.close()

    def close(self):
        """close(self) -> None
        Close the view.
        """
        self.clear()

    def refresh(self):
        """refresh(self) -> None
        Refresh the view.
        """
        self.fill()
        super( MenuView, self).refresh()
