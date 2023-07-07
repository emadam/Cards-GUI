<<<<<<< HEAD
import subprocess
import PySimpleGUI as sg
import os
import re
from datetime import datetime

rmr_icon = r'X:\Productn\I_A\Beverages\C-Drive\SelectCards\RMR.ico'
version = '1.7.0'
input_bcp = ''


def usage_text():
    usage_txt = """SELECT CARDS:
    - Card List: Select the File Containing List of Cards
    - Month(s): Choose the Month(s) to Select Data for
    - Data Store:
      - TOT: Select TOT survey
      - ES: Select ES survey
      - BCP: Select from a single named BCP file
    - Output File Name: Specify the Output File Name for the generated data
    - Open Output Directory When Finished Successfully: Check this option to open the output directory after completion
    - Create DAT File with BCP: Check this option to create a DAT file using CPANGLOSS
    - Create DISCRETE BCP Files from Months File: Check this option to generate a BCP file for each month in the list
    - Use Created BCP File to Replace Cards in a Master File: Check this option to replace cards in a Master File
    - Master File: Select the BCP master file to replace data
----------------------------------------------------------
REPLACE CARDS/COLUMNS:
    - Master File: Select the BCP master file to replace data
    - Updates File: Select the Updates File to replace data in the Master File
    - Output File Name: Specify the Output File Name containing the replaced data
    - Open Output Directory When Finished Successfully: Check this option to open the output directory after completion
    - Replace Finance Data: Check this option to merge finance data items, where an item is stored on a pair of cards
    - Replace Columns in the Master File: Check this option to replace columns in the Master File
----------------------------------------------------------
SORT CARDS:
    - Input File: Select the BCP File to Sort
    - Output File Name: Specify the Output Sorted File Name
    - Open Output Directory When Finished Successfully: Check this option to open the output directory after completion
    - Merge With Another BCP File: Check this option to merge with another BCP file
    - File to Merge: Select the BCP File to Merge
    """
    return usage_txt


def faq_text():
    faq_text = '''
    Frequently Asked Questions:

             Q: How do I select a card list?
             A: Click on the "Card List" field and browse for the file containing the list of cards.

             Q: Can I enter month(s) manually?
             A: Yes, you can select the option "Enter month manually" to manually enter the month(s).

             Q: What is the output file name?
             A: The output file name is the name you specify for the file containing the processed data.

             Q: How can I open the output directory?
             A: By default, the output directory opens automatically when the process is finished successfully. 
                  You can uncheck the "Open Output Directory When Finished Successfully" option to disable this.

             Q: How can I create a DAT file with BCP?
             A: You can enable the "Create DAT File with BCP" option to generate a DAT file along with the BCP file.

             Q: How do I replace cards in a master file?
             A: Select the "Use Created BCP File to Replace Cards in a Master File" option and provide the master file to replace the data.

             Q: How can I sort a BCP file?
             A: In the "Sort Cards" tab, select the BCP file and specify the output file name for the sorted data.'''
    return faq_text


def ui_layout():
    sg.theme("Reddit")
    # Help menu layout
    help_menu_layout = [['    Help    ', ['Usage...', 'FAQ...', '---', 'About...']]]
    tab1_layout = [
        [sg.Frame('Select Cards', size=(500, 280), layout=[
            [sg.Text("Card List:", font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (5, 5)),
                     tooltip='Select the File Containing List of Cards'),
             sg.Input(key="-CARD_LIST-", enable_events=True, disabled=True,
                      disabled_readonly_background_color='ivory2'),
             sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                           file_types=(('CARD Files', '*.cards'), ('CARD Files', '*.txt'), ('CARD Files', '*.list')))],
            [sg.Text('Month(s):', font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (5, 5)),
                     tooltip='Choose the Month(s) to Select Data for'),
             sg.Combo(['Select month(s) from file', 'Enter month manually'], key='-OPTION-', enable_events=True,
                      readonly=True,
                      background_color='ivory2'),
             sg.Text(size=(1, 1), pad=((1, 0), (1, 0))), sg.Text(key="-MONTH_DIR-", font=('Calibri', 11, 'bold'))],
            [sg.Text("Data Store:", font=('Calibri', 11, 'bold'), size=(15, 1), pad=((1, 0), (1, 0))),
             sg.Radio("TOT", group_id="survey_radio", key="-SURVEY_TOT-", default=True, font=('Calibri', 11, 'bold'),
                      enable_events=True),
             sg.Radio("ES", group_id="survey_radio", key="-SURVEY_ES-", font=('Calibri', 11, 'bold'),
                      enable_events=True),
             sg.Radio("BCP", group_id="survey_radio", key="-SURVEY_BCP-", font=('Calibri', 11, 'bold'),
                      enable_events=True,
                      tooltip='Uses Selectcards2 to read input from a single BCP file'),
             sg.Text(size=(20, 1), pad=((40, 0), (1, 0)), key="-BCP_DATA_STORE-", font=('Calibri', 11, 'bold')),
             ],
            [sg.Text("Output File Name:", font=('Calibri', 11, 'bold'), size=(15, 1), pad=((2, 0), (2, 0))),
             sg.Input(size=(28, 1),
                      key="-OUTPUT_FILE-", background_color="ivory2"),
             sg.Text(".BCP", size=(4, 1), pad=((0, 2), (2, 0)))],
            [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
            [sg.Checkbox('Open Output Directory When Finished Successfully', font=('Calibri', 11, 'italic'),
                         key='-CHECKBOX-',
                         default=True, enable_events=True)],
            [sg.Checkbox('Create DAT File with BCP', font=('Calibri', 11, 'italic'), key='-PANGLOSS-',
                         default=False, enable_events=True, tooltip='Use CPANGLOSS to Create DAT File')],
            [sg.Checkbox('Create DISCRETE BCP Files from Months File', font=('Calibri', 11, 'italic'), key='-DISCRETE-',
                         default=False, enable_events=True,
                         tooltip='Generate a BCP file for each month in the list of months')],
            ], font='Impact', border_width=2, title_color='teal'),
        ],
            [sg.Frame('Select Then Replace', size=(500, 100), layout=[
            [sg.Checkbox('Use Selected Output BCP File to Replace Cards in a Master File',
                         font=('Calibri', 11, 'italic'),
                         key='-MASTER_SELECT-', default=False, enable_events=True,
                         tooltip="Replace cards in a Master File with the BCP File")],
            [sg.Text("Master File:", font=('Calibri', 11, 'bold'), size=(11, 1), pad=((1, 33), (0, 0)),
                     tooltip="Select the BCP master file to replace data", visible=False, key='-MASTER_TEXT-'),
             sg.Input(size=(45, 1), key="-INPUT_REP-", enable_events=True, disabled=True,
                      disabled_readonly_background_color='ivory2', visible=False),
             sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                           file_types=(('BCP FILE', '*.BCP'),), visible=False, key='-REP_BROWSE-',
                           enable_events=True)],
        ], font='Impact', border_width=2, title_color='darkgreen')
    ],
                   [sg.Column([
                       [sg.Text('', size=(1, 1))],
                       [sg.Button("Submit", key='-SUBMIT-', enable_events=True, size=(8, 1),
                                  button_color=('white', 'green'), font=("Helvetica", 10)),
                        sg.Button("Exit", key='-EXIT-', enable_events=True, size=(8, 1), button_color=('white', 'red'),
                                  font=("Helvetica", 10))]
                   ], justification='center')]
                   ]
    tab2_layout = [[sg.Frame('Replace Cards', size=(500, 190), layout=[
        [sg.Text("Master File:", font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (5, 5)),
                 tooltip="Select the BCP master file to replace data"), sg.Input(size=(45, 1), key="-MASTER_FILE-",
                                                                                 enable_events=True, disabled=True,
                                                                                 disabled_readonly_background_color='ivory2'),
         sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                       file_types=(('BCP FILE', '*.BCP'),))],
        [sg.Text("Updates File:", font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (5, 5)),
                 tooltip="Select the Updates File to replace data in the Master File"),
         sg.Input(size=(45, 1), key="-UPDATES_FILE-", enable_events=True, disabled=True,
                  disabled_readonly_background_color='ivory2'),
         sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                       file_types=(('BCP FILE', '*.BCP'),))],
        [sg.Text("Output File Name:", font=('Calibri', 11, 'bold'), size=(15, 1), pad=((2, 3), (5, 5)),
                 tooltip='Specify the Output File Name containing the replaced data'),
         sg.Input(size=(28, 1), key="-REPLACED_FILE-", background_color='ivory2', pad=((2, 0), (5, 0))),
         sg.Text(".BCP", size=(4, 1), pad=((5, 0), (5, 0)))],
        # [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
        [sg.Checkbox('Open Output Directory When Finished Successfully', font=('Calibri', 11, 'italic'),
                     key='-OPEN_FOLDER-',
                     default=True, enable_events=True)],
        [sg.Checkbox('Replace Finance Data', font=('Calibri', 11, 'italic'),
                     key='-FIN_REP-', default=False, enable_events=True,
                     tooltip="Merge finance data items by ReplaceTrailerPairs")],
        ], font='Impact', border_width=2, title_color='teal')
        ],
        [sg.Frame('Replace Columns', size=(500, 95), layout=[
            [sg.Checkbox('Replace Columns in the Master File', font=('Calibri', 11, 'italic'),
                     key='-REP_COL-', default=False, enable_events=True,
                     tooltip="Replace columns in a Master File with updated columns from an Updates File")],
            [sg.Text("Column List:", font=('Calibri', 11, 'bold'), size=(11, 1), pad=((2, 30), (5, 5)),
                 tooltip="Select the column list file to replace data", visible=False, key='-REP_COL_TEXT-'),
            sg.Combo(['Select column(s) from file', 'Enter columns manually'], key='-REP_COL_OPTION-', enable_events=True,
                  readonly=True, visible=False,
                  background_color='ivory2'),
         ],
    ], font='Impact', border_width=2, title_color='darkgreen')
                    ],
                   # [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
                   [sg.Multiline(size=(69, 8), reroute_stdout=True, reroute_stderr=False, reroute_cprint=True,
                                 enable_events=True,
                                 write_only=True, font='Courier 9', autoscroll=True, auto_refresh=True,
                                 background_color="ivory2",
                                 text_color="maroon", do_not_clear=True, key='-ML-')],
                   [sg.Column([
                       [sg.Button("Submit", key='-SUBMIT2-', enable_events=True, size=(8, 1),
                                  button_color=('white', 'green'), font=("Helvetica", 10)),
                        sg.Button("Exit", key='-EXIT2-', enable_events=True, size=(8, 1), button_color=('white', 'red'),
                                  font=("Helvetica", 10)),
                        sg.Button("Cancel", key='-CANCEL-', enable_events=True, size=(8, 1),
                                  button_color=('black', 'oldlace'),
                                  font=("Helvetica", 10), border_width=2, tooltip='Terminate replace process')]
                   ], justification='center')
                   ]
                   ]
    tab3_layout = [[sg.Frame('Sort and Merge', size=(500, 190), layout=[
        [sg.Text("Input File:", font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (2, 0)),
                 tooltip="Select the BCP File to Sort"), sg.Input(size=(45, 1), key="-INPUT_FILE-",
                                                                  enable_events=True, disabled=True,
                                                                  disabled_readonly_background_color='ivory2'),
         sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                       file_types=(('BCP FILE', '*.BCP'),))],
        [sg.Text("Output File Name:", font=('Calibri', 11, 'bold'), size=(15, 1), pad=((2, 3), (0, 5)),
                 tooltip='Specify the Output Sorted File Name'),
         sg.Input(size=(28, 1), key="-SORTED_FILE-", background_color='ivory2', pad=((2, 0), (5, 0))),
         sg.Text(".BCP", size=(4, 1), pad=((5, 0), (5, 0)))],
        [sg.Checkbox('Open Output Directory When Finished Successfully', font=('Calibri', 11, 'italic'),
                     key='-OPEN_SORT_DIR-', default=True, enable_events=True, pad=((5, 0), (10, 0)))],
        [sg.Checkbox('Merge With Another BCP File(s)', font=('Calibri', 11, 'italic'),
                     key='-MERGE_SELECT-', default=False, enable_events=True)],
        [sg.Text("File(s) to Merge:", font=('Calibri', 11, 'bold'), size=(13, 1), pad=((1, 17), (0, 0)),
                 tooltip="Select the BCP File(s) to Merge", visible=False, key='-MERGE_TEXT-'), sg.Input(size=(45, 1),
                                                                                                         key="-INPUT_MERGE-",
                                                                                                         enable_events=True,
                                                                                                         disabled=True,
                                                                                                         disabled_readonly_background_color='ivory2',
                                                                                                         visible=False),
         sg.FilesBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                        file_types=(('BCP FILE', '*.BCP'),), visible=False, key='-MERGE_BROWSE-', enable_events=True)],
    ], font='Impact', border_width=2, title_color='teal')
                    ],
                    [sg.Frame('Merge then Replace', size=(500, 95), layout=[
                           [sg.Checkbox('Use Merged Output BCP File to Replace Cards in a Master File',
                                        font=('Calibri', 11, 'italic'),
                                        key='-MASTER_SELECT_2-', default=False, enable_events=True, disabled=True,
                                        tooltip="Replace cards in a Master File with the BCP File",
                                        pad=((1, 1), (0, 1)))
                            ],
                           [sg.Text("Master File:", font=('Calibri', 11, 'bold'), size=(11, 1), pad=((1, 33), (0, 0)),
                                    tooltip="Select the BCP master file to replace data", visible=False,
                                    key='-MASTER_TEXT_2-'),
                            sg.Input(size=(45, 1), key="-INPUT_REP_2-", enable_events=True, disabled=True,
                                     disabled_readonly_background_color='ivory2', visible=False),
                            sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                                          file_types=(('BCP FILE', '*.BCP'),), visible=False, key='-REP_BROWSE_2-',
                                          enable_events=True)]
                       ], font='Impact', border_width=2, title_color='darkgreen')
                    ],

                   [sg.Multiline(size=(69, 8), reroute_stdout=True, reroute_stderr=False, reroute_cprint=True,
                                 enable_events=True,
                                 write_only=True, font='Courier 9', autoscroll=True, auto_refresh=True,
                                 background_color="ivory2",
                                 text_color="maroon", do_not_clear=True, key='-ML_SORT-')],
                   [sg.Column([
                       [sg.Button("Submit", key='-SUBMIT3-', enable_events=True, size=(8, 1),
                                  button_color=('white', 'green'), font=("Helvetica", 10)),
                        sg.Button("Exit", key='-EXIT3-', enable_events=True, size=(8, 1), button_color=('white', 'red'),
                                  font=("Helvetica", 10)),
                        sg.Button("Cancel", key='-CANCEL2-', enable_events=True, size=(8, 1),
                                  button_color=('black', 'oldlace'),
                                  font=("Helvetica", 10), border_width=2, tooltip='Terminate replace process')]
                   ], justification='center')
                ]
        ]
    tab4_layout = [[sg.Frame('Select Respondent Cards', size=(500, 190), layout=[
            [sg.Text("Input BCP File:", font=('Calibri', 11, 'bold'), size=(13, 1), pad=((2, 16), (5, 5)),
                     tooltip='Select the Input BCP File'),
             sg.Input(key="-RES_BCP-", enable_events=True, disabled=True,
                      disabled_readonly_background_color='ivory2'),
             sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                           file_types=(('BCP File', '*.bcp'),))],
            [sg.Text("Output File Name (Optional):", font=('Calibri', 11, 'bold'), size=(23, 1), pad=((2, 3), (5, 5)),
                 tooltip='Specify the Output File Name for Respondent Data'),
            sg.Input(size=(35, 1), key="-ASC_FILE-", background_color='ivory2', pad=((7, 0), (5, 5))),
            sg.Text(".ASC", size=(4, 1), pad=((5, 0), (5, 5)))],
            [sg.Text("ID Number (9 digits):", font=('Calibri', 11, 'bold'), size=(20, 1), pad=((2, 5), (5, 0)),
                         tooltip='Type the 9-digit RID'),
                 sg.Input(size=(35, 1), key="-RES_ID-", enable_events=True, background_color='ivory2',
                          pad=((29, 0), (5, 0)))],
            [sg.Text("Not a valid Respondent ID", font=('Calibri', 8), size=(22, 1), pad=((198, 0), (0, 0)),
                         visible=False, enable_events=True, key='-RID_CHECK-', text_color='red')],
            [sg.Checkbox('Open Output Directory When Finished Successfully', font=('Calibri', 11, 'italic'),
                     key='-OPEN_RESP_DIR-', default=True, enable_events=True, pad=((5, 0), (10, 0)))]
    ], font='Impact', border_width=2, title_color='teal')],
                   [sg.Text('', size=(1, 1))],
                   [sg.Multiline(size=(69, 12), reroute_stdout=True, reroute_stderr=False, reroute_cprint=True,
                                 enable_events=True,
                                 write_only=True, font='Courier 9', autoscroll=True, auto_refresh=True,
                                 background_color="ivory2",
                                 text_color="maroon", do_not_clear=True, key='-ML_RESP-')],
                   [sg.Column([
                       [sg.Button("Submit", key='-SUBMIT4-', enable_events=True, size=(8, 1),
                                  button_color=('white', 'green'), font=("Helvetica", 10)),
                        sg.Button("Exit", key='-EXIT4-', enable_events=True, size=(8, 1), button_color=('white', 'red'),
                                  font=("Helvetica", 10)),
                        sg.Button("Cancel", key='-CANCEL3-', enable_events=True, size=(8, 1),
                                  button_color=('black', 'oldlace'),
                                  font=("Helvetica", 10), border_width=2, tooltip='Terminate replace process')]
                   ], justification='center', pad=((0, 0), (15, 0)))
                   ]
                   ]
    tab_group = [[sg.TabGroup(
        [[sg.Tab('SELECT CARDS', tab1_layout), sg.Tab('REPLACE CARDS/COLUMNS', tab2_layout),
          sg.Tab('SORT CARDS', tab3_layout), sg.Tab('RESPONDENT CARDS', tab4_layout)
          ]], border_width=0, font=('Calibri', 11, 'bold'), title_color='gray'
    ),
    ]]
    final_layout = [
        [sg.Menu(help_menu_layout)],
        tab_group  # Your existing UI layout here
    ]
    return final_layout


