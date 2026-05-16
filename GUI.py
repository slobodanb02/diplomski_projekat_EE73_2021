from PySide6.QtWidgets import (QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QTreeWidget, QPushButton,
                             QGroupBox, QFrame, QDialog, QMenu, QInputDialog, QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget, QTabBar, QLineEdit, QLabel, QComboBox)
from PySide6.QtCore import Qt
import data_manager
import graph_view
AVAILABLE_COLUMNS = [
    "Range", "Measured Value", "Reference Value", 
    "Frequency", "Error", "Error Uncertainty"  
]

class MainWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PilotProject")
        self.setFixedSize(600, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        master_layout = QHBoxLayout(central_widget)

        self.left_panel = QGroupBox("Instruments")
        self.left_panel.setFixedWidth(320)
        
        panel_layout = QVBoxLayout(self.left_panel)
    
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["TYPE", "SN"])
        self.tree.setFixedHeight(400)
        self.tree.header().setStretchLastSection(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        panel_layout.addWidget(self.tree)

        button_grid = QGridLayout()
        self.btn_add = QPushButton("Add")
        self.btn_edit = QPushButton("Edit")
        self.btn_close = QPushButton("Remove device")

        button_grid.addWidget(self.btn_add, 0, 0)
        button_grid.addWidget(self.btn_edit, 0, 1)
        button_grid.addWidget(self.btn_close, 1, 0, 1, 2) 

        panel_layout.addLayout(button_grid)
        master_layout.addWidget(self.left_panel)

        self.right_container = QFrame() 
        right_layout = QVBoxLayout(self.right_container)
        right_layout.setContentsMargins(10, 20, 10, 20)
        right_layout.setAlignment(Qt.AlignCenter)

        self.btn_display_data = QPushButton("Display data")
        self.btn_display_data.setMinimumSize(150, 40)
        right_layout.addWidget(self.btn_display_data)
        master_layout.addWidget(self.right_container, stretch=1)

class CertEditDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle("Certification Editor")
        self.resize(1000, 700)
        
        self.main_layout = QVBoxLayout(self)
        
        self.year_tabs = QTabWidget()
        self.year_tabs.setTabsClosable(True)
        self.year_tabs.tabBarDoubleClicked.connect(self.rename_year_tab)
        self.year_tabs.tabCloseRequested.connect(self.remove_year)
        
        self.controls = QHBoxLayout()
        
        self.btn_add_year = QPushButton("Add New Year")
        self.btn_add_property = QPushButton("Add New Property")
        self.btn_save = QPushButton("Save Changes")
        
        self.btn_save.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        
        self.btn_add_year.clicked.connect(self.handle_add_and_rename_year)
        self.btn_add_property.clicked.connect(self.add_property_to_current_year)
        self.btn_save.clicked.connect(self.save_to_json)
        
        self.controls.addWidget(self.btn_add_year)
        self.controls.addWidget(self.btn_add_property)
        self.controls.addStretch()
        self.controls.addWidget(self.btn_save)
        
        self.main_layout.addLayout(self.controls)
        self.main_layout.addWidget(self.year_tabs)

        if not self.load_from_json():
            self.add_year()
        
    def save_to_json(self):
        raw_years_ui_list = []
        
        for i in range(self.year_tabs.count()):
            year_name = self.year_tabs.tabText(i)
            inner_tabs = self.year_tabs.widget(i).findChild(QTabWidget)

            year_entry = {"name": year_name, "properties": []}
            if inner_tabs:
                for j in range(inner_tabs.count()):
                    table = inner_tabs.widget(j).findChild(QTableWidget)

                    headers = [table.horizontalHeaderItem(c).text() if table.horizontalHeaderItem(c) 
                               else f"Column {c+1}" for c in range(table.columnCount())]

                    table_data = [[(table.item(r, c).text() if table.item(r, c) else "") 
                                   for c in range(table.columnCount())] 
                                  for r in range(table.rowCount())]

                    year_entry["properties"].append({
                        "name": inner_tabs.tabText(j),
                        "headers": headers,
                        "data": table_data
                    })
            raw_years_ui_list.append(year_entry)

        if data_manager.prepare_and_save_certificate_data(self.file_path, raw_years_ui_list):
            QMessageBox.information(self, "Saved", "Changes saved to disk successfully.")

    def load_from_json(self):
        content = data_manager.load_certificate(self.file_path)
        if not content or "years" not in content:
            return False

        self.year_tabs.clear()

        for year_data in content["years"]:
            year_container, inner_tabs = self.add_year(year_data["name"], auto_populate=False)
            
            for prop_data in year_data.get("properties", []):
                self.create_property_sheet(
                    inner_tabs, 
                    name=prop_data["name"], 
                    data=prop_data.get("data"),
                    headers=prop_data.get("headers")
                )
        return True

    def handle_add_and_rename_year(self):
        _, _ = self.add_year()
        
        new_tab_index = self.year_tabs.count() - 1
        
        self.year_tabs.setCurrentIndex(new_tab_index)
        
        success = self.prompt_rename_year(new_tab_index)
        
        if not success:
            self.year_tabs.removeTab(new_tab_index)

    def add_year(self, name=None, auto_populate=True):
        year_container = QWidget()
        year_layout = QVBoxLayout(year_container)
        
        inner_tabs = QTabWidget()
        inner_tabs.setTabsClosable(True)
        inner_tabs.tabBarDoubleClicked.connect(lambda index, it=inner_tabs: self.rename_property_tab(index, it))
        inner_tabs.tabCloseRequested.connect(lambda index, it=inner_tabs: self.remove_property(index, it))
        
        year_layout.addWidget(inner_tabs)
        
        if name is None:
            name = f"Year {self.year_tabs.count() + 1}"
            
        new_index = self.year_tabs.addTab(year_container, name)

        if new_index == 0:
            self.year_tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)

        if auto_populate:
            self.create_property_sheet(inner_tabs)

        return year_container, inner_tabs

    def add_property_to_current_year(self):
        current_widget = self.year_tabs.currentWidget()
        if current_widget:
            inner_tabs = current_widget.findChild(QTabWidget)
            if inner_tabs:
                self.create_property_sheet(inner_tabs)

    def create_property_sheet(self, inner_tabs, name=None, data=None, headers=None):
        property_widget = QWidget()
        layout = QVBoxLayout(property_widget)

        column_labels = headers if headers else ["Range", "Mess. Value", "Ref Value", "Error", "Error Uncertanty"]
        
        starting_rows = max(50, len(data) if data else 0)
        
        table = QTableWidget(starting_rows, len(column_labels))
        table.setHorizontalHeaderLabels(column_labels)

        table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        table.horizontalHeader().customContextMenuRequested.connect(
            lambda pos, t=table: self.show_header_menu(pos, t)
        ) 

        if data:
            for r, row_data in enumerate(data):
                for c, value in enumerate(row_data):
                    if r < table.rowCount() and c < table.columnCount():
                        table.setItem(r, c, QTableWidgetItem(str(value)))
                        
        layout.addWidget(table)
        
        if name is None:
            name = f"Property {inner_tabs.count() + 1}"
            
        inner_tabs.addTab(property_widget, name)
        
        self._refresh_tab_close_buttons(inner_tabs)

    def show_header_menu(self, pos, table):
        column_index = table.horizontalHeader().logicalIndexAt(pos)
        
        if column_index < 0:
            return

        menu = QMenu(self)
        add_act = menu.addAction("Insert Column Right")
        rem_act = menu.addAction("Remove This Column")
        menu.addSeparator()

        rename_menu = menu.addMenu("Set Header As >")
        for col_name in AVAILABLE_COLUMNS:
            def make_callback(name):
                def callback():
                    if self.column_exists(table, name):
                        QMessageBox.warning(self, "Duplicate Column", 
                                          f"The column '{name}' already exists in this sheet.")
                    else:
                        table.setHorizontalHeaderItem(column_index, QTableWidgetItem(name))
                return callback
            
            preset_act = rename_menu.addAction(col_name)
            preset_act.triggered.connect(make_callback(col_name))

        action = menu.exec(table.horizontalHeader().mapToGlobal(pos))

        if action == add_act:
            table.insertColumn(column_index + 1)
            table.setHorizontalHeaderItem(column_index + 1, QTableWidgetItem("New Column"))
        elif action == rem_act:
            if table.columnCount() > 1:
                table.removeColumn(column_index)

    def column_exists(self, table, name_to_check):
        for c in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(c)
            if header_item and header_item.text() == name_to_check:
                return True
        return False

    def rename_year_tab(self, index):
        self.prompt_rename_year(index)

    def prompt_rename_year(self, index):
        current_text = self.year_tabs.tabText(index)
        
        while True:
            new_text, ok = QInputDialog.getText(
                self, 
                "Rename Year", 
                "Enter new year (numbers only):", 
                text=current_text
            )
            
            if not ok:
                return False
                
            cleaned_text = new_text.strip()
            
            if cleaned_text.isdigit():
                self.year_tabs.setTabText(index, cleaned_text)
                return True
            else:
                QMessageBox.warning(
                    self, 
                    "Invalid Format", 
                    "Year designations must contain numbers only (e.g., 2026)."
                )

    def rename_property_tab(self, index, inner_tabs):
        current_text = inner_tabs.tabText(index)
        new_text, ok = QInputDialog.getText(self, "Rename Property", "Enter new name:", text=current_text)
        if ok and new_text.strip():
            inner_tabs.setTabText(index, new_text.strip())

    def remove_year(self, index):
        if self.year_tabs.count() > 1:
            widget_to_delete = self.year_tabs.widget(index)
            self.year_tabs.removeTab(index)
            if widget_to_delete:
                widget_to_delete.deleteLater()
            
            self._refresh_tab_close_buttons(self.year_tabs)

    def remove_property(self, index, inner_tabs):
        if inner_tabs.count() > 1:
            widget_to_delete = inner_tabs.widget(index)
            inner_tabs.removeTab(index)
            if widget_to_delete:
                widget_to_delete.deleteLater()
                
            self._refresh_tab_close_buttons(inner_tabs)

    def _refresh_tab_close_buttons(self, tab_widget):
        tab_bar = tab_widget.tabBar()
        
        for i in range(tab_widget.count()):
            btn = tab_bar.tabButton(i, QTabBar.RightSide)
            if btn:
                btn.setVisible(i != 0)

class CertificateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Certificate")
        self.result_data = None  
        self.import_existing = False
        
        layout = QVBoxLayout()

        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Please enter device name")
        self.sn_input = QLineEdit()
        self.sn_input.setPlaceholderText("Please enter device serial number")

        layout.addWidget(QLabel("Type:"))
        layout.addWidget(self.type_input)
        layout.addWidget(QLabel("Serial Number (SN):"))
        layout.addWidget(self.sn_input)

        btn_layout = QHBoxLayout()
        add_new_btn = QPushButton("Add New")
        add_existing_btn = QPushButton("Add Existing Certificate")
        add_new_btn.clicked.connect(self.handle_add)
        add_existing_btn.clicked.connect(self.handle_import)
        
        btn_layout.addWidget(add_new_btn)
        btn_layout.addWidget(add_existing_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def handle_add(self):
        t = self.type_input.text().strip()
        s = self.sn_input.text().strip()
        if t and s:
            self.result_data = (t, s)
            self.accept()
        else:
            QMessageBox.warning(self, "Input Error", "Both fields are required.")

    def handle_import(self):
        self.import_existing = True
        self.accept()

class DisplayDataDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(f"Certificate Analysis: {file_path}")
        layout = QVBoxLayout(self)
        layout.setSpacing(0)

        self.cert_data = data_manager.fetch_certificate_data(file_path)

        self.latest_year = None
        if self.cert_data and self.cert_data.keys():
            self.latest_year = list(self.cert_data.keys())[-1]

        self.label_prop = QLabel("Select a property:")
        layout.addWidget(self.label_prop)

        self.combo_properties = QComboBox()
        layout.addWidget(self.combo_properties)
        layout.addSpacing(10)

        self.label_header = QLabel("Select a header:")
        layout.addWidget(self.label_header)

        self.combo_headers = QComboBox()
        layout.addWidget(self.combo_headers)
        layout.addSpacing(10)

        self.label_value = QLabel("Select a value:")
        layout.addWidget(self.label_value)
        self.combo_values = QComboBox()
        layout.addWidget(self.combo_values)
        layout.addSpacing(40)

        self.btn_confirm = QPushButton("View Data")
        self.btn_confirm.clicked.connect(self.handle_selection)
        layout.addWidget(self.btn_confirm)

        layout.addSpacing(10)

        self.btn_close = QPushButton("Cancel")
        self.btn_close.clicked.connect(self.reject)
        layout.addWidget(self.btn_close)

        self.combo_properties.currentTextChanged.connect(self.display_headers)
        self.combo_headers.currentTextChanged.connect(self.display_values)

        self.initialize_properties()
        self.setMinimumWidth(500)


    def initialize_properties(self):
        if not self.latest_year:
            self.combo_properties.addItem("No data found")
            self.combo_properties.setEnabled(False)
            self.combo_headers.setEnabled(False)
            self.combo_values.setEnabled(False)
            return

        year_entry = self.cert_data.get(self.latest_year, {})
        properties_list = year_entry.get("properties", [])
        property_names = [prop.get("name") for prop in properties_list if "name" in prop]

        self.combo_properties.blockSignals(True)
        self.combo_properties.clear()
        if property_names:
            self.combo_properties.addItems(property_names)
            self.combo_properties.blockSignals(False)
            self.display_headers(self.combo_properties.currentText())
        else:
            self.combo_properties.addItem("No properties found")
            self.combo_properties.blockSignals(False)

    def display_headers(self, selected_property):
        if not selected_property or selected_property == "No properties found":
             return 
        
        year_entry = self.cert_data.get(self.latest_year, {})
        properties_list = year_entry.get("properties", [])

        target_property = next((prop for prop in properties_list if prop.get("name") == selected_property), None)

        self.combo_headers.blockSignals(True)
        self.combo_headers.clear()
        
        if target_property:
            headers = target_property.get("headers", [])
            if headers:
                self.combo_headers.addItems(headers)
                self.combo_headers.blockSignals(False)
                self.display_values(self.combo_headers.currentText())
            else:
                self.combo_headers.addItem("No headers found")
                self.combo_headers.blockSignals(False)

    def display_values(self, selected_header):
        if not selected_header or selected_header == "No headers found":
            return

        selected_property = self.combo_properties.currentText()

        unique_values = data_manager.get_unique_column_values(
            self.cert_data, 
            self.latest_year, 
            selected_property, 
            selected_header
        )

        self.combo_values.blockSignals(True)
        self.combo_values.clear()
        
        if unique_values:
            self.combo_values.addItems(unique_values)
        else:
            self.combo_values.addItem("No values found")
            
        self.combo_values.blockSignals(False)

    def handle_selection(self):
        target_prop = self.combo_properties.currentText()
        target_head = self.combo_headers.currentText()
        target_val = self.combo_values.currentText()
        
        self.final_graph_data = data_manager.get_historical_graph_data(
            self.cert_data, 
            target_prop, 
            target_head, 
            target_val
        )
        
        print(f"--- GRAPH DATA PREPARED VIA DATA_MANAGER ---")
        print(f"Resulting Nested Dictionary: {self.final_graph_data}")
        
        if self.final_graph_data:
            graph_dialog = graph_view.ErrorGraphDialog(
                graph_data=self.final_graph_data, 
                error_col_name="Error",
                uncert_col_name="Error Uncertanty",
                parent=self
            )
            graph_dialog.exec()
        else:
            print("No data found to graph!")

        self.accept()

    