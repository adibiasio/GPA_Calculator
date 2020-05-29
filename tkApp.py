"""
The Dialog Class was Adopted From http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
The ScrollableFrame class was Adopted from https://blog.tecladocode.com/tkinter-scrollable-frames/
Changes to the these Classes have been made

Mac and Linux <MouseWheel> event bindings have not been tested
"""

import platform
import tkinter as tk
from tkinter import Grid, messagebox, ttk

import core
from core import EmptyRow

# Retrieves the users OS
OS = platform.system()


class ScrollableFrame(tk.Frame):
    # Creates a scrollable frame (including a scrollbar)
    # This class was adopted from https://blog.tecladocode.com/tkinter-scrollable-frames/

    # A list of all canvases in the parent notebook
    notebook_canvases = []

    def __init__(self, container, *args, **kwargs):
        # All frames & widgets inside of self.canvas are in the scrollable frame
        # self is a tk Frame object
        # Takes in the parent frame

        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.pack()

        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self.on_frame_config)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=1)
        scrollbar.pack(side="right", fill="y")

        if type(container) == ttk.Notebook:
            ScrollableFrame.notebook_canvases.append(self.canvas)

        # When using PACK, insert multiple frames managed by pack into the
        # Scrollable Frame, so the grid in the main_frame is not disturbed

    def on_frame_config(self, event):
        # Reconfigures the canvas when the scroll feature is used
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    @staticmethod
    def on_mouse_wheel(event, tab_num=None, scrollable_frame_obj=None):
        # Changes view of a scrollable frame on <MouseWheel> event
        # When notebooks are parents of a scrollable Frame, the event binding cannot resolve
        # the on_mouse_wheel function to the correct canvas The tab_num parameter address this by
        # indexing a class list of all canvases in the parent notebook
        """
        When Using this function, either the tab_num or the scrollable_frame
        arguments must be passed in. If neither are passed in the canvas in focus
        will not be identified.
        """

        # Finds the canvas in focus
        if scrollable_frame_obj != None:
            canvas = scrollable_frame_obj.canvas
        else:
            canvas = ScrollableFrame.notebook_canvases[tab_num()]

        # Determines the y_view scroll event (based on OS)
        if OS == "Linux":
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            if event.num == 5:
                canvas.yview_scroll(1, "units")

        elif OS == "Windows":
            canvas.yview_scroll(-1*int(event.delta/120), "units")

        elif OS == "Darwin":
            canvas.yview_scroll(event.delta, "units")


class tkCourseRow(core.courseRow):
    # Creates a row of tkinter specific GUI and allows the user to input course data
    def __init__(self, row, frame, del_button_command):
        # Takes in an integer (row) that contains the row number of the object within the tkinter grid
        # Takes in an tkinter frame object, indicating to which frame the course row belongs
        # Takes in the remove course on click function and binds it to the del_button widget
        self.row = row

        # Initializes all tkinter objects and within the object's row
        self.name_label = ttk.Label(frame, text="Course:")
        self.name_label.grid(row=self.row, column=0)

        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=self.row, column=1)

        self.space1 = ttk.Label(frame, text=" ")
        self.space1.grid(row=self.row, column=2)

        self.level_combo = ttk.Combobox(frame, state="readonly")
        self.level_combo.grid(row=self.row, column=3)
        self.level_combo["values"] = ("AP", "H", "CP1", "CP2")
        self.level_combo.unbind_class("TCombobox", "<MouseWheel>")

        self.space2 = ttk.Label(frame, text=" ")
        self.space2.grid(row=self.row, column=4)

        self.grade_entry = ttk.Entry(frame)
        self.grade_entry.grid(row=self.row, column=5)

        self.space3 = ttk.Label(frame, text=" ")
        self.space3.grid(row=self.row, column=6)

        self.credits_combo = ttk.Combobox(frame, state="readonly")
        self.credits_combo.grid(row=self.row, column=7)
        self.credits_combo["values"] = (
            "2.5 (1st-Semester)", "2.5 (2nd-Semester)", "5")
        self.credits_combo.unbind_class("TCombobox", "<MouseWheel>")

        self.space4 = ttk.Label(frame, text=" ")
        self.space4.grid(row=self.row, column=8)

        self.del_button = ttk.Button(frame, text="X")
        self.del_button.config(
            command=lambda: del_button_command(self.del_button))
        self.del_button.grid(row=self.row, column=9)

        entry_widget_values = ["name", "level", "grade", "credits"]
        entry_widgets = [self.name_entry, self.level_combo,
                         self.grade_entry, self.credits_combo]

        super().__init__(
            entry_widget_values,
            entry_widgets,
            Grid.grid_forget,
            lambda widget: widget.get()
        )

        self.widgets = [self.name_label, self.name_entry, self.space1, self.level_combo, self.space2, self.grade_entry,
                        self.space3, self.credits_combo, self.space4, self.del_button]

    def validate_row_data(self):
        # Notifies users of detected errors
        try:
            core.courseRow.validate_row_data(self)
        except ValueError as error:
            if error.args[0] == "grade error":
                tkApp.notification("Error", "Invalid Grade Entry: "
                                   "\n\nPlease enter an integer or float between 0 and 100 under the grade field.")
            elif error.args[0] == "level error":
                tkApp.notification("Error", "Invalid Level Entry: "
                                   "\n\nPlease select a level.")
            elif error.args[0] == "credits error":
                tkApp.notification("Error", "Invalid Credits Entry: "
                                   "\n\nPlease select a number of credits.")
            raise ValueError


