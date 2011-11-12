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
from copy import copy
from lib.gui.locals import encode_string

ESCAPES = [ '\xc5', '\xc4', '\xc3' ]

class Text(object):
    def __init__(self, y, x, title = None, text = '', only_digits = False, width = 25):
        self.x = x
        self.y = y
        self._title = title
        self.text = text
        self._running = True
        self._win = None
        self._cursor = 0
        self._low_cursor = 0
        self._startpost = 0
        self._width = width
        self._only_digits = only_digits
        self.cursor_end()
        self.run()

    @property
    def text_width(self):
        return self._width - 3

    def run(self):
        gflags = curses.A_BOLD

        width = self._width
        self._win = curses.newwin( 3, width, self.y, self.x)
        self._win.border()
        if self._title:
            width = self._win.getmaxyx()[1] - 2 # TODO: I don't know why it needs to be "-2" but it does not work otherwise

            center = ( width/2 ) - ( len(self._title)/2 ) + 1
            self._win.addstr( 0, center, encode_string(self._title), gflags )
        self._win.refresh()
        self._win2 = curses.newwin( 1, width, self.y+1, self.x+1)

        curses.curs_set(1)
        while self._running:
            self.refresh()
            self._win2.keypad(1)
            char = self._win2.getch()
            self.validator( char )
        curses.curs_set(0)

        self._win.erase()
        self._win.refresh()

    def text_length(self):
        text = copy( self.text )
        for esc in ESCAPES:
            text = text.replace( esc, '')
        return len( text )

    def refresh(self):
        width = self.text_width
        if self.text_length() < width:
            text = self.text
        else:
            text = self.text[self._startpost: self._startpost+width]
            if len( text ) < width:
                text = self.text[:width]
        self._win2.move( 0, 0 )
        self._win2.clrtoeol()
        try:
            #I don't know what is the source of the problem, so I made workaround
            #When someone use "polish" letter in front it prints something strange
            if len(text) < 2:
                text += ' '
            #end of workaround
            self._win2.addstr( 0, 0, text, curses.A_BOLD )
        except curses.error:
            raise RuntimeError( text )
        self._win2.move( 0, self._low_cursor )

    def cursor_home(self):
        self._cursor = 0
        self._low_cursor = 0
        self._startpost = 0

    def cursor_end(self):
        self._cursor = self.text_length()
        if self.text_length() > self.text_width:
            self._low_cursor = self.text_width
        else:
            self._low_cursor = self.text_length()
        self._startpost = self.text_length() - self.text_width
        if self._startpost < 0:
            self._startpost = 0

    def backspace(self):
        if self._cursor > 0:
            tmp = list( self.text )
            listtext = []
            last = []
            for char in tmp:
                if char in ESCAPES:
                    last = [char]
                else:
                    listtext.append( last + [char] )
                    last = []
            listtext.pop( self._cursor - 1 )
            self.text = ''
            for char in listtext:
                for skladowa in char:
                    self.text += skladowa
            self._cursor -= 1
            length = self.text_length()
            if length < self.text_width:
                self._low_cursor -= 1
            else:
                self._startpost -= 1

    def cursor_right(self):
        if self._cursor < self.text_length():
            self._cursor += 1
            if self._low_cursor < self.text_width:
                self._low_cursor += 1
            else:
                if self._startpost < self.text_length():
                    self._startpost += 1

    def cursor_left(self):
        if self._cursor > 0:
            self._cursor -= 1
        if self._low_cursor > 0:
            self._low_cursor -= 1
        else:
            if self._startpost > 0:
                self._startpost -= 1

    def validator(self, var):
        #raise RuntimeError( var )
        #print var
        if var == 10:
            self._running = False
            return False
        elif var == 263 or var == 127:
            self.backspace()
            return False
        elif var == 260: # Cursor left
            self.cursor_left()
            return False
        elif var == 261: # Cursor right
            self.cursor_right()
            return False
        elif var == 262: # home
            self.cursor_home()
            return False
        elif var == 360:
            self.cursor_end()
            return False
        elif var == 274:
            self._running = False
            self.text = None
            return False
        elif var > 250:
            return False
            #raise RuntimeError( var )

        if self._only_digits and not var in [ 48, 49, 50, 51, 52, 53, 54, 55, 56, 57 ]:
            return False

        # We end up here if there was no other action
        if self._cursor >= self.text_length():
            self.text += chr( var )
        else:
            listtext = list( self.text )
            listtext[ self._cursor ] = chr( var )
            self.text = ''.join( listtext )
        self.cursor_right()
        return True

class ROText(object):
    def __init__(self, y, x, text, title = None ):
        self._x = x
        self._y = y
        self._title = title
        self.text = text
        self.refresh()

    def refresh(self):
        width = self.text_length() + 2
        gflags = curses.A_BOLD

        self._win = curses.newwin( 3, width, self._y, self._x)
        self._win.border()
        swidth = self._win.getmaxyx()[1] - 2 # TODO: I don't know why it needs to be "-2" but it does not work otherwise
        if self._title:
            center = ( swidth/2 ) - ( len(self._title)/2 ) + 1
            self._win.addstr( 0, center, encode_string(self._title), gflags )
        self._win.refresh()
        self._win2 = curses.newpad( 1, swidth + 1)
        try:
            self._win2.addstr( 0, 0, encode_string(self.text), curses.A_BOLD )
        except curses.error, er:
            raise RuntimeError( self.text )
        self._win2.refresh( 0, 0, self._y+1, self._x+1,  self._y+2, self._x+swidth)

    def clear(self):
        self._win.clear()
        self._win.refresh()

    def run(self):
        self._win.getch()

    def text_length(self):
        text = copy( self.text )
        #for esc in ESCAPES:
        #    text = text.replace( esc, '')
        return len( text )
