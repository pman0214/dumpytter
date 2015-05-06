# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Shigemi ISHIDA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Institute nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

import os
import ConfigParser

#======================================================================
class Config():
    def __init__(self, conffile=None):
        # if no file name is given, read a default config file.
        if conffile is None:
            conffile = os.environ["HOME"] + "/.dumpytter/config.ini"
        self.conffile = conffile

        # open config file.
        self.__conf = ConfigParser.SafeConfigParser()
        self.__conf.read(self.conffile)
        return

    #--------------------------------------------------
    def get(self):

        # read parameters.
        #   set None when item is not written in the config file.
        try:
            self.consumer_key = self.__conf.get("global", "consumer_key")
            self.consumer_sec = self.__conf.get("global", "consumer_sec")
            self.access_token = self.__conf.get("global", "access_token")
            self.access_sec   = self.__conf.get("global", "access_sec")
        except:
            return False

        # db file name.
        try:
            self.dbfile = self.__conf.get("db", "filename")
        except:
            # set a default DB file.
            self.dbfile = os.environ["HOME"] + "/.dumpytter/dumpytter.db"
            # store to the config file.
            self.__conf.add_section("db")
            self.__conf.set("db", "filename", self.dbfile)
            with open(self.conffile, "wb") as f:
                self.__conf.write(f)

        return True
