import csv
import os
from pathlib import Path


class EmptyRow(Exception):
    # EmptyRow Errors used when dealing with empty rows in the GUI
    def __init__(self):
        pass


class Course(object):
    # Creates a course object from the users input and allows the data to be used in calculations
    grade_and_gpa_increments = [(64, 0.0), (69, 2.0), (72, 2.7), (76, 3.0), (79, 3.4), (82, 3.7),
                                (86, 4.0), (89, 4.3), (92, 4.5), (97, 4.7), (100, 5.0)]  # (grade cutoff, equiv gpa)

    levels = ["AP", "H", "CP1", "CP2"]

    def __init__(self, summary):
        # Takes in a dictionary (summary) with the courses name, grade, level, and credits
        self.name = summary.get("name", "")
        self.grade = summary.get("grade", "")
        self.credits = summary.get("credits", "")

        # Deletes Semester attr if course is full year
        if summary.get("semester", "") != None:
            self.semester = summary.get("semester", "")

        # AP courses have a set scale, and each subsequent level retains that scale (difference in points between increments)
        # However, for each level, the same grade is worth less. This is noted by the deduction factor
        # The deduction_amt indicates by how many times the factor should be applied (subtract 0.5 (factor) per level (amt) under AP)
        self.deduction_factor = 0.5
        self.deduction_amt = Course.levels.index(summary["level"])

        self.gpa = self.grade_to_gpa()

        # QP = Quality Points (name for gpa * credits)
        self.QP = self.gpa * self.credits

    def grade_to_gpa(self):
        # Returns equivalent GPA value of a grade in respect to the course level
        for increment in self.grade_and_gpa_increments:
            # Compares the grade entered to the cutoff; Adds thousandth to self.grade to overcome rounding error
            if round(self.grade + 0.001) <= increment[0]:
                # Retrieves the corresponding gpa value
                deducted_gpa = increment[1] - \
                    (self.deduction_factor * self.deduction_amt)
                # Returns equivalent GPA conversion
                return max(0, deducted_gpa)


class Row(object):
    # Creates a row of GUI and allows the user to input their course data
    def __init__(self, entry_widget_keys, entry_widgets, widget_hide_fn, widget_read_fn):
        # Takes in a list of keys corresponding to their entry widgets
        # Takes in a list of entry widgets in a row
        # Takes in a hide function pointer used to hide a widget from the GUI
        # Takes in a read function pointer used to read values from a widget

        self.entry_widget_keys = entry_widget_keys
        self.entry_widgets = entry_widgets
        self.widgets = []
        self.widget_hide_fn = widget_hide_fn
        self.widget_read_fn = widget_read_fn

    def read(self):
        # Reads values of the entry fields and returns a dictionary with the aggregated data
        read_dict = {}
        for key, widget in zip(self.entry_widget_keys, self.entry_widgets):
            read_dict[key] = self.widget_read_fn(widget)
        return read_dict

    def hide(self):
        # Deletes all widgets within the row from the GUI
        for widget in self.widgets:
            self.widget_hide_fn(widget)

    def is_empty(self):
        # Checks if a row is empty
        values = self.read()
        for value in values.items():
            if value[1] != "":
                return False
        return True


class courseRow(Row):
    # Row objects specific to inputting course data
    def validate_row_data(self):
        # Validates the input of one row
        values = self.read()

        try:
            values["grade"] = float(values.get("grade"))

            # Removes the 1st / 2nd Semester Indicator from the credits
            credits_value = values.get("credits").split(" ")[0]
            values["credits"] = float(credits_value)
        except ValueError:
            pass

        if type(values.get("grade")) != float or values.get("grade") < 0 or values.get("grade") > 100:
            raise ValueError("grade error")
        if values.get("level") not in Course.levels:
            raise ValueError("level error")
        if values.get("credits") not in [2.5, 5.0]:
            raise ValueError("credits error")


