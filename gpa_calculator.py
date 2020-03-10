import tkinter as tk
import csv
from tkinter import ttk, messagebox

"""
TODO:
- Implement a cumulative gpa function
- Make a desktop shortcut
- Look into storing data into MySQL / SQLite database instead of CSV file
- Add descriptive Comments in Application Class

#Possible Future Add on, Grade Breakdown & Calculator
#Possible Future Add on, parse data from ipass pdf Report Card or Progress Report

git commit New edits:
- Added feature of inputting data over multiple years
- Fixed Saving Bug (Invalid entry causes a save to be incomplete)
"""


class Course:
    # Creates a course object from the users input and allows the data to be used in calculations

    grade_and_gpa_increments = [(64, 0), (69, 2), (72, 2.7), (76, 3), (79, 3.4), (82, 3.7),
                                (86, 4), (89, 4.3), (92, 4.5), (97, 4.7), (100, 5)]  # (grade cutoff, equiv gpa)
    levels = ["AP", "H", "CP1", "CP2"]

    def __init__(self, summary):
        # takes in a dictionary (summary) with the courses name, grade, level, and credits
        self.name = summary["name"]
        self.grade = summary["grade"]
        self.credits = summary["credits"]
        self.deduction = Course.levels.index(summary["level"])
        self.gpa = self.grade_to_gpa()

    def grade_to_gpa(self):
        # returns equivalent GPA value of a grade in respect to the class level
        for increment in Course.grade_and_gpa_increments:
            # compares the grade entered to the cutoff; Adds thousandth to self.grade to overcome rounding error
            if round(self.grade + 0.001) <= increment[0]:
                # retrieves the corresponding gpa value
                gpa = increment[1] - (0.5 * self.deduction)
                return max(0, gpa)  # returns equivalent GPA conversion


class CourseGUI:
    # Creates a row of GUI and allows the user to input their course data
    def __init__(self, row, frame, del_button_command):
        # takes in an integer (row) that contains the row number of the object within the tkinter grid
        # takes in an tkinter frame object, indicating to which frame the course row belongs
        # takes in the remove course function from the Application class to bind it to the del_button widget
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

        self.widgets = [self.name_label, self.name_entry, self.space1, self.level_combo, self.space2, self.grade_entry,
                        self.space3, self.credits_combo, self.space4, self.del_button]

    def read(self):
        # reads values of the entry fields and returns a dictionary with the aggregated data
        return {"name": self.name_entry.get(), "level": self.level_combo.get(),
                "grade": self.grade_entry.get(), "credits": self.credits_combo.get()}

    def hide(self):
        # Deletes all widgets within the course row from the grid
        for field in self.widgets:
            field.grid_forget()


