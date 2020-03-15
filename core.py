import tkinter as tk
import csv
from tkinter import ttk, messagebox

"""
TODO:
- Implement a cumulative gpa function, Quarter GPA Function
- Parse from pdf file
- Make a desktop shortcut
- Make available with Android
- Look into storing data into MySQL / SQLite database instead of CSV file

#Possible Future Add on, Grade Breakdown & Calculator
#Possible Future Add on, parse data from ipass pdf Report Card or Progress Report
""" 


class EmptyCourse(Exception):
    # EmptyCourse Errors used when dealing with empty courses in the GUI
    def __init__(self):
        pass


class Course(object):
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


class CourseGUI(object):
    # Creates a row of GUI and allows the user to input their course data
    def __init__(self, entry_widgets, widget_hide_fn):
        # Takes in a list of tuples (key, value) of all entry widgets in a row
        # Takes in a hide function used to hide a widget from the GUI

        self.entry_widgets = entry_widgets
        self.widgets = []
        self.widget_hide_fn = widget_hide_fn

    def validate_course_data(self):
        # Validates the input of one course
        values = self.read()

        try:
            values["grade"] = float(values.get("grade"))
            values["credits"] = float(values.get("credits"))
        except ValueError:
            pass

        if type(values.get("grade")) != float or values.get("grade") < 0 or values.get("grade") > 100:
            raise ValueError("grade error")
        if values.get("level") not in Course.levels:
            raise ValueError("level error")
        if values.get("credits") not in [2.5, 5]:
            raise ValueError("credits error")

    def is_empty(self):
        values = self.read()
        if values.get("name") == '' and values.get("level") == '' and values.get("grade") == '' and values.get("credits") == '':
            return True
        else:
            return False

    def read(self):
        # reads values of the entry fields and returns a dictionary with the aggregated data
        read_dict = {}
        for entry in self.entry_widgets:
            read_dict[entry[0]] = entry[1].get()
        return read_dict

    def hide(self):
        # Deletes all widgets within the course row from the grid
        for widget in self.widgets:
            self.widget_hide_fn(widget)