class Tab(object):
    # Defines functions used for row management
    def __init__(self, add_row_action):
        # Takes in a add row fn pointer used to create all widgets in one row
        self.rows = []
        self.add_row_action = add_row_action

    def add_row(self):
        # Executes an add row action
        self.rows.append(self.add_row_action())

    def add_row_if_empty(self):
        # Adds a blank row if the tab is empty
        if len(self.rows) == 0:
            self.add_row()

    def remove_row(self, del_row):
        # Takes in a Row object (del_row) and deletes it from the GUI and the list of all rows
        del_row.hide()
        self.rows.remove(del_row)

    def remove_row_on_click(self, del_button_clicked):
        # Removes and handles the specified row from the GUI & the list of rows on Button Click
        for row_obj in self.rows:
            if row_obj.del_button == del_button_clicked:
                self.remove_row(row_obj)
                self.add_row_if_empty()

    def empty_rows(self):
        # Returns all empty rows in a tab
        empty_rows = []
        for row_obj in self.rows:
            if row_obj.is_empty():
                empty_rows.append(row_obj)
        return empty_rows

    def is_empty_row_present(self):
        # Checks for empty rows within a tab
        if len(self.empty_rows()) > 0:
            return True
        else:
            return False

    def clean_up(self):
        # Removes empty rows from GUI & forgets their objects
        # Leaves at least one empty row in each tab (if there are no filled rows)
        filled_rows = []

        for row_obj in self.rows:
            if not row_obj.is_empty():
                filled_rows.append(row_obj)
            else:
                row_obj.hide()
        self.rows = filled_rows

        self.add_row_if_empty()

    def validate_tab_data(self):
        # Validates all course data in a tab
        for row_obj in self.rows:
            row_obj.validate_row_data()


class YearTab(Tab):
    # Defines functions used for course management
    def __init__(self, add_row_action, create_compute_widgets, ytd_gpa_pop_up):
        # Takes in a GUI add row action fn pointer
        # Takes in a compute widget fn pointer used to create widgets related to the GPA Display
        # Takes in a ytd gpa fn pointer used to get input from the user
        super().__init__(add_row_action)

        self.courses = []
        self.selected_calculations_widgets = []
        self.selected_calculations = []
        self.create_compute_widgets = create_compute_widgets

        # Used to make sure the user isn't prompted multiple times
        self.ytd_gpa_pop_up = ytd_gpa_pop_up
        self.is_quarter_found = False

    def add_row(self):
        # Adds a row to the GUI
        super().add_row()

    def remove_row(self, del_row):
        # Takes in a Row object (del_row) and deletes it from the GUI and the list of all rows
        super().remove_row(del_row)

    def init_course_obj(self, row_obj):
        # Takes in Row object and instantiates it as a Course object
        values = row_obj.read()
        values["grade"] = float(values.get("grade"))

        credits_option = values.get("credits").split(" ")
        # Selects the number portion (2.5)
        values["credits"] = float(credits_option[0])

        # Selects the semester portion (nth semester) and gets the semester # (n)
        values["semester"] = int(credits_option[1][1]) if len(
            credits_option) > 1 else None

        self.courses.append(Course(values))

    def init_all_course_obj(self):
        # Initializes all course objects in a tab

        # Empties current courses list, & updates it
        self.courses = []
        for row_obj in self.rows:
            self.init_course_obj(row_obj)

    def ytd_gpa(self, pop_up_query=True, quarter=None, return_raw_values=False):
        # Calculates & returns YTD GPA
        # Takes in an optional boolean, indicating whether to prompt user for a Quarter
        # Takes in an optional quarter arg (1, 2, 3, or 4) allowing for direct fn calls
        # Quarter can be NotImplemented if the user closed out of an earlier pop up query
        # Takes in an optional boolean, indicating whether the total QP / credits should be returned
        # instead of the gpa (for calculations beyond ytd), returns a tuple, (total_QP, total_credits)
        """
        By default a pop up query is used. If pop_up_query is set to False and
        there is not quarter provided, no value will be calculated.
        """

        if quarter == NotImplemented:
            # Skips pop up query
            q = None
        elif quarter != None:
            q = quarter
        elif pop_up_query == True:
            # q is set to none if the user cancels the pop up
            q = self.ytd_gpa_pop_up().quarter
        else:
            q = None

        if q == None:
            return None

        total_QP = 0
        total_credits = 0

        # Adds the course to the ongoing QP and credits totals
        def add_course_values(course, factor):
            nonlocal total_QP
            nonlocal total_credits
            total_QP += course.gpa * (factor * course.credits)
            total_credits += (factor * course.credits)

        # Handles different credits & QP for diff numbers of q
        for course in self.courses:
            if getattr(course, "semester", None) != None:
                # Checks against Semester Courses only
                if q == 1:
                    if course.semester == 1:
                        add_course_values(course, 0.5)
                if q == 2:
                    if course.semester == 1:
                        add_course_values(course, 1)
                if q == 3:
                    if course.semester == 1:
                        add_course_values(course, 1)
                    if course.semester == 2:
                        add_course_values(course, 0.5)
                if q == 4:
                    add_course_values(course, 1)

            else:
                # For Full Year Courses Only
                total_QP += course.gpa * (1.25 * q)
                total_credits += (1.25 * q)

        if return_raw_values:
            return (total_QP, total_credits)

        return "%.2f" % (total_QP / total_credits)

    def sem_gpa(self):
        # Calculates & returns Semester GPA
        return self.ytd_gpa(pop_up_query=False, quarter=2)

    def year_gpa(self):
        # Calculates & returns Year GPA
        return self.ytd_gpa(pop_up_query=False, quarter=4)

    def compute_gpa(self):
        # Calls child create widget fn to update the GUI
        if sum(self.selected_calculations) == 0:
            self.clean_up()
            raise RuntimeError

        # Validates User Input & Cleans Up Tab
        try:
            self.clean_up()
            if self.is_empty_row_present():
                raise EmptyRow
            self.validate_tab_data()
        except ValueError:
            return

        self.init_all_course_obj()
        self.create_compute_widgets()


