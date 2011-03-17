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
from base import BaseView
from main import get_stdscr, BARS

class BaseROView(BaseView):
    """Basic Read Only view."""
    def __init__(self, title, bar = BARS['standard']):
        super( BaseROView, self).__init__(title, bar)
        self._running = True
        self._up = 0
        self._maxlines = 0

    def __call__(self):
        """__call__(self) -> None
        Invoke the view.
        """
        self.fill()
        self.refresh()
        self.run()

    def _get_main_size(self):
        """_get_main_size(self) -> (int, int)
        Height and width of the main window.
        """
        (maxy,maxx) = get_stdscr().getmaxyx()
        if self._title != None:
            maxy -= 1
        if self._bar_info:
            maxy -= self._bar_info['lines']
        return (maxy, maxx)

    def go_up(self):
        """go_up(self) -> None
        Scroll the view one line up.
        """
        if self._up >0:
            self._up -= 1
        self.refresh()

    def go_down(self):
        """go_down(self) -> None
        Scroll the view one line down.
        """
        (maxy,maxx) = self._get_main_size()
        if self._up + 1 < self._maxlines - maxy:
            self._up += 1

    def go_home(self):
        """go_home(self) -> None
        Scroll the view to the top.
        """
        self._up = 0

    def go_end(self):
        """go_end(self) -> None
        Scroll the view to the bottom.
        """
        (maxy,maxx) = self._get_main_size()
        self._up = self._maxlines - maxy - 1

    def go_page_down(self):
        """go_page_down(self) -> None
        Scroll the view oe page down.
        """
        (maxy,maxx) = self._get_main_size()
        self._up += maxy - 1
        if self._maxlines - self._up <= maxy:
            self.go_end()

    def go_page_up(self):
        """go_page_up(self) -> None
        Scroll the view one page up.
        """
        (maxy,maxx) = self._get_main_size()
        self._up -= maxy - 1
        if self._up < 0:
            self.go_home()

    def run(self):
        """run(self) -> None
        View invocation, reacting to events.
        """
        self._running = True
        while self._running:
            # 259 - up
            # 258 - down
            # 262 - Home
            # 360 - End
            # 10 - enter
            self._main.keypad(1)
            self._char = self._main.getch()
            if self._char == 259:
                self.go_up()
            elif self._char == 258:
                self.go_down()
            #elif self._char == 10:
                #self.run_item()
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