def popup_error(error_message):
    sg.popup_error(error_message, button_color=('white', 'red'), title="Error",
                   background_color='lightgray', text_color='red', keep_on_top=True,
                   non_blocking=False, icon=rmr_icon)


def select_columns(column_count, main_window_location):
    # Create the layout for the popup window
    layout = [
        [sg.Text("Select the columns you want to replace:", text_color='darkblue', font=('Calibri', 11, 'bold'))],
        [
            sg.Column([
                [sg.Checkbox(f"Column {i}", key=f"column{i}", enable_events=True)] for i in range(10, 24)
            ]),
            sg.VerticalSeparator(),
            sg.Column([
                [sg.Checkbox(f"Column {i}", key=f"column{i}", enable_events=True)] for i in range(24, 38)
            ]),
            sg.VerticalSeparator(),
            sg.Column([
                [sg.Checkbox(f"Column {i}", key=f"column{i}", enable_events=True)] for i in range(38, 52)
            ]),
            sg.VerticalSeparator(),
            sg.Column([
                [sg.Checkbox(f"Column {i}", key=f"column{i}", enable_events=True)] for i in range(52, 66)
            ]),
            sg.VerticalSeparator(),
            sg.Column([
                [sg.Checkbox(f"Column {i}", key=f"column{i}", enable_events=True)] for i in range(66, column_count + 1)
            ]),
        ],
        [sg.Button("OK"), sg.Button("Cancel")]
    ]
    popup_location = (
        main_window_location[0] - 50, main_window_location[1] - 100)
    # Create the window
    window = sg.Window("Column Selector", layout,
                       font=('Calibri', 11),
                       background_color='white',
                       keep_on_top=True,
                       grab_anywhere=False,
                       location=popup_location,
                       icon=rmr_icon)

    # Read events from the window
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Cancel"):
            selected_columns = []
            break
        elif event == "OK":
            selected_columns = []
            for i in range(10, column_count + 1):
                if values[f"column{i}"]:
                    selected_columns.append(f"{i}".strip())
            break

    window.close()
    selected_columns = ', '.join([str(item) for item in selected_columns])
    return selected_columns


