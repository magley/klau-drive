from typing import List
from dataclasses import dataclass
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import requests
from src.gui.dashboard.upload_screen import UploadScreen

import src.service.session as session
from src.gui.common import show_success, show_error
from src.service.update_file import update_file
from src.service.upload_file import FileData
from src.service.list_files import list_files
from src.service.delete_file import delete_file
from src.service.create_album import create_album
from src.service.move_file import move_file
from src.service.get_albums import get_albums
from src.service.download_file import download_file
from src.service.share import share


FILE_TYPE_ALBUM = 'Album'


@dataclass
class MoveFilePopup(QDialog):
    btn_ok: QPushButton
    owner: "FileEdit"
    lst_albums: QListView
    lst_albums_model: QStandardItemModel()
    available_albums: List
    selected_row: int

    def __init__(self, owner: "FileEdit"):
        QDialog.__init__(self)
        self.owner = owner

        self.setModal(True)
        self.setWindowTitle("Move to different album")
        self.available_albums = get_albums()
        self.selected_row = 0

        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.txt_new_album = QLineEdit()
        self.btn_ok = QPushButton("Add")
        self.btn_ok.clicked.connect(self.on_ok)
        self.lst_albums = QListView()
        self.lst_albums_model = QStandardItemModel()
        self.lst_albums.setModel(self.lst_albums_model)
        self.lst_albums.clicked.connect(self.on_click_row)
        self.lst_albums.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        for album in self.available_albums:
            self.lst_albums_model.appendRow(QStandardItem(album['name']))

    def make_layout(self):
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(self.lst_albums)
        main_layout.addWidget(self.btn_ok)

    def on_click_row(self, index: QModelIndex):
        self.selected_row = index.row()

    def on_ok(self):
        album_uuid = self.available_albums[self.selected_row]['album_uuid']

        if self.owner.file_uuid == album_uuid:
            show_error('Cannot move album inside itself.')
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        move_file(self.owner.owner.current_album_uuid, album_uuid, self.owner.file_uuid)
        QApplication.restoreOverrideCursor()

        self.close()


@dataclass
class AddAlbumPopup(QDialog):
    txt_name: QLineEdit
    btn_ok: QPushButton
    owner: "OverviewScreen"

    def __init__(self, owner: "OverviewScreen"):
        QDialog.__init__(self)
        self.owner = owner

        self.setModal(True)
        self.setWindowTitle("Add new album")
        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.txt_name = QLineEdit()
        self.btn_ok = QPushButton("Add")
        self.btn_ok.clicked.connect(self.on_ok)

    def make_layout(self):
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(self.txt_name)
        main_layout.addWidget(self.btn_ok)

    def on_ok(self):
        album_name = self.txt_name.text()

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        create_album(self.owner.current_album_uuid, album_name)
        QApplication.restoreOverrideCursor()

        self.close()


@dataclass
class SharePopup(QDialog):
    txt_name: QLineEdit
    btn_ok: QPushButton
    owner: "FileEdit"

    def __init__(self, owner: "FileEdit"):
        QDialog.__init__(self)
        self.owner = owner

        self.setModal(True)
        self.setWindowTitle("Share with user:")
        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.txt_name = QLineEdit()
        self.btn_ok = QPushButton("Add")
        self.btn_ok.clicked.connect(self.on_ok)

    def make_layout(self):
        main_layout = QVBoxLayout(self)

        main_layout.addWidget(self.txt_name)
        main_layout.addWidget(self.btn_ok)

    def on_ok(self):
        username = self.txt_name.text()

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        share(username, self.owner.file_uuid, self.owner.selected_file.type == FILE_TYPE_ALBUM)
        QApplication.restoreOverrideCursor()

        self.close()