class YearTab:
    # Creates a window Application and allows the user to manage the Application Window
    def __init__(self, notebook, year):
        # Sets up GUI related to the application
        # takes in a parent tkinter Notebook object and a string variable containing the HS year

        self.notebook = notebook
        self.year = year

        self.courses = []
        self.courses_GUI = []
        self.selected_calculations = []
        self.compute_widgets = []

        self.course_frame = ttk.Frame(self.notebook)
        self.course_frame.pack(expand=1, fill="both")

        self.notebook.add(self.course_frame, text=self.year)

        self.headerName = ttk.Label(self.course_frame, text="Name")
        self.headerName.grid(row=0, column=1)
        self.headerLevel = ttk.Label(self.course_frame, text="Level")
        self.headerLevel.grid(row=0, column=3)
        self.headerGrade = ttk.Label(self.course_frame, text="Grade")
        self.headerGrade.grid(row=0, column=5)
        self.headerCredits = ttk.Label(self.course_frame, text="Credits")
        self.headerCredits.grid(row=0, column=7)

        self.empty_cloumn = ttk.Label(self.course_frame, text = " ")
        self.empty_cloumn.grid(row = len(self.courses_GUI) + 1, column = 0)

        self.actionLabel = ttk.Label(self.course_frame, text="Actions:")
        self.actionLabel.grid(row=len(self.courses_GUI) + 2, column=0)

        self.ytd_checked = tk.IntVar()
        self.ytd_checkbox = ttk.Checkbutton(self.course_frame, text="Year GPA",
                                            variable=self.ytd_checked, offvalue=0, onvalue=1)
        self.ytd_checkbox.grid(row=len(self.courses_GUI) + 2, column=1)

        self.sem_checked = tk.IntVar()
        self.sem_checkbox = ttk.Checkbutton(self.course_frame, text="Semester GPA",
                                            variable=self.sem_checked, offvalue=0, onvalue=1)
        self.sem_checkbox.grid(row=len(self.courses_GUI) + 2, column=3)

        self.add_course_button = ttk.Button(self.course_frame, text="Add Course", command=self.add_course)
        self.add_course_button.grid(row = len(self.courses_GUI) + 2, column = 7, sticky="E")

        self.compute_GPA_button = ttk.Button(self.course_frame, text="Compute GPA",
                                             command=lambda: self.compute_gpa(self.selected_calculations))
        self.compute_GPA_button.grid(row = len(self.courses_GUI) + 2, column = 9, sticky="W")

        [self.selected_calculations.append(int_var) for int_var in [self.ytd_checked, self.sem_checked]]
        #lists group together widgets of the same row
        self.compute_widgets.extend([[self.empty_cloumn], [self.actionLabel, self.ytd_checkbox, self.sem_checkbox,
                                                           self.add_course_button, self.compute_GPA_button]])

    def add_course(self):
        #  instantiates a new courseGUI object & shifts objects below it
        self.courses_GUI.append(CourseGUI(len(self.courses_GUI) + 1, self.course_frame, self.remove_course))
        self.shift_widgets(self.compute_widgets, False)

    def remove_course(self, del_button_clicked):
        #  Removes and handles the specified course from the gui & the course data
        for course in self.courses_GUI:
            if course.del_button == del_button_clicked:
                #  retrieves the CourseGUI object linked to the row to be deleted
                del_row = self.courses_GUI[course.row - 1]

        del_row.hide()
        self.courses_GUI.remove(del_row)

        for course in self.courses_GUI:
            for widget in course.widgets:
                widget.grid(row=self.courses_GUI.index(course) + 1)
            course.row = self.courses_GUI.index(course) + 1
        self.shift_widgets(self.compute_widgets, True)

    @staticmethod
    def shift_widgets(rows, shift_up):
        #  Takes in an iterable of rows in the GUI.
        #  Takes in a boolean, indicating whether the widgets should be shifted up or down
        row_change = -1 if shift_up else 1
        for gui_row in rows:
            for widget in gui_row:
                old_row = widget.grid_info().get("row")
                widget.grid(row=old_row + row_change)

    def validate_course_data(self):
        #  validates user input & raises errors. Notifies User of any Errors
        for course in self.courses_GUI:
            values = course.read()
            try:
                values["grade"] = float(values.get("grade"))
                values["credits"] = float(values.get("credits"))
            except ValueError:
                pass

            if type(values.get("grade")) != float or values.get("grade") < 0 or values.get("grade") > 100:
                pop_up("Error", "Invalid Grade Entry: "
                                     "\n\nPlease enter an integer or float between 0 and 100 under the grade field.")
                raise ValueError
            if values.get("level") not in Course.levels:
                pop_up("Error", "Invalid Level Entry: "
                                     "\n\nPlease select a level.")
                raise ValueError
            if values.get("credits") not in [2.5, 5]:
                pop_up("Error", "Invalid Credits Entry: "
                                     "\n\nPlease select a number of credits.")
                raise ValueError

    def init_course_obj(self):
        #  Retrieves new course data and instantiates them as Course objects.
        self.validate_course_data()
        for course in self.courses_GUI:
            values = course.read()
            values["grade"] = float(values.get("grade"))
            values["credits"] = float(values.get("credits"))
            self.courses.append(Course(values))

    def compute_gpa(self, options):
        #  Calculates the gpa for the selected options & displays them
        try:
            self.courses = []  # empties current courses, so that the latest course data can be retrieved
            self.init_course_obj()
        except ValueError:
            return

        label_texts = ["Year GPA: ", "Sem GPA: "]
        corresponding_func = [self.year_gpa(), self.sem_gpa()]

        #  clears previously calculated gpa's & resets the compute_widget list to the action selection row
        excess_widgets = self.compute_widgets[2:]
        for pair in excess_widgets:
            for widget in pair:
                widget.grid_forget()
        self.compute_widgets = self.compute_widgets[:2]

        #  Creating the GPA Display
        for option in options:
            if option.get() == 1:
                #  compute_widgets[-1][-1].grid_info()["row"] retrieves the row of the last widget in the GUI
                label = ttk.Label(self.course_frame, text=label_texts[options.index(option)])
                label.grid(row=self.compute_widgets[-1][-1].grid_info()["row"] + 2, column=0)
                calculated_gpa = ttk.Label(self.course_frame, text=str(corresponding_func[options.index(option)]))
                calculated_gpa.grid(row=self.compute_widgets[-1][-1].grid_info()["row"] + 2, column=1)
                self.compute_widgets.append((label, calculated_gpa))

    def year_gpa(self):
        #  Calculates & returns Year GPA rounded to the hundreths place
        total_weighted_gpa = sum([course.gpa * course.credits for course in self.courses])
        total_credits = sum([course.credits for course in self.courses])
        return round(total_weighted_gpa / total_credits, 2)

    def sem_gpa(self):
        #  Calculates & returns Semester GPA rounded to the hundreths place
        return round(sum([course.gpa * 2.5 for course in self.courses]) / (len(self.courses) * 2.5), 2)