def main():
    # Event loop to process events and get inputs
    while True:
        event, values = window.read()

        # #MENU commands start here  ########################################
        if event in (None, '-EXIT-', '-EXIT2-', '-EXIT3-'):
            break
            # Handle events
        elif event == 'About...':
            main_window_location = window.CurrentLocation()
            popup_location = (
                main_window_location[0] + 70, main_window_location[1] + 100)  # Adjust the coordinates as needed
            sg.popup(f'Cards Graphical User Interface v{version}',
                     'This is a Python application designed to perform various tasks.',
                     'It provides features such as selecting cards, replacing data in BCP files,'
                     ' and sorting BCP files.',
                     'For more information and support, please contact:',
                     'emad.aminmoghadam@roymorgan.com',
                     font=('Calibri', 11),
                     background_color='white',
                     text_color='black',
                     title='About',
                     non_blocking=True,
                     keep_on_top=True,
                     grab_anywhere=True,
                     icon=rmr_icon,
                     any_key_closes=True,
                     location=popup_location)
        elif event == 'Usage...':
            usage_context = usage_text()
            usage_layout = [
                [sg.Multiline(usage_context, size=(110, 26), auto_size_text=True, no_scrollbar=True, do_not_clear=True,
                              expand_y=True, font=('Calibri', 11), background_color='ivory2', text_color='black',
                              disabled=True)]
            ]
            main_window_location = window.CurrentLocation()
            popup_location = (
                main_window_location[0] - 100, main_window_location[1] + 50)  # Adjust the coordinates as needed
            usage_popup_window = sg.Window("Usage", usage_layout, icon=rmr_icon, location=popup_location)
            usage_popup_window.read()
        elif event == 'FAQ...':
            faq_context = faq_text()
            faq_layout = [
                [sg.Multiline(faq_context, size=(120, 25), auto_size_text=True, no_scrollbar=True, do_not_clear=True,
                              expand_y=True, font=('Calibri', 11), background_color='ivory2', text_color='black',
                              disabled=True)]
            ]
            main_window_location = window.CurrentLocation()
            popup_location = (
                main_window_location[0] - 100, main_window_location[1] + 50)  # Adjust the coordinates as needed
            usage_popup_window = sg.Window("Usage", faq_layout, icon=rmr_icon, location=popup_location)
            usage_popup_window.read()

        # #SELECTCARDS commands start here  #################################
        elif event == '-CARD_LIST-':
            try:
                output_dir = os.path.dirname(values["-CARD_LIST-"])
                # Check if the directory exists
                if os.path.exists(output_dir):
                    # Check if the path points to a directory
                    if os.path.isdir(output_dir):
                        # Check if the directory is readable
                        if os.access(output_dir, os.R_OK):
                            os.chdir(output_dir)
                        else:
                            popup_error("The output directory is not correct!")
                            window['-CARD_LIST-'].update(value='')

            except FileNotFoundError as e:
                # Display an error message to the user
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
        elif event == '-OPTION-':
            if values['-OPTION-'] == 'Select month(s) from file':
                popup_layout = [[sg.Text('Month list file(s):'), sg.InputText(key='-MONTH_FILE-'),
                                 sg.FilesBrowse(file_types=(
                                     ('MONTH Files', '*.months'), ('MONTH Files', '*.txt'),
                                     ('MONTH Files', '*.list')))],
                                [sg.Button('OK'), sg.Button('Cancel')]
                                ]
                main_window_location = window.CurrentLocation()
                popup_location = (
                    main_window_location[0] + 10, main_window_location[1] + 150)  # Adjust the coordinates as needed
                popup_window = sg.Window('Select a month file', popup_layout, keep_on_top=True, icon=rmr_icon,
                                         location=popup_location)
                while True:
                    dis_month = values["-DISCRETE-"]
                    popup_event, popup_values = popup_window.read()
                    if popup_event in (sg.WINDOW_CLOSED, 'Cancel'):
                        break
                    if popup_event == 'OK':
                        if ";" in popup_values['-MONTH_FILE-']:
                            months = popup_values['-MONTH_FILE-'].split(';')
                            months_list = os.path.dirname(months[0]) + r'/cardsguimonths.list'
                            with open(months_list, 'w') as f:
                                for month in months:
                                    with open(month, 'r') as file:
                                        lines = file.readlines()
                                        for line in lines:
                                            f.write(line.strip() + '\n')
                            window['-MONTH_DIR-'].update(value=os.path.basename(months_list))
                            break
                        else:
                            months_list = popup_values['-MONTH_FILE-']
                            filename = os.path.basename(months_list)
                            window["-MONTH_DIR-"].update(filename)
                            if dis_month:
                                with open(months_list, 'r') as f:
                                    months = [line.strip() for line in f.readlines()]
                            break
                popup_window.close()
                window['-DISCRETE-'].update(disabled=False)
            else:
                months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                          'October',
                          'November', 'December']
                years = [str(year) for year in range(2018, 2030)]
                # Get the current year
                current_year = datetime.now().year
                # Get the current month
                current_month = datetime.now().month
                # Calculate the previous month
                if current_month == 1:
                    previous_month = 12
                else:
                    previous_month = current_month - 1
                # Get the month name for the previous month
                previous_month_name = datetime.strptime(str(previous_month), '%m').strftime('%B')

                layout = [
                    [sg.Text('Month', size=(7, 1), pad=((70, 0), (0, 0)), font=('Calibri', 11, 'bold')),
                     sg.Combo(months, default_value=previous_month_name, readonly=True)],
                    [sg.Text('Year', size=(7, 1), pad=((70, 0), (20, 0)), font=('Calibri', 11, 'bold')),
                     sg.Slider(range=(2018, 2030), orientation='h', default_value=current_year)],
                    [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
                    [sg.Submit(), sg.Cancel()]
                ]
                main_window_location = window.CurrentLocation()
                popup_location = (
                    main_window_location[0] + 100, main_window_location[1] + 150)  # Adjust the coordinates as needed
                window3 = sg.Window('Select Month and Year', layout, keep_on_top=True, icon=rmr_icon,
                                    location=popup_location)
                event, values = window3.read()
                if event == 'Submit':
                    try:
                        month = values[0]
                        year = values[1]
                        window["-MONTH_DIR-"].update(f'{month} {int(year)}')
                        year = str(round(float(year)))[2:]
                        month_number = months.index(month) + 1
                        if month_number < 10:
                            month_number_str = f'0{month_number}'
                        else:
                            month_number_str = str(month_number)
                        months_list = (year + month_number_str)
                    except Exception as e:
                        # Code to handle the exception and show the error message
                        print("An error occurred:", str(e))
                    window3.close()
                    window['-DISCRETE-'].update(value=False, disabled=True)
                    for key in ['-INPUT_REP-', '-REP_BROWSE-', '-MASTER_SELECT-']:
                        window[key].update(disabled=False)
                elif event == 'Cancel':
                    months_list = ''
                    window["-MONTH_DIR-"].update(months_list)
                    window3.close()
        elif event == '-DISCRETE-':
            if values['-DISCRETE-']:
                for key in ['-MASTER_SELECT-']:
                    window[key].update(disabled=True, value='')
                    for key in ['-INPUT_REP-', '-REP_BROWSE-', '-MASTER_TEXT-']:
                        window[key].update(visible=False)
                        if key == '-MASTER_SELECT-':
                            window[key].update(value=False)
                        elif key == '-INPUT_REP-':
                            window[key].update(value='')
            elif not values['-DISCRETE-']:
                for key in ['-INPUT_REP-', '-REP_BROWSE-', '-MASTER_SELECT-']:
                    window[key].update(disabled=False)
            if values['-OPTION-']:
                try:
                    if months_list:
                        with open(months_list, 'r') as f:
                            months = [line.strip() for line in f.readlines()]
                except NameError:
                    sg.popup_error("NameError: Probably a month file is not selected yet!", icon=rmr_icon)
                except FileNotFoundError as e:
                    sg.popup_error("FileNotFoundError" + str(e), icon=rmr_icon)
            # window['-MASTER_SELECT-'].update(value=False, disabled=True)
        elif event == '-MASTER_SELECT-':
            for key in ['-MASTER_TEXT-', '-INPUT_REP-', '-REP_BROWSE-']:
                window[key].update(visible=values['-MASTER_SELECT-'])
        elif event in ['-SURVEY_TOT-', '-SURVEY_ES-']:
            for key in ['-OPTION-', '-DISCRETE-', '-MASTER_SELECT-']:
                window[key].update(disabled=False)
            window['-BCP_DATA_STORE-'].update(value='')
            window['-MONTH_DIR-'].update(visible=True)
        elif event == '-SURVEY_BCP-':
            for key in ['-OPTION-', '-DISCRETE-', '-MASTER_SELECT-']:
                window[key].update(value='', disabled=True)
            for key in ['-MASTER_TEXT-', '-INPUT_REP-', '-REP_BROWSE-', '-MONTH_DIR-']:
                window[key].update(visible=False)
            window['-MONTH_DIR-'].update(value='')
            popup_layout = [[sg.Text('BCP File:'), sg.InputText(key='-BCP_STORE-'),
                             sg.FilesBrowse(file_types=(
                                 (('BCP Files', '*.bcp'),)))],
                            [sg.Button('OK'), sg.Button('Cancel')]
                            ]
            main_window_location = window.CurrentLocation()
            popup_location = (
                main_window_location[0] + 30, main_window_location[1] + 150)  # Adjust the coordinates as needed
            popup_window = sg.Window('Select a BCP file', popup_layout, keep_on_top=True, icon=rmr_icon,
                                     location=popup_location)
            while True:
                popup_event, popup_values = popup_window.read()
                if popup_event in (sg.WINDOW_CLOSED, 'Cancel'):
                    break
                if popup_event == 'OK':
                    input_bcp = popup_values['-BCP_STORE-']
                    window['-BCP_DATA_STORE-'].update(value=os.path.basename(input_bcp))
                    break
            popup_window.close()
        elif event == '-SUBMIT-':
            try:
                for key in ['REPLACE CARDS/COLUMNS', 'SORT CARDS', 'RESPONDENT CARDS']:
                    window[key].update(disabled=True)
                cards_list = values["-CARD_LIST-"]
                output_dir = os.path.dirname(cards_list)
                survey_dict = {'-SURVEY_TOT-': 'TOT', '-SURVEY_ES-': 'ES', '-SURVEY_BCP-': 'BCP'}
                for key in survey_dict.keys():
                    if values[key]:
                        data_store = survey_dict.get(key)
                # Check if the output file name is provided
                output_file = values["-OUTPUT_FILE-"] + '.bcp'
                output_file_rep = values["-OUTPUT_FILE-"] + '_replaced.bcp'
                if values["-OUTPUT_FILE-"] == ' .bcp':
                    output_file = ''
                    del values["-OUTPUT_FILE-"]
                open_dir = values["-CHECKBOX-"]
                cpangl = values["-PANGLOSS-"]
                dis_month = values["-DISCRETE-"]
                master_select = values["-MASTER_SELECT-"]
                input_rep = values["-INPUT_REP-"]
                # Check if all inputs are provided
                if master_select:
                    required_inputs = ['-CARD_LIST-', '-OPTION-', '-OUTPUT_FILE-', '-INPUT_REP-']
                elif data_store == 'BCP':
                    required_inputs = ['-CARD_LIST-', '-OUTPUT_FILE-']
                else:
                    required_inputs = ['-CARD_LIST-', '-OPTION-', '-OUTPUT_FILE-']
                # Check if all inputs are provided
                if any(not values[key] or values[key] == 'Please select a file' or values[
                    key] == 'Please select an option'
                       for key in required_inputs):
                    for key in ['REPLACE CARDS/COLUMNS', 'SORT CARDS', 'RESPONDENT CARDS']:
                        window[key].update(disabled=False)
                    event, _ = window.read(timeout=30)
                    for key in required_inputs:
                        if not values[key]:
                            element = window[key]
                            if key == '-CARD_LIST-':
                                element.Update('Please select a file', background_color='lightyellow')
                            elif key == '-OUTPUT_FILE-':
                                element.Update(background_color='lightyellow')
                            elif isinstance(element, sg.Combo):
                                element.update('Please select an option')
                        if master_select:
                            if not values['-INPUT_REP-']:
                                element = window['-INPUT_REP-']
                                element.Update('Please select a file', background_color='lightyellow')
                    continue
                window['-INPUT_REP-'].Update(background_color='lightgray')
                window['-OUTPUT_FILE-'].Update(background_color='lightgray')
                if data_store != 'BCP':
                    if not dis_month:
                        command = ["Y:\\ASTEROID\\Builder_Unreleased\\SELECTCARDS", cards_list, months_list, data_store,
                                   output_file]
                        try:
                            # Execute the command with a progress bar
                            progress_bar = sg.ProgressBar(100, orientation='h', size=(20, 20),
                                                          bar_color=('blue', 'gray'),
                                                          )
                            layout = [
                                [sg.Text(key='-BCPNAME-')],
                                [progress_bar],
                                [sg.Text('', key='-PROGRESS-', size=(20, 1))],
                                # #if you wish to see selectcards output, uncomment these lines
                                # [sg.Multiline(size=(80, 10), reroute_stdout=True, reroute_stderr=False, reroute_cprint=True,
                                #               write_only=True, font='Courier 8', autoscroll=True, horizontal_scroll=True,
                                #               do_not_clear=True, key='-ML-')],
                                [sg.Cancel()]
                            ]
                            window2 = sg.Window('SelectCards', layout, finalize=True, keep_on_top=True, icon=rmr_icon)
                            window2.refresh()
                            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                       universal_newlines=True,
                                                       creationflags=subprocess.CREATE_NO_WINDOW)
                            # Read the output of the command and update the progress bar
                            output = ""
                            keep_out_dir = ""
                            output_window = ''
                            # Compile the regex patterns
                            percentage_pattern = re.compile(r'\d+\.\d+%')
                            success_pattern = re.compile(r"Successfully\s+completed")
                            bcp_name_pattern = re.compile(r"Reading.+\\(.+)\.bcp")
                            while True:
                                event, values = window2.read(timeout=30)
                                if event in (sg.WIN_CLOSED, 'Cancel'):
                                    process.terminate()  # Terminate the subprocess
                                    break
                                output = process.stdout.readline()
                                if output == '' and process.poll() is not None:
                                    break
                                if output:
                                    matches = percentage_pattern.findall(output)
                                    matches2 = success_pattern.findall(output)
                                    matches3 = bcp_name_pattern.findall(output)
                                    if matches3:
                                        window2['-BCPNAME-'].update(f'Reading {matches3[0]}...')
                                    elif matches:
                                        percentage = int(float(matches[0][:-1]))
                                        # Update the progress bar and label
                                        progress_bar.UpdateBar(percentage)
                                        window2['-PROGRESS-'].update(f'{percentage:.0f}%')
                                    elif matches2:
                                        sg.popup_no_buttons(success_message, non_blocking=True,
                                                            background_color='mediumspringgreen', no_titlebar=True,
                                                            font=('Calibri', 11, 'bold'), text_color='black',
                                                            grab_anywhere=True, icon=rmr_icon,
                                                            keep_on_top=True, auto_close=True, auto_close_duration=3)
                                    elif "**** ERROR" in output:
                                        error_message = re.findall(r'ERROR : (.+)', output)[0]
                                        popup_error(error_message)
                                        keep_out_dir = output_dir
                                        output_dir = ''
                                        break
                            try:
                                if open_dir and output_dir != '':
                                    if cpangl:
                                        if event in (sg.WIN_CLOSED, 'Cancel'):
                                            process.terminate()  # Terminate the subprocess
                                            break
                                        # Define the layout of the popup window
                                        layout = [[sg.Text('Please wait while creating dat file...')],
                                                  [sg.Text('', key='_OUTPUT_')]]
                                        # Create the popup window
                                        window3 = sg.Window('Creating dat file', layout, no_titlebar=True,
                                                            finalize=True,
                                                            keep_on_top=True)
                                        current_path = os.getcwd()
                                        sg.popup_notify("Please Wait, this process might take a few seconds...")
                                        # Launch the subprocess
                                        dat_file = f'{os.path.splitext(output_file)[0]}.dat'
                                        command2 = ["Y:\\Asteroid\\cpangloss", "P", "Q", output_file, dat_file]
                                        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE,
                                                                    stderr=subprocess.STDOUT,
                                                                    universal_newlines=True,
                                                                    creationflags=subprocess.CREATE_NO_WINDOW)
                                        print(dat_file, command2)
                                        try:
                                            # Wait for the subprocess to finish
                                            stdout, stderr = process2.communicate(timeout=600)
                                        except subprocess.TimeoutExpired as timeout_error:
                                            sg.popup_error(str(timeout_error), title="Subprocess timed out",
                                                           background_color='lightgray', icon=rmr_icon,
                                                           text_color='red')
                                            break
                                        except Exception as e:
                                            sg.popup_error(f"Exception occurred: {e}", icon=rmr_icon)
                                            break
                                        finally:
                                            window3.close()
                                            os.startfile(output_dir)
                                    else:
                                        os.startfile(output_dir)
                            except Exception as e:
                                window2.close()
                                continue
                            # Close the window
                            if output_dir == '':
                                output_dir = keep_out_dir
                            window2.close()
                        except FileNotFoundError as e:
                            # Code to handle the exception and show the error message
                            sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray',
                                           text_color='red',
                                           icon=rmr_icon)
                        except Exception as error:
                            popup_error(str(error))
                        # FOR SELECT THEN REPLACE OPERATION
                        if master_select:
                            # Master File: input_rep, Updates File: updates_file_name, output file name: output_file_rep
                            updates_file_name = output_dir + '/' + output_file

                            try:
                                # Execute the command with a progress bar
                                progress_bar = sg.ProgressBar(100, orientation='h', size=(20, 20),
                                                              bar_color=('blue', 'gray'), )
                                layout = [
                                    [sg.Text('', key='-OUTPUT_TEXT-')],
                                    [progress_bar],
                                    [sg.Text('', key='-PROGRESS-', size=(20, 1))],
                                    [sg.Cancel()]
                                ]
                                window3 = sg.Window('ReplaceCards', layout, finalize=True, keep_on_top=True,
                                                    icon=rmr_icon)
                                window3.refresh()

                                command = ["Y:\\ASTEROID\\Builder_Unreleased\\REPLACECARDS", input_rep,
                                           updates_file_name,
                                           output_file_rep]
                                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                           universal_newlines=True,
                                                           creationflags=subprocess.CREATE_NO_WINDOW)
                                # Read the output of the command and update the progress bar
                                output = ""
                                # Compile the regex patterns
                                percentage_pattern = re.compile(r'\d+\.\d+%')
                                split_complete_pattern = re.compile(r"Splitting\s+complete")
                                sorting_complete_pattern = re.compile(r"Sorting\s+chunks\s+completed")
                                merging_complete_pattern = re.compile(r"Merging\s+complete")
                                success_pattern = re.compile(r"Successfully\s+completed")
                                splitting_pattern = re.compile(r"Splitting")
                                while True:
                                    event, values = window3.read(timeout=30)
                                    if event in (sg.WIN_CLOSED, 'Cancel'):
                                        process.terminate()  # Terminate the subprocess
                                        break
                                    output = process.stdout.readline()
                                    if output == '' and process.poll() is not None:
                                        break
                                    if output:
                                        matches = percentage_pattern.findall(output)
                                        matches2 = split_complete_pattern.findall(output)
                                        matches3 = sorting_complete_pattern.findall(output)
                                        matches4 = merging_complete_pattern.findall(output)
                                        matches5 = success_pattern.findall(output)
                                        matches6 = splitting_pattern.findall(output)
                                        if matches:
                                            percentage = int(float(matches[0][:-1]))
                                            # Update the progress bar and label
                                            progress_bar.UpdateBar(percentage)
                                            window3['-PROGRESS-'].update(f'{percentage:.0f}%')
                                        # Check if there was an error in the output
                                        elif "**** ERROR" in output:
                                            error_message = re.findall(r'ERROR : (.+)', output)[0]
                                            popup_error(error_message)
                                            break
                                        elif matches2:
                                            window3['-OUTPUT_TEXT-'].update('Splitting complete...')
                                            window3['-OUTPUT_TEXT-'].update('Sorting chunks...')
                                        elif matches3:
                                            window3['-OUTPUT_TEXT-'].update('Merging, Please Wait...')
                                        elif matches4:
                                            window3['-OUTPUT_TEXT-'].update('Merging complete...')
                                            window3['-OUTPUT_TEXT-'].update('Replacing Cards...')
                                        elif matches5:
                                            sg.popup_no_buttons('Replaced Successfully!', non_blocking=True,
                                                                background_color='mediumspringgreen', no_titlebar=True,
                                                                font=('Calibri', 11, 'bold'), text_color='black',
                                                                grab_anywhere=True, icon=rmr_icon,
                                                                keep_on_top=True, auto_close=True,
                                                                auto_close_duration=3)
                                        elif matches6:
                                            window3['-OUTPUT_TEXT-'].update('Splitting...')
                                        elif "not found in master (check sort order?)" in output:
                                            error_message = 'Some Response IDs not found in master file (check sort order)'
                                            popup_error(error_message)
                                            break
                                window3.close()
                            except FileNotFoundError as e:
                                # Code to handle the exception and show the error message
                                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray',
                                               text_color='red', icon=rmr_icon)
                            except Exception as error:
                                popup_error(str(error))

                        for key in ['REPLACE CARDS/COLUMNS', 'SORT CARDS', 'RESPONDENT CARDS']:
                            window[key].update(disabled=False)
                    if dis_month:
                        for key in ['REPLACE CARDS/COLUMNS', 'SORT CARDS', 'RESPONDENT CARDS']:
                            window[key].update(disabled=True)
                        output_file = os.path.splitext(output_file)[0]
                        for month in months:
                            command = ["Y:\\ASTEROID\\Builder_Unreleased\\SELECTCARDS", cards_list, month, data_store,
                                       f'{output_file}_{month}.bcp']
                            try:
                                # Execute the command with a progress bar
                                progress_bar = sg.ProgressBar(100, orientation='h', size=(20, 20),
                                                              bar_color=('blue', 'gray'), )
                                layout = [
                                    [sg.Text(key='-BCPNAME-')],
                                    [progress_bar],
                                    [sg.Text('', key='-PROGRESS-', size=(20, 1))],
                                    [sg.Cancel()]
                                ]
                                window2 = sg.Window('SelectCards', layout, finalize=True, keep_on_top=True,
                                                    icon=rmr_icon)
                                window2.refresh()
                                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                           universal_newlines=True,
                                                           creationflags=subprocess.CREATE_NO_WINDOW)
                                # Read the output of the command and update the progress bar
                                output = ""
                                keep_out_dir = ""
                                # Compile the regex patterns
                                percentage_pattern = re.compile(r'\d+\.\d+%')
                                success_pattern = re.compile(r"Successfully\s+completed")
                                bcp_name_pattern = re.compile(r"Reading.+\\(.+)\.bcp")
                                while True:
                                    event, values = window2.read(timeout=30)
                                    if event in (sg.WIN_CLOSED, 'Cancel'):
                                        process.terminate()  # Terminate the subprocess
                                        break
                                    output = process.stdout.readline()
                                    if output == '' and process.poll() is not None:
                                        break
                                    if output:
                                        # Parse the output to extract the percentage value
                                        matches = percentage_pattern.findall(output)
                                        matches2 = success_pattern.findall(output)
                                        matches3 = bcp_name_pattern.findall(output)
                                        if matches3:
                                            window2['-BCPNAME-'].update(f'Reading {matches3[0]}...')
                                        if matches:
                                            percentage = int(float(matches[0][:-1]))
                                            # Update the progress bar and label
                                            progress_bar.UpdateBar(percentage)
                                            window2['-PROGRESS-'].update(f'{percentage:.0f}%')
                                        # Check if there was an error in the output
                                        elif "**** ERROR" in output:
                                            error_message = re.findall(r'ERROR : (.+)', output)[0]
                                            popup_error(error_message)
                                            keep_out_dir = output_dir
                                            output_dir = ''
                                            break
                                try:
                                    if open_dir and output_dir != '':
                                        if cpangl:
                                            # Define the layout of the popup window
                                            layout = [[sg.Text('Please wait while creating dat file...')],
                                                      [sg.Text('', key='_OUTPUT_')]]
                                            # Create the popup window
                                            window3 = sg.Window('Creating dat file', layout, no_titlebar=True,
                                                                finalize=True,
                                                                keep_on_top=True)
                                            current_path = os.getcwd()
                                            sg.popup_notify("Please Wait, this process might take a few seconds...")
                                            # Launch the subprocess
                                            dat_file = f'{os.path.splitext(output_file)[0]}_{month}.dat'
                                            bcp_file = f'{os.path.splitext(output_file)[0]}_{month}.bcp'
                                            command2 = ["Y:\\Asteroid\\cpangloss", "P", "Q", bcp_file, dat_file]
                                            process2 = subprocess.Popen(command2, stdout=subprocess.PIPE,
                                                                        stderr=subprocess.STDOUT,
                                                                        universal_newlines=True,
                                                                        creationflags=subprocess.CREATE_NO_WINDOW)
                                            try:
                                                # Wait for the subprocess to finish
                                                stdout, stderr = process2.communicate(timeout=600)
                                            except subprocess.TimeoutExpired as timeout_expire:
                                                sg.popup_error(str(timeout_expire), title="Subprocess timed out",
                                                               background_color='lightgray',
                                                               text_color='red', icon=rmr_icon)
                                            except Exception as e:
                                                sg.popup_error(f"Exception occurred: {e}", icon=rmr_icon)
                                            finally:
                                                window3.close()
                                except Exception as e:
                                    window2.close()
                                    continue
                                # Close the window
                                if output_dir == '':
                                    output_dir = keep_out_dir
                                    if output_dir == '':
                                        output_dir = os.path.dirname(values["-CARD_LIST-"])
                                window2.close()
                            except FileNotFoundError as e:
                                # Code to handle the exception and show the error message
                                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray',
                                               text_color='red')
                                break
                            except Exception as other_errors:
                                popup_error(str(other_errors))
                                break
                        sg.popup_no_buttons(success_message, non_blocking=True, background_color='mediumspringgreen',
                                            no_titlebar=True,
                                            font=('Calibri', 11, 'bold'), text_color='black', grab_anywhere=True,
                                            keep_on_top=False, auto_close=True, auto_close_duration=3, icon=rmr_icon)
                        os.startfile(output_dir)
                        for key in ['REPLACE CARDS/COLUMNS', 'SORT CARDS', 'RESPONDENT CARDS']:
                            window[key].update(disabled=False)
                elif input_bcp and data_store == 'BCP':
                    command = ["Y:\\ASTEROID\\Builder_Unreleased\\SELECTCARDS2", input_bcp, "78,80", cards_list,
                               output_file]
                    try:
                        # Execute the command with a progress bar
                        progress_bar = sg.ProgressBar(100, orientation='h', size=(20, 20), bar_color=('blue', 'gray'), )
                        layout = [
                            [sg.Text(key='-BCPNAME-')],
                            [progress_bar],
                            [sg.Text('', key='-PROGRESS-', size=(20, 1))],
                            [sg.Cancel()]
                        ]
                        window2 = sg.Window('SelectCards', layout, finalize=True, keep_on_top=True, icon=rmr_icon)
                        window2.refresh()
                        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                   universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        # Compile the regex patterns
                        percentage_pattern = re.compile(r'\d+\.\d+%')
                        success_pattern = re.compile(r"Successfully\s+completed")
                        bcp_name_pattern = re.compile(r"Reading.+/(.+)\.bcp")
                        while True:
                            event, values = window2.read(timeout=30)
                            if event in (sg.WIN_CLOSED, 'Cancel'):
                                process.terminate()  # Terminate the subprocess
                                break
                            output = process.stdout.readline()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                matches = percentage_pattern.findall(output)
                                matches2 = success_pattern.findall(output)
                                matches3 = bcp_name_pattern.findall(output)
                                if matches3:
                                    window2['-BCPNAME-'].update(f'Reading {matches3[0]}...')
                                elif matches:
                                    percentage = int(float(matches[0][:-1]))
                                    # Update the progress bar and label
                                    progress_bar.UpdateBar(percentage)
                                    window2['-PROGRESS-'].update(f'{percentage:.0f}%')
                                elif matches2:
                                    sg.popup_no_buttons(success_message, non_blocking=True,
                                                        background_color='mediumspringgreen', no_titlebar=True,
                                                        font=('Calibri', 11, 'bold'), text_color='black',
                                                        grab_anywhere=True, icon=rmr_icon,
                                                        keep_on_top=True, auto_close=True, auto_close_duration=3)
                                elif "**** ERROR" in output:
                                    error_message = re.findall(r'ERROR : (.+)', output)[0]
                                    popup_error(error_message)
                                    keep_out_dir = output_dir
                                    output_dir = ''
                                    break
                        window2.close()
                        try:
                            if open_dir and output_dir != '':
                                if cpangl:
                                    if event in (sg.WIN_CLOSED, 'Cancel'):
                                        process.terminate()  # Terminate the subprocess
                                        break
                                    # Define the layout of the popup window
                                    layout = [[sg.Text('Please wait while creating dat file...')],
                                              [sg.Text('', key='_OUTPUT_')]]
                                    # Create the popup window
                                    window3 = sg.Window('Creating dat file', layout, no_titlebar=True, finalize=True,
                                                        keep_on_top=True)
                                    current_path = os.getcwd()
                                    sg.popup_notify("Please Wait, this process might take a few seconds...")
                                    # Launch the subprocess
                                    dat_file = f'{os.path.splitext(output_file)[0]}.dat'
                                    command2 = ["Y:\\Asteroid\\cpangloss", "P", "Q", output_file, dat_file]
                                    process2 = subprocess.Popen(command2, stdout=subprocess.PIPE,
                                                                stderr=subprocess.STDOUT,
                                                                universal_newlines=True,
                                                                creationflags=subprocess.CREATE_NO_WINDOW)
                                    print(dat_file, command2)
                                    try:
                                        # Wait for the subprocess to finish
                                        stdout, stderr = process2.communicate(timeout=600)
                                    except subprocess.TimeoutExpired as timeout_error:
                                        sg.popup_error(str(timeout_error), title="Subprocess timed out",
                                                       background_color='lightgray', icon=rmr_icon,
                                                       text_color='red')
                                        break
                                    except Exception as e:
                                        sg.popup_error(f"Exception occurred: {e}", icon=rmr_icon)
                                        break
                                    finally:
                                        window3.close()
                                        os.startfile(output_dir)
                                else:
                                    os.startfile(output_dir)
                        except Exception as e:
                            window2.close()
                    except FileNotFoundError as e:
                        # Code to handle the exception and show the error message
                        sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray',
                                       text_color='red',
                                       icon=rmr_icon)
                    except Exception as error:
                        popup_error(str(error))
                for key in ['REPLACE CARDS/COLUMNS', 'SORT CARDS', 'RESPONDENT CARDS']:
                    window[key].update(disabled=False)
            except FileNotFoundError as output_dir_error:
                popup_error("You have likely selected an incorrect directory for the output file. Please make sure you "
                            "choose a local directory instead of a network directory (e.g., rmndcfile03//...). "
                            "Your files have been created, and you can manually open the directory to access them. "
                            "Please ensure to specify the correct directory next time.")
                for key in ['REPLACE CARDS/COLUMNS', 'SORT CARDS', 'RESPONDENT CARDS']:
                    window[key].update(disabled=False)

        # #REPLACECARDS commands start here  #################################
        elif event == '-MASTER_FILE-':
            try:
                output_dir = os.path.dirname(values["-MASTER_FILE-"])
                os.chdir(output_dir)
            except FileNotFoundError as e:
                # Display an error message to the user
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
        elif event == '-FIN_REP-':
            if values['-FIN_REP-']:
                for key in ['-REP_COL-']:
                    window[key].update(disabled=True, value='')
                    window['-ML-'].update(value='')
                    for key in ['-REP_COL_TEXT-', '-REP_COL_OPTION-']:
                        window[key].update(visible=False)
                        if key == '-REP_COL-':
                            window[key].update(value=False)
                        elif key == '-REP_COL_OPTION-':
                            window[key].update(value='')
            elif not values['-FIN_REP-']:
                for key in ['-REP_COL-']:
                    window[key].update(disabled=False)
        elif event == '-REP_COL-':
            for key in ['-REP_COL_TEXT-', '-REP_COL_OPTION-']:
                window[key].update(visible=values['-REP_COL-'])
        elif event == '-REP_COL_OPTION-':
            if values['-REP_COL_OPTION-'] == 'Select column(s) from file':
                popup_layout = [[sg.Text('Column(s) list file:'), sg.InputText(key='-COLUMN_FILE-'),
                                 sg.FilesBrowse(file_types=(
                                     ('COLUMN Files', '*.cols'), ('COLUMN Files', '*.txt'),
                                     ('COLUMN Files', '*.list')))],
                                [sg.Button('OK'), sg.Button('Cancel')]
                                ]
                main_window_location = window.CurrentLocation()
                popup_location = (
                    main_window_location[0] + 10, main_window_location[1] + 150)  # Adjust the coordinates as needed
                popup_window = sg.Window('Select a Column List File with the Right Format', popup_layout,
                                         keep_on_top=True, icon=rmr_icon,
                                         location=popup_location)
                while True:
                    popup_event, popup_values = popup_window.read()
                    if popup_event in (sg.WINDOW_CLOSED, 'Cancel'):
                        break
                    if popup_event == 'OK':
                        columns_list = popup_values['-COLUMN_FILE-']
                        break
                popup_window.close()
            else:
                main_window_location = window.CurrentLocation()
                columns_list = select_columns(column_count, main_window_location)
                for key in ['-ML-']:
                    window['-ML-'].update(value='')
                    window[key].print(f'Columns selected: {columns_list}')
        elif event == '-SUBMIT2-':
            for key in ['SELECT CARDS', 'SORT CARDS', 'RESPONDENT CARDS']:
                window[key].update(disabled=True)
            # Construct the command
            master_file = values['-MASTER_FILE-']
            updates_file = values['-UPDATES_FILE-']
            # Check if the output file name is provided
            output_file = values["-REPLACED_FILE-"] + '.bcp'
            if values["-REPLACED_FILE-"] == ' .bcp':
                output_file = ''
                del values["-REPLACED_FILE-"]
            open_dir = values['-OPEN_FOLDER-']
            rep_col = values['-REP_COL-']
            fin_rep = values['-FIN_REP-']

            # Check if all inputs are provided
            if rep_col:
                required_inputs = ['-MASTER_FILE-', '-UPDATES_FILE-', '-REPLACED_FILE-', '-REP_COL_OPTION-']
            else:
                required_inputs = ['-MASTER_FILE-', '-UPDATES_FILE-', '-REPLACED_FILE-']

            # Check if all inputs are provided
            if any(not values[key] or values[key] == 'Please select a file' for key in required_inputs):
                event, _ = window.read(timeout=30)
                for key in ['SELECT CARDS', 'SORT CARDS', 'RESPONDENT CARDS']:
                    window[key].update(disabled=False)
                for key in required_inputs:
                    if not values[key]:
                        element = window[key]
                        if key == '-MASTER_FILE-' or key == '-UPDATES_FILE-':
                            element.Update('Please select a file', text_color='brown', background_color='lightyellow')
                        elif key == '-REPLACED_FILE-':
                            element.Update(background_color='lightyellow')
                        elif isinstance(element, sg.Combo):
                            element.update('Please select an option')
                continue
            window['-REPLACED_FILE-'].Update(background_color='ivory2')

            if fin_rep:
                command = ["Y:\\ASTEROID\\Builder_Unreleased\\REPLACETRAILERPAIRS", master_file, updates_file,
                           output_file]
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                    # Read the output of the command and update the progress bar
                    output = ""
                    output_window = ""
                    while True:
                        event, _ = window.read(timeout=30)
                        if event in (sg.WIN_CLOSED, '-EXIT2-'):
                            process.terminate()  # Terminate the subprocess
                            break
                        elif event == '-CANCEL-':
                            process.terminate()  # Terminate the subprocess
                            output_window = output_window + "Process cancelled by user."
                            window["-ML-"].update(value=output_window)
                            break
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        elif output:
                            # Parse the output to extract the percentage value
                            output_window = output_window + output
                            window["-ML-"].update(value=output_window)
                            if "Successfully completed" in output and open_dir:
                                os.startfile(output_dir)
                            # Check if there was an error in the output
                            elif "Unhandled Exception" in output:
                                sg.popup_error("Illegal characters in path!", button_color=('white', 'red'),
                                               title="Error",
                                               background_color='lightgray', text_color='red', keep_on_top=True,
                                               non_blocking=True, icon=rmr_icon,
                                               auto_close=True, auto_close_duration=3)
                                break
                except FileNotFoundError as e:
                    # Code to handle the exception and show the error message
                    sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                                   icon=rmr_icon)
                except Exception as error:
                    popup_error(str(error))

            elif rep_col:
                command = ["Y:\\ASTEROID\\Builder_Unreleased\\REPLACECOLUMNS", master_file, updates_file, columns_list,
                           output_file]
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                    # Read the output of the command and update the progress bar
                    output = ""
                    output_window = ""
                    while True:
                        event, _ = window.read(timeout=30)
                        if event in (sg.WIN_CLOSED, '-EXIT2-'):
                            process.terminate()  # Terminate the subprocess
                            break
                        elif event == '-CANCEL-':
                            process.terminate()  # Terminate the subprocess
                            output_window = output_window + "Process cancelled by user."
                            window["-ML-"].update(value=output_window)
                            break
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        elif output:
                            # Parse the output to extract the percentage value
                            output_window = output_window + output
                            window["-ML-"].update(value=output_window)
                            if "Successfully completed" in output and open_dir:
                                os.startfile(output_dir)
                            # Check if there was an error in the output
                            elif "Unhandled Exception" in output:
                                sg.popup_error("Illegal characters in path!", button_color=('white', 'red'),
                                               title="Error",
                                               background_color='lightgray', text_color='red', keep_on_top=True,
                                               non_blocking=True, icon=rmr_icon,
                                               auto_close=True, auto_close_duration=3)
                                break
                except FileNotFoundError as e:
                    # Code to handle the exception and show the error message
                    sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                                   icon=rmr_icon)
                except Exception as error:
                    popup_error(str(error))

            else:
                command = ["Y:\\ASTEROID\\Builder_Unreleased\\REPLACECARDS", master_file, updates_file, output_file]
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                    # Read the output of the command and update the progress bar
                    output = ""
                    output_window = ""
                    while True:
                        event, _ = window.read(timeout=30)
                        if event in (sg.WIN_CLOSED, '-EXIT2-'):
                            process.terminate()  # Terminate the subprocess
                            break
                        elif event == '-CANCEL-':
                            process.terminate()  # Terminate the subprocess
                            output_window = output_window + "Process cancelled by user."
                            window["-ML-"].update(value=output_window)
                            break
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        elif output:
                            # Parse the output to extract the percentage value
                            output_window = output_window + output
                            window["-ML-"].update(value=output_window)
                            if "Successfully completed" in output and open_dir:
                                os.startfile(output_dir)
                            # Check if there was an error in the output
                            elif "Unhandled Exception" in output:
                                sg.popup_error("Illegal characters in path!", button_color=('white', 'red'),
                                               title="Error",
                                               background_color='lightgray', text_color='red', keep_on_top=True,
                                               non_blocking=True, icon=rmr_icon,
                                               auto_close=True, auto_close_duration=3)
                                break
                except FileNotFoundError as e:
                    # Code to handle the exception and show the error message
                    sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                                   icon=rmr_icon)
                except Exception as error:
                    popup_error(str(error))

            for key in ['SELECT CARDS', 'SORT CARDS', 'RESPONDENT CARDS']:
                window[key].update(disabled=False)

        # #SORTCARDS START HERE ##############################################
        elif event == '-INPUT_FILE-':
            try:
                output_dir = os.path.dirname(values["-INPUT_FILE-"])
                os.chdir(output_dir)
            except FileNotFoundError as e:
                # Display an error message to the user
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
        elif event == '-MERGE_SELECT-':
            if values['-MERGE_SELECT-']:
                for key in ['-MERGE_TEXT-', '-INPUT_MERGE-', '-MERGE_BROWSE-']:
                    window[key].update(visible=values['-MERGE_SELECT-'])
                    for key in ['-MASTER_SELECT_2-']:
                        window[key].update(disabled=False)
            elif not values['-MERGE_SELECT-']:
                for key in ['-MERGE_TEXT-', '-INPUT_MERGE-', '-MERGE_BROWSE-']:
                    window[key].update(visible=values['-MERGE_SELECT-'])
                window['-MASTER_SELECT_2-'].update(value=False, disabled=True)
                for key in ['-MASTER_TEXT_2-', '-INPUT_REP_2-', '-REP_BROWSE_2-']:
                    window[key].update(visible=values['-MERGE_SELECT-'])
        elif event == '-MASTER_SELECT_2-':
            for key in ['-MASTER_TEXT_2-', '-INPUT_REP_2-', '-REP_BROWSE_2-']:
                window[key].update(visible=values['-MASTER_SELECT_2-'])
        elif event == '-SUBMIT3-':
            for key in ['SELECT CARDS', 'REPLACE CARDS/COLUMNS', 'RESPONDENT CARDS']:
                window[key].update(disabled=True)
            # Construct the command
            input_file = values['-INPUT_FILE-']
            # Check if the output file name is provided
            output_file = values["-SORTED_FILE-"] + '.bcp'
            output_file_2 = values["-SORTED_FILE-"] + '_Merged_Replaced.bcp'
            if values["-SORTED_FILE-"] == ' .bcp':
                output_file = ''
                del values["-SORTED_FILE-"]
            open_dir = values['-OPEN_SORT_DIR-']
            merge_files = values['-MERGE_SELECT-']
            input_merge = values['-INPUT_MERGE-']
            master_select_2 = values['-MASTER_SELECT_2-']
            master_file_2 = values['-INPUT_REP_2-']

            if not merge_files:
                # Check if all inputs are provided
                required_inputs = ['-INPUT_FILE-', '-SORTED_FILE-']
                # Check if all inputs are provided
                if any(not values[key] or values[key] == 'Please select a file' for key in required_inputs):
                    event, _ = window.read(timeout=30)
                    for key in ['SELECT CARDS', 'REPLACE CARDS/COLUMNS', 'RESPONDENT CARDS']:
                        window[key].update(disabled=False)
                    for key in required_inputs:
                        if not values[key]:
                            element = window[key]
                            if key == '-INPUT_FILE-':
                                element.Update('Please select a file', text_color='brown',
                                               background_color='lightyellow')
                            elif key == '-SORTED_FILE-':
                                element.Update(background_color='lightyellow')
                    continue
                window['-SORTED_FILE-'].Update(background_color='ivory2')

                command = ["Y:\\ASTEROID\\Builder_Unreleased\\SORTBCP", input_file, '2, 1, 9, 78, 80', output_file]
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                    # Read the output of the command and update the progress bar
                    output = ""
                    output_window = ""
                    while True:
                        event, _ = window.read(timeout=30)
                        if event in (sg.WIN_CLOSED, '-EXIT3-'):
                            process.terminate()  # Terminate the subprocess
                            break
                        elif event == '-CANCEL2-':
                            process.terminate()  # Terminate the subprocess
                            output_window = output_window + "Process cancelled by user."
                            window["-ML_SORT-"].update(value=output_window)
                            break
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        elif output:
                            # Parse the output to extract the percentage value
                            output_window = output_window + output
                            window["-ML_SORT-"].update(value=output_window)
                            if "Successfully sorted" in output and open_dir:
                                os.startfile(output_dir)
                            # Check if there was an error in the output
                            elif "**** ERROR" in output:
                                sg.popup_error("Illegal characters in path!", button_color=('white', 'red'),
                                               title="Error",
                                               background_color='lightgray', text_color='red', keep_on_top=True,
                                               non_blocking=True, icon=rmr_icon,
                                               auto_close=True, auto_close_duration=3)
                                break
                except FileNotFoundError as e:
                    # Code to handle the exception and show the error message
                    sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                                   icon=rmr_icon)
                except Exception as error:
                    popup_error(str(error))
            elif merge_files:
                # Check if all inputs are provided
                if master_select_2:
                    required_inputs = ['-INPUT_FILE-', '-SORTED_FILE-', '-INPUT_MERGE-', '-INPUT_REP_2-']
                else:
                    required_inputs = ['-INPUT_FILE-', '-SORTED_FILE-', '-INPUT_MERGE-']
                # Check if all inputs are provided
                if any(not values[key] or values[key] == 'Please select a file' for key in required_inputs):
                    event, _ = window.read(timeout=30)
                    for key in ['SELECT CARDS', 'REPLACE CARDS/COLUMNS', 'RESPONDENT CARDS']:
                        window[key].update(disabled=False)
                    for key in required_inputs:
                        if not values[key]:
                            element = window[key]
                            if key in ['-INPUT_FILE-', '-INPUT_MERGE-', '-INPUT_REP_2-']:
                                element.Update('Please select a file', text_color='brown',
                                               background_color='lightyellow')
                            elif key == '-SORTED_FILE-':
                                element.Update(background_color='lightyellow')
                    continue
                window['-SORTED_FILE-'].Update(background_color='ivory2')

                input_merge = input_merge.replace(';', ',')
                command = ["Y:\\ASTEROID\\Builder_Unreleased\\SORTBCP", f"{input_file}, {input_merge}",
                           '2, 1, 9, 78, 80', output_file]
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    # Read the output of the command and update the progress bar
                    output = ""
                    output_window = ""
                    while True:
                        event, _ = window.read(timeout=30)
                        if event in (sg.WIN_CLOSED, '-EXIT3-'):
                            process.terminate()  # Terminate the subprocess
                            break
                        elif event == '-CANCEL2-':
                            process.terminate()  # Terminate the subprocess
                            output_window = output_window + "Process cancelled by user."
                            window["-ML_SORT-"].update(value=output_window)
                            break
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        elif output:
                            # Parse the output to extract the percentage value
                            output_window = output_window + output
                            window["-ML_SORT-"].update(value=output_window)
                            if "Successfully sorted" in output and open_dir:
                                os.startfile(output_dir)
                            # Check if there was an error in the output
                            elif "**** ERROR" in output:
                                sg.popup_error("Illegal characters in path!", button_color=('white', 'red'),
                                               title="Error",
                                               background_color='lightgray', text_color='red', keep_on_top=True,
                                               non_blocking=True, icon=rmr_icon,
                                               auto_close=True, auto_close_duration=3)
                                break
                except FileNotFoundError as e:
                    # Code to handle the exception and show the error message
                    sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                                   icon=rmr_icon)
                except Exception as error:
                    popup_error(str(error))

                if master_select_2:
                    command = ["Y:\\ASTEROID\\Builder_Unreleased\\REPLACECARDS", master_file_2, output_file,
                               output_file_2]
                    try:
                        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                   universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                        # Read the output of the command and update the progress bar
                        output = ""
                        output_window = ""
                        while True:
                            event, _ = window.read(timeout=30)
                            if event in (sg.WIN_CLOSED, '-EXIT3-'):
                                process.terminate()  # Terminate the subprocess
                                break
                            elif event == '-CANCEL2-':
                                process.terminate()  # Terminate the subprocess
                                output_window = output_window + "Process cancelled by user."
                                window["-ML_SORT-"].update(value=output_window)
                                break
                            output = process.stdout.readline()
                            if output == '' and process.poll() is not None:
                                break
                            elif output:
                                # Parse the output to extract the percentage value
                                output_window = output_window + output
                                window["-ML_SORT-"].update(value=output_window)
                                if "Successfully completed" in output and open_dir:
                                    os.startfile(output_dir)
                                # Check if there was an error in the output
                                elif "Unhandled Exception" in output:
                                    sg.popup_error("Illegal characters in path!", button_color=('white', 'red'),
                                                   title="Error",
                                                   background_color='lightgray', text_color='red', keep_on_top=True,
                                                   non_blocking=True, icon=rmr_icon,
                                                   auto_close=True, auto_close_duration=3)
                                    break
                    except FileNotFoundError as e:
                        # Code to handle the exception and show the error message
                        sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray',
                                       text_color='red',
                                       icon=rmr_icon)
                    except Exception as error:
                        popup_error(str(error))

            for key in ['SELECT CARDS', 'REPLACE CARDS/COLUMNS', 'RESPONDENT CARDS']:
                window[key].update(disabled=False)

        # #SELECTRESPONDENTS ##############################################
        elif event == '-RES_BCP-':
            try:
                resp_dir = os.path.dirname(values["-RES_BCP-"])
                os.chdir(resp_dir)
            except FileNotFoundError as e:
                # Display an error message to the user
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
        elif event == '-RES_ID-':
            resp_id = values['-RES_ID-']
            if len(resp_id) == 9:
                if resp_id.isnumeric():
                    window['-RES_ID-'].update(background_color='ivory2')
                    window['-RID_CHECK-'].update(visible=False)
            elif len(resp_id) == 0:
                window['-RES_ID-'].update(background_color='ivory2')
                window['-RID_CHECK-'].update(visible=False)
            elif len(resp_id) > 9:
                window["-RES_ID-"].update(resp_id[:9])
            else:
                window['-RES_ID-'].update(background_color='lightsalmon')
                window['-RID_CHECK-'].update(visible=True)
        elif event == '-SUBMIT4-':
            for key in ['SELECT CARDS', 'REPLACE CARDS/COLUMNS', 'SORT CARDS']:
                window[key].update(disabled=True)
            input_resp = values['-RES_BCP-']
            resp_id = values['-RES_ID-']
            resp_output = values['-ASC_FILE-'] + '.asc'
            open_resp = values['-OPEN_RESP_DIR-']

            required_inputs = ['-RES_BCP-', '-RES_ID-']
            # Check if all inputs are provided
            if any(not values[key] or values[key] == 'Please select a file' for key in required_inputs):
                event, _ = window.read(timeout=30)
                for key in ['SELECT CARDS', 'REPLACE CARDS/COLUMNS', 'RESPONDENT CARDS']:
                    window[key].update(disabled=False)
                for key in required_inputs:
                    if not values[key]:
                        element = window[key]
                        element.Update('Please select a file', text_color='brown')
                continue
            if resp_output:
                command = ["Y:\\ASTEROID\\Builder_Unreleased\\SELRESP", input_resp, resp_id, resp_output]
            else:
                command = ["Y:\\ASTEROID\\Builder_Unreleased\\SELRESP", input_resp, resp_id]
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                # Read the output of the command and update the progress bar
                output = ""
                output_window = ""
                while True:
                    event, _ = window.read(timeout=30)
                    if event in (sg.WIN_CLOSED, '-EXIT4-'):
                        process.terminate()  # Terminate the subprocess
                        break
                    elif event == '-CANCEL3-':
                        process.terminate()  # Terminate the subprocess
                        output_window = output_window + "Process cancelled by user."
                        window["-ML_RESP-"].update(value=output_window)
                        break
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    elif output:
                        # Parse the output to extract the percentage value
                        output_window = output_window + output
                        window["-ML_RESP-"].update(value=output_window)
                        if "Successfully completed" in output and open_resp:
                            os.startfile(resp_dir)
                        # Check if there was an error in the output
                        elif "**** ERROR" in output:
                            sg.popup_error("Illegal characters in path!", button_color=('white', 'red'),
                                           title="Error",
                                           background_color='lightgray', text_color='red', keep_on_top=True,
                                           non_blocking=True, icon=rmr_icon,
                                           auto_close=True, auto_close_duration=3)
                            break
            except FileNotFoundError as e:
                # Code to handle the exception and show the error message
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
            except Exception as error:
                popup_error(str(error))
            for key in ['SELECT CARDS', 'REPLACE CARDS/COLUMNS', 'SORT CARDS']:
                window[key].update(disabled=False)

    # Close the GUI window
    window.close()