class Tab(object):
    # Defines functions used for course management
    def __init__(self, widget_container, GUI_specific_course_GUI_class):
        # Takes in a GUI container (e.g. a Frame) of the widgets
        # Takes in the GUI specific CourseGUI class

        self.courses = []
        self.courses_GUI = []
        self.selected_calculations = []
        self.compute_widgets = []

        self.course_widget_container = widget_container
        self.GUI_specific_course_GUI_class = GUI_specific_course_GUI_class

    def add_course(self):
        # Instantiates a new courseGUI object & shifts objects below it
        self.courses_GUI.append(self.GUI_specific_course_GUI_class(len(self.courses_GUI) + 1, 
                                self.course_widget_container, self.remove_course_on_click))
        self.shift_widgets(self.compute_widgets, False)

    def add_course_if_empty(self):
        # Adds a course if the tab is empty
        if len(self.courses_GUI) == 0:
            self.add_course()

    def remove_course(self, del_course):
        del_course.hide()
        self.courses_GUI.remove(del_course)

        # Shifts widgets
        for course in self.courses_GUI:
            for widget in course.widgets:
                widget.grid(row=self.courses_GUI.index(course) + 1)
            course.row = self.courses_GUI.index(course) + 1
        self.shift_widgets(self.compute_widgets, True)

    def remove_course_on_click(self, del_button_clicked):
        # Removes and handles the specified course from the GUI & the course data on Button Click
        for course in self.courses_GUI:
            if course.del_button == del_button_clicked:
                # Retrieves the CourseGUI object linked to the row to be deleted
                del_course = self.courses_GUI[course.row - 1]
                self.remove_course(del_course)
                self.add_course_if_empty()

    @staticmethod
    def shift_widgets(rows, shift_up):
        # Takes in an iterable of rows in the GUI.
        # Takes in a boolean, indicating whether the widgets should be shifted up or down
        row_change = -1 if shift_up else 1
        for gui_row in rows:
            for widget in gui_row:
                old_row = widget.grid_info().get("row")
                widget.grid(row=old_row + row_change)

    def validate_tab_data(self):
        # Validates all course data in a tab
        for course in self.courses_GUI:
            course.validate_course_data()

    def empty_courses(self):
        # Returns all empty rows in a tab
        empty_courses = []
        for course in self.courses_GUI:
            values = course.read()
            if course.is_empty():
                empty_courses.append(course)
        return empty_courses

    def is_empty_course_in_tab(self):
        # Checks for empty rows within a tab
        if len(self.empty_courses()) > 0:
            return True
        else:
            return False

    def tab_clean_up(self):
        # Removes empty rows from GUI & forgets their objects
        # Leaves at least one empty row in each tab (if there are no filled rows)
        filled_courses = []
        for course in self.courses_GUI:
            if not course.is_empty():
                filled_courses.append(course)
            else:
                course.hide()
        self.courses_GUI = filled_courses

        self.add_course_if_empty()

    def init_course_obj(self, course):
        # Takes in CourseGUI obbject, retrieves new course data and instantiates it as a Course object
        values = course.read()
        values["grade"] = float(values.get("grade"))
        values["credits"] = float(values.get("credits"))
        self.courses.append(Course(values))

    def year_gpa(self):
        # Calculates & returns Year GPA rounded to the hundreths place
        total_weighted_gpa = sum([course.gpa * course.credits for course in self.courses])
        total_credits = sum([course.credits for course in self.courses])
        return round(total_weighted_gpa / total_credits, 2)

    def sem_gpa(self):
        # Calculates & returns Semester GPA rounded to the hundreths place
        return round(sum([course.gpa * 2.5 for course in self.courses]) / (len(self.courses) * 2.5), 2)

    def compute_gpa(self, options):
        # Calculates the gpa for the selected options & displays them
        # Takes in a list of 0's and 1's, indicating which calculations are selected

        if sum(options) == 0:
            self.tab_clean_up()
            raise RuntimeError
        else:
            # Validates User Input & Cleans Up Tab
            try:
                self.tab_clean_up()
                if self.is_empty_course_in_tab():
                    raise EmptyCourse 
                self.validate_tab_data()
            except ValueError:
                return
            
            # Empties current courses, & updates course objects list
            self.courses = []
            for course in self.courses_GUI:
                self.init_course_obj(course)

            label_texts = ["Year GPA: ", "Sem GPA: "]
            corresponding_value = [self.year_gpa(), self.sem_gpa()]

            # Clears previously calculated gpa's & resets the compute_widget list to the action selection row
            excess_widgets = self.compute_widgets[2:]
            for pair in excess_widgets:
                for widget in pair:
                    widget.grid_forget()
            self.compute_widgets = self.compute_widgets[:2]

            # Creating the GPA Display
            for i, option in enumerate(options):
                if option == 1:
                    # compute_widgets[-1][-1].grid_info()["row"] retrieves the row of the last widget in the GUI
                    label = ttk.Label(self.course_widget_container, text=label_texts[i])
                    label.grid(row=self.compute_widgets[-1][-1].grid_info()["row"] + 2, column=0)
                    calculated_gpa = ttk.Label(self.course_widget_container, text=str(corresponding_value[i]))
                    calculated_gpa.grid(row=self.compute_widgets[-1][-1].grid_info()["row"] + 2, column=1)
                    self.compute_widgets.append((label, calculated_gpa))


class Application(object):
    # Defines application window functions
    def __init__(self):
        self.tabs = []

    def validate_and_del_empty_courses_all_tabs(self):
        # Validates data of all tabs & deletes all empty courses
        for tab in self.tabs:
            for empty_course in tab.empty_courses():
                tab.remove_course(empty_course) 
            tab.validate_tab_data()

    def save(self):
        # Writes data across all tabs to csv file

        # Validates data & terminates save fn if any invalid data is found
        try:   
            self.validate_and_del_empty_courses_all_tabs()
        except ValueError:
            return

        with open("course_data.csv", "w") as csv_file:
            field_names = ["year", "name", "level", "grade", "credits"]
            csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
            csv_writer.writeheader()

            for tab in self.tabs:
                for course in tab.courses_GUI:
                    course_data = course.read()
                    course_data["year"] = tab.year
                    csv_writer.writerow(course_data)

        for tab in self.tabs:
            tab.tab_clean_up()

    def load(self):
        # Loads data to all tabs from csv file
        with open("course_data.csv", "r") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            lines = list(csv_reader)

            current_tab = 0
            for line in lines:
                if line.get("year", "") != self.tabs[current_tab].year: # Finds Tab Obj and its year {str}
                    current_tab += 1

                if line.get("year", "") == self.tabs[current_tab].year:
                    tab = self.tabs[current_tab]
                    tab.add_course()
                    current_course = tab.courses_GUI[-1]

                    current_course.name_entry.insert(0, line.get("name", ""))
                    current_course.level_combo.set(line.get("level", ""))
                    current_course.grade_entry.insert(0, line.get("grade", ""))
                    current_course.credits_combo.set(line.get("credits", ""))

                    try:
                        current_course.validate_course_data()
                        tab.init_course_obj(current_course)
                    except ValueError:
                        return

            for tab in self.tabs:
                tab.add_course_if_empty()

