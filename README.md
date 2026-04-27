PilotProject: Instrument Calibration Manager
PilotProject is a desktop application built with PySide6 (Qt for Python) designed to manage measuring instrument certifications. It allows technicians to track devices and manage calibration data via a dynamic, spreadsheet-style editor.

📂 Project Architecture
    The project follows a Separated Concerns architecture to ensure the code is maintainable and scalable:

    main.py: The application entry point. It initializes the UI and connects user actions to the underlying logic.

    GUI.py: Defines the visual layout. It contains the classes for the Main Window, the Certificate Editor, and various Dialogs. It is responsible for how things look.

    button_functions.py: Acts as the controller. It manages user interactions, confirmation dialogs, and coordinates between the UI and the data layer. It is responsible for what happens.

    data_manager.py (formerly scanfiles.py): The data access layer. It handles all JSON reading/writing, file system operations (copying, deleting), and certificate scanning. It is responsible for data integrity.

    Certificates/: The local storage directory where each instrument is saved as a unique .json file.

🚀 Key Features
    1️⃣ Dynamic Spreadsheet Editor
        The CertEditDialog generates tables on the fly. Users can organize data by Year and Property, ensuring a clean history for every device.

    2️⃣ Smart Header Management
        Instead of static columns, PilotProject uses an interactive header system:
        Right-Click Menu: Insert or remove columns directly from the table header.
        Parameter Presets: Choose from a pool of standard calibration headers (e.g., Range, Measured Value, Frequency).
        Duplicate Prevention: The system automatically checks to ensure column names are unique within a sheet.

    3️⃣ Structural Persistence
        The application doesn't just save numbers; it saves the structure. When a user customizes a table layout, the specific headers and column counts are stored in the JSON, so the editor looks exactly the same when re-opened.

🛠 Installation
Requirement: Python 3.10+
Dependencies: "requirements.txt", Standard Python 3.14 libraries.

📋"Requirements.txt": 
    PySide6==6.11.0
    PySide6_Addons==6.11.0
    PySide6_Essentials==6.11.0
    shiboken6==6.11.0

To install required dependencies, open your terminal and run following command:
    pip install -r requirements.txt

🛠 Technical Note for Developers
To add new measurement parameters to the selection menu, simply update the AVAILABLE_COLUMNS list at the top of GUI.py. The UI will automatically update the right-click menus across the entire application.