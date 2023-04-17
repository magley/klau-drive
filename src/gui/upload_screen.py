from PyQt6.QtWidgets import *

class UploadScreen(QWidget):
    def __init__(self, win: QStackedWidget):
        QWidget.__init__(self)
        
        self.fname: str = None

        self.win = win
        self.btn_pick: QPushButton
        self.lbl_fname = QLabel
        self.txt_desc: QLineEdit
        self.btn_upload: QPushButton

        self.init_gui()
        self.make_layout()


    def init_gui(self):
        self.btn_pick = QPushButton("Select File")
        self.lbl_fname = QLabel("No File Selected")
        self.txt_desc = QLineEdit()
        self.btn_upload = QPushButton('Upload')

        self.txt_desc.setPlaceholderText("Enter description")
        self.btn_pick.clicked.connect(self.pick_file)
        self.btn_pick.clicked.connect(self.set_btn_upload_enabled)
        self.btn_upload.clicked.connect(self.upload_file)
        self.set_btn_upload_enabled()


    def make_layout(self):
        layout_main = QVBoxLayout()
        
        layout_file_pick = QHBoxLayout()
        layout_file_pick.addWidget(self.btn_pick)
        layout_file_pick.addWidget(self.lbl_fname)

        layout_main.addLayout(layout_file_pick)
        layout_main.addWidget(self.txt_desc)
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


    def upload_file(self):
        fname: str = self.fname
        desc: str = self.txt_desc.text()

        print(fname, desc)