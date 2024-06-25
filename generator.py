from flask import Flask, render_template, request
import random
from ortools.sat.python import cp_model

app = Flask(__name__)

MAX_DAYS = 7
MAX_NAME_LENGTH = 50
MAX_SUBJECT_LENGTH = 50
MAX_DIVISIONS = 5

# Class definitions
class Class:
    def __init__(self, name, time, faculty, subject, division, classroom):
        self.name = name
        self.time = time
        self.faculty = faculty
        self.subject = subject
        self.division = division
        self.classroom = classroom

class Timetable:
    def __init__(self):
        self.classes = [[] for _ in range(MAX_DAYS)]
        self.num_classes = [0] * MAX_DAYS

class Subject:
    def __init__(self, name, faculty):
        self.name = name
        self.faculty = faculty

# Function to generate class name
def generate_class_name(subject, faculty, division):
    return f"{subject.name}_{faculty}_{division}"

# Round robin scheduling function using OR-Tools
def round_robin_scheduling(professors, subjects, divisions, time_quantum):
    timetables = {}
    classrooms = {}  # Dictionary to store classrooms for each division

    # Ask for classrooms for each division
    for division in range(1, divisions + 1):
        classroom = input(f"Enter the classroom for Division {division}: ")
        classrooms[division] = classroom

    # Define time slots for each day, excluding break times
    time_slots = [
        # Sunday (Holiday)
        [],
        # Monday to Saturday (excluding break times)
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"],
        ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM"]  # Half Day (Saturday)
    ]

    model = cp_model.CpModel()

    num_time_slots = sum(len(slots) for slots in time_slots)

    assignments = {}
    for division in range(1, divisions + 1):
        for day in range(1, MAX_DAYS):
            for time_slot in range(len(time_slots[day])):
                for professor in professors:
                    for subject in subjects[professor]:
                        var_name = f"{division}_{day}_{time_slot}_{professor}_{subject.name}"
                        assignments[(division, day, time_slot, professor, subject.name)] = model.NewBoolVar(var_name)

    for division in range(1, divisions + 1):
        for day in range(1, MAX_DAYS):
            for time_slot in range(len(time_slots[day])):
                model.AddExactlyOne(assignments[(division, day, time_slot, professor, subject.name)] for professor in professors for subject in subjects[professor])

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    for division in range(1, divisions + 1):
        timetable = Timetable()
        timetables[division] = timetable

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for division in range(1, divisions + 1):
            for day in range(1, MAX_DAYS):
                for time_slot in range(len(time_slots[day])):
                    for professor in professors:
                        for subject in subjects[professor]:
                            if solver.Value(assignments[(division, day, time_slot, professor, subject.name)]):
                                class_name = generate_class_name(subject, professor, division)
                                class_ = Class(class_name, time_slots[day][time_slot], professor, subject.name, division, classrooms[division])
                                timetables[division].classes[day].append(class_)
                                timetables[division].num_classes[day] += 1
    else:
        print("No solution found.")

    return timetables

# Function to print timetable in HTML format
def print_timetable_html(timetables):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    time_slots = ["8:00 AM", "9:00 AM", "10:00 AM", "11:15 AM", "12:15 PM", "2:00 PM"]

    timetable_html = ""
    for division, timetable in timetables.items():
        timetable_html += f"<h2>Timetable for Division {division} (Classroom: {timetable.classes[1][0].classroom})</h2>"
        timetable_html += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        
        # Header Row
        timetable_html += "<tr><th>Time</th>"
        for day in days_of_week:
            timetable_html += f"<th>{day}</th>"
        timetable_html += "</tr>"

        # Time Slot Rows
        for time in time_slots:
            # Insert breaks as rows
            if time == "11:15 AM":
                timetable_html += f"<tr><td colspan='{len(days_of_week) + 1}' style='text-align: center;'>Breakfast Break(11:00-11:15)</td></tr>"

            if time == "1:15 PM":  # New condition for lunch break
                timetable_html += f"<tr><td colspan='{len(days_of_week) + 1}' style='text-align: center;'>Lunch Break(1:15-2:00)</td></tr>"

            timetable_html += f"<tr><td>{time}</td>"
            for day in range(1, MAX_DAYS):
                if day == 0:  # Skip Sunday (Holiday)
                    continue
                cell_content = ""
                for class_ in timetable.classes[day]:
                    if class_.time == time:
                        cell_content = f"{class_.name} ({class_.faculty})"
                        break
                timetable_html += f"<td>{cell_content}</td>"
            timetable_html += "</tr>"

        timetable_html += "</table>"
    return timetable_html

# Route for displaying the input form
@app.route("/")
def input_form():
    return render_template("input_form.html")

# Route for handling form submission and generating timetable
@app.route("/generate", methods=["POST"])
def generate_timetable():
    num_faculty = int(request.form["num_faculty"])
    professors = []
    subjects = {}
    for i in range(num_faculty):
        professor_name = request.form[f"faculty_{i + 1}_name"]
        professors.append(professor_name)
        subjects[professor_name] = []
        num_subjects = int(request.form[f"faculty_{i + 1}_subjects"])
        for j in range(num_subjects):
            subject_name = request.form[f"faculty_{i + 1}_subject_{j + 1}"]
            subjects[professor_name].append(Subject(subject_name, professor_name))

    divisions = int(request.form["divisions"])
    time_quantum = int(request.form["time_quantum"])

    timetables = round_robin_scheduling(professors, subjects, divisions, time_quantum)

    timetable_html = print_timetable_html(timetables)
    return render_template("timetable.html", timetable_html=timetable_html)

if __name__ == "__main__":
    app.run(debug=True)
