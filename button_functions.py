import os
from PySide6.QtWidgets import QFileDialog, QMessageBox, QDialog
import data_manager
from GUI import CertEditDialog, CertificateDialog, DisplayDataDialog

def add_new_certificate(parent_window, tree_widget, certificates_dir):
    dialog = CertificateDialog(parent_window)
    
    if dialog.exec_() == QDialog.Accepted:
        if dialog.import_existing:
            file_path, _ = QFileDialog.getOpenFileName(parent_window, "Select JSON", "", "JSON Files (*.json)")
            if file_path:
                success, message = data_manager.import_external_certificate(file_path, certificates_dir)
                if success:
                    QMessageBox.information(parent_window, "Success!", f"Imported: {message}")
                else:
                    QMessageBox.critical(parent_window, "Error!", message)

        elif dialog.result_data:
            cert_type, cert_sn = dialog.result_data
            filename = f"{cert_type}_SN_{cert_sn}.json"
            full_path = os.path.join(certificates_dir, filename)
            
            if data_manager.create_blank_certificate(full_path, cert_type, cert_sn):
                QMessageBox.information(parent_window, "Success!", f"Created: {filename}")
            else:
                QMessageBox.critical(parent_window, "Error!", "Failed to create file.")

        data_manager.scan_and_populate_list(tree_widget, certificates_dir)

def delete_existing_certificate(parent_window, tree_widget, certificates_dir):
    selected_item = tree_widget.currentItem()
    if not selected_item:
        QMessageBox.warning(parent_window, "Selection Error!", "Please select an instrument to delete.")
        return

    instr_type = selected_item.text(0)
    sn_value = selected_item.text(1)
    
    confirm = QMessageBox.question(
        parent_window, "Confirm Delete", 
        f"Are you sure you want to delete {instr_type} (SN: {sn_value})?",
        QMessageBox.Yes | QMessageBox.No
    )

    if confirm == QMessageBox.Yes:
        deleted_count = data_manager.delete_certificate_files(certificates_dir, instr_type, sn_value)
        
        if deleted_count > 0:
            index = tree_widget.indexOfTopLevelItem(selected_item)
            tree_widget.takeTopLevelItem(index)
            QMessageBox.information(parent_window, "Deleted!", f"Successfully removed {deleted_count} file(s).")
        else:
            QMessageBox.critical(parent_window, "Error!", "Something went wrong, no files were deleted!")

def edit_certificate_data(parent_window, tree_widget, certificates_dir):
    selected_item = tree_widget.currentItem()
    if not selected_item:
        QMessageBox.warning(parent_window, "Selection Error!", "Please select an item to edit.")
        return

    instr_type = selected_item.text(0)
    sn_value = selected_item.text(1)

    file_path = data_manager.get_certificate_file_path(certificates_dir, instr_type, sn_value)

    if not os.path.exists(file_path):
        QMessageBox.critical(parent_window, "Error!", "Certificate file not found!")
        return

    editor = CertEditDialog(file_path, parent_window)
    editor.exec()

def display_certificate_data(parent_window, tree_widget, certificates_dir):
    selected_item = tree_widget.currentItem()
    if not selected_item:
        QMessageBox.warning(parent_window, "Selection Error!", "Please select an item from the list to display data.")
        return

    instr_type = selected_item.text(0)
    sn_value = selected_item.text(1)

    file_path = data_manager.get_certificate_file_path(certificates_dir, instr_type, sn_value)

    if not os.path.exists(file_path):
        QMessageBox.critical(parent_window, "Error!", "Certificate file not found!")
        return
    
    editor = DisplayDataDialog(file_path, parent_window)
    editor.exec()
