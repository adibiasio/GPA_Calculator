import core
from core import EmptyCourse
import tkinter as tk
from tkinter import ttk, messagebox, Grid


class tkCourseGUI(core.CourseGUI):
    # Creates a row of GUI and allows the user to input their course data
    def __init__(self, row, frame, del_button_command):
        # Takes in an integer (row) that contains the row number of the object within the tkinter grid
        # Takes in an tkinter frame object, indicating to which frame the course row belongs
        # Takes in the remove course function from the Application class to bind it to the del_button widget
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

        self.space2 = ttk.Label(frame, text=" ")
        self.space2.grid(row=self.row, column=4)

        self.grade_entry = ttk.Entry(frame)
        self.grade_entry.grid(row=self.row, column=5)

        self.space3 = ttk.Label(frame, text=" ")
        self.space3.grid(row=self.row, column=6)

        self.credits_combo = ttk.Combobox(frame, state="readonly")
        self.credits_combo.grid(row=self.row, column=7)
        self.credits_combo["values"] = ("2.5", "5")

        self.space4 = ttk.Label(frame, text=" ")
        self.space4.grid(row=self.row, column=8)

        self.del_button = ttk.Button(frame, text="X")
        self.del_button.config(command=lambda: del_button_command(self.del_button))
        self.del_button.grid(row=self.row, column=9)

        entry_widgets = [("name", self.name_entry), ("level", self.level_combo), 
                        ("grade", self.grade_entry), ("credits", self.credits_combo)]

        core.CourseGUI.__init__(self, entry_widgets, Grid.grid_forget)

        self.widgets = [self.name_label, self.name_entry, self.space1, self.level_combo, self.space2, self.grade_entry,
                        self.space3, self.credits_combo, self.space4, self.del_button]
    
    def validate_course_data(self):
        try:
            core.CourseGUI.validate_course_data(self)
        except ValueError as error:
            if error.args[0] == "grade error":
                tkApp.pop_up("Error", "Invalid Grade Entry: "
                    "\n\nPlease enter an integer or float between 0 and 100 under the grade field.")
            elif error.args[0] == "level error":
                tkApp.pop_up("Error", "Invalid Level Entry: "
                    "\n\nPlease select a level.")
            elif error.args[0] == "credits error":
                tkApp.pop_up("Error", "Invalid Credits Entry: "
                    "\n\nPlease select a number of credits.")
            raise ValueError



