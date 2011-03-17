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
_SQL_MSG = {}
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

def SQL_MSG(uid):
    global _SQL_MSG
    uid = strip_gg(uid)
    if not _SQL_MSG.has_key(uid):
        _SQL_MSG[uid] = sqlite3.connect(FileManager._gg_history_sql_of(uid))
        create_tables_msg( _SQL_MSG[uid] )
        _SQL_MSG[uid].text_factory = unicode
        _SQL_MSG[uid].row_factory = sqlite3.Row
    return _SQL_MSG[uid]

def create_tables_msg(sql):
    querys = []
    querys.append( '''create table if not exists msg (
        id integer primary key UNIQUE,
        type char(25) not null,
        nick char(255),
        time date not null,
        send_time date,
        descr char(255),
        msg text,
        status char(25),
        ip char(100)
    );''' )
    for query in querys:
        sql.execute( query )
    sql.commit()

def create_tables():
    """create_tables() -> None
    Create tables if not exists.
    """
    sql = SQL()
    querys = []
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
    if type(string) == int:
        return str(string)
    elif string.startswith('gg:'):
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
        query = '''insert into users(name, surname, nick, display, phone, groups, email, ggnumber) values
        (:name, :surname, :nick, :display, :phone, :groups, :email, :ggnumber);'''
        if len(row) > 7:
          email = row[7]
        else:
          email = ''
        tab = {
            'name'      : row[0],
            'surname'   : row[1],
            'nick'      : row[2],
            'display'   : row[3],
            'phone'     : row[4],
            'groups'    : row[5],
            'ggnumber'  : row[6],
            'email'     : email,
        }
        sql.execute( query, tab )
    sql.commit()

def cache_history( number ):
    """cache_history( number ) -> None
    Update cache for the specific user.
    number - GG number of the person to reloads cache
    """
    main_sql = SQL()
    ret = main_sql.execute( 'select seek from cache_info where ggnumber=:ggnumber', {'ggnumber':number} )
    row = ret.fetchone()
    if row != None:
        offset = row[0]
    else:
        offset = 0
    
    sql = SQL_MSG(number)
    if not FileManager.has_history(number):
        return
    file = open(FileManager.history_of(number), "rb")
    file.seek(offset)
    
    reader = GaduReader(file, encoding=FileManager.history_encoding)
    loop = -1
    for row in reader:
        try:
            #jeśli jest już taki rekord, to nie dodawaj nowego
            query = 'select * from msg where time=:time'
            tab = {}
            if row[0] in ['chatsend', 'msgsend']:
                tab['msg']  = row[4]
                tab['time'] = row[3]
            else:    
                tab['msg']  = row[5]
                tab['time'] = row[4]
            ret = sql.execute(query,tab)
            rows = ret.fetchall()
            if len(rows) > 0:
                continue
            #--------------------------------
            
            loop += 1
            if row[0] == 'status':
                
                
                tab = {
                    'type'      : row[0],
                    #'ggnumber'  : int( strip_gg( row[1] ) ),
                    'nick'      : row[2],
                    'ip'        : row[3],
                    'time'      : int( row[4] ),
                    'status'    : row[5],
                }
                if len( row ) > 6:
                    tab['descr'] = row[6]
                else:
                    tab['descr'] = None
                query = '''insert into msg( type, nick, ip, time, status, descr ) values
                ( :type, :nick, :ip, datetime(:time, 'unixepoch'), :status, :descr);'''
            elif row[0] in ['chatrecvign', 'msgrecvign', 'chatrecv', 'msgrecv', 'chatrcv']:
                tab = {
                    'type'      : row[0],
                    #'ggnumber'  : int( strip_gg( row[1] ) ),
                    'nick'      : row[2],
                    'time'      : int( row[3] ),
                    'send_time' : int( row[4] ),
                    'msg'       : row[5],
                }
                query = '''insert into msg( type, nick, time, send_time, msg ) values
                ( :type, :nick, datetime(:time, 'unixepoch'), :send_time, :msg);'''
            elif row[0] in ['chatsend', 'msgsend']:
                tab = {
                    'type'      : row[0],
                    #'ggnumber'  : int( strip_gg( row[1] ) ),
                    'nick'      : row[2],
                    'time'      : int( row[3] ),
                    'msg'       : row[4],
                }
                query = '''insert into msg( type, nick, time, msg ) values
                ( :type, :nick, datetime(:time, 'unixepoch'), :msg);'''
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
        main_sql.execute( query, tab )
    except sqlite3.IntegrityError:
        query = 'update cache_info set seek=:seek where ggnumber=:ggnumber;'
        main_sql.execute( query, tab )
    main_sql.commit()
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
