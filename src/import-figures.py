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

import json
import os
import sys

import omero_tools

def main(figure_fpath):
    conn = omero_tools.get_connection()
    conn.SERVICE_OPTS.setOmeroGroup(omero_tools.project_gid)

    figure_json = None
    with open(figure_fpath, 'r') as fh:
        figure_json = json.load(fh)

    ## This file id should be the file annotation id.  It shouldn't
    ## exist yet because we're import a new one.  The only reason to
    ## exist is if we were updating an existing figure but we aren't
    ## right?
    if figure_json.has_key('fileId'):
        raise RuntimeError('this figure refers an already existing annotation')

    name = figure_json['figureName']
    ## description of file annotations that were created via the
    ## OMERO.figure plugin also include the image ID of the first
    ## image on the description.  Don't see the point of that so I'm
    ## not doing it.
    description = {'name': name}

    ## Figures created via the OMERO.figure plugin have a fileId
    ## attribute with the file annotation id.  I think we can get away
    ## without it.
    file_ann = conn.createFileAnnfromLocalFile(figure_fpath,
        origFilePathAndName=name, mimetype='application/json',
        ns='omero.web.figure.json', desc=description)

if __name__ == '__main__':
    main(*sys.argv[1:])
