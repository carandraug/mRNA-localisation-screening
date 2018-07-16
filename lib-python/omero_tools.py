#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (C) 2018 David Pinto <david.pinto@bioch.ox.ac.uk>
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import omero.gateway
import omero.util.sessions

def get_connection():
    store = omero.util.sessions.SessionsStore()
    if store.count() < 1:
        raise RuntimeError('no OMERO sessions around')
    session_props = store.get_current()
    session_uuid = session_props[2]
    if not session_uuid:
        raise RuntimeError('current session has no UUID')
    conn = omero.gateway.BlitzGateway(host=session_props[0],
                                      port=session_props[3])
    if not conn.connect(session_uuid):
        raise RuntimeError('failed to connect to session')
    return conn
