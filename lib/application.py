##-*- coding: utf-8 -*-
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

import locale
locale.setlocale(locale.LC_ALL,"")

from lib.cache import cache_history, create_tables, cache_userlist
from lib.user import Users
from lib.ekgconfig import EKG_CONFIG

from lib import gui

import curses

class AppClass(object):
    def __init__(self):
        self._stdscr = None
        self._version = 0.5
        EKG_CONFIG.read()

    def init(self):
        """init(self) -> None
        Initialization of curses.
        """
        self._stdscr = gui.get_stdscr()

    def close(self):
        """close(self) -> None
        Cleanup before program edns.
        """
        curses.endwin()

    def first_view(self):
        """first_view(self) -> None
        Running of the firs View.
        """
        from views.userlist import UserlistView
        view = UserlistView()
        view()

    def _scr(self):
        """Curses screen object.
        """
        return self._stdscr
    scr = property(_scr)

app = AppClass()
