from typing import List
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from src.lambdas.upload_file import upload_file, init, list_files
import json


class UploadScreen(QWidget):
    def __init__(self, win: QStackedWidget):
        QWidget.__init__(self)
        
        self.fname: str = None
        self.tags: List[str] = []

        self.win = win
        self.btn_pick: QPushButton = None
        self.lbl_fname: QLabel = None
        self.txt_desc: QTextEdit = None
        self.txt_tag: QLineEdit = None
        self.btn_tag_add: QPushButton = None
        self.btn_tag_rem: QPushButton = None
        self.lst_tags: QListWidget = None
        self.btn_upload: QPushButton = None

        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.btn_pick = QPushButton("Select File")
        self.lbl_fname = QLabel("No File Selected")
        self.txt_desc = QTextEdit()
        self.txt_tag = QLineEdit()
        self.btn_tag_add = QPushButton('Add Tag')
        self.btn_tag_rem = QPushButton('Remove Tag')
        self.lst_tags = QListWidget()
        self.btn_upload = QPushButton('Upload')

        self.txt_desc.setPlaceholderText("Enter description")
        self.txt_tag.setPlaceholderText("Enter tag name")
        self.btn_tag_add.clicked.connect(self.add_tag)
        self.btn_tag_add.clicked.connect(self.set_btn_tag_add_enabled)
        self.btn_tag_rem.clicked.connect(self.rem_tag)
        self.txt_tag.textEdited.connect(self.set_btn_tag_add_enabled)
        self.lst_tags.itemSelectionChanged.connect(self.set_btn_tag_rem_enabled)
        self.btn_pick.clicked.connect(self.pick_file)
        self.btn_pick.clicked.connect(self.set_btn_upload_enabled)
        self.btn_upload.clicked.connect(self.upload_file)

        self.set_btn_upload_enabled()
        self.set_btn_tag_add_enabled()
        self.set_btn_tag_rem_enabled()

    def make_layout(self):
        layout_main = QVBoxLayout()
        
        layout_file_pick = QHBoxLayout()
        layout_file_pick.addWidget(self.btn_pick)
        layout_file_pick.addWidget(self.lbl_fname)
        layout_main.addLayout(layout_file_pick)

        layout_file_details = QHBoxLayout()
        layout_file_details.addWidget(self.txt_desc)

        layout_file_tags = QVBoxLayout()
        layout_file_tags_input = QHBoxLayout()
        layout_file_tags_input.addWidget(self.txt_tag)
        layout_file_tags_input.addWidget(self.btn_tag_add)
        layout_file_tags_input.addWidget(self.btn_tag_rem)

        layout_file_tags.addLayout(layout_file_tags_input)
        layout_file_tags.addWidget(self.lst_tags)
        layout_file_details.addLayout(layout_file_tags)
        layout_main.addLayout(layout_file_details)

        layout_main.addWidget(self.btn_upload)
        layout_main.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(layout_main)

    def pick_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File')
        if fname == "":
            self.lbl_fname.setText("No File Selected")
            self.fname = None
        else:
            self.lbl_fname.setText(fname)
            self.fname = fname


    def set_btn_upload_enabled(self):
        if self.fname is None:
            self.btn_upload.setEnabled(False)
        else:
            self.btn_upload.setEnabled(True)

    def set_btn_tag_add_enabled(self):
        if self.txt_tag.text().strip() == "":
            self.btn_tag_add.setEnabled(False)
        else:
            self.btn_tag_add.setEnabled(True)  

    def set_btn_tag_rem_enabled(self):
        if len(self.lst_tags.selectedIndexes()) == 0:
            self.btn_tag_rem.setEnabled(False)
        else:
            self.btn_tag_rem.setEnabled(True)

    def add_tag(self):
        new_tag = self.txt_tag.text()
        self.tags.append(new_tag)
        self.lst_tags.addItem(QListWidgetItem(new_tag))
        self.txt_tag.setText("")

    def rem_tag(self):
        selected_rows = [t.row() for t in self.lst_tags.selectedIndexes()]
        for row in selected_rows:
            self.tags.remove(self.tags[row])
            self.lst_tags.takeItem(row)

    def clear_form(self):
        self.tags.clear()
        self.lst_tags.clear()
        self.txt_tag.clear()
        self.txt_desc.clear()
        self.lbl_fname.setText("No File Selected")
        self.fname = None

    def upload_file(self):
        fname: str = self.fname
        desc: str = self.txt_desc.toPlainText()
        tags: List[str] = self.tags

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        init() # All buckets and tables will be deleted before this file is uploaded. Remove this later (maybe call it one time, after the program boots up)
        upload_file(fname, desc, tags)
        for file in list_files():
            print(json.dumps(file, indent=2, default=str))

        self.clear_form()
        QApplication.restoreOverrideCursor()