@dataclass
class FileEdit(QGroupBox):
    file_uuid: str
    txt_name: QLineEdit
    txt_desc: QTextEdit
    btn_update: QPushButton
    lbl_upload_date: QLabel
    lbl_modify_date: QLabel
    txt_tag: QLineEdit
    btn_tag_add: QPushButton
    btn_tag_rem: QPushButton
    btn_download: QPushButton
    lst_tags: QListWidget
    btn_switch_file: QPushButton
    btn_delete: QPushButton
    btn_move: QPushButton
    btn_move_dialog: MoveFilePopup
    btn_share: QPushButton
    btn_share_dialog: SharePopup
    lbl_size: QLabel
    owner: "OverviewScreen"
    new_fname: str
    selected_file: FileData
    tags: List[str]


    def __init__(self, owner: "OverviewScreen"):
        QGroupBox.__init__(self)
        self.owner = owner

        self.init_gui()
        self.init_layout()

    def init_gui(self):
        self.file_uuid = ""
        self.new_fname = None
        self.selected_file = None
        self.tags = []
        self.txt_name = QLineEdit()
        self.txt_desc = QTextEdit()
        self.txt_tag = QLineEdit()
        self.btn_tag_add = QPushButton('Add Tag')
        self.btn_tag_rem = QPushButton('Remove Tag')
        self.lst_tags = QListWidget()
        self.lbl_upload_date = QLabel()
        self.lbl_modify_date = QLabel()
        self.lbl_size = QLabel()
        self.btn_update = QPushButton("Save Changes")
        self.btn_switch_file = QPushButton("Pick Different File")
        self.btn_delete = QPushButton("Delete")
        self.btn_move = QPushButton("Move")
        self.btn_download = QPushButton("Download")
        self.btn_share = QPushButton("Share")

        self.txt_tag.setPlaceholderText("Enter tag name")
        self.txt_tag.textEdited.connect(self.set_btn_tag_add_enabled)
        self.btn_tag_add.clicked.connect(self.add_tag)
        self.btn_tag_add.clicked.connect(self.set_btn_tag_add_enabled)
        self.btn_tag_rem.clicked.connect(self.rem_tag)
        self.lst_tags.itemSelectionChanged.connect(self.set_btn_tag_rem_enabled)
        self.btn_switch_file.clicked.connect(self.pick_file)
        self.btn_delete.clicked.connect(self.delete_file)
        self.btn_update.clicked.connect(self.on_click_update)
        self.btn_move.clicked.connect(self.on_click_move)
        self.btn_download.clicked.connect(self.on_click_download)
        self.btn_share.clicked.connect(self.on_click_share)

    def init_layout(self):
        layout_main = QVBoxLayout()

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Size: "))
        h1.addWidget(self.lbl_size)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Uploaded: "))
        h2.addWidget(self.lbl_upload_date)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel("Modified: "))
        h3.addWidget(self.lbl_modify_date)

        layout_main.addWidget(QLabel("Name:"))
        layout_main.addWidget(self.txt_name)
        layout_main.addWidget(QLabel("Description:"))
        layout_main.addWidget(self.txt_desc)

        layout_main.addWidget(QLabel("Tags:"))

        h4 = QHBoxLayout()
        h4.addWidget(self.txt_tag)
        h4.addWidget(self.btn_tag_add)
        h4.addWidget(self.btn_tag_rem)

        layout_main.addLayout(h4)
        layout_main.addWidget(self.lst_tags)

        layout_main.addLayout(h1)
        layout_main.addLayout(h2)
        layout_main.addLayout(h3)

        layout_main.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        layout_main.addWidget(self.btn_move)
        layout_main.addWidget(self.btn_switch_file)
        layout_main.addWidget(self.btn_update)
        layout_main.addWidget(self.btn_delete)
        layout_main.addWidget(self.btn_download)
        layout_main.addWidget(self.btn_share)

        self.setLayout(layout_main)

    def on_selected_file(self, file: FileData):
        self.txt_name.setText(file.name)
        self.file_uuid = file.uuid
        self.txt_desc.setText(file.desc)
        
        self.lbl_size.setText(f"{file.size} B")
        self.lbl_upload_date.setText(file.upload_date.strftime('%a %d %b %Y, %I:%M%p'))
        self.lbl_modify_date.setText(file.last_modified.strftime('%a %d %b %Y, %I:%M%p'))

        self.lst_tags.clear()
        for tag in file.tags:
            self.lst_tags.addItem(QListWidgetItem(tag))
            self.tags.append(tag)

        self.selected_file = file

        self.btn_update.setEnabled(True)
        self.btn_share.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self.btn_move.setEnabled(True)
        self.btn_download.setEnabled(True)
        self.btn_switch_file.setEnabled(True)
        
        if file.shared == True:
            self.btn_update.setEnabled(False)
            self.btn_share.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_move.setEnabled(False)
            self.btn_switch_file.setEnabled(False)
        if file.type == FILE_TYPE_ALBUM:
            self.btn_update.setEnabled(False)
            self.btn_download.setEnabled(False)
            self.btn_switch_file.setEnabled(False)


    def on_click_update(self):
        new_name: str = self.txt_name.text()
        new_desc: str = self.txt_desc.toPlainText()

        new_tags = []
        for x in range(self.lst_tags.count()):
            new_tags.append(self.lst_tags.item(x).text())

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        update_file(
            self.file_uuid,
            new_name,
            new_desc,
            new_tags,
            self.new_fname
        )
        QApplication.restoreOverrideCursor()
        
        self.new_fname = ""

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

    def pick_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File')
        if fname == "":
            self.new_fname = None
        else:
            self.new_fname = fname

    def delete_file(self):
        uuid = self.file_uuid
   
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        result: requests.Response = delete_file(uuid, self.owner.current_album_uuid)
        QApplication.restoreOverrideCursor()

        if result.status_code in [401, 403, 404]:
            show_error(result.json())

    def on_click_move(self):
        self.btn_move_dialog = MoveFilePopup(self)
        self.btn_move_dialog.show()

    def on_click_share(self):
        self.btn_share_dialog = SharePopup(self)
        self.btn_share_dialog.show()
        

    def on_click_download(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Download File', directory = f'{self.selected_file.name}{self.selected_file.type}')
        if fname == "":
            fname = None

        if fname is None:
            return
        
        fname += self.selected_file.type

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        result: requests.Response = download_file(self.file_uuid, self.selected_file.owner)
        QApplication.restoreOverrideCursor()

        with open(fname, 'wb') as f:
            f.write(result)


@dataclass
class OverviewScreen(QWidget):
    owner: QTabWidget
    table: QTableWidget
    edit_region: FileEdit
    files: List[FileData]
    columns: List[str]

    btn_add_album: QPushButton
    btn_add_dialog: AddAlbumPopup
    btn_to_root: QPushButton
    btn_upload: QPushButton

    _current_album_uuid: str
    _current_album_owner: str

    @property
    def current_album_uuid(self) -> str:
        if self._current_album_uuid is None:
            return f"{session.get_username()}_root"
        return self._current_album_uuid

    def __init__(self, owner: QTabWidget):
        QWidget.__init__(self)
        self.owner = owner

        self._current_album_uuid = None
        self._current_album_owner = None

        self.files = []
        self.columns = ['Name', 'Type', 'Date Modified']

        self.init_gui()
        self.make_layout()

    def init_gui(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.clicked.connect(self.on_click_item)
        self.table.itemDoubleClicked.connect(self.on_doubleclick_item)

        self.edit_region = FileEdit(self)
        self.edit_region.setVisible(False)

        self.btn_add_album = QPushButton("New Album")
        self.btn_add_album.clicked.connect(self.on_click_add_album)
        self.btn_add_album.setIcon(QIcon('res/ico_add_folder.png'))

        self.btn_upload = QPushButton("Upload file")
        self.btn_upload.clicked.connect(self.on_click_upload)
        self.btn_upload.setIcon(QIcon('res/ico_add_file.png'))

        self.btn_to_root = QPushButton("Jump to home")
        self.btn_to_root.clicked.connect(self.on_click_to_root)
        self.btn_to_root.setIcon(QIcon('res/ico_home.png'))

    def make_layout(self):
        layout_main = QVBoxLayout()
        layout_top_bar = QHBoxLayout()
        layout_table_edit = QHBoxLayout()

        layout_main.addLayout(layout_top_bar)
        layout_main.addLayout(layout_table_edit)
        
        hsplitter = QSplitter(Qt.Orientation.Horizontal)
        hsplitter.addWidget(self.table)
        hsplitter.addWidget(self.edit_region)
        layout_table_edit.addWidget(hsplitter)

        layout_top_bar.addWidget(self.btn_to_root)
        layout_top_bar.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout_top_bar.addWidget(self.btn_add_album)
        layout_top_bar.addWidget(self.btn_upload)

        self.setLayout(layout_main)

    def refresh(self):
        self.load_files_from_cloud()

    def load_files_from_cloud(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.clear_list()

        self.files = list_files(self.current_album_uuid, self._current_album_owner)
        self.table.setRowCount(len(self.files))

        for row, file in enumerate(self.files):
            file: FileData = file
            self.put_file_in_table(file, row)
            self.table.setRowHeight(row, 8)
        QApplication.restoreOverrideCursor()

    def clear_list(self):
        self.files.clear()
        self.table.clearContents()
        
    def put_file_in_table(self, file: FileData, row: int):
        pixmapi = QStyle.StandardPixmap.SP_FileIcon
        fullname = f"{file.name} {file.type}"

        if file.type == FILE_TYPE_ALBUM:
            pixmapi = QStyle.StandardPixmap.SP_DirIcon
            fullname = f"{file.name}"

        icon = self.style().standardIcon(pixmapi)
        icon_item = QTableWidgetItem()
        icon_item.setIcon(icon)
        icon_item.setText(fullname)

        self.table.setItem(row, 0, QTableWidgetItem(icon_item))
        self.table.setItem(row, 1, QTableWidgetItem(file.type))
        self.table.setItem(row, 2, QTableWidgetItem(file.last_modified.strftime('%a %d %b %Y, %I:%M%p')))

    def on_click_item(self, item: QModelIndex):
        self.edit_region.on_selected_file(self.files[item.row()])
        self.edit_region.setVisible(True)

    def on_doubleclick_item(self, item: QModelIndex):
        file: FileData = self.files[item.row()]
        if file.type == FILE_TYPE_ALBUM:
            self.open_folder(file.uuid, file.owner)

    def on_click_add_album(self):
        self.btn_add_dialog = AddAlbumPopup(self)
        self.btn_add_dialog.show()

    def open_folder(self, uuid, owner):
        self._current_album_uuid = uuid
        self._current_album_owner = owner
        self.refresh()

    def on_click_to_root(self):
        self.open_folder(f"{session.get_username()}_root", None)

    def on_click_upload(self):
        self.btn_add_dialog = UploadScreen(self.current_album_uuid)
        self.btn_add_dialog.show()