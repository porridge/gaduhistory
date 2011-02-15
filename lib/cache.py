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
import sqlite3
from lib.ggcsv import UnicodeReader, userlist_dialect, GaduReader
from lib.files import FileManager

_SQL = None
def SQL():
    """SQL() -> sqlite3
    Gets connection with the databaes.
    """
    global _SQL
    if _SQL == None:
        _SQL = sqlite3.connect(FileManager.cache)
        create_tables()
        _SQL.text_factory = unicode
        _SQL.row_factory = sqlite3.Row
    return _SQL

def create_tables():
    """create_tables() -> None
    Create tables if not exists.
    """
    sql = SQL()
    querys = []
    querys.append( '''create table if not exists gadu (
        id integer primary key UNIQUE,
        type char(25) not null,
        ggnumber integer not null,
        nick char(255),
        time date not null,
        send_time date,
        descr char(255),
        msg text,
        status char(25),
        ip char(100)
    );''' )
    querys.append( '''create table if not exists cache_info (
        ggnumber integer not null primary key UNIQUE,
        seek integer
    );''' )
    querys.append( '''drop table if exists users;''' )
    querys.append( '''create table if not exists users (
        ggnumber integer not null primary key UNIQUE,
        name char(100),
        surname char(100),
        nick char(255),
        display char(100),
        phone char(20),
        groups char(255),
        email char(100)
    );''')

    for query in querys:
        sql.execute( query )
    sql.commit()

def strip_gg(string):
    """strip_gg(string) -> str
    Returns gg number from the row.
    """
    if string.startswith('gg:'):
        return string[3:]
    else:
        return string

def cache_userlist():
    """cache_userlist() -> None
    Reloads cache for the user list.
    """
    sql = SQL()
    file = open(FileManager.user_list, "rb")
    reader = UnicodeReader( file, dialect=userlist_dialect, encoding="iso-8859-2"  )
    for row in reader:
        query = '''insert into users(ggnumber, name, surname, nick, display, phone, groups, email) values
        (:ggnumber, :name, :surname, :nick, :display, :phone, :groups, :email);'''
        if len(row) > 7:
          email = row[7]
        else:
          email = ''
        tab = {
            'ggnumber'  : int( strip_gg( row[6] ) ),
            'name'      : row[0],
            'surname'   : row[1],
            'nick'      : row[2],
            'display'   : row[3],
            'phone'     : row[4],
            'groups'    : row[5],
            'email'     : email,
        }
        sql.execute( query, tab )
    sql.commit()

def cache_history( number ):
    """cache_history( number ) -> None
    Update cache for the specific user.
    number - GG number of the person to reloads cache
    """
    sql = SQL()
    if not FileManager.has_history(number):
        return
    file = open(FileManager.history_of(number), "rb")
    ret = sql.execute( 'select seek from cache_info where ggnumber=:ggnumber', {'ggnumber':number} )
    rows = ret.fetchall()
    if len(rows) >= 1:
        offset = rows[0][0]
        file.seek(offset)
    else:
        offset = 0
    reader = GaduReader(file, encoding=FileManager.history_encoding)
    loop = -1
    for row in reader:
        try:
            loop += 1
            if row[0] == 'status':
                tab = {
                    'type'      : row[0],
                    'ggnumber'  : int( strip_gg( row[1] ) ),
                    'nick'      : row[2],
                    'ip'        : row[3],
                    'time'      : int( row[4] ),
                    'status'    : row[5],
                }
                if len( row ) > 6:
                    tab['descr'] = row[6]
                else:
                    tab['descr'] = None
                query = '''insert into gadu( type, ggnumber, nick, ip, time, status, descr ) values
                ( :type, :ggnumber, :nick, :ip, datetime(:time, 'unixepoch'), :status, :descr);'''
            elif row[0] in ['chatrecvign', 'msgrecvign', 'chatrecv', 'msgrecv', 'chatrcv']:
                tab = {
                    'type'      : row[0],
                    'ggnumber'  : int( strip_gg( row[1] ) ),
                    'nick'      : row[2],
                    'time'      : int( row[3] ),
                    'send_time' : int( row[4] ),
                    'msg'       : row[5],
                }
                query = '''insert into gadu( type, ggnumber, nick, time, send_time, msg ) values
                ( :type, :ggnumber, :nick, datetime(:time, 'unixepoch'), :send_time, :msg);'''
            elif row[0] in ['chatsend', 'msgsend']:
                tab = {
                    'type'      : row[0],
                    'ggnumber'  : int( strip_gg( row[1] ) ),
                    'nick'      : row[2],
                    'time'      : int( row[3] ),
                    'msg'       : row[4],
                }
                query = '''insert into gadu( type, ggnumber, nick, time, msg ) values
                ( :type, :ggnumber, :nick, datetime(:time, 'unixepoch'), :msg);'''
            else:
                raise ValueError('Unknown row type [%s] in %s when reading line %d from %s.' %
                                  (row[0], str(row), loop, str(file)))
            sql.execute( query, tab )
        except IndexError:
            raise ValueError('Row %s has less fields (%d) than expected when reading '
                             'line %d from %s, counting from byte %d.' %
                             (str(row), len(row), loop, str(file), offset))
        except UnicodeEncodeError:
            pass
            #raise ValueError('Unicode Encoding Error in %s when reading line %d from %s, '
            #                 'couting from byte %d.' % (str(row), loop, str(file), offset))
        except ValueError:
            pass
    from datetime import datetime
    tab = {
        'ggnumber'  : number,
        'seek'      : file.tell(),
    }
    try:
        query = 'insert into cache_info values ( :ggnumber, :seek );'
        sql.execute( query, tab )
    except sqlite3.IntegrityError:
        query = 'update cache_info set seek=:seek where ggnumber=:ggnumber;'
        sql.execute( query, tab )
    sql.commit()

def is_cache_needed(ggnumber):
    """is_cache_needed(ggnumber) -> bool
    Is new cache for the GG number needed.
    """
    sql = SQL()
    query = 'select seek from cache_info where ggnumber=:ggnumber'
    tab = {
        'ggnumber' : ggnumber,
    }
    try:
        seek = sql.execute( query, tab ).fetchall()[0][0]
    except:
        return True
    fp = open(FileManager.history_of(ggnumber), "rb")
    fp.seek(0, 2) #seek to the end
    if seek != fp.tell():
        return True
    else:
        return False
