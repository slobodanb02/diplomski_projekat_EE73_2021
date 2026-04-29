import sys
from PySide6.QtWidgets import QApplication
from GUI import MainWindowUI
import data_manager
import button_functions

class AppLogic(MainWindowUI):
    def __init__(self):
        super().__init__()

        self.files_path= "./Certificates"
        self.populate_list()
        self.tree.clearSelection()
        self.tree.setCurrentItem(None)
        self.btn_add.clicked.connect(self.handle_add)
        self.btn_edit.clicked.connect(self.handle_edit)
        self.btn_close.clicked.connect(self.handle_delete)

    def populate_list(self):
        data_manager.scan_and_populate_list(self.tree, self.files_path)

    def handle_add(self):
        button_functions.add_new_certificate(self, self.tree, self.files_path)

    def handle_edit(self):
        button_functions.edit_certificate_data(self, self.tree, self.files_path)

    def handle_delete(self):
        button_functions.delete_existing_certificate(self, self.tree, self.files_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppLogic()
    window.show()
    sys.exit(app.exec())