if __name__ == '__main__':
    # Update the layout to include the TabGroup
    layout = ui_layout()
    # Create the GUI window
    window = sg.Window(f"CARDS GUI (Version: {version})", layout,
                       icon=rmr_icon)
    success_message = "Data Collected Successfully!"
    column_count = 77

    main()
=======
import subprocess
import PySimpleGUI as sg
import os
import re
from datetime import datetime

rmr_icon = $ICON_DIR
version = '1.3.1'
input_bcp = ''


def usage_text():
    usage_txt = """SELECT CARDS:
    - Card List: Select the File Containing List of Cards
    - Month(s): Choose the Month(s) to Select Data for
    - Data Store:
      - TOT: Select TOT survey
      - ES: Select ES survey
      - BCP: Select from a single named BCP file
    - Output File Name: Specify the Output File Name for the generated data
    - Open Output Directory When Finished Successfully: Check this option to open the output directory after completion
    - Create DAT File with BCP: Check this option to create a DAT file using CPANGLOSS
    - Create DISCRETE BCP Files from Months File: Check this option to generate a BCP file for each month in the list
    - Use Created BCP File to Replace Cards in a Master File: Check this option to replace cards in a Master File
    - Master File: Select the BCP master file to replace data
----------------------------------------------------------
REPLACE CARDS:
    - Master File: Select the BCP master file to replace data
    - Updates File: Select the Updates File to replace data in the Master File
    - Output File Name: Specify the Output File Name containing the replaced data
    - Open Output Directory When Finished Successfully: Check this option to open the output directory after completion
----------------------------------------------------------
SORT CARDS:
    - Input File: Select the BCP File to Sort
    - Output File Name: Specify the Output Sorted File Name
    - Open Output Directory When Finished Successfully: Check this option to open the output directory after completion
    - Merge With Another BCP File: Check this option to merge with another BCP file
    - File to Merge: Select the BCP File to Merge
    """
    return usage_txt


