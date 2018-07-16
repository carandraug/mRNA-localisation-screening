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

import omero_tools


def main():
    conn = omero_tools.get_connection()
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
        print('%d,%s,%s' % (fig.getId(), fig_metadata[0], fig_metadata[2]))


if __name__ == '__main__':
    main()
