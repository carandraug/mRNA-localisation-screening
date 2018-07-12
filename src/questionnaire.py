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

import sys

from PyQt5 import QtWidgets


questions = [
    'Is the RNA localized in the mushroom body lobe?',
    'Is the protein localized in the mushroom body lobe?',
    'Is the RNA localized in the mushroom body heel?',
    'Is the protein localized in the mushroom body heel?',
]


class Answers(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Answers, self).__init__(*args, **kwargs)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QRadioButton('yes'))
        layout.addWidget(QtWidgets.QRadioButton('no'))

        ## The last one (unsure) is the default)
        button = QtWidgets.QRadioButton('unsure')
        button.setChecked(True)
        layout.addWidget(button)
        self.setLayout(layout)


class QuestionWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(QuestionWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle('Blind Questions')

        ## layout is a vertical box.  First row is a button to open
        ## image on separate application.  Second row is a grid with
        ## the questions and answers.
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QPushButton('open in Viewer'))

        grid_box = QtWidgets.QGroupBox()
        grid = QtWidgets.QGridLayout()
        for i in range(len(questions)):
            grid.addWidget(QtWidgets.QLabel(questions[i]), i, 0)
            grid.addWidget(Answers(), i, 1)
        grid_box.setLayout(grid)

        layout.addWidget(grid_box)

        layout.addWidget(QtWidgets.QPushButton('save and next'))

        self.setLayout(layout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = QuestionWindow()
    window.show()
    sys.exit(app.exec_())