def faq_text():
    faq_text = '''
    Frequently Asked Questions:

             Q: How do I select a card list?
             A: Click on the "Card List" field and browse for the file containing the list of cards.

             Q: Can I enter month(s) manually?
             A: Yes, you can select the option "Enter month manually" to manually enter the month(s).

             Q: What is the output file name?
             A: The output file name is the name you specify for the file containing the processed data.

             Q: How can I open the output directory?
             A: By default, the output directory opens automatically when the process is finished successfully. 
                  You can uncheck the "Open Output Directory When Finished Successfully" option to disable this.

             Q: How can I create a DAT file with BCP?
             A: You can enable the "Create DAT File with BCP" option to generate a DAT file along with the BCP file.

             Q: How do I replace cards in a master file?
             A: Select the "Use Created BCP File to Replace Cards in a Master File" option and provide the master file to replace the data.

             Q: How can I sort a BCP file?
             A: In the "Sort Cards" tab, select the BCP file and specify the output file name for the sorted data.'''
    return faq_text


def ui_layout():
    sg.theme("Reddit")
    # Help menu layout
    help_menu_layout = [['    Help    ', ['Usage...', 'FAQ...', '---', 'About...']]]
    selectcards_layout = [
        sg.Frame('User  Inputs', size=(500, 350), layout=[
            [sg.Text("Card List:", font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (5, 5)),
                     tooltip='Select the File Containing List of Cards'),
             sg.Input(key="-CARD_LIST-", enable_events=True, disabled=True,
                      disabled_readonly_background_color='ivory2'),
             sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                           file_types=(('CARD Files', '*.cards'), ('CARD Files', '*.txt'), ('CARD Files', '*.list')))],
            [sg.Text('Month(s):', font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (5, 5)),
                     tooltip='Choose the Month(s) to Select Data for'),
             sg.Combo(['Select month(s) from file', 'Enter month manually'], key='-OPTION-', enable_events=True,
                      readonly=True,
                      background_color='ivory2'),
             sg.Text(size=(1, 1), pad=((1, 0), (1, 0))), sg.Text(key="-MONTH_DIR-", font=('Calibri', 11, 'bold'))],
            [sg.Text("Data Store:", font=('Calibri', 11, 'bold'), size=(15, 1), pad=((1, 0), (1, 0))),
             sg.Radio("TOT", group_id="survey_radio", key="-SURVEY_TOT-", default=True, font=('Calibri', 11, 'bold'),
                      enable_events=True),
             sg.Radio("ES", group_id="survey_radio", key="-SURVEY_ES-", font=('Calibri', 11, 'bold'),
                      enable_events=True),
             sg.Radio("BCP", group_id="survey_radio", key="-SURVEY_BCP-", font=('Calibri', 11, 'bold'),
                      enable_events=True,
                      tooltip='Uses Selectcards2 to read input from a single BCP file'),
             sg.Text(size=(20, 1), pad=((40, 0), (1, 0)), key="-BCP_DATA_STORE-", font=('Calibri', 11, 'bold')),
             ],
            [sg.Text("Output File Name:", font=('Calibri', 11, 'bold'), size=(15, 1), pad=((2, 0), (2, 0))),
             sg.Input(size=(28, 1),
                      key="-OUTPUT_FILE-", background_color="ivory2"),
             sg.Text(".BCP", size=(4, 1), pad=((0, 2), (2, 0)))],
            [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
            [sg.Checkbox('Open Output Directory When Finished Successfully', font=('Calibri', 11, 'italic'),
                         key='-CHECKBOX-',
                         default=True, enable_events=True)],
            [sg.Checkbox('Create DAT File with BCP', font=('Calibri', 11, 'italic'), key='-PANGLOSS-',
                         default=False, enable_events=True, tooltip='Use CPANGLOSS to Create DAT File')],
            [sg.Checkbox('Create DISCRETE BCP Files from Months File', font=('Calibri', 11, 'italic'), key='-DISCRETE-',
                         default=False, enable_events=True,
                         tooltip='Generate a BCP file for each month in the list of months')],
            [sg.Checkbox('Use Created BCP File to Replace Cards in a Master File', font=('Calibri', 11, 'italic'),
                         key='-MASTER_SELECT-', default=False, enable_events=True,
                         tooltip="Replace cards in a Master File with the BCP File")],
            [sg.Text("Master File:", font=('Calibri', 11, 'bold'), size=(11, 1), pad=((1, 33), (0, 0)),
                        tooltip="Select the BCP master file to replace data", visible=False, key='-MASTER_TEXT-'),
                        sg.Input(size=(45, 1), key="-INPUT_REP-", enable_events=True, disabled=True,
                        disabled_readonly_background_color='ivory2', visible=False),
             sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                           file_types=(('BCP FILE', '*.BCP'),), visible=False, key='-REP_BROWSE-',
                           enable_events=True)],
        ], font='Impact', border_width=2, title_color='teal')
    ]
    tab1_layout = [selectcards_layout,
                   [sg.Column([
                       [sg.Button("Submit", key='-SUBMIT-', enable_events=True, size=(8, 1),
                                  button_color=('white', 'green'), font=("Helvetica", 10)),
                        sg.Button("Exit", key='-EXIT-', enable_events=True, size=(8, 1), button_color=('white', 'red'),
                                  font=("Helvetica", 10))]
                   ], justification='center')]
                   ]
    tab2_layout = [[sg.Frame('User  Inputs', layout=[
        [sg.Text("Master File:", font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (5, 5)),
                 tooltip="Select the BCP master file to replace data"), sg.Input(size=(45, 1), key="-MASTER_FILE-",
                                                                                 enable_events=True, disabled=True,
                                                                                 disabled_readonly_background_color='ivory2'),
         sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                       file_types=(('BCP FILE', '*.BCP'),))],
        [sg.Text("Updates File:", font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (5, 5)),
                 tooltip="Select the Updates File to replace data in the Master File"), sg.Input(size=(45, 1),
                                                                                                 key="-UPDATES_FILE-",
                                                                                                 enable_events=True,
                                                                                                 disabled=True,
                                                                                                 disabled_readonly_background_color='ivory2'),
         sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                       file_types=(('BCP FILE', '*.BCP'),))],
        [sg.Text("Output File Name:", font=('Calibri', 11, 'bold'), size=(15, 1), pad=((2, 3), (5, 5)),
                 tooltip='Specify the Output File Name containing the replaced data'),
         sg.Input(size=(28, 1), key="-REPLACED_FILE-", background_color='ivory2', pad=((2, 0), (5, 0))),
         sg.Text(".BCP", size=(4, 1), pad=((5, 0), (5, 0)))],
        [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
        [sg.Checkbox('Open Output Directory When Finished Successfully', font=('Calibri', 11, 'italic'),
                     key='-OPEN_FOLDER-',
                     default=True, enable_events=True)],
    ], font='Impact', border_width=2, title_color='teal')
                    ],
                   [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
                   [sg.Multiline(size=(69, 10), reroute_stdout=True, reroute_stderr=False, reroute_cprint=True,
                                 enable_events=True,
                                 write_only=True, font='Courier 9', autoscroll=True, auto_refresh=True,
                                 background_color="ivory2",
                                 text_color="maroon", do_not_clear=True, key='-ML-')],
                   [sg.Column([
                       [sg.Button("Submit", key='-SUBMIT2-', enable_events=True, size=(8, 1),
                                  button_color=('white', 'green'), font=("Helvetica", 10)),
                        sg.Button("Exit", key='-EXIT2-', enable_events=True, size=(8, 1), button_color=('white', 'red'),
                                  font=("Helvetica", 10)),
                        sg.Button("Cancel", key='-CANCEL-', enable_events=True, size=(8, 1),
                                  button_color=('black', 'oldlace'),
                                  font=("Helvetica", 10), border_width=2, tooltip='Terminate replace process')]
                   ], justification='center')
                   ]
                   ]
    tab3_layout = [[sg.Frame('User  Inputs', size=(500, 205), layout=[
        [sg.Text("Input File:", font=('Calibri', 11, 'bold'), size=(10, 1), pad=((2, 40), (2, 0)),
                 tooltip="Select the BCP File to Sort"), sg.Input(size=(45, 1), key="-INPUT_FILE-",
                                                                  enable_events=True, disabled=True,
                                                                  disabled_readonly_background_color='ivory2'),
         sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                       file_types=(('BCP FILE', '*.BCP'),))],
        [sg.Text("Output File Name:", font=('Calibri', 11, 'bold'), size=(15, 1), pad=((2, 3), (0, 5)),
                 tooltip='Specify the Output Sorted File Name'),
         sg.Input(size=(28, 1), key="-SORTED_FILE-", background_color='ivory2', pad=((2, 0), (5, 0))),
         sg.Text(".BCP", size=(4, 1), pad=((5, 0), (5, 0)))],
        [sg.Checkbox('Open Output Directory When Finished Successfully', font=('Calibri', 11, 'italic'),
                     key='-OPEN_SORT_DIR-', default=True, enable_events=True, pad=((5, 0), (10, 0)))],
        [sg.Checkbox('Merge With Another BCP File', font=('Calibri', 11, 'italic'),
                     key='-MERGE_SELECT-', default=False, enable_events=True)],
        [sg.Text("File to Merge:", font=('Calibri', 11, 'bold'), size=(11, 1), pad=((1, 33), (0, 0)),
                 tooltip="Select the BCP File to Merge", visible=False, key='-MERGE_TEXT-'), sg.Input(size=(45, 1),
                 key="-INPUT_MERGE-", enable_events=True, disabled=True, disabled_readonly_background_color='ivory2',
                 visible=False),
         sg.FileBrowse(button_text=' ... ', button_color=("white", "#0078d7"),
                       file_types=(('BCP FILE', '*.BCP'),), visible=False, key='-MERGE_BROWSE-', enable_events=True)],
    ], font='Impact', border_width=2, title_color='teal')
                    ],
                   [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
                   [sg.Multiline(size=(69, 8), reroute_stdout=True, reroute_stderr=False, reroute_cprint=True,
                                 enable_events=True,
                                 write_only=True, font='Courier 9', autoscroll=True, auto_refresh=True,
                                 background_color="ivory2",
                                 text_color="maroon", do_not_clear=True, key='-ML_SORT-')],
                   [sg.Column([
                       [sg.Button("Submit", key='-SUBMIT3-', enable_events=True, size=(8, 1),
                                  button_color=('white', 'green'), font=("Helvetica", 10)),
                        sg.Button("Exit", key='-EXIT3-', enable_events=True, size=(8, 1), button_color=('white', 'red'),
                                  font=("Helvetica", 10)),
                        sg.Button("Cancel", key='-CANCEL2-', enable_events=True, size=(8, 1),
                                  button_color=('black', 'oldlace'),
                                  font=("Helvetica", 10), border_width=2, tooltip='Terminate replace process')]
                   ], justification='center')
                   ]
                   ]
    tab_group = [[sg.TabGroup(
        [[sg.Tab('SELECT CARDS', tab1_layout), sg.Tab('REPLACE CARDS', tab2_layout),
          sg.Tab('SORT CARDS', tab3_layout)
          ]], border_width=0, font=('Calibri', 11, 'bold'), title_color='gray'
    ),
    ]]
    final_layout = [
        [sg.Menu(help_menu_layout)],
        tab_group  # Your existing UI layout here
         ]
    return final_layout


