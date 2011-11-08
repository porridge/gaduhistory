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

import csv, codecs, cStringIO
from lib.gui.locals import encode_string, create_unicode

class ekg_dialect(csv.Dialect):
    """dialect of the file with history of ekg."""
    delimiter = ","
    doublequote = True
    escapechar = "\\"
    lineterminator = "\n"
    quotechar = '"'
    quoting = True
    skipinitialspace = False

class userlist_dialect(csv.Dialect):
    """dialect of the file with userlist of ekg."""
    delimiter = ";"
    doublequote = True
    escapechar = "\\"
    lineterminator = "\r\n"
    quotechar = '"'
    quoting = True
    skipinitialspace = False

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return encode_string(self.reader.next())

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=ekg_dialect, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [create_unicode(text) for text in row]

    def __iter__(self):
        return self

class GaduReader(object):
    def __init__(self, file, encoding="iso-8859-2", dialect = ekg_dialect ):
        self._f = UTF8Recoder(file, encoding)
        self.dialect = dialect

    def next(self):
        row = []
        line = self._f.next().strip()
        last_str = ''
        last_char = ''

        is_quoting = False
        for char in line:
            if char == self.dialect.escapechar:
                if last_char == self.dialect.escapechar:
                    last_str += self.dialect.escapechar
            elif last_char == self.dialect.escapechar:
                if char == 'n':
                    last_str += "\n"
                elif char == 'r':
                    pass
                else:
                    last_str += char
            elif not is_quoting:
                if char == self.dialect.delimiter:
                    row.append( last_str )
                    last_str = ''
                elif char == self.dialect.quotechar and last_char == self.dialect.delimiter:
                    is_quoting = True
                else:
                    last_str += char
            else:
                if char == self.dialect.quotechar:
                    is_quoting = False
                    row.append( last_str )
                    last_str = ''
                else:
                    last_str += char
            last_char = char
        row.append( last_str )
        return [create_unicode(text) for text in row]

    def __iter__(self):
        return self
