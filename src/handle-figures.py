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

import os.path
import sys


def omero_connection():
    import omero.gateway
    import omero.util.sessions

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


def list_figures():
    conn = omero_connection()
    ## We should be using *all* figures in the mRNA localisation OMERO
    ## group.  However, they have their figures scattered all over the
    ## place so instead we search in all groups and grep by having the
    ## string 'zegami' anywhere in the file name.
    conn.SERVICE_OPTS.setOmeroGroup(-1)

    for fig in conn.getObjects('FileAnnotation',
                               attributes={'ns': 'omero.web.figure.json'}):
        filename = fig.getFileName()
        if 'zegami' not in filename:
            continue
        fig_metadata = filename.split('_')
        print('%i,%s,%s' % (fig.getId(), fig_metadata[0], fig_metadata[2]))


def download_json(dir_path, metadata_fpath):
    fig_ids = [int(line.split(',')[0]) for line in open(metadata_fpath, 'r')]

    conn = omero_connection()
    conn.SERVICE_OPTS.setOmeroGroup(-1)
    for id in fig_ids:
        fig = conn.getObject('FileAnnotation', id)
        if fig is None:
            print("no object with id '%i'" % id)
        with open(os.path.join(dir_path, '%i.json' % id), 'w') as fh:
            for chunk in fig.getFileInChunks():
                fh.write(chunk)


def main(command, *args):
    if command == 'list-figures':
        list_figures(*args)
    elif command == 'download-json':
        download_json(*args)
    else:
        raise RuntimeError("unknown command '%s'" % command)

if __name__ == '__main__':
    main(*sys.argv[1:])