class Application(object):
    # Defines application window functions
    def __init__(self):
        self.tabs = []

    def cumulative_gpa(self, quarter=None):
        total_QP = 0
        total_credits = 0
        tabs_with_courses = []

        for tab in self.tabs:
            # Initializes course of all tabs if not already initialized

            try:
                if len(tab.courses) == 0:
                    tab.init_all_course_obj()
                tabs_with_courses.append(tab)
            except ValueError:
                pass

        # Adds Values
        for tab in tabs_with_courses:
            if tab == tabs_with_courses[-1]:
                values = tab.ytd_gpa(quarter=quarter, return_raw_values=True)

                if values == None:
                    return None

                total_QP += values[0]
                total_credits += values[1]
            else:
                for course in tab.courses:
                    total_QP += course.gpa * course.credits
                    total_credits += course.credits

        return "%.2f" % (total_QP / total_credits)

    def save(self):
        # Writes data across all tabs to csv file
        path_to_csv = find_path("course_data.csv")

        for tab in self.tabs:
            for empty_row in tab.empty_rows():
                tab.remove_row(empty_row)

        with open(path_to_csv, "w") as csv_file:
            field_names = ["year", "name", "level", "grade", "credits"]
            csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
            csv_writer.writeheader()

            for tab in self.tabs:
                for row_obj in tab.rows:
                    row_data = row_obj.read()
                    row_data["year"] = tab.year
                    csv_writer.writerow(row_data)
                tab.add_row_if_empty()

    def load(self, insert_values_fn):
        # Loads data to all tabs from csv file
        # Takes in fn used to insert csv values into the GUI
        try:
            path_to_csv = find_path("course_data.csv")

            with open(path_to_csv, "r") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                lines = list(csv_reader)

                current_tab = 0
                for line in lines:
                    # Finds Tab Obj and its year (str)
                    if line.get("year", "") != self.tabs[current_tab].year:
                        current_tab += 1

                    if line.get("year", "") == self.tabs[current_tab].year:
                        tab = self.tabs[current_tab]
                        tab.add_row()
                        current_row_obj = tab.rows[-1]

                        insert_values_fn(current_row_obj, line, [
                            "name", "level", "grade", "credits"])

        except FileNotFoundError:
            pass

        for tab in self.tabs:
            tab.add_row_if_empty()


def find_path(relative_path):
    # Used for locating data files from users home dir
    home_path = str(Path.home())
    return os.path.join(home_path, relative_path)
