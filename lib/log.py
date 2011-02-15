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
import sys

from os import getenv

from lib.files import FileManager

class _Logger:

    def init(self):
        """init(self) -> None
        Start of logging to file.
        """
        print "Wszelkie logi mieszczą się w pliku %s." % FileManager.debug_log
        self._fp = open( FileManager.debug_log, 'w', 0 )
        sys.stdout = self._fp
        sys.stderr = self._fp
        print " === Log rozpoczęty === "

    def end(self):
        """end(self) -> None
        End of logging to file
        """
        print " === Log zakończony === "

Log = _Logger()
