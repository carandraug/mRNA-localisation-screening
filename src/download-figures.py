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
import os.path
import sys

import omero_tools


## OMERO image ID with a blank image.  It is used to place text in
## arbitrary figure locations.
BLANK_IMAGE_ID = 283965


def main(dir_path, metadata_fpath):
    metadata = [line.split(',') for line in open(metadata_fpath, 'r')]

    conn = omero_tools.get_connection()
    conn.SERVICE_OPTS.setOmeroGroup(-1)
    for fig_metadata in metadata:
        fig_id = int(fig_metadata[0])
        gene_name = fig_metadata[1]

        fig = conn.getObject('FileAnnotation', fig_id)
        if fig is None:
            print("no object with id '%d'" % fig_id)
        fig_json = json.loads("".join(fig.getFileInChunks()))

        ## The gene name is in the 'title' of the figure.  The 'title'
        ## is the label of a panel with a blank image.  We want to
        ## remove this panel so that the scoring is done blindly.
        ## However, the same image is used in other places in the
        ## figure to introduce text and we want to keep those.  So
        ## only remove panels if the gene name is used in the label.
        panels = fig_json['panels']
        for i, panel in enumerate(panels):
            if panel['imageId'] == BLANK_IMAGE_ID:
                if any([gene_name in l['text'] for l in panel['labels']]):
                    panels.pop(i)
                    break
        with open(os.path.join(dir_path, '%d.json' % fig_id), 'w') as fh:
            json.dump(fig_json, fh)


if __name__ == '__main__':
    main(*sys.argv[1:])
