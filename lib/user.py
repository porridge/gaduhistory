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
from lib.ggcsv import UnicodeReader, userlist_dialect
from os import getenv
from lib.cache import SQL, cache_userlist

class User(object):

    def __init__(self, row, ggnumber = None):
        if row == None:
            self._name      = ''
            self._surname   = ''
            self._nick      = ''
            self._show      = ''
            self._phone     = ''
            self._groups    = []
            self._ggnumber  = ggnumber
            self._email     = ''
        else:
            self._name      = row['name']
            self._surname   = row['surname']
            self._nick      = row['nick']
            self._show      = row['display']
            self._phone     = row['phone']
            self._groups    = row['groups'].split( ',' )
            self._ggnumber  = row['ggnumber']
            self._email     = row['email']

    @property
    def name(self):
        """name of the user"""
        return self._name

    @property
    def surname(self):
        """surname of the user"""
        return self._surname

    @property
    def nick(self):
        """nick of the user"""
        return self._nick

    @property
    def show(self):
        """showed string of the user"""
        return self._show

    @property
    def phone(self):
        """phone number of the user"""
        return self._phone

    @property
    def groups(self):
        """name of groups assigned to the user"""
        return self._groups

    @property
    def ggnumber(self):
        """GG number of the user"""
        return self._ggnumber

    @property
    def email(self):
        """email of the user"""
        return self._nick

_users = None
def Users():
    """Users() -> list
    List of all users in userlist of ekg.
    """
    global _users
    if _users == None:
        cache_userlist()
        sql = SQL()
        _users = []

        query = 'select * from users where not display = "" order by display asc;'
        ret = sql.execute(query)
        for row in ret.fetchall():
            _users.append( User(row) )
        query = 'select * from users where display = "" order by ggnumber asc;'
        ret = sql.execute(query)
        for row in ret.fetchall():
            _users.append( User(row) )
    return _users