class tkYearTab(core.YearTab, ScrollableFrame):
    # Creates a Tab within the Application and allows the user to manage their courses / rows
    def __init__(self, master_window, parent_notebook, year, *args, **kwargs):
        # Sets up GUI related to a YearTab
        # Takes in the master Tk Window
        # Takes in a parent tkinter Notebook object and a string variable containing the HS year
        # Takes in its tab number within the parent notebook

        self.master_window = master_window
        self.parent_notebook = parent_notebook
        self.year = year

        ScrollableFrame.__init__(self, self.parent_notebook, *args, **kwargs)
        core.YearTab.__init__(self, self.add_row_action,
                              self.create_compute_widgets,
                              lambda: tkYTDPopUp(self.master_window)
                              )

        # Setting up GUI (initializing widgets)
        self.pack(expand=1, fill="both")
        self.parent_notebook.add(self, text=self.year)

        self.main_frame = tk.Frame(self.scrollable_frame)
        self.main_frame.pack()

        self.headerName = ttk.Label(self.main_frame, text="Name")
        self.headerName.grid(row=0, column=1)
        self.headerLevel = ttk.Label(
            self.main_frame, text="Level")
        self.headerLevel.grid(row=0, column=3)
        self.headerGrade = ttk.Label(
            self.main_frame, text="Grade")
        self.headerGrade.grid(row=0, column=5)
        self.headerCredits = ttk.Label(
            self.main_frame, text="Credits")
        self.headerCredits.grid(row=0, column=7)

        spacer1 = ttk.Label(self.main_frame, text=" ")
        spacer1.grid(row=100, column=0)
        spacer2 = ttk.Label(self.main_frame, text=" ")
        spacer2.grid(row=101, column=0)

        self.separator = ttk.Separator(
            self.canvas, orient="horizontal")
        self.separator.pack(fill="x")

        self.extra_widgets_frame = tk.Frame(self.canvas)
        self.extra_widgets_frame.pack(side="bottom", fill="x")

        self.compute_gpa_options_frame = tk.Frame(
            self.extra_widgets_frame)
        self.compute_gpa_options_frame.pack(side="left", anchor="w")

        self.buttons_frame = tk.Frame(self.extra_widgets_frame)
        self.buttons_frame.pack(side="right")

        self.actionLabel = ttk.Label(
            self.compute_gpa_options_frame, text="Actions:")
        self.actionLabel.pack(side="left")

        self.year_checked = tk.IntVar()
        self.year_checkbox = ttk.Checkbutton(self.compute_gpa_options_frame, text="Year GPA",
                                             variable=self.year_checked, offvalue=0, onvalue=1)
        self.year_checkbox.pack(side="left")

        self.sem_checked = tk.IntVar()
        self.sem_checkbox = ttk.Checkbutton(self.compute_gpa_options_frame, text="Semester GPA",
                                            variable=self.sem_checked, offvalue=0, onvalue=1)
        self.sem_checkbox.pack(side="left")

        self.ytd_checked = tk.IntVar()
        self.ytd_checkbox = ttk.Checkbutton(self.compute_gpa_options_frame, text="YTD GPA",
                                            variable=self.ytd_checked, offvalue=0, onvalue=1)
        self.ytd_checkbox.pack(side="left")

        self.cum_checked = tk.IntVar()
        self.cum_checkbox = ttk.Checkbutton(self.compute_gpa_options_frame, text="Cumulative GPA",
                                            variable=self.cum_checked, offvalue=0, onvalue=1)
        self.cum_checkbox.pack(side="left")

        self.compute_GPA_button = ttk.Button(
            self.buttons_frame, text="Compute GPA", command=self.compute_gpa)
        self.compute_GPA_button.pack(side="right")

        self.add_row_button = ttk.Button(
            self.buttons_frame, text="Add Course", command=self.add_row)
        self.add_row_button.pack(side="right")

        self.clean_up_button = ttk.Button(
            self.buttons_frame, text="Clean Up", command=lambda: [self.clean_up(), self.delete_gpa_value_widgets()])
        self.clean_up_button.pack(side="right")

        self.selected_calculations_widgets.extend(
            (self.year_checked, self.sem_checked, self.ytd_checked, self.cum_checked))

    def add_row_action(self):
        # Defines the action made when adding a row
        return tkCourseRow(len(self.rows) + 1,
                           self.main_frame,
                           self.remove_row_on_click
                           )

    def remove_row(self, del_row_obj):
        # Removes row from the GUI and shifts the other rows
        core.Tab.remove_row(self, del_row_obj)

        # Shifts widgets
        for row_obj in self.rows:
            row_obj.row = self.rows.index(row_obj) + 1
            for widget in row_obj.widgets:
                widget.grid(row=row_obj.row)

    def delete_gpa_value_widgets(self):
        # Clears previously calculated gpa values
        values_frame = getattr(self, "compute_widgets_values_frame", None)
        if values_frame != None:
            self.compute_widgets_values_frame.destroy()

    def create_compute_widgets(self):
        # Creating the GPA Calculations Display

        self.delete_gpa_value_widgets()

        # Creates new frame for displaying values
        self.compute_widgets_values_frame = tk.Frame(
            self.scrollable_frame)
        self.compute_widgets_values_frame.pack(
            side="left", anchor="n", expand=1, fill="x")

        quarter = None
        label_texts = ["Year GPA: ", "Sem GPA: ", "YTD GPA: ", "Cum GPA: "]

        corresponding_funcs = [
            lambda quarter: self.year_gpa(),
            lambda quarter: self.sem_gpa(),
            lambda quarter: self.ytd_gpa(quarter=quarter),
            lambda quarter: self.master_window.cumulative_gpa(quarter=quarter)
        ]

        # Prompts user for the quarter if one of the calculations requiring
        # the quarter was selected
        if self.ytd_checked.get() == 1 or self.cum_checked.get() == 1:
            quarter = tkYTDPopUp(
                self.master_window).quarter if quarter == None else None

        gpa_values = [func(quarter) if self.selected_calculations[i]
                      == 1 else None for i, func in enumerate(corresponding_funcs)]

        # Displays new values
        for i, (label, value) in enumerate(zip(label_texts, gpa_values)):
            if value != None:
                label = ttk.Label(
                    self.compute_widgets_values_frame, text=label_texts[i])
                label.grid(row=i+3, column=0, sticky="w")
                calculated_gpa = ttk.Label(
                    self.compute_widgets_values_frame, text=str(value))
                calculated_gpa.grid(row=i+3, column=1, sticky="e")

        # Styling
        if not all(value == None for value in gpa_values):
            separator = ttk.Separator(
                self.compute_widgets_values_frame, orient="horizontal")
            separator.grid(row=1, columnspan=5, sticky="ew")

            title_label = ttk.Label(
                self.compute_widgets_values_frame, text="GPA Statistics:")
            title_label.grid(row=2, column=0, sticky="w")

        label = ttk.Label(
            self.compute_widgets_values_frame, text=" ")
        label.grid(row=100, column=0, sticky="w")

    def compute_gpa(self):
        # Notifies users of errors when computing gpa
        self.selected_calculations = [
            calc.get() for calc in self.selected_calculations_widgets]
        try:
            super().compute_gpa()
        except RuntimeError:
            tkApp.notification("Error", "No Action Selected: "
                               "\n\nPlease select an action. Actions include \"Year GPA\", "
                               "\"Semester GPA\", \"YTD GPA\", and \"Cumulative GPA\"")
        except EmptyRow:
            tkApp.notification("Error", "Empty Row: "
                               "\n\nPlease enter a course.")