def popup_error(error_message):
    sg.popup_error(error_message, button_color=('white', 'red'), title="Error",
                   background_color='lightgray', text_color='red', keep_on_top=True,
                   non_blocking=False, icon=rmr_icon)


def main():
    # Event loop to process events and get inputs
    while True:
        event, values = window.read()

        # #MENU commands start here  ########################################
        if event in (None, '-EXIT-', '-EXIT2-', '-EXIT3-'):
            break
            # Handle events
        elif event == 'About...':
            main_window_location = window.CurrentLocation()
            popup_location = (
                main_window_location[0] + 70, main_window_location[1] + 100)  # Adjust the coordinates as needed
            sg.popup(f'Cards Graphical User Interface v{version}',
                     'This is a simple Python application designed to perform various tasks.',
                     'It provides features such as selecting cards, replacing data in BCP files,'
                     ' and sorting BCP files.',
                     'For more information and support, please contact:',
                     'user@example.com',
                     font=('Calibri', 11),
                     background_color='white',
                     text_color='black',
                     title='About',
                     non_blocking=True,
                     keep_on_top=True,
                     grab_anywhere=True,
                     icon=rmr_icon,
                     any_key_closes=True,
                     location=popup_location)
        elif event == 'Usage...':
            usage_context = usage_text()
            usage_layout = [
                [sg.Multiline(usage_context, size=(110, 26), auto_size_text=True, no_scrollbar=True, do_not_clear=True,
                              expand_y=True, font=('Calibri', 11), background_color='ivory2', text_color='black',
                              disabled=True)]
            ]
            main_window_location = window.CurrentLocation()
            popup_location = (
                main_window_location[0] - 100, main_window_location[1] + 50)  # Adjust the coordinates as needed
            usage_popup_window = sg.Window("Usage", usage_layout, icon=rmr_icon, location=popup_location)
            usage_popup_window.read()
        elif event == 'FAQ...':
            faq_context = faq_text()
            faq_layout = [
                [sg.Multiline(faq_context, size=(120, 25), auto_size_text=True, no_scrollbar=True, do_not_clear=True,
                              expand_y=True, font=('Calibri', 11), background_color='ivory2', text_color='black',
                              disabled=True)]
            ]
            main_window_location = window.CurrentLocation()
            popup_location = (
                main_window_location[0] - 100, main_window_location[1] + 50)  # Adjust the coordinates as needed
            usage_popup_window = sg.Window("Usage", faq_layout, icon=rmr_icon, location=popup_location)
            usage_popup_window.read()

        # #SELECTCARDS commands start here  #################################
        elif event == '-CARD_LIST-':
            try:
                output_dir = os.path.dirname(values["-CARD_LIST-"])
                # Check if the directory exists
                if os.path.exists(output_dir):
                    # Check if the path points to a directory
                    if os.path.isdir(output_dir):
                        # Check if the directory is readable
                        if os.access(output_dir, os.R_OK):
                            os.chdir(output_dir)
                        else:
                            popup_error("The output directory is not correct!")
                            window['-CARD_LIST-'].update(value='')

            except FileNotFoundError as e:
                # Display an error message to the user
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
        elif event == '-OPTION-':
            if values['-OPTION-'] == 'Select month(s) from file':
                popup_layout = [[sg.Text('Month list file(s):'), sg.InputText(key='-MONTH_FILE-'),
                                 sg.FilesBrowse(file_types=(
                                 ('MONTH Files', '*.months'), ('MONTH Files', '*.txt'), ('MONTH Files', '*.list')))],
                                [sg.Button('OK'), sg.Button('Cancel')]
                                ]
                main_window_location = window.CurrentLocation()
                popup_location = (
                main_window_location[0]+ 10, main_window_location[1] + 150)  # Adjust the coordinates as needed
                popup_window = sg.Window('Select a month file', popup_layout, keep_on_top=True, icon=rmr_icon,
                                         location=popup_location)
                while True:
                    dis_month = values["-DISCRETE-"]
                    popup_event, popup_values = popup_window.read()
                    if popup_event in (sg.WINDOW_CLOSED, 'Cancel'):
                        break
                    if popup_event == 'OK':
                        if ";" in popup_values['-MONTH_FILE-']:
                            months = popup_values['-MONTH_FILE-'].split(';')
                            months_list = os.path.dirname(months[0])+r'/cardsguimonths.list'
                            with open(months_list, 'w') as f:
                                for month in months:
                                    with open(month, 'r') as file:
                                        lines = file.readlines()
                                        for line in lines:
                                            f.write(line.strip() + '\n')
                            window['-MONTH_DIR-'].update(value=os.path.basename(months_list))
                            break
                        else:
                            months_list = popup_values['-MONTH_FILE-']
                            filename = os.path.basename(months_list)
                            window["-MONTH_DIR-"].update(filename)
                            if dis_month:
                                with open(months_list, 'r') as f:
                                    months = [line.strip() for line in f.readlines()]
                            break
                popup_window.close()
                window['-DISCRETE-'].update(disabled=False)
            else:
                months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                          'November', 'December']
                years = [str(year) for year in range(2018, 2030)]
                # Get the current year
                current_year = datetime.now().year
                # Get the current month
                current_month = datetime.now().month
                # Calculate the previous month
                if current_month == 1:
                    previous_month = 12
                else:
                    previous_month = current_month - 1
                # Get the month name for the previous month
                previous_month_name = datetime.strptime(str(previous_month), '%m').strftime('%B')

                layout = [
                    [sg.Text('Month', size=(7, 1), pad=((70, 0), (0, 0)), font=('Calibri', 11, 'bold')),
                     sg.Combo(months, default_value=previous_month_name, readonly=True)],
                    [sg.Text('Year', size=(7, 1), pad=((70, 0), (20, 0)), font=('Calibri', 11, 'bold')),
                     sg.Slider(range=(2018, 2030), orientation='h', default_value=current_year)],
                    [sg.Text('', size=(1, 1))],  # Add an empty row for vertical space
                    [sg.Submit(), sg.Cancel()]
                ]
                main_window_location = window.CurrentLocation()
                popup_location = (
                    main_window_location[0] + 100, main_window_location[1] + 150)  # Adjust the coordinates as needed
                window3 = sg.Window('Select Month and Year', layout, keep_on_top=True, icon=rmr_icon,
                                    location=popup_location)
                event, values = window3.read()
                if event == 'Submit':
                    try:
                        month = values[0]
                        year = values[1]
                        window["-MONTH_DIR-"].update(f'{month} {int(year)}')
                        year = str(round(float(year)))[2:]
                        month_number = months.index(month) + 1
                        if month_number < 10:
                            month_number_str = f'0{month_number}'
                        else:
                            month_number_str = str(month_number)
                        months_list = (year + month_number_str)
                    except Exception as e:
                        # Code to handle the exception and show the error message
                        print("An error occurred:", str(e))
                    window3.close()
                    window['-DISCRETE-'].update(value=False, disabled=True)
                    for key in ['-INPUT_REP-', '-REP_BROWSE-', '-MASTER_SELECT-']:
                        window[key].update(disabled=False)
                elif event == 'Cancel':
                    months_list = ''
                    window["-MONTH_DIR-"].update(months_list)
                    window3.close()
        elif event == '-DISCRETE-':
            if values['-DISCRETE-']:
                for key in ['-MASTER_SELECT-']:
                    window[key].update(disabled=True, value='')
                    for key in ['-INPUT_REP-', '-REP_BROWSE-', '-MASTER_TEXT-']:
                        window[key].update(visible=False)
                        if key == '-MASTER_SELECT-':
                            window[key].update(value=False)
                        elif key == '-INPUT_REP-':
                            window[key].update(value='')
            elif not values['-DISCRETE-']:
                for key in ['-INPUT_REP-', '-REP_BROWSE-', '-MASTER_SELECT-']:
                    window[key].update(disabled=False)
            if values['-OPTION-']:
                try:
                    if months_list:
                        with open(months_list, 'r') as f:
                            months = [line.strip() for line in f.readlines()]
                except NameError:
                    sg.popup_error("NameError: Probably a month file is not selected yet!", icon=rmr_icon)
                except FileNotFoundError as e:
                    sg.popup_error("FileNotFoundError" + str(e), icon=rmr_icon)
            # window['-MASTER_SELECT-'].update(value=False, disabled=True)
        elif event == '-MASTER_SELECT-':
            for key in ['-MASTER_TEXT-', '-INPUT_REP-', '-REP_BROWSE-']:
                window[key].update(visible=values['-MASTER_SELECT-'])
        elif event in ['-SURVEY_TOT-', '-SURVEY_ES-']:
            for key in ['-OPTION-', '-DISCRETE-', '-MASTER_SELECT-']:
                window[key].update(disabled=False)
            window['-BCP_DATA_STORE-'].update(value='')
            window['-MONTH_DIR-'].update(visible=True)
        elif event == '-SURVEY_BCP-':
            for key in ['-OPTION-', '-DISCRETE-', '-MASTER_SELECT-']:
                window[key].update(value='', disabled=True)
            for key in ['-MASTER_TEXT-', '-INPUT_REP-', '-REP_BROWSE-', '-MONTH_DIR-']:
                window[key].update(visible=False)
            window['-MONTH_DIR-'].update(value='')
            popup_layout = [[sg.Text('BCP File:'), sg.InputText(key='-BCP_STORE-'),
                             sg.FilesBrowse(file_types=(
                                 (('BCP Files', '*.bcp'),)))],
                            [sg.Button('OK'), sg.Button('Cancel')]
                            ]
            main_window_location = window.CurrentLocation()
            popup_location = (
                main_window_location[0] + 30, main_window_location[1] + 150)  # Adjust the coordinates as needed
            popup_window = sg.Window('Select a BCP file', popup_layout, keep_on_top=True, icon=rmr_icon,
                                     location=popup_location)
            while True:
                popup_event, popup_values = popup_window.read()
                if popup_event in (sg.WINDOW_CLOSED, 'Cancel'):
                    break
                if popup_event == 'OK':
                    input_bcp = popup_values['-BCP_STORE-']
                    window['-BCP_DATA_STORE-'].update(value=os.path.basename(input_bcp))
                    break
            popup_window.close()
        elif event == '-SUBMIT-':
            try:
                for key in ['REPLACE CARDS', 'SORT CARDS']:
                    window[key].update(disabled=True)
                cards_list = values["-CARD_LIST-"]
                output_dir = os.path.dirname(cards_list)
                survey_dict = {'-SURVEY_TOT-': 'TOT', '-SURVEY_ES-': 'ES', '-SURVEY_BCP-': 'BCP'}
                for key in survey_dict.keys():
                    if values[key]:
                        data_store = survey_dict.get(key)
                # Check if the output file name is provided
                output_file = values["-OUTPUT_FILE-"] + '.bcp'
                output_file_rep = values["-OUTPUT_FILE-"] + '_replaced.bcp'
                if values["-OUTPUT_FILE-"] == ' .bcp':
                    output_file = ''
                    del values["-OUTPUT_FILE-"]
                open_dir = values["-CHECKBOX-"]
                cpangl = values["-PANGLOSS-"]
                dis_month = values["-DISCRETE-"]
                master_select = values["-MASTER_SELECT-"]
                input_rep = values["-INPUT_REP-"]
                # Check if all inputs are provided
                if master_select:
                    required_inputs = ['-CARD_LIST-', '-OPTION-', '-OUTPUT_FILE-', '-INPUT_REP-']
                elif data_store == 'BCP':
                    required_inputs = ['-CARD_LIST-', '-OUTPUT_FILE-']
                else:
                    required_inputs = ['-CARD_LIST-', '-OPTION-', '-OUTPUT_FILE-']
                # Check if all inputs are provided
                if any(not values[key] or values[key] == 'Please select a file' or values[key] == 'Please select an option'
                       for key in required_inputs):
                    for key in ['REPLACE CARDS', 'SORT CARDS']:
                        window[key].update(disabled=False)
                    event, _ = window.read(timeout=30)
                    for key in required_inputs:
                        if not values[key]:
                            element = window[key]
                            if key == '-CARD_LIST-':
                                element.Update('Please select a file', background_color='lightyellow')
                            elif key == '-OUTPUT_FILE-':
                                element.Update(background_color='lightyellow')
                            elif isinstance(element, sg.Combo):
                                element.update('Please select an option')
                        if master_select:
                            if not values['-INPUT_REP-']:
                                element = window['-INPUT_REP-']
                                element.Update('Please select a file', background_color='lightyellow')
                    continue
                window['-INPUT_REP-'].Update(background_color='lightgray')
                window['-OUTPUT_FILE-'].Update(background_color='lightgray')
                if data_store != 'BCP':
                    if not dis_month:
                        command = [$COMMAND, cards_list, months_list, data_store, output_file]
                        try:
                            # Execute the command with a progress bar
                            progress_bar = sg.ProgressBar(100, orientation='h', size=(20, 20), bar_color=('blue', 'gray'), )
                            layout = [
                                [sg.Text(key='-BCPNAME-')],
                                [progress_bar],
                                [sg.Text('', key='-PROGRESS-', size=(20, 1))],
                                # #if you wish to see selectcards output, uncomment these lines
                                # [sg.Multiline(size=(80, 10), reroute_stdout=True, reroute_stderr=False, reroute_cprint=True,
                                #               write_only=True, font='Courier 8', autoscroll=True, horizontal_scroll=True,
                                #               do_not_clear=True, key='-ML-')],
                                [sg.Cancel()]
                            ]
                            window2 = sg.Window('SelectCards', layout, finalize=True, keep_on_top=True, icon=rmr_icon)
                            window2.refresh()
                            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                       universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                            # Read the output of the command and update the progress bar
                            output = ""
                            keep_out_dir = ""
                            output_window = ''
                            # Compile the regex patterns
                            percentage_pattern = re.compile(r'\d+\.\d+%')
                            success_pattern = re.compile(r"Successfully\s+completed")
                            bcp_name_pattern = re.compile(r"Reading.+\\(.+)\.bcp")
                            while True:
                                event, values = window2.read(timeout=30)
                                if event in (sg.WIN_CLOSED, 'Cancel'):
                                    process.terminate()  # Terminate the subprocess
                                    break
                                output = process.stdout.readline()
                                if output == '' and process.poll() is not None:
                                    break
                                if output:
                                    matches = percentage_pattern.findall(output)
                                    matches2 = success_pattern.findall(output)
                                    matches3 = bcp_name_pattern.findall(output)
                                    if matches3:
                                        window2['-BCPNAME-'].update(f'Reading {matches3[0]}...')
                                    elif matches:
                                        percentage = int(float(matches[0][:-1]))
                                        # Update the progress bar and label
                                        progress_bar.UpdateBar(percentage)
                                        window2['-PROGRESS-'].update(f'{percentage:.0f}%')
                                    elif matches2:
                                        sg.popup_no_buttons(success_message, non_blocking=True,
                                                            background_color='mediumspringgreen', no_titlebar=True,
                                                            font=('Calibri', 11, 'bold'), text_color='black',
                                                            grab_anywhere=True, icon=rmr_icon,
                                                            keep_on_top=True, auto_close=True, auto_close_duration=3)
                                    elif "**** ERROR" in output:
                                        error_message = re.findall(r'ERROR : (.+)', output)[0]
                                        popup_error(error_message)
                                        keep_out_dir = output_dir
                                        output_dir = ''
                                        break
                            try:
                                if open_dir and output_dir != '':
                                    if cpangl:
                                        if event in (sg.WIN_CLOSED, 'Cancel'):
                                            process.terminate()  # Terminate the subprocess
                                            break
                                        # Define the layout of the popup window
                                        layout = [[sg.Text('Please wait while creating dat file...')],
                                                  [sg.Text('', key='_OUTPUT_')]]
                                        # Create the popup window
                                        window3 = sg.Window('Creating dat file', layout, no_titlebar=True, finalize=True,
                                                            keep_on_top=True)
                                        current_path = os.getcwd()
                                        sg.popup_notify("Please Wait, this process might take a few seconds...")
                                        # Launch the subprocess
                                        dat_file = f'{os.path.splitext(output_file)[0]}.dat'
                                        command2 = [$COMMAND, "P", "Q", output_file, dat_file]
                                        process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                                    universal_newlines=True,
                                                                    creationflags=subprocess.CREATE_NO_WINDOW)
                                        print(dat_file, command2)
                                        try:
                                            # Wait for the subprocess to finish
                                            stdout, stderr = process2.communicate(timeout=600)
                                        except subprocess.TimeoutExpired as timeout_error:
                                            sg.popup_error(str(timeout_error), title="Subprocess timed out",
                                                           background_color='lightgray', icon=rmr_icon,
                                                           text_color='red')
                                            break
                                        except Exception as e:
                                            sg.popup_error(f"Exception occurred: {e}", icon=rmr_icon)
                                            break
                                        finally:
                                            window3.close()
                                            os.startfile(output_dir)
                                    else:
                                        os.startfile(output_dir)
                            except Exception as e:
                                window2.close()
                                continue
                            # Close the window
                            if output_dir == '':
                                output_dir = keep_out_dir
                            window2.close()
                        except FileNotFoundError as e:
                            # Code to handle the exception and show the error message
                            sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                                           icon=rmr_icon)
                        except Exception as error:
                            popup_error(str(error))
                        # FOR SELECT THEN REPLACE OPERATION
                        if master_select:
                            # Master File: input_rep, Updates File: updates_file_name, output file name: output_file_rep
                            updates_file_name = output_dir + '/' + output_file

                            try:
                                # Execute the command with a progress bar
                                progress_bar = sg.ProgressBar(100, orientation='h', size=(20, 20),
                                                                  bar_color=('blue', 'gray'), )
                                layout = [
                                        [sg.Text('', key='-OUTPUT_TEXT-')],
                                        [progress_bar],
                                        [sg.Text('', key='-PROGRESS-', size=(20, 1))],
                                        [sg.Cancel()]
                                    ]
                                window3 = sg.Window('ReplaceCards', layout, finalize=True, keep_on_top=True, icon=rmr_icon)
                                window3.refresh()

                                command = [$COMMAND, input_rep, updates_file_name,
                                           output_file_rep]
                                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                           universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                                # Read the output of the command and update the progress bar
                                output = ""
                                # Compile the regex patterns
                                percentage_pattern = re.compile(r'\d+\.\d+%')
                                split_complete_pattern = re.compile(r"Splitting\s+complete")
                                sorting_complete_pattern = re.compile(r"Sorting\s+chunks\s+completed")
                                merging_complete_pattern = re.compile(r"Merging\s+complete")
                                success_pattern = re.compile(r"Successfully\s+completed")
                                splitting_pattern = re.compile(r"Splitting")
                                while True:
                                    event, values = window3.read(timeout=30)
                                    if event in (sg.WIN_CLOSED, 'Cancel'):
                                        process.terminate()  # Terminate the subprocess
                                        break
                                    output = process.stdout.readline()
                                    if output == '' and process.poll() is not None:
                                        break
                                    if output:
                                        matches = percentage_pattern.findall(output)
                                        matches2 = split_complete_pattern.findall(output)
                                        matches3 = sorting_complete_pattern.findall(output)
                                        matches4 = merging_complete_pattern.findall(output)
                                        matches5 = success_pattern.findall(output)
                                        matches6 = splitting_pattern.findall(output)
                                        if matches:
                                            percentage = int(float(matches[0][:-1]))
                                            # Update the progress bar and label
                                            progress_bar.UpdateBar(percentage)
                                            window3['-PROGRESS-'].update(f'{percentage:.0f}%')
                                        # Check if there was an error in the output
                                        elif "**** ERROR" in output:
                                            error_message = re.findall(r'ERROR : (.+)', output)[0]
                                            popup_error(error_message)
                                            break
                                        elif matches2:
                                            window3['-OUTPUT_TEXT-'].update('Splitting complete...')
                                            window3['-OUTPUT_TEXT-'].update('Sorting chunks...')
                                        elif matches3:
                                            window3['-OUTPUT_TEXT-'].update('Merging, Please Wait...')
                                        elif matches4:
                                            window3['-OUTPUT_TEXT-'].update('Merging complete...')
                                            window3['-OUTPUT_TEXT-'].update('Replacing Cards...')
                                        elif matches5:
                                            sg.popup_no_buttons('Replaced Successfully!', non_blocking=True,
                                                                background_color='mediumspringgreen', no_titlebar=True,
                                                                font=('Calibri', 11, 'bold'), text_color='black',
                                                                grab_anywhere=True, icon=rmr_icon,
                                                                keep_on_top=True, auto_close=True, auto_close_duration=3)
                                        elif matches6:
                                            window3['-OUTPUT_TEXT-'].update('Splitting...')
                                        elif "not found in master (check sort order?)" in output:
                                            error_message = 'Some Response IDs not found in master file (check sort order)'
                                            popup_error(error_message)
                                            break
                                window3.close()
                            except FileNotFoundError as e:
                                # Code to handle the exception and show the error message
                                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray',
                                               text_color='red', icon=rmr_icon)
                            except Exception as error:
                                popup_error(str(error))

                        for key in ['REPLACE CARDS', 'SORT CARDS']:
                            window[key].update(disabled=False)
                    if dis_month:
                        for key in ['REPLACE CARDS', 'SORT CARDS']:
                            window[key].update(disabled=True)
                        output_file = os.path.splitext(output_file)[0]
                        for month in months:
                            command = [$COMMAND, cards_list, month, data_store,
                                       f'{output_file}_{month}.bcp']
                            try:
                                # Execute the command with a progress bar
                                progress_bar = sg.ProgressBar(100, orientation='h', size=(20, 20), bar_color=('blue', 'gray'), )
                                layout = [
                                    [sg.Text(key='-BCPNAME-')],
                                    [progress_bar],
                                    [sg.Text('', key='-PROGRESS-', size=(20, 1))],
                                    [sg.Cancel()]
                                ]
                                window2 = sg.Window('SelectCards', layout, finalize=True, keep_on_top=True, icon=rmr_icon)
                                window2.refresh()
                                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                           universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                                # Read the output of the command and update the progress bar
                                output = ""
                                keep_out_dir = ""
                                # Compile the regex patterns
                                percentage_pattern = re.compile(r'\d+\.\d+%')
                                success_pattern = re.compile(r"Successfully\s+completed")
                                bcp_name_pattern = re.compile(r"Reading.+\\(.+)\.bcp")
                                while True:
                                    event, values = window2.read(timeout=30)
                                    if event in (sg.WIN_CLOSED, 'Cancel'):
                                        process.terminate()  # Terminate the subprocess
                                        break
                                    output = process.stdout.readline()
                                    if output == '' and process.poll() is not None:
                                        break
                                    if output:
                                        # Parse the output to extract the percentage value
                                        matches = percentage_pattern.findall(output)
                                        matches2 = success_pattern.findall(output)
                                        matches3 = bcp_name_pattern.findall(output)
                                        if matches3:
                                            window2['-BCPNAME-'].update(f'Reading {matches3[0]}...')
                                        if matches:
                                            percentage = int(float(matches[0][:-1]))
                                            # Update the progress bar and label
                                            progress_bar.UpdateBar(percentage)
                                            window2['-PROGRESS-'].update(f'{percentage:.0f}%')
                                        # Check if there was an error in the output
                                        elif "**** ERROR" in output:
                                            error_message = re.findall(r'ERROR : (.+)', output)[0]
                                            popup_error(error_message)
                                            keep_out_dir = output_dir
                                            output_dir = ''
                                            break
                                try:
                                    if open_dir and output_dir != '':
                                        if cpangl:
                                            # Define the layout of the popup window
                                            layout = [[sg.Text('Please wait while creating dat file...')],
                                                      [sg.Text('', key='_OUTPUT_')]]
                                            # Create the popup window
                                            window3 = sg.Window('Creating dat file', layout, no_titlebar=True, finalize=True,
                                                                keep_on_top=True)
                                            current_path = os.getcwd()
                                            sg.popup_notify("Please Wait, this process might take a few seconds...")
                                            # Launch the subprocess
                                            dat_file = f'{os.path.splitext(output_file)[0]}_{month}.dat'
                                            bcp_file = f'{os.path.splitext(output_file)[0]}_{month}.bcp'
                                            command2 = [$COMMAND, "P", "Q", bcp_file, dat_file]
                                            process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                                        universal_newlines=True,
                                                                        creationflags=subprocess.CREATE_NO_WINDOW)
                                            try:
                                                # Wait for the subprocess to finish
                                                stdout, stderr = process2.communicate(timeout=600)
                                            except subprocess.TimeoutExpired as timeout_expire:
                                                sg.popup_error(str(timeout_expire), title="Subprocess timed out", background_color='lightgray',
                                                               text_color='red', icon=rmr_icon)
                                            except Exception as e:
                                                sg.popup_error(f"Exception occurred: {e}", icon=rmr_icon)
                                            finally:
                                                window3.close()
                                except Exception as e:
                                    window2.close()
                                    continue
                                # Close the window
                                if output_dir == '':
                                    output_dir = keep_out_dir
                                    if output_dir == '':
                                        output_dir = os.path.dirname(values["-CARD_LIST-"])
                                window2.close()
                            except FileNotFoundError as e:
                                # Code to handle the exception and show the error message
                                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red')
                                break
                            except Exception as other_errors:
                                popup_error(str(other_errors))
                                break
                        sg.popup_no_buttons(success_message, non_blocking=True, background_color='mediumspringgreen',
                                            no_titlebar=True,
                                            font=('Calibri', 11, 'bold'), text_color='black', grab_anywhere=True,
                                            keep_on_top=False, auto_close=True, auto_close_duration=3, icon=rmr_icon)
                        os.startfile(output_dir)
                        for key in ['REPLACE CARDS', 'SORT CARDS']:
                            window[key].update(disabled=False)
                elif input_bcp and data_store == 'BCP':
                    command = [$COMMAND, input_bcp, "78,80", cards_list, output_file]
                    try:
                        # Execute the command with a progress bar
                        progress_bar = sg.ProgressBar(100, orientation='h', size=(20, 20), bar_color=('blue', 'gray'), )
                        layout = [
                            [sg.Text(key='-BCPNAME-')],
                            [progress_bar],
                            [sg.Text('', key='-PROGRESS-', size=(20, 1))],
                            [sg.Cancel()]
                        ]
                        window2 = sg.Window('SelectCards', layout, finalize=True, keep_on_top=True, icon=rmr_icon)
                        window2.refresh()
                        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                                   universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        # Compile the regex patterns
                        percentage_pattern = re.compile(r'\d+\.\d+%')
                        success_pattern = re.compile(r"Successfully\s+completed")
                        bcp_name_pattern = re.compile(r"Reading.+/(.+)\.bcp")
                        while True:
                            event, values = window2.read(timeout=30)
                            if event in (sg.WIN_CLOSED, 'Cancel'):
                                process.terminate()  # Terminate the subprocess
                                break
                            output = process.stdout.readline()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                matches = percentage_pattern.findall(output)
                                matches2 = success_pattern.findall(output)
                                matches3 = bcp_name_pattern.findall(output)
                                if matches3:
                                    window2['-BCPNAME-'].update(f'Reading {matches3[0]}...')
                                elif matches:
                                    percentage = int(float(matches[0][:-1]))
                                    # Update the progress bar and label
                                    progress_bar.UpdateBar(percentage)
                                    window2['-PROGRESS-'].update(f'{percentage:.0f}%')
                                elif matches2:
                                    sg.popup_no_buttons(success_message, non_blocking=True,
                                                        background_color='mediumspringgreen', no_titlebar=True,
                                                        font=('Calibri', 11, 'bold'), text_color='black',
                                                        grab_anywhere=True, icon=rmr_icon,
                                                        keep_on_top=True, auto_close=True, auto_close_duration=3)
                                elif "**** ERROR" in output:
                                    error_message = re.findall(r'ERROR : (.+)', output)[0]
                                    popup_error(error_message)
                                    keep_out_dir = output_dir
                                    output_dir = ''
                                    break
                        window2.close()
                        try:
                            if open_dir and output_dir != '':
                                if cpangl:
                                    if event in (sg.WIN_CLOSED, 'Cancel'):
                                        process.terminate()  # Terminate the subprocess
                                        break
                                    # Define the layout of the popup window
                                    layout = [[sg.Text('Please wait while creating dat file...')],
                                              [sg.Text('', key='_OUTPUT_')]]
                                    # Create the popup window
                                    window3 = sg.Window('Creating dat file', layout, no_titlebar=True, finalize=True,
                                                        keep_on_top=True)
                                    current_path = os.getcwd()
                                    sg.popup_notify("Please Wait, this process might take a few seconds...")
                                    # Launch the subprocess
                                    dat_file = f'{os.path.splitext(output_file)[0]}.dat'
                                    command2 = [$COMMAND, "P", "Q", output_file, dat_file]
                                    process2 = subprocess.Popen(command2, stdout=subprocess.PIPE,
                                                                stderr=subprocess.STDOUT,
                                                                universal_newlines=True,
                                                                creationflags=subprocess.CREATE_NO_WINDOW)
                                    print(dat_file, command2)
                                    try:
                                        # Wait for the subprocess to finish
                                        stdout, stderr = process2.communicate(timeout=600)
                                    except subprocess.TimeoutExpired as timeout_error:
                                        sg.popup_error(str(timeout_error), title="Subprocess timed out",
                                                       background_color='lightgray', icon=rmr_icon,
                                                       text_color='red')
                                        break
                                    except Exception as e:
                                        sg.popup_error(f"Exception occurred: {e}", icon=rmr_icon)
                                        break
                                    finally:
                                        window3.close()
                                        os.startfile(output_dir)
                                else:
                                    os.startfile(output_dir)
                        except Exception as e:
                            window2.close()
                    except FileNotFoundError as e:
                        # Code to handle the exception and show the error message
                        sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray',
                                       text_color='red',
                                       icon=rmr_icon)
                    except Exception as error:
                        popup_error(str(error))
                for key in ['REPLACE CARDS', 'SORT CARDS']:
                    window[key].update(disabled=False)
            except FileNotFoundError as output_dir_error:
                popup_error("You have likely selected an incorrect directory for the output file. Please make sure you "
                            "choose a local directory instead of a network directory (e.g., rmndcfile03//...). "
                            "Your files have been created, and you can manually open the directory to access them. "
                            "Please ensure to specify the correct directory next time.")
                for key in ['REPLACE CARDS', 'SORT CARDS']:
                    window[key].update(disabled=False)

        # #REPLACECARDS commands start here  #################################
        elif event == '-MASTER_FILE-':
            try:
                output_dir = os.path.dirname(values["-MASTER_FILE-"])
                os.chdir(output_dir)
            except FileNotFoundError as e:
                # Display an error message to the user
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
        elif event == '-SUBMIT2-':
            for key in ['SELECT CARDS', 'SORT CARDS']:
                window[key].update(disabled=True)
            # Construct the command
            master_file = values['-MASTER_FILE-']
            updates_file = values['-UPDATES_FILE-']
            # Check if the output file name is provided
            output_file = values["-REPLACED_FILE-"] + '.bcp'
            if values["-REPLACED_FILE-"] == ' .bcp':
                output_file = ''
                del values["-REPLACED_FILE-"]
            open_dir = values['-OPEN_FOLDER-']

            # Check if all inputs are provided
            required_inputs = ['-MASTER_FILE-', '-UPDATES_FILE-', '-REPLACED_FILE-']

            # Check if all inputs are provided
            if any(not values[key] or values[key] == 'Please select a file' for key in required_inputs):
                event, _ = window.read(timeout=30)
                for key in ['SELECT CARDS', 'SORT CARDS']:
                    window[key].update(disabled=False)
                for key in required_inputs:
                    if not values[key]:
                        element = window[key]
                        if key == '-MASTER_FILE-' or key == '-UPDATES_FILE-':
                            element.Update('Please select a file', text_color='brown', background_color='lightyellow')
                        elif key == '-REPLACED_FILE-':
                            element.Update(background_color='lightyellow')
                continue
            window['-REPLACED_FILE-'].Update(background_color='ivory2')

            command = [$COMMAND, master_file, updates_file, output_file]
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                # Read the output of the command and update the progress bar
                output = ""
                output_window = ""
                while True:
                    event, _ = window.read(timeout=30)
                    if event in (sg.WIN_CLOSED, '-EXIT2-'):
                        process.terminate()  # Terminate the subprocess
                        break
                    elif event == '-CANCEL-':
                        process.terminate()  # Terminate the subprocess
                        output_window = output_window + "Process cancelled by user."
                        window["-ML-"].update(value=output_window)
                        break
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    elif output:
                        # Parse the output to extract the percentage value
                        output_window = output_window + output
                        window["-ML-"].update(value=output_window)
                        if "Successfully completed" in output and open_dir:
                            os.startfile(output_dir)
                        # Check if there was an error in the output
                        elif "Unhandled Exception" in output:
                            sg.popup_error("Illegal characters in path!", button_color=('white', 'red'), title="Error",
                                           background_color='lightgray', text_color='red', keep_on_top=True,
                                           non_blocking=True, icon=rmr_icon,
                                           auto_close=True, auto_close_duration=3)
                            break
            except FileNotFoundError as e:
                # Code to handle the exception and show the error message
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
            except Exception as error:
                popup_error(str(error))
            for key in ['SELECT CARDS', 'SORT CARDS']:
                window[key].update(disabled=False)

        # #SORTCARDS START HERE ##############################################
        elif event == '-INPUT_FILE-':
            try:
                output_dir = os.path.dirname(values["-INPUT_FILE-"])
                os.chdir(output_dir)
            except FileNotFoundError as e:
                # Display an error message to the user
                sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                               icon=rmr_icon)
        elif event == '-MERGE_SELECT-':
            for key in ['-MERGE_TEXT-', '-INPUT_MERGE-', '-MERGE_BROWSE-']:
                window[key].update(visible=values['-MERGE_SELECT-'])
        elif event == '-SUBMIT3-':
            for key in ['SELECT CARDS', 'REPLACE CARDS']:
                window[key].update(disabled=True)
            # Construct the command
            input_file = values['-INPUT_FILE-']
            # Check if the output file name is provided
            output_file = values["-SORTED_FILE-"] + '.bcp'
            if values["-SORTED_FILE-"] == ' .bcp':
                output_file = ''
                del values["-SORTED_FILE-"]
            open_dir = values['-OPEN_SORT_DIR-']
            merge_files = values['-MERGE_SELECT-']

            if not merge_files:
                # Check if all inputs are provided
                required_inputs = ['-INPUT_FILE-', '-SORTED_FILE-']
                # Check if all inputs are provided
                if any(not values[key] or values[key] == 'Please select a file' for key in required_inputs):
                    event, _ = window.read(timeout=30)
                    for key in ['SELECT CARDS', 'REPLACE CARDS']:
                        window[key].update(disabled=False)
                    for key in required_inputs:
                        if not values[key]:
                            element = window[key]
                            if key == '-INPUT_FILE-':
                                element.Update('Please select a file', text_color='brown', background_color='lightyellow')
                            elif key == '-SORTED_FILE-':
                                element.Update(background_color='lightyellow')
                    continue
                window['-SORTED_FILE-'].Update(background_color='ivory2')

                command = [$COMMAND, input_file, '2, 1, 9, 78, 80', output_file]
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)

                    # Read the output of the command and update the progress bar
                    output = ""
                    output_window = ""
                    while True:
                        event, _ = window.read(timeout=30)
                        if event in (sg.WIN_CLOSED, '-EXIT3-'):
                            process.terminate()  # Terminate the subprocess
                            break
                        elif event == '-CANCEL2-':
                            process.terminate()  # Terminate the subprocess
                            output_window = output_window + "Process cancelled by user."
                            window["-ML_SORT-"].update(value=output_window)
                            break
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        elif output:
                            # Parse the output to extract the percentage value
                            output_window = output_window + output
                            window["-ML_SORT-"].update(value=output_window)
                            if "Successfully sorted" in output and open_dir:
                                os.startfile(output_dir)
                            # Check if there was an error in the output
                            elif "**** ERROR" in output:
                                sg.popup_error("Illegal characters in path!", button_color=('white', 'red'), title="Error",
                                               background_color='lightgray', text_color='red', keep_on_top=True,
                                               non_blocking=True, icon=rmr_icon,
                                               auto_close=True, auto_close_duration=3)
                                break
                except FileNotFoundError as e:
                    # Code to handle the exception and show the error message
                    sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                                   icon=rmr_icon)
                except Exception as error:
                    popup_error(str(error))
            else:
                # Check if all inputs are provided
                input_merge = values['-INPUT_MERGE-']
                required_inputs = ['-INPUT_FILE-', '-SORTED_FILE-', '-INPUT_MERGE-']
                # Check if all inputs are provided
                if any(not values[key] or values[key] == 'Please select a file' for key in required_inputs):
                    event, _ = window.read(timeout=30)
                    for key in ['SELECT CARDS', 'REPLACE CARDS']:
                        window[key].update(disabled=False)
                    for key in required_inputs:
                        if not values[key]:
                            element = window[key]
                            if key in ['-INPUT_FILE-', '-INPUT_MERGE-']:
                                element.Update('Please select a file', text_color='brown', background_color='lightyellow')
                            elif key == '-SORTED_FILE-':
                                element.Update(background_color='lightyellow')
                    continue
                window['-SORTED_FILE-'].Update(background_color='ivory2')

                command = [$COMMAND, f"{input_file}, {input_merge}", '2, 1, 9, 78, 80', output_file]
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    # Read the output of the command and update the progress bar
                    output = ""
                    output_window = ""
                    while True:
                        event, _ = window.read(timeout=30)
                        if event in (sg.WIN_CLOSED, '-EXIT3-'):
                            process.terminate()  # Terminate the subprocess
                            break
                        elif event == '-CANCEL2-':
                            process.terminate()  # Terminate the subprocess
                            output_window = output_window + "Process cancelled by user."
                            window["-ML_SORT-"].update(value=output_window)
                            break
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        elif output:
                            # Parse the output to extract the percentage value
                            output_window = output_window + output
                            window["-ML_SORT-"].update(value=output_window)
                            if "Successfully sorted" in output and open_dir:
                                os.startfile(output_dir)
                            # Check if there was an error in the output
                            elif "**** ERROR" in output:
                                sg.popup_error("Illegal characters in path!", button_color=('white', 'red'), title="Error",
                                               background_color='lightgray', text_color='red', keep_on_top=True,
                                               non_blocking=True,icon=rmr_icon,
                                               auto_close=True, auto_close_duration=3)
                                break
                except FileNotFoundError as e:
                    # Code to handle the exception and show the error message
                    sg.popup_error(str(e), title="File Not Found Error", background_color='lightgray', text_color='red',
                                   icon=rmr_icon)
                except Exception as error:
                    popup_error(str(error))

            for key in ['SELECT CARDS', 'REPLACE CARDS']:
                window[key].update(disabled=False)

    # Close the GUI window
    window.close()


if __name__ == '__main__':
    # Update the layout to include the TabGroup
    layout = ui_layout()
    # Create the GUI window
    window = sg.Window(f"CARDS GUI (Version: {version})", layout,
                       icon=rmr_icon)
    success_message = "Data Collected Successfully!"

    main()
>>>>>>> 10888554063c44e18048f4184c51c04b9a74ebc7
