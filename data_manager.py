import os
import re
import json
import glob
import shutil
from PySide6.QtWidgets import QTreeWidgetItem

def scan_and_populate_list(tree_widget, directory_path):
    tree_widget.clear()
    pattern = re.compile(r"^([^_]+)_SN_([0-9]+).*?\.json$")

    if not os.path.exists(directory_path):
        return

    # Use a set to track devices we've already added
    seen_devices = set()

    for filename in os.listdir(directory_path):
        match = pattern.match(filename)
        if match:
            instr_type = match.group(1)
            sn_value = match.group(2)

            unique_key = (instr_type, sn_value)

            if unique_key not in seen_devices:
                item = QTreeWidgetItem([instr_type, sn_value])
                tree_widget.addTopLevelItem(item)

                # Mark this device as "seen"
                seen_devices.add(unique_key)
            else:
                # Optional: Log that a duplicate was skipped
                print(f"Skipped duplicate SN: {sn_value} ({filename})")

def create_blank_certificate(file_path, cert_type, cert_sn):
    cert_content = {
        "type": cert_type,
        "sn": cert_sn,
        "years": [
            {
                "name": "Year 1",
                "properties": [
                    {
                        "name": "Property 1", 
                        "headers": ["Range", "Mess. Value", "Ref Value", "Error", "Error Uncertanty"],
                        "data": [["" for _ in range(3)] for _ in range(50)]
                    }
                ]
            }
        ]
    }
    return save_certificate(file_path, cert_content)

def _normalize_and_clean_data(properties_input):

    cleaned_properties = []
    for prop in properties_input:
        raw_data = prop.get("data", [])
        
        last_filled_row = -1
        for i, row in enumerate(raw_data):
            if any(str(cell).strip() for cell in row):
                last_filled_row = i
                
        cutoff = max(50, last_filled_row + 1)
        trimmed_data = raw_data[:cutoff]
        
        cleaned_properties.append({
            "name": prop.get("name"),
            "headers": prop.get("headers"),
            "data": trimmed_data
        })
        
    return cleaned_properties

def prepare_and_save_certificate_data(file_path, raw_years_ui_list):
    full_data = {"years": []}
    
    for year_data in raw_years_ui_list:
        year_entry = {
            "name": year_data.get("name"),
            "properties": _normalize_and_clean_data(year_data.get("properties", []))
        }
        full_data["years"].append(year_entry)
        
    return save_certificate(file_path, full_data)

def import_external_certificate(source_path, destination_dir):
    filename = os.path.basename(source_path)
    destination_path = os.path.join(destination_dir, filename)
    try:
        shutil.copy(source_path, destination_path)
        return True, filename
    except Exception as e:
        return False, str(e)

def get_certificate_file_path(directory, instr_type, sn_value):
    return os.path.join(directory, f"{instr_type}_SN_{sn_value}.json")

def delete_certificate_files(directory, instr_type, sn_value):
    search_pattern = os.path.join(directory, f"{instr_type}_SN_{sn_value}*.json")
    matching_files = glob.glob(search_pattern)
    
    count = 0
    for file_path in matching_files:
        try:
            os.remove(file_path)
            count += 1
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    return count

def load_certificate(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Load Error: {e}")
        return None

def save_certificate(file_path, data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Save Error: {e}")
        return False

def fetch_certificate_data(file_path):
    cert_data = load_certificate(file_path)
    extracted_years = {}

    if not cert_data or "years" not in cert_data:
        return {}
    
    for entry in cert_data["years"]:
        year_name = entry.get("name")
        if year_name:
            extracted_years[year_name] = entry
            
    return extracted_years

def get_unique_column_values(cert_data, year, property_name, header):
    year_entry = cert_data.get(year, {})
    properties_list = year_entry.get("properties", [])
    target_property = next((prop for prop in properties_list if prop.get("name") == property_name), None)

    if not target_property:
        return []

    headers = target_property.get("headers", [])
    data_matrix = target_property.get("data", [])

    if header not in headers:
        return []

    col_index = headers.index(header)
    
    column_values = []
    for row in data_matrix:
        if col_index < len(row): 
            val = str(row[col_index]).strip()
            if val:  # Ignore empty string entries
                column_values.append(val)

    unique_values = list(dict.fromkeys(column_values))
    
    return unique_values

def _clean_numeric_value(raw_value):
    try:
        if isinstance(raw_value, str):
            clean_value = raw_value.replace('$', '').replace(',', '').strip()
            
            match = re.search(r'[-+]?\d*\.?\d+', clean_value)
            
            if match:
                return float(match.group())
            
            return raw_value 
            
        return float(raw_value)
    except (ValueError, TypeError):
        return raw_value


def _process_row_data(headers, raw_row_list):
    row_dict = dict(zip(headers, raw_row_list))
    return {key: _clean_numeric_value(val) for key, val in row_dict.items()}


def _find_row_in_property(target_property, filter_header, filter_value):
    headers = target_property.get("headers", [])
    data_matrix = target_property.get("data", [])

    if filter_header not in headers:
        return None

    col_index = headers.index(filter_header)
    
    for row in data_matrix:
        if col_index < len(row) and str(row[col_index]).strip() == filter_value:
            return row
            
    return None


def get_historical_graph_data(cert_data, property_name, header, value):
    graph_dict = {}

    for year in sorted(cert_data.keys()):
        year_entry = cert_data.get(year, {})
        properties_list = year_entry.get("properties", [])
        
        target_property = next((p for p in properties_list if p.get("name") == property_name), None)
        if not target_property:
            continue

        matching_row_list = _find_row_in_property(target_property, header, value)
        
        if matching_row_list:
            headers = target_property.get("headers", [])
            graph_dict[year] = _process_row_data(headers, matching_row_list)
            
    return graph_dict