class tkApp(core.Application, tk.Tk):
    # Creates a window Application and allows the user to manage the Application Window
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Setting up the window and size specifications
        self.title("GPA Calculator")
        self.geometry("710x300")
        self.resizable(0, 1)
        self.maxsize(width=710, height=600)

        self.notebook = ttk.Notebook()
        self.notebook.pack(side="left", expand=1, fill="both")

        # Setting up the menu bar
        self.menubar = tk.Menu()
        self.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu = tk.Menu(self.menubar, tearoff=0)

        self.menubar.add_cascade(menu=self.file_menu, label="File")
        self.menubar.add_cascade(menu=self.help_menu, label="Help")

        self.directions = "Directions: " \
            "\n\nSelect the tab with your desired year before entering your courses." \
            "\n\nWhen entering your courses, only include those that are weighted. " \
            "Any courses without a level (AP, Honors, CP1, or CP2) should not be included. " \
            "Enter in the name, level, grade and number of credits for each course. " \
            "\n\n-------------------------------------------------------------------------------" \
            "\nNOTE: " \
            "\nTHE GRADE YOU ENTER FOR EACH COURSE SHOULD BE AN AVERAGE OF ALL QUARTER GRADES, " \
            "MIDYEAR, AND FINAL EXAMS PRIOR TO YOUR DESIRED CALCULATION" \
            "\n-------------------------------------------------------------------------------" \
            "\n\nFull year courses are 5 credits, while half year courses are 2.5 credits. Be sure to " \
            "specify which semester each semester course belongs to. (1st-Semester or 2nd-Semester). " \
            "Courses can be added or removed using the \"Add Course\" and \"X\" buttons, respectively." \
            "\n\nTo calculate a YEAR GPA, enter all weighted courses for that year, " \
            "and then select the \"Year GPA\" check box and press the \"Compute GPA\" button." \
            "\n\nTo calculate a SEMESTER GPA, enter all weighted courses for that year. " \
            "For full year courses, enter in the average of the first semester. If you want to calculate the GPA of " \
            "second semester only, enter in all second semester courses as if they were in the first semester." \
            "Select the \"Semester GPA\" check box and press the \"Compute GPA\" button." \
            "\n\nTo calculate YTD GPA, enter all weighted full year courses and semester courses " \
            "taken for that year. Select the \"YTD GPA\" check box and enter" \
            "the quarter that has most recently finished. Finally, press the \"Compute GPA\" button." \
            "\n\nTo calculate a CUMULATIVE GPA, enter all weighted courses taken during your HS career. " \
            "The cumulative gpa will be calculated across all tabs. The tab that the gpa is calculated is irrelevant." \
            "i.e. Calculating a Cumulative GPA on the \"Freshman\" tab will yield the same gpa as if it were the \"Senior\" tab." \
            "\n\nFor any calculation, if the returned GPA is not what you expect, " \
            "double check the values entered for all courses." \
            "\n\nThe \"Clean Up\" button deletes all empty rows in a tab and gets rid of " \
            "previously calculated gpa's." \
            "\n\nThe Scale System can be changed under File > Settings"

        self.about_message = "GPA Calculator " \
            "\n\nCalculates Various GPA and Course Statistics per Westford Academy " \
            "GPA Calculation Guidelines." \
            "\n\nBy Andrew DiBiasio"

        self.help_menu.add_command(
            label="Directions", command=lambda: self.notification("Directions", self.directions))
        self.help_menu.add_command(
            label="About", command=lambda: self.notification("About", self.about_message))
        self.file_menu.add_command(
            label="Save", command=self.save, accelerator="Ctrl+S")
        self.file_menu.add_command(
            label="Settings", command=lambda: tkSettingsPopUp(self))
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Exit", command=lambda: self.destroy(), accelerator="Ctrl+Q")

        self.bind("<Control-s>", lambda event: self.save())
        self.bind("<Control-q>", lambda event: self.destroy())

        # Creating the Tabs
        self.tabs = [tkYearTab(self, self.notebook, "Freshman"), tkYearTab(self, self.notebook, "Sophomore"),
                     tkYearTab(self, self.notebook, "Junior"), tkYearTab(self, self.notebook, "Senior")]

        if OS == "Linux":
            self.bind(
                "<4>",
                lambda event: ScrollableFrame.on_mouse_wheel(
                    event,
                    self.tab_num)
            )
            self.bind(
                "<5>",
                lambda event: ScrollableFrame.on_mouse_wheel(
                    event,
                    tab_num=self.tab_num)
            )

        else:
            # Windows & Mac OS
            self.bind(
                "<MouseWheel>",
                lambda event: ScrollableFrame.on_mouse_wheel(
                    event,
                    tab_num=self.tab_num)
            )

        self.load(self.insert_values)

    # Returns the current tab number
    def tab_num(self): return self.notebook.index(self.notebook.select())

    def cumulative_gpa(self, quarter=None):
        tabs = self.tabs[:]
        self.tabs = self.tabs[:self.tab_num()+1]
        gpa = core.Application.cumulative_gpa(self, quarter=quarter)
        self.tabs = tabs
        return gpa

    def insert_values(self, row_obj, line, keys):
        # Inserts csv file data into the data input widgets
        # Takes in a courseRow object
        # Takes in the current line from a csv file
        # Takes in the keys of the csv file (to access the values)

        for widget, key in zip(row_obj.entry_widgets, keys):
            if type(widget) == ttk.Entry:
                widget.insert(0, line.get(key, ""))
            elif type(widget) == ttk.Combobox:
                widget.set(line.get(key, ""))

    @staticmethod
    def notification(title, message):
        # Displays given information in a message box window
        messagebox.showinfo(
            title=title,
            message=message
        )


