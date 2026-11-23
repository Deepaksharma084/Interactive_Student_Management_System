import streamlit as st

FILE_NAME = "students.txt"
COURSES = ["Python", "Java", "C++"]


# ----------------------------------------------------------
# Classes (inheritance and polymorphism)
# --------------------------------------------------------
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def get_details(self):
        return f"{self.name}, age {self.age}"


class Student(Person):
    def __init__(self, roll_no, name, age, course, marks):
        super().__init__(name, age)
        self.roll_no = roll_no
        self.course = course
        self.marks = marks
        self.validate()

    # These methods are overridden by the child classes
    def get_level(self):
        return "Student"

    def get_min_age(self):
        return 15

    def get_pass_marks(self):
        return 40

    def get_fee(self):
        return 0

    def validate(self):
        """Raises ValueError when any value is not acceptable."""
        if self.roll_no == "" or not self.roll_no.isalnum():
            raise ValueError("Roll number must contain only letters and digits.")
        if self.name == "" or not self.name.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters and spaces.")
        if self.age < self.get_min_age():
            raise ValueError(
                f"A {self.get_level()} student must be at least {self.get_min_age()} years old."
            )
        if self.marks < 0 or self.marks > 100:
            raise ValueError("Marks must be between 0 and 100.")

    def get_result(self):
        if self.marks >= self.get_pass_marks():
            return "Pass"
        return "Fail"

    def get_details(self):
        return f"{self.roll_no} - {super().get_details()}, {self.course}, {self.get_level()}"

    def to_line(self):
        return f"{self.roll_no},{self.name},{self.age},{self.course},{self.marks},{self.get_level()}"


class UndergraduateStudent(Student):
    def get_level(self):
        return "Undergraduate"

    def get_min_age(self):
        return 16

    def get_pass_marks(self):
        return 40

    def get_fee(self):
        return 100000


class PostgraduateStudent(Student):
    def get_level(self):
        return "Postgraduate"

    def get_min_age(self):
        return 20

    def get_pass_marks(self):
        return 50

    def get_fee(self):
        return 150000


def create_student(level, roll_no, name, age, course, marks):
    roll_no = roll_no.strip()
    name = name.strip()
    if level == "Postgraduate":
        return PostgraduateStudent(roll_no, name, age, course, marks)
    return UndergraduateStudent(roll_no, name, age, course, marks)


# ----------------------------------------------------------
# File handling
# ---------------------------------------------------------------
def load_students():
    students = []
    try:
        file = open(FILE_NAME, "r")
    except FileNotFoundError:
        return students

    for line in file:
        line = line.strip()
        if line == "":
            continue
        try:
            roll_no, name, age, course, marks, level = line.split(",")
            students.append(create_student(level, roll_no, name, int(age), course, float(marks)))
        except ValueError:
            continue  # skip a damaged line
    file.close()
    return students


def save_students(students):
    file = open(FILE_NAME, "w")
    for s in students:
        file.write(s.to_line() + "\n")
    file.close()


def find_student(students, roll_no):
    for s in students:
        if s.roll_no == roll_no:
            return s
    return None


def search_students(students, query):
    query = query.strip().lower()
    found = []
    for s in students:
        text = f"{s.roll_no} {s.name} {s.course}".lower()
        if query in text:
            found.append(s)
    return found


def pick_student(students, key):
    """Step 1: search. Step 2: choose from the matches.
    Returns the chosen student, or None if nothing is chosen yet."""
    query = st.text_input("Search by name, roll number or course", key=key + "_query")
    if query.strip() == "":
        st.info("Type a name, roll number or course to search.")
        return None

    matches = search_students(students, query)
    if len(matches) == 0:
        st.warning("No matching student found.")
        return None

    options = {}
    for s in matches:
        options[f"{s.roll_no} - {s.name} ({s.course})"] = s

    label = st.selectbox(
        f"{len(matches)} match(es) found - choose one",
        list(options.keys()),
        key=key + "_choice",
    )
    return options[label]


