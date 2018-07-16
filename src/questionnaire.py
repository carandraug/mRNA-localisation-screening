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
import pickle
import subprocess
import sys

from PyQt5 import QtWidgets


LABELS = ('yes', 'no', 'unsure')
DEFAULT_LABEL = 'unsure'

class Questionnaire(QtWidgets.QWidget):
    default_label_idx = LABELS.index(DEFAULT_LABEL)

    def __init__(self, questions, *args, **kwargs):
        super(Questionnaire, self).__init__(*args, **kwargs)
        self.questions = questions
        self.answers = [None] * len(questions)
        self.set_ui()

    def set_ui(self):
        grid_box = QtWidgets.QGroupBox()
        grid = QtWidgets.QGridLayout()

        ## Header
        for i, label in enumerate(LABELS):
            grid.addWidget(QtWidgets.QLabel(label), 0, i+1)

        ## Questions/Answers
        for i, question in enumerate(self.questions):
            grid.addWidget(QtWidgets.QLabel(question), i+1, 0)

            self.answers[i] = QtWidgets.QButtonGroup(parent=self)
            for j in range(len(LABELS)):
                button = QtWidgets.QRadioButton(parent=self)
                if j == Questionnaire.default_label_idx:
                    button.setChecked(True)
                ## Manually set id with the index for labels list.
                self.answers[i].addButton(button, id=j)
                grid.addWidget(button, i+1 , j+1)

        self.setLayout(grid)

    def to_serializable(self):
        results = dict()
        for question, answer in zip(self.questions, self.answers):
            results[question] = LABELS[answer.checkedId()]
        return results

    def reset(self):
        for answer in self.answers:
            answer.button(Questionnaire.default_label_idx).setChecked(True)


class QuestionWindow(QtWidgets.QWidget):
    def __init__(self, questions, answers_dir, img_fpaths,
                 *args, **kwargs):
        super(QuestionWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle('Blind Questions')

        self.answers_dir = answers_dir
        self.img_fpaths = img_fpaths
        self.current_img = 0

        if len(img_fpaths) < 1:
            raise RuntimeError('no images to question')

        open_button = QtWidgets.QPushButton('Open in Viewer', parent=self)
        open_button.clicked.connect(self.open_image)

        self.questionnaire = Questionnaire(questions, parent=self)

        save_button = QtWidgets.QPushButton('save and next', parent=self)
        save_button.clicked.connect(self.save_and_next)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(open_button)
        layout.addWidget(self.questionnaire)
        layout.addWidget(save_button)
        self.setLayout(layout)
        print "list is ", self.img_fpaths

    def open_image(self):
        fig_file = self.img_fpaths[self.current_img]
        args = ['xdg-open', fig_file]
        status = subprocess.call(args, shell=False)
        if status != 0:
            error_dialog = QtWidgets.QErrorMessage(parent=self)
            error_dialog.setModal(True)
            error_dialog.showMessage("failed to call %s" % args)

    def save_and_next(self):
        fig_file = self.img_fpaths[self.current_img]
        fname = os.path.splitext(os.path.basename(fig_file))[0]
        fpath = os.path.join(self.answers_dir, fname + '.pickle')
        if os.path.exists(fpath):
            raise RuntimeError('file already exists, do not overwrite results')
        with open(fpath, 'wb') as fh:
            pickle.dump(self.questionnaire.to_serializable(), fh)

        self.next_image()

    def next_image(self):
        self.questionnaire.reset()
        self.current_img +=1
        if not self.current_img < len(self.img_fpaths):
            error_dialog = QtWidgets.QErrorMessage(parent=self)
            error_dialog.setModal(True)
            error_dialog.showMessage("This is the end.")
            error_dialog.exec_()
            QtWidgets.qApp.quit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    questions_fpath = sys.argv[1]
    questions = [l.strip() for l in open(questions_fpath, 'r').readlines()]

    answers_dir = sys.argv[2]

    img_fpaths = sys.argv[3:]

    window = QuestionWindow(questions, answers_dir, img_fpaths)
    window.show()
    sys.exit(app.exec_())