class Dialog(tk.Toplevel):
    # Makes a pop up Toplevel window that captures the users focus
    # Class Adopted from http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
    def __init__(self, parent, title=None):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent
        self.result = None

        self.container_frame = ScrollableFrame(self)
        self.container_frame.pack(expand=1, fill="both")

        self.body_frame = tk.Frame(self.container_frame.scrollable_frame)
        self.body_frame.pack(expand=1, fill="both", padx=5, pady=5)

        self.extra_widgets_frame = tk.Frame(self.container_frame.canvas)
        self.extra_widgets_frame.pack(side="bottom", fill="x")

        self.button_frame = tk.Frame(self.extra_widgets_frame)
        self.button_frame.pack()

        self.buttonbox()
        self.body()

        self.grab_set()

        self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        if OS == "Linux":
            self.bind(
                "<4>", lambda event: ScrollableFrame.on_mouse_wheel(event, scrollable_frame_obj=self.container_frame))
            self.bind(
                "<5>", lambda event: ScrollableFrame.on_mouse_wheel(event, scrollable_frame_obj=self.container_frame))
        else:
            # Windows & Mac OS
            self.bind(
                "<MouseWheel>", lambda event: ScrollableFrame.on_mouse_wheel(event, scrollable_frame_obj=self.container_frame))

        x = parent.winfo_rootx() + 125
        y = parent.winfo_rooty() + 25
        self.geometry("+{}+{}".format(x, y))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self):
        # Creates dialog body. Returns widget that should have
        # initial focus. This method should be overridden.
        pass

    def buttonbox(self):
        # Adding Standard "DONE" and "CANCEL" Buttons
        done_button = ttk.Button(self.button_frame, text="DONE", width=10,
                                 command=self.done, default="active")
        done_button.pack(side="left", padx=5, pady=5)
        cancel_button = ttk.Button(
            self.button_frame, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side="left", padx=5, pady=5)

        self.bind("<Return>", self.done)
        self.bind("<Escape>", self.cancel)

    def done(self, event=None):
        # Wraps up pop up window dialog when the user is done
        try:
            self.validate()
        except (ValueError, EmptyRow):
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()
        self.save_settings()
        self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        # Puts focus back to the parent window & ends dialog
        self.parent.focus_set()
        self.destroy()

    def validate(self):
        return 1  # child overriden method

    def save_settings(self):
        pass  # child overriden method


