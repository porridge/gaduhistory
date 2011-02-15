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
import curses
from main import Colors, get_stdscr
from lib.gui.text import ROText

class BaseView(object):
    """Base view."""

    def __init__(self, title = None, bar = None):
        def bar_init():
            self._bar_info = bar
            if self._bar_info == None:
                return
            (maxy,maxx) = get_stdscr().getmaxyx()
            lines = self._bar_info['lines']
            self._bar = curses.newwin( lines, maxx, maxy - lines , 0 )
        #-----------------------------
        self._title_text = title
        self.title = title
        self._main = None
        bar_init()

    def _get_title(self):
        """Title, shown at the top of the screen."""
        return self._title

    def _set_title(self, title):
        (maxy,maxx) = get_stdscr().getmaxyx()
        if title == None:
            self._title = None
        else:
            self._title = curses.newwin( 1, maxx, 0, 0 )
            title = title.strip().encode( 'utf-8' )
            center = ( maxx / 2 ) - ( len(title) / 2 )
            flags = curses.color_pair(Colors.title )
            self._title.bkgd( ' ', flags )
            self._title.addstr( 0, center, title )

    title = property( _get_title, _set_title )

    def refresh(self):
        """refresh(self) -> None
        Refreshing of windows.
        """
        if self._title_text != None:
            self.title = self._title_text
            self._title.refresh()
        if self._main != None:
            (maxy,maxx) = get_stdscr().getmaxyx()

            #if we have the title, then we need to cut the upper line
            if self._title == None:
                y = 0
            else:
                y = 1
            #if we have bottom bar, then we need to cut the bottom lines
            if self._bar_info:
                bottom = maxy - self._bar_info['lines'] - 1
            else:
                bottom = maxy-1
            self._main.refresh( self._up, 0, y, 0, bottom, maxx-1 )
        if self._bar_info:
            self._bar.clear()

            (maxy,maxx) = get_stdscr().getmaxyx()
            lines = self._bar_info['lines']
            self._bar.mvwin( maxy - lines , 0 )

            flags = curses.color_pair(Colors.title )
            self._bar.bkgd( ' ', flags )
            loop = -1
            for line in self._bar_info['text']:
                loop += 1
                self._bar.addstr( loop, 0, line )
            self._bar.refresh()

    def clear(self):
        """clear(self) -> None
        Clearing of windows.
        """
        if self._title != None:
            self._title.clear()
            self._title.refresh()
        if self._main != None:
            self._main.clear()

            (maxy,maxx) = get_stdscr().getmaxyx()
            if self._title == None:
                y = 0
            else:
                y = 1
            self._main.refresh( self._up, 0, y, 0, maxy-1, maxx-1 )

    def please_wait(self):
        return ROText(1, 0, u'Proszę czekać')
