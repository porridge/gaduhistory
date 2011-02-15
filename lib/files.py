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


from optparse import OptionParser, OptionValueError
from os import getenv, path, mkdir

KNOWN_CLIENTS = ['ekg', 'ekg2']

class _FileManager(object):
    def __init__(self):
        self.home = getenv('HOME')
        if not self.home:
            raise EnvironmentError('$HOME not defined')
        parser = OptionParser()
        parser.add_option('-c', '--client', default='ekg',
                        help='Read history from the given client program. '
                        'Supported values: ' + ', '.join(KNOWN_CLIENTS))
        parser.add_option('-s', '--session', default=None,
                        help='Session identifier for clients which require one. '
                        'Example: gg:123456')
        (options, args) = parser.parse_args()

        if options.client == 'ekg':
            self._base_path = path.join(self.home, '.gg', 'gaduhistory')
            if not path.exists(self._base_path):
                mkdir(self._base_path)
            self.user_list = path.join(self.home, '.gg', 'userlist')
            self.history_of = self._gg_history_of
            self.history_encoding = 'iso-8859-2'

        elif options.client == 'ekg2':
            if options.session:
                self._session = options.session
            else:
                raise OptionValueError('No session specified for ekg2.')

            self._base_path = path.join(self.home, '.ekg2', 'gaduhistory')
            if not path.exists(self._base_path):
                mkdir(self._base_path)
            self._base_path = path.join(self._base_path, self._session)
            if not path.exists(self._base_path):
                mkdir(self._base_path)
            self.user_list = path.join(self.home, '.ekg2', self._session + '-userlist')
            self.history_of = self._ekg2_history_of
            self.history_encoding = 'utf-8'
        else:
            raise OptionValueError('Unknown client ' + options.client)

        self.debug_log = self._base('debug.log')
        self.cache = self._base('cache.db')

    def _base(self, *components):
        return path.join(self._base_path, *components)

    def _history_dir(self):
        return path.join(self.home, '.gg', 'history' )
    
    def _gg_history_of(self, number):
        return path.join(self.home, '.gg', 'history', str(number))

    def _ekg2_history_of(self, number):
        return path.join(self.home, '.ekg2', 'logs', self._session,
                       'gg:%s.txt' % str(number))

    def has_history(self, number):
        return path.exists(self.history_of(number))

FileManager = _FileManager()
