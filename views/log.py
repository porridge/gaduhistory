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
from datetime import datetime, timedelta
import curses

class LogView(BaseROView):
    def __init__(self, user, time):
        self._user = user
        self._base_time = time
        self._time = time
        title = u"%10d: %s - %s" % ( user.ggnumber, user.show, time )
        super( LogView, self ).__init__(title)
    
    def change_date(self, day):
        sql = SQL_MSG(self._user.ggnumber)
        
        tab = [ int(obj) for obj in self._time.split('-') ]
        date = datetime(*tab)
        msg = None
        
        if int(day)>0:
            query = 'select *, strftime( "%H:%M:%S", time) as showtime from msg where time>=:time order by time asc limit 1;'
            tab = {
            'time'      : date + timedelta(day),
        }
        else:
            query = 'select *, strftime( "%H:%M:%S", time) as showtime from msg where time<=:time order by time asc limit 1;'
            tab = {
                'time'      : date,
            }
        ret = sql.execute( query, tab )
        obj = ret.fetchone()
        if obj == None:
            print query
            print dir(ret)
            print date + timedelta(day)
            
            import time
            print time.mktime((date + timedelta(day)).timetuple())
            return False
        while msg == None:
            date += timedelta(day)
            
            query = 'select *, strftime( "%H:%M:%S", time) as showtime from msg where strftime( "%Y-%m-%d", time)=:time order by time asc limit 1;'
            tab = {
                'time'      : date.strftime( "%Y-%m-%d" ),
            }
            ret = sql.execute( query, tab )
            msg = ret.fetchone()
        self._time = date.strftime( "%Y-%m-%d" )
        return True
    
    def go_up(self):
        """go_up(self) -> None
        Scroll the view one line up.
        """
        if self._up >0:
            self._up -= 1
        else:
            if self.change_date(-1):
                self.fill()
                self.go_end()
        self.refresh()

    def go_down(self):
        """go_down(self) -> None
        Scroll the view one line down.
        """
        (maxy,maxx) = self._get_main_size()
        if self._up + 1 < self._maxlines - maxy:
            self._up += 1
        else:
            if self.change_date(1):
                self.fill()
                self.go_home()

    def fill(self):
        if self._main != None:
            self._main.clear()
            self.refresh()
        self._title_text = u"%10d: %s - %s" % ( self._user.ggnumber, self._user.show, self._time )

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
    
    def __call__(self):
        self._time = self._base_time
        self._title_text = u"%10d: %s - %s" % ( self._user.ggnumber, self._user.show, self._time )
        return super(LogView, self).__call__()
        
