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

class LogView(BaseROView):
    def __init__(self, user, time):
        self._user = user
        self._time = time
        title = u"%10d: %s - %s" % ( user.ggnumber, user.show, time )
        super( LogView, self ).__init__(title)

    def fill(self):
        sql = SQL_MSG(self._user.ggnumber)
        query = 'select *, strftime( "%H:%M:%S", time) as showtime from msg where strftime( "%Y-%m-%d", time)=:time order by time asc;'
        tab = {
            'time'      : self._time,
        }
        ret = sql.execute( query, tab )
        list = ret.fetchall()

        (maxy, maxx) = self._get_main_size()
        max = maxx

        lines = []
        for obj in list:
            if obj['type'] in ['chatrecvign', 'msgrecvign', 'chatrecv', 'chatrcv', 'msgrecv', 'msgrcv']:
                text = u"%(showtime)s <%(nick)s> %(msg)s" % {
                    'showtime'  : obj['showtime'],
                    'nick'      : obj['nick'],
                    'msg'       : obj['msg'],
                }
            elif obj['type'] in ['chatsend', 'msgsend']:
                text = u"%(showtime)s <ME> %(msg)s" % {
                    'showtime'  : obj['showtime'],
                    'msg'       : obj['msg'],
                }
            else:
                text = u"%(showtime)s * %(nick)s - %(status)s: %(descr)s" % {
                    'showtime'  : obj['showtime'],
                    'nick'      : obj['nick'],
                    'status'    : obj['status'],
                    'descr'     : obj['descr'],
                }
            text = text.replace( '\r', '' )
            tmp_lines = text.split( '\n' )
            for tmp_line in tmp_lines:
                tmp_line = tmp_line.strip()
                while len( tmp_line ) > max:
                    lines.append( tmp_line[:max] )
                    tmp_line = tmp_line[max:]
                lines.append( tmp_line )

        self._maxlines = len( lines ) + 1
        self._main = curses.newpad( self._maxlines, 255 )
        loop = -1
        for line in lines:
            try:
                loop += 1
                self._main.addstr( loop, 0, line.encode( 'UTF-8' ) )
            except:
                pass
