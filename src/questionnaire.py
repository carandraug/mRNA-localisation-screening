#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (C) 2020 David Pinto <david.pinto@bioch.ox.ac.uk>
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

## SYNOPSIS
##   questionnaire QUESTIONS-FPATH SAVE-DIR [IMG-FPATHS ...]
##      Run the following command from the src directory:
##          >python3 questionnaire.py questions.py answers/ figures/*.jpg
##
## FORMAT OF QUESTIONS FILE
##
##   The questions file is a python file with a QUESTIONS variable.
##   This QUESTIONS variable must be a list of objects subclassing
##   QuestionWidget (see source code).  There are CheckQuestion,
##   RadioQuestion, and TextQuestion:
##
##       CheckQuestion provides a question with multiple answers with
##           the choice of selecting multiple ones.
##
##       RadioQuestion provides a question with multiple answers with
##           the possibility of selecting only one.
##
##       TextQuestion provides a question and a box to type any
##           answer.
##
##   For example:
##
##       QUESTIONS = [
##           RadioQuestion('Level of expression',
##                         ('none', 'low', 'high')),
##           TextQuestion('What is the problem on this image?',
##                        'This is the initial answer text'),
##           CheckQuestion('How is the distribution?',
##                         ('Punctate', 'Diffuse', 'Nuclear')),
##       ]


import argparse
import collections.abc
import os
import os.path
import pickle
import subprocess
import sys
import typing
import pandas as pd
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QFileDialog


class QuestionWidget(QtWidgets.QWidget):
    def __init__(self, question: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._question = QtWidgets.QLabel(text=question, parent=self)

    def to_serializable(self) -> typing.Tuple[str, str]:
        """Two element tuple with question and answer text"""
        raise NotImplementedError()

    def reset(self) -> None:
        raise NotImplementedError()

class RadioQuestion(QuestionWidget):
    """QuestionWidget for group of radio buttons."""
    def __init__(self, question: str, options: typing.Sequence[str],
                 *args, **kwargs) -> None:
        super().__init__(question, *args, **kwargs)
        self._answer = QtWidgets.QButtonGroup(parent=self)

        for i, option in enumerate(options):
            button = QtWidgets.QRadioButton(text=option, parent=self)
            # By default, select first option.  We need to
            # start with one select otherwise we may end in a
            # state where none is selected.
            if i == 0:
                button.setChecked(True)
            self._answer.addButton(button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._question)
        button_box = QtWidgets.QHBoxLayout()
        for button in self._answer.buttons():
            button_box.addWidget(button)
        button_box.addStretch() # left align buttons
        layout.addLayout(button_box)
        self.setLayout(layout)

    def to_serializable(self) -> typing.Tuple[str, str]:
        return (self._question.text(),
                self._answer.checkedButton().text())

    def reset(self) -> None:
        self._answer.buttons()[0].setChecked(True)


class CheckQuestion(QuestionWidget):
    """QuestionWidget for group of check boxes."""
    def __init__(self, question: str, options: typing.Sequence[str],
                 *args, **kwargs) -> None:
        super().__init__(question, *args, **kwargs)
        self._answer = QtWidgets.QButtonGroup(parent=self)
        self._answer.setExclusive(False)

        for i, option in enumerate(options):
            button = QtWidgets.QCheckBox(text=option, parent=self)
            self._answer.addButton(button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._question)
        button_box = QtWidgets.QHBoxLayout()
        for button in self._answer.buttons():
            button_box.addWidget(button)
        button_box.addStretch() # left align buttons
        layout.addLayout(button_box)
        self.setLayout(layout)

    def to_serializable(self) -> typing.Tuple[str, str]:
        answers = [b.text() for b in self._answer.buttons() if b.isChecked()]
        return (self._question.text(), '\t'.join(answers))

    def reset(self) -> None:
        for button in self._answer.buttons():
            button.setChecked(False)


class TextQuestion(QuestionWidget):
    """QuestionWidget for text box."""
    def __init__(self, question: str, start_text: str = '',
                 *args, **kwargs) -> None:
        super().__init__(question, *args, **kwargs)
        self._answer = QtWidgets.QPlainTextEdit(start_text, parent=self)
        self._start_text = start_text

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._question)
        layout.addWidget(self._answer)
        self.setLayout(layout)

    def to_serializable(self) -> typing.Tuple[str, str]:
        return (self._question.text(),
                self._answer.toPlainText())

    def reset(self) -> None:
        self._answer.setPlainText(self._start_text)