class tkYTDPopUp(Dialog):
    # Creates a smaller Pop up window for YTD calculations
    # Requires more extensive customization than the generic pop up class

    def body(self):
        # Window Size specifications
        self.geometry("215x85")
        self.resizable(0, 0)

        # Setting up the GUI
        self.label = ttk.Label(
            self.body_frame, text="Which Quarter has most recently finished?")
        self.label.pack()

        self.quarter_combo = ttk.Combobox(self.body_frame, state="readonly")
        self.quarter_combo.pack()
        self.quarter_combo["values"] = ("1", "2", "3", "4")
        self.quarter_combo.unbind_class("TCombobox", "<MouseWheel>")

    def validate(self):
        # Validates the users input
        try:
            self.quarter = int(self.quarter_combo.get())
        except ValueError:
            tkApp.notification(
                "Invalid Entry", "Please select a quarter")
            raise ValueError

    def cancel(self):
        # Handles self.quarter attr when cancelled
        Dialog.cancel(self)
        self.quarter = NotImplemented


class tkSettingsPopUp(Dialog, core.Tab):
    # Child Class of Dialog
    # Requires more extensive customization than the generic pop up class
    # Creates a separate root window allowing the user to edit calculation guidelines
    def __init__(self, parent):
        # Takes in main tkinter window object
        super().__init__(parent, title="Settings")
        core.Tab.__init__(self, self.add_row_action)

    def body(self):
        # Window Size specifications
        self.geometry("425x375")
        self.maxsize(width=425, height=550)
        self.resizable(0, 1)

       # Setting up the menu bar
        self.menubar = tk.Menu(self, tearoff=0)
        self.config(menu=self.menubar)
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(menu=self.help_menu, label="Help")

        self.directions = "Directions" \
            "\n\nHere you can set the grade and gpa increments. " \
            "Enter your schools scale for AP courses, each level will use the same scale, " \
            "deducted by your specified factor. " \
            "Close the settings window when you are finished and the main window will reappear. " \
            "The scale is automatically set to a 5.0 scale for AP classes per the Westford Academy " \
            "scaling system." \
            "\n\nPressing \"Enter\" will submit your data, and \"Escape\" will close the Pop Up without "\
            "saving your data."

        self.help_menu.add_command(
            label="Directions",
            command=lambda: tkApp.notification(
                "Settings", self.directions)
        )

        # Setting up the Header row labels
        self.grade_label = ttk.Label(
            self.body_frame, text="Grade:")
        self.grade_label.grid(row=0, column=1)
        self.spacer = ttk.Label(self.body_frame, text=" ")
        self.spacer.grid(row=0, column=2)
        self.gpa_label = ttk.Label(
            self.body_frame, text="GPA:")
        self.gpa_label.grid(row=0, column=3)

        # Styling
        self.spacer_frame = tk.Frame(self.body_frame)
        self.spacer_frame.grid(row=100, column=0)

        self.spacer1 = ttk.Label(self.spacer_frame, text=" ")
        self.spacer1.pack()
        self.spacer2 = ttk.Label(self.spacer_frame, text=" ")
        self.spacer2.pack()

        # Creating the functional Buttons
        self.add_button = ttk.Button(
            self.button_frame, text="Add Increment", command=self.add_row)
        self.add_button.pack(side="left")

        self.clean_up_button = ttk.Button(
            self.button_frame, text="Clean Up", command=self.clean_up)
        self.clean_up_button.pack(side="left")

        self.rows = []

        if not self.load_settings():
            self.add_row()

        return self.add_button  # initial focus

    def add_row_action(self):
        # An Add row of GUI action to be executed when the add button is clicked
        row = len(self.rows) + 1

        # Creating the widgets in a row of GUI
        increment_label = ttk.Label(
            self.body_frame, text="Increment: ")
        increment_label.grid(row=row, column=0)

        grade_entry = ttk.Entry(self.body_frame)
        grade_entry.grid(row=row, column=1)

        spacer = ttk.Label(self.body_frame, text=" ")
        spacer.grid(row=row, column=2)

        gpa_entry = ttk.Entry(self.body_frame)
        gpa_entry.grid(row=row, column=3)

        gui_row = core.Row(
            ["grade", "gpa"],
            [grade_entry, gpa_entry],
            Grid.grid_forget,
            lambda widget: widget.get()

        )

        # Reassigning the widgets as attributes of the gui_row object
        gui_row.increment_label = increment_label
        gui_row.grade_entry = grade_entry
        gui_row.spacer = spacer
        gui_row.gpa_entry = gpa_entry
        gui_row.row = row

        gui_row.del_button = ttk.Button(self.body_frame, text="X")
        gui_row.del_button.config(
            command=lambda: self.remove_row_on_click(gui_row.del_button))
        gui_row.del_button.grid(row=row, column=4)

        gui_row.widgets = [gui_row.increment_label, gui_row.grade_entry,
                           gui_row.spacer, gui_row.gpa_entry, gui_row.del_button]
        return gui_row

    def validate(self):
        # Validates all increment values & notifies users of detected errors
        self.clean_up()
        for row_obj in self.rows:
            values = row_obj.read()

            # Executes when no increments are entered
            if row_obj.is_empty():
                tkApp.notification(
                    "Empty Row", "Please enter a valid value into the entry field")
                raise EmptyRow

            try:
                values["grade"] = float(values.get("grade"))
                values["gpa"] = float(values.get("gpa"))
            except ValueError:
                tkApp.notification(
                    "Invalid Entry", "Please enter a valid grade: an integer or float (0-100)")
                raise ValueError

            if values.get("grade") < 0 or values.get("grade") > 100:
                tkApp.notification(
                    "Invalid Entry", "Please enter a valid grade: an integer or float (0-100)")
                raise ValueError

    def save_settings(self):
        # Saves the users increments

        increments = []

        # Clears all empty rows
        for empty_row in self.empty_rows():
            self.remove_row(empty_row)

        # Appends tuple (grade, gpa) for each row
        for row_obj in self.rows:
            values = row_obj.read()
            increments.append(
                (float(values.get("grade")), float(values.get("gpa"))))

        # Sorts the increments by grade value
        core.Course.grade_and_gpa_increments = sorted(
            increments, key=lambda increment: increment[0])

    def load_settings(self):
        # Loads the current increments into the Pop Up window
        for increment in core.Course.grade_and_gpa_increments:
            grade = increment[0]
            gpa = increment[1]

            self.add_row()
            row_obj = self.rows[-1]

            # Sets values to integers if they are divisible by 1
            grade = int(grade) if grade % 1 == 0 else grade
            gpa = int(gpa) if gpa == 0.0 else gpa

            row_obj.grade_entry.insert(0, grade)
            row_obj.gpa_entry.insert(0, gpa)

        if len(core.Course.grade_and_gpa_increments) > 0:
            return True
        else:
            return False


if __name__ == "__main__":
    app = tkApp()
    app.mainloop()