class tkTab(core.Tab):
    # Creates a Tab within the Application and allows the user to manage their courses
    def __init__(self, notebook, year):
        # Sets up GUI related to the application
        # Takes in a parent tkinter Notebook object and a string variable containing the HS year

        self.notebook = notebook
        self.year = year

        course_frame = ttk.Frame(self.notebook)
        course_frame.pack(expand=1, fill="both")

        core.Tab.__init__(self, course_frame, tkCourseGUI)

        self.notebook.add(self.course_widget_container, text=self.year)

        self.headerName = ttk.Label(self.course_widget_container, text="Name")
        self.headerName.grid(row=0, column=1)
        self.headerLevel = ttk.Label(self.course_widget_container, text="Level")
        self.headerLevel.grid(row=0, column=3)
        self.headerGrade = ttk.Label(self.course_widget_container, text="Grade")
        self.headerGrade.grid(row=0, column=5)
        self.headerCredits = ttk.Label(self.course_widget_container, text="Credits")
        self.headerCredits.grid(row=0, column=7)

        self.empty_cloumn = ttk.Label(self.course_widget_container, text = " ")
        self.empty_cloumn.grid(row = len(self.courses_GUI) + 1, column = 0)

        self.actionLabel = ttk.Label(self.course_widget_container, text="Actions:")
        self.actionLabel.grid(row=len(self.courses_GUI) + 2, column=0)

        self.ytd_checked = tk.IntVar()
        self.ytd_checkbox = ttk.Checkbutton(self.course_widget_container, text="Year GPA",
                                            variable=self.ytd_checked, offvalue=0, onvalue=1)
        self.ytd_checkbox.grid(row=len(self.courses_GUI) + 2, column=1)

        self.sem_checked = tk.IntVar()
        self.sem_checkbox = ttk.Checkbutton(self.course_widget_container, text="Semester GPA",
                                            variable=self.sem_checked, offvalue=0, onvalue=1)
        self.sem_checkbox.grid(row=len(self.courses_GUI) + 2, column=3)

        self.add_course_button = ttk.Button(self.course_widget_container, text="Add Course", command=self.add_course)
        self.add_course_button.grid(row = len(self.courses_GUI) + 2, column = 7, sticky="E")

        self.compute_GPA_button = ttk.Button(self.course_widget_container, text="Compute GPA",
                                             command=lambda: self.compute_gpa([calc.get() for calc in self.selected_calculations]))
        self.compute_GPA_button.grid(row = len(self.courses_GUI) + 2, column = 9, sticky="W")

        self.selected_calculations.extend((self.ytd_checked, self.sem_checked))
        # Widgets are grouped together by row
        self.compute_widgets.extend([[self.empty_cloumn], [self.actionLabel, self.ytd_checkbox, self.sem_checkbox,
                                                           self.add_course_button, self.compute_GPA_button]])

    def compute_gpa(self, options):
        try:
            core.Tab.compute_gpa(self, options)
        except RuntimeError:
            tkApp.pop_up("Error", "Invalid Range: "
                "\n\nPlease select an action. Actions include \"Year GPA\" and \"Semester GPA\"")
        except EmptyCourse:
            tkApp.pop_up("Error", "Invalid Range: "
                "\n\nPlease enter a course.")


class tkApp(core.Application):
    # Creates a window Application and allows the user to manage the Application Window
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPA Calculator")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side="left", expand=1, fill = "both")

        self.menubar = tk.Menu()
        self.root.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar)
        self.help_menu = tk.Menu(self.menubar)

        self.menubar.add_cascade(menu=self.file_menu, label="File")
        self.menubar.add_cascade(menu=self.help_menu, label="Help")

        self.directions = "Directions" \
            "\n\n Select the tab with your desired year before entering your courses." \
            "\n\nWhen entering your courses, only include those that are weighted. " \
            "Any courses without a level (AP, Honors, CP1, or CP2) should not be included. " \
            "Enter in the name, level, grade and number of credits for each course. " \
            "Full year courses are 5 credits, while half year courses are 2.5 credits." \
            "\n\n" \
            "To calculate a Year GPA, enter all weighted courses for that year, and then select the \"Year GPA\" check box. " \
            "Finally, press the \"Compute GPA\" button."\
            "\n\n" \
            "To calculate a Semester GPA, enter all weighted full year courses and semester courses taken in the first semester. " \
            "Select the \"Semester GPA\" check box and press the \"Compute GPA\" button. " \
            "\n\n" \
            "If the returned GPA is not what you expect, double check the values entered for all courses."

        self.about_message = "GPA Calculator " \
            "\n\nCalculates Various GPA and Course Statistics per Westford Academy GPA Calculation Guidelines." \
            "\n\nBy Andrew DiBiasio"

        self.help_menu.add_command(label="Directions", command=lambda: self.pop_up("Directions", self.directions))
        self.help_menu.add_command(label="About", command=lambda: self.pop_up("About", self.about_message))
        self.file_menu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        self.root.bind("<Control-s>", lambda event: self.save())

        self.tabs = [tkTab(self.notebook, "Freshman"), tkTab(self.notebook, "Sophomore"),
                      tkTab(self.notebook, "Junior"), tkTab(self.notebook, "Senior")]

        self.load()

        self.root.mainloop()

    @staticmethod
    def pop_up(title, message):
        #  Displays given information in a popup window
        messagebox.showinfo(
            title=title,
            message=message
        )


if __name__ == "__main__":
    app = tkApp()