class Questionnaire(QtWidgets.QWidget):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._questions = questions

        layout = QtWidgets.QVBoxLayout()
        for question in self._questions:
            layout.addWidget(question)
        self.setLayout(layout)

    def to_serializable(self):
        return [q.to_serializable() for q in self._questions]

    def reset(self):
        for question in self._questions:
            question.reset()


class QuestionWidget(QtWidgets.QWidget):
    def __init__(self, questions, save_dir, img_fpaths,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Blind Questions')

        self.save_dir = save_dir
        self.img_fpaths = img_fpaths
        self.current_img = 0

        if len(img_fpaths) < 1:
            raise RuntimeError('no images to question')

        open_button = QtWidgets.QPushButton('Open in Viewer', parent=self)
        open_button.clicked.connect(self.open_image)
        self.questionnaire = Questionnaire(questions, parent=self)

        save_button = QtWidgets.QPushButton('save and next', parent=self)
        save_button.clicked.connect(self.save_and_next)

        back_button = QtWidgets.QPushButton('previous image', parent=self)
        back_button.clicked.connect(self.prev_image)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(open_button)
        layout.addWidget(self.questionnaire)
        layout.addWidget(save_button)
        layout.addWidget(back_button)
        self.setLayout(layout)

    def open_image(self):
        fig_file = self.img_fpaths[self.current_img]

        # use these lines to open in Preview on Mac
        #export_command = "open "+fig_file
        #self.viewer = subprocess.Popen(export_command, shell=True, stdout=subprocess.PIPE)
        #subprocess.Popen(export_command, shell=True, stdout=subprocess.PIPE)

        # use these lines to open with PIL
        im = Image.open(fig_file)
        self.viewer = im.show('image')

        # use these lines to open in Linux
        #args = ['xdg-open', fig_file]
        #self.viewer = subprocess.Popen(args, shell=False)

        # removed this to enable PIL
        #if not self.viewer.returncode is None:
        #    error_dialog = QtWidgets.QErrorMessage(parent=self)
        #    error_dialog.setModal(True)
        #    error_dialog.showMessage("failed to call %s" % args)

    def save_and_next(self):
        fig_file = self.img_fpaths[self.current_img]
        fname = os.path.splitext(os.path.basename(fig_file))[0]
        fpath = os.path.join(self.save_dir, fname + '.pickle')
        if os.path.exists(fpath):
            #error_dialog = QtWidgets.QErrorMessage(parent=self)
            #error_dialog.setModal(True)
            #error_dialog.showMessage('A file named \'%s\' for this image'
            #                         ' answers already exists.  Doing nothing'
            #                         ' until that is resolved' % fpath)
            #error_dialog.exec_();

            warning_dialog = QMessageBox()
            warning_dialog.setIcon(QMessageBox.Warning)
            warning_dialog.setText('File already exists. Do you want to replace it?')
            warning_dialog.setStandardButtons(QMessageBox.Cancel)
            replace_button = warning_dialog.addButton('Replace', QMessageBox.YesRole)
            replace_button.clicked.connect(self.write_files)
            warning_dialog.exec_()
            return

        self.write_files()

    def write_files(self):
        fig_file = self.img_fpaths[self.current_img]
        fname = os.path.splitext(os.path.basename(fig_file))[0]
        fpath = os.path.join(self.save_dir, fname + '.pickle')
        with open(fpath, 'wb') as fh:
            pickle.dump(self.questionnaire.to_serializable(), fh)

        # Close the image viewer to prevent situation where the users
        # ends up with more than one image to score open and
        # accidentally scores the wrong one.
        #self.viewer.terminate()
        export_command = """osascript -e 'quit app "PREVIEW"'"""
        subprocess.Popen(export_command, shell=True, stdout=subprocess.PIPE)
        self.next_image()
        self.parse_pickles()

    def next_image(self):
        self.questionnaire.reset()
        self.current_img +=1
        if not self.current_img < len(self.img_fpaths):
            error_dialog = QtWidgets.QErrorMessage(parent=self)
            error_dialog.setModal(True)
            error_dialog.showMessage("This is the end. Building database.")
            #exec(open('buildZegamiDatabase.py').read(), globals(), locals())
            #import buildZegamiDatabase #bad practice, but the line above does not find variables properly
            import runFlymineQueries
            error_dialog.exec_()
            QtWidgets.qApp.quit()

    def prev_image(self):
        self.questionnaire.reset()
        self.current_img -=1
        if not self.current_img < len(self.img_fpaths):
            error_dialog = QtWidgets.QErrorMessage(parent=self)
            error_dialog.setModal(True)
            error_dialog.showMessage("This is the end.")
            error_dialog.exec_()
            QtWidgets.qApp.quit()

        # Close the image viewer to prevent situation where the users
        # ends up with more than one image to score open and
        # accidentally scores the wrong one.
        #self.viewer.terminate()
        export_command = """osascript -e 'quit app "PREVIEW"'"""
        subprocess.Popen(export_command, shell=True, stdout=subprocess.PIPE)
        self.open_image()

    def parse_pickles(self):
        infiles = os.listdir(self.save_dir)
        figure_list = []
        d = {}

        for file in infiles:
            if file.endswith('.pickle'):
                figure_list.append(file[:-7])

        for figure in figure_list:
            thisfile = os.path.join(self.save_dir, str(figure)+'.pickle')
            try:
                with open(thisfile, 'rb') as f:
                    p = pickle.load(f)
                    #some modifications to deal with the new pickle format
                    col_names = [x[0] for x in p]
                    d[figure] = [x[1] for x in p]
            except:
                pass

        df = pd.DataFrame.from_dict(d, orient = 'index', columns = col_names)
        df.index.name = 'figure_id'
        df.to_csv(os.path.join(self.save_dir, 'questionnaire_results.csv'))

        # open next image after saving the previous image
        fig_file = self.img_fpaths[self.current_img]
        im = Image.open(fig_file)
        self.viewer = im.show('image')

class QuestionWindow(QtWidgets.QMainWindow):
    def __init__(self, questions, save_dir, img_fpaths,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = QuestionWidget(questions, save_dir, img_fpaths,
                                     parent=self)

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidget(self.widget)
        self.scroll_area.setAlignment(QtCore.Qt.AlignHCenter)
        self.setCentralWidget(self.scroll_area)


def validate_questions(questions) -> None:
    if not isinstance(questions, collections.abc.Sequence):
        raise ValueError('QUESTIONS must be a sequence')
    if any([isinstance(q, QuestionWidget) for q in questions]):
        raise ValueError('Questions must be a sequence of QuestionWidgets')


def read_questions(filepath: str) -> typing.Sequence[QuestionWidget]:
    contents = {
        'CheckQuestion' : CheckQuestion,
        'RadioQuestion' : RadioQuestion,
        'TextQuestion' : TextQuestion,
    }
    try:
        exec(open(filepath).read(), contents)
    except:
        raise RuntimeError('could not read QUESTIONS file %s' % filepath)
    if 'QUESTIONS' not in contents:
        raise ValueError('could not find QUESTIONS on file %s' % filepath)
    questions = contents['QUESTIONS']
    validate_questions(questions)
    return questions


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(prog='mRNA loc questionnaire')
    parser.add_argument('questions_fpath', action='store', type=str,
                        help='Filepath for python file with questions')
    parser.add_argument('save_dir', action='store', type=str,
                        help='Directory where to save the answers')
    parser.add_argument('img_fpaths', action='store', type=str, nargs='+',
                        help='Image files to make questions about')
    args = parser.parse_args(arguments[1:])
    if not os.path.isfile(args.questions_fpath):
        raise ValueError('no file \'%s\' for questions' % args.questions_fpath)
    if not os.path.isdir(args.save_dir):
        raise ValueError('no dir \'%s\' to save answers' % args.save_dir)
    for img_fpath in args.img_fpaths:
        if not os.path.isfile(img_fpath):
            raise ValueError('no img file \'%s\'' % img_fpath)
    return args

def main(argv):
    app = QtWidgets.QApplication(argv)

    args = parse_arguments(app.arguments())
    questions = read_questions(args.questions_fpath)

    # conditional statement to avoid opening images that have already been scored
    img_fpaths = [x for x in args.img_fpaths if os.path.splitext(os.path.basename(x))[0]+".pickle" not in os.listdir(args.save_dir)]

    window = QuestionWindow(questions, args.save_dir, img_fpaths)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)
