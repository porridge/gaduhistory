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

BARS = {
    'standard' : {
        'lines' : 2,
        'text'  : [ 'Up / Down / Home / End / PageUp / PageDown', 'q - exit' ],
    },
    'userlist' : {
        'lines' : 3,
        'text'  : [ 'Up / Down / Home / End / PageUp / PageDown', 'q - exit | l - historia numeru | s - przeszukaj', 'm - pokaż wszystkie numery | F1 - o programie' ],
    }
}

class _Colors:
    _ColorSets = {
        'normal'   : {
            'pair'  : ( curses.COLOR_WHITE, curses.COLOR_BLACK ),
        },
        'hover'    : {
            'pair'  : ( curses.COLOR_BLACK, curses.COLOR_CYAN ),
        },
        'title'     : {
            'pair'  : ( curses.COLOR_BLUE, curses.COLOR_WHITE ),
        }
    }

    def __init__(self):
        #zapełnianie niepowtarzalnymi idkami
        loop = 0
        for key, item in self._ColorSets.items():
            loop += 1
            item['id'] = loop

    def init(self):
        """init(self) -> None
        Colour initialization.
        """
        curses.start_color()
        for key, color in self._ColorSets.items():
            curses.init_pair( color['id'], color['pair'][0],  color['pair'][1] )

    def __getattr__(self, name ):
        return self._ColorSets[ name ]['id']

    def __iter__(self):
        return self._ColorSets.keys()

Colors = _Colors()

stdscr = None
def get_stdscr():
    """initstdscr() -> stdscr
    Curses initialization.
    """
    global stdscr
    if stdscr == None:
        stdscr = curses.initscr()
        curses.curs_set(0)
        Colors.init()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
    return stdscr