class Application:
    #Creates the Application window, setup, and application functions
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

        self.help_menu.add_command(label="Directions", command=lambda: pop_up("Directions", self.directions))
        self.help_menu.add_command(label="About", command=lambda: pop_up("About", self.about_message))
        self.file_menu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        self.root.bind("<Control-s>", lambda event: self.save())

        self.years = [YearTab(self.notebook, "Freshman"), YearTab(self.notebook, "Sophomore"),
                      YearTab(self.notebook, "Junior"), YearTab(self.notebook, "Senior")]

        self.load()

        self.root.mainloop()

    def validate_all_courses_data(self):
        #validates data across all years
        for year in self.years:
            YearTab.validate_course_data(year)

    def save(self):
        #Writes data across all years to csv file

        #validates data & terminates save fn if any invalid data is found
        try:
            self.validate_all_courses_data()
        except ValueError:
            return

        with open("course_data.csv", "w") as csv_file:
            field_names = ["year", "name", "level", "grade", "credits"]
            csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
            csv_writer.writeheader()

            for year in self.years:
                for course in year.courses_GUI:
                    course_data = course.read()
                    course_data["year"] = year.year
                    csv_writer.writerow(course_data)

    def load(self):
        #Loads data across all years from csv file
        with open("course_data.csv", "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            lines = list(csv_reader)

            current_year = 0
            for line in lines:
                if line.get("year", "") != self.years[current_year].year: #finds YearTab Obj and its year {str}
                    current_year += 1

                if line.get("year", "") == self.years[current_year].year:
                    year = self.years[current_year]
                    year.add_course()
                    current_course = year.courses_GUI[-1]

                    current_course.name_entry.insert(0, line.get("name", ""))
                    current_course.level_combo.set(line.get("level", ""))
                    current_course.grade_entry.insert(0, line.get("grade", ""))
                    current_course.credits_combo.set(line.get("credits", ""))

                    try:
                        year.init_course_obj()
                    except ValueError:
                        return

            #adds an empty course row if there were no courses saved for that year
            for year in self.years:
                if len(year.courses_GUI) == 0:
                    year.add_course()


def pop_up(title, message):
    #  Displays given information in a popup window
    messagebox.showinfo(
        title=title,
        message=message
    )


if __name__ == "__main__":
    app = Application()