def show_table(students):
    rows = []
    for s in students:
        rows.append(
            {
                "Roll No": s.roll_no,
                "Name": s.name,
                "Age": s.age,
                "Course": s.course,
                "Level": s.get_level(),
                "Marks": s.marks,
                "Result": s.get_result(),
                "Fee": s.get_fee(),
            }
        )
    st.dataframe(rows)


# --------------------------------------------------------------
# Streamlit interface
# ------------------------------------------------------
st.title("Student Management System")

menu = st.selectbox(
    "Choose an option",
    ["Add Student", "View All Students", "Search Student", "Update Student", "Delete Student"],
)
students = load_students()

if menu == "Add Student":
    st.header("Add Student")
    roll_no = st.text_input("Roll Number")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=100, value=18)
    level = st.radio("Level", ["Undergraduate", "Postgraduate"])
    course = st.selectbox("Course", COURSES)
    marks = st.number_input("Marks (pass marks for UG is 40 and for PG is 50)", min_value=0.0, max_value=100.0)

    if st.button("Add Student"):
        try:
            if len(roll_no.strip()) != 3 or not roll_no.strip().isdigit():
                raise ValueError("Roll number must be exactly 3 digits (for example 101).")
            student = create_student(level, roll_no, name, age, course, marks)
            if find_student(students, student.roll_no) is not None:
                raise ValueError("This roll number already exists.")
            students.append(student)
            save_students(students)
            st.success(f"{student.name} was added.")
        except ValueError as error:
            st.error(str(error))

elif menu == "View All Students":
    st.header("All Students")
    if len(students) == 0:
        st.warning("No student records yet.")
    else:
        st.write("Total students:", len(students))
        show_table(students)

elif menu == "Search Student":
    st.header("Search Student")
    query = st.text_input("Enter name, roll number or course")
    if query != "":
        found = search_students(students, query)
        if len(found) == 0:
            st.warning("No matching student found.")
        else:
            st.write("Matches found:", len(found))
            show_table(found)

elif menu == "Update Student":
    st.header("Update Student")
    if len(students) == 0:
        st.warning("No student records yet.")
    else:
        current = pick_student(students, "update")

        if current is not None:
            st.divider()
            st.subheader(f"Editing {current.roll_no}")
            k = "update_" + current.roll_no  # keys make the form refresh for each student

            name = st.text_input("Name", value=current.name, key=k + "_name")
            age = st.number_input(
                "Age", min_value=1, max_value=100, value=current.age, key=k + "_age"
            )
            levels = ["Undergraduate", "Postgraduate"]
            level = st.radio(
                "Level", levels, index=levels.index(current.get_level()), key=k + "_level"
            )
            course = st.selectbox(
                "Course", COURSES, index=COURSES.index(current.course), key=k + "_course"
            )
            marks = st.number_input(
                "Marks",
                min_value=0.0,
                max_value=100.0,
                value=float(current.marks),
                key=k + "_marks",
            )

            if st.button("Update Student"):
                try:
                    updated = create_student(level, current.roll_no, name, age, course, marks)
                    students[students.index(current)] = updated
                    save_students(students)
                    st.success(f"{current.roll_no} was updated.")
                except ValueError as error:
                    st.error(str(error))

elif menu == "Delete Student":
    st.header("Delete Student")
    if len(students) == 0:
        st.warning("No student records yet.")
    else:
        current = pick_student(students, "delete")

        if current is not None:
            st.divider()
            st.write(current.get_details())

            confirm = st.checkbox(
                "I confirm that I want to delete this student",
                key="delete_confirm_" + current.roll_no,
            )
            if st.button("Delete Student"):
                if confirm:
                    students.remove(current)
                    save_students(students)
                    st.success(f"{current.roll_no} was deleted.")
                else:
                    st.warning("Tick the confirmation box first.")