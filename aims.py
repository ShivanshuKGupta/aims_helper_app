from selenium import webdriver
import re
import os


def search(l, e):
    """Returns list of indexes where element [e] is found in list [l]"""
    ans = []
    for i in range(len(l)):
        if l[i] == e:
            ans += [i]
    return ans


def grade_point(grade: str):
    """Returns equivalent score for a grade"""
    grade = grade.strip().replace(' ', '').upper()
    if (grade == 'A' or grade == 'A+'):
        return 10
    elif grade == 'A-':
        return 9
    elif grade == 'B':
        return 8
    elif grade == 'B-':
        return 7
    elif grade == 'C':
        return 6
    elif grade == 'C-':
        return 5
    elif grade == 'D':
        return 4
    elif grade == 'F':
        return 0
    elif grade == 'FR':
        return 0
    else:
        return 0


class Course:
    def __init__(self, id, title, credits, reg_type, elective_type, segment, coordinator, grade, reg_date):
        self.id = id
        self.title = title
        self.credits = credits
        self.reg_type = reg_type
        self.elective_type = elective_type
        self.segment = segment
        self.coordinator = coordinator
        self.grade = grade
        self.reg_date = reg_date

    def __str__(self) -> str:
        return f"<tr><td>{self.id}</td><td>{self.title}</td><td>{self.credits}</td><td>{self.grade}</td></tr>"


print("Opening a browser session.")
driver = webdriver.Chrome()
driver.get("https://aims.iiitr.ac.in/iiitraichur/")

username_input = driver.find_element(by="id", value="uid")
password_input = driver.find_element(by="id", value="pswrd")

username_input.send_keys("CS21B1027")   # enter your id here
password_input.send_keys("")   # enter your pwd here

input("First login and navigate to your grades page and then press enter to continue extraction.")

# login_button = driver.find_element("login_button")
# login_button.click()

src_code = driver.page_source.replace('\n', '').replace('\t', '')

student_name = re.search(r'loginId\s+=\s+"(.*?)"', src_code)
if student_name == None:
    print("Student name can't be extracted. Aborting.")
    exit(1)
student_name = student_name.group(1)
print(f"Extracted {student_name=}")

cur_date_time = re.search(r'currentDateTime\s+=\s+"(.*?)"', src_code)
if cur_date_time == None:
    print("Date can't be extracted. Aborting.")
    exit(1)
cur_date_time = cur_date_time.group(1)
print(f"Extracted {cur_date_time=}")

# Extracting data from html
print("Extracting student info...")
StudentInfo = [element.text for element in driver.find_elements(
    by='class name', value='flexDiv')]
print(f"{StudentInfo=}")

roll_no = StudentInfo[0].split('\n')[1]
branch_name = StudentInfo[1].split('\n')[1]

image_element = driver.find_element('class name', "studentPhoto")
image_source = image_element.get_attribute("src")

print("Extracting course ids...")
course_ids = [element.text for element in driver.find_elements(
    by='class name', value='col1')]
print(f"{course_ids=}")

print("Extracting course names...")
course_names = [element.text for element in driver.find_elements(
    by='class name', value='col2')]
print(f"{course_names=}")

print("Extracting credits...")
credits = [element.text for element in driver.find_elements(
    by='class name', value='col3')]
print(f"{credits=}")

print("Extracting course registration types...")
course_reg_type = [element.text for element in driver.find_elements(
    by='class name', value='col4')]
print(f"{course_reg_type=}")

print("Extracting course elective types...")
course_elective_type = [element.text for element in driver.find_elements(
    by='class name', value='col5')]
print(f"{course_elective_type=}")

print("Extracting segment\'s info...")
segment = [element.text for element in driver.find_elements(
    by='class name', value='col6')]
print(f"{segment=}")

print("Extracting course instructors...")
course_instructor = [element.text for element in driver.find_elements(
    by='class name', value='col7')]
print(f"{course_instructor=}")

print("Extracting your grades...")
grades: list[str] = [element.text for element in driver.find_elements(
    by='class name', value='col8')]
print(f"{grades=}")

print("Extracting course registration date...")
course_reg_date = [element.text for element in driver.find_elements(
    by='class name', value='col9')]
print(f"{course_reg_date=}")

html_output = ""
courses = []
score = 0
total_score = 0

print("Calculating your GPA...")
for i in range(1, len(course_ids)):
    if len(grades[i].strip()) == 0:
        continue
    same_courses = search(course_ids, course_ids[i])
    ans = i
    if len(same_courses) > 1:
        for j in range(len(same_courses)):
            if grades[j] > grades[ans]:
                ans = j
    if (i != ans):
        continue
    course = Course(id=course_ids[i],
                    reg_type=course_reg_type[i],
                    title=course_names[i],
                    credits=credits[i],
                    elective_type=course_elective_type[i],
                    segment=segment[i],
                    coordinator=course_instructor[i],
                    grade=grades[i],
                    reg_date=course_reg_date[i]
                    )
    courses += [course]
    credit = float(course.credits)
    score += credit*grade_point(course.grade)
    print(f"{course.grade=}, {credit=}, {score=}")
    total_score += credit*grade_point('A')
    html_output += str(course)

CGPA = round(score/total_score*10, 2)

print("Generating \'output.html\'...")
with open("output.html", "w+") as output_file:
    template = ""
    with open("template.html", "r") as template_file:
        template = template_file.read()
    template = template.replace("<!--$student_name-->", student_name)
    template = template.replace("<!--$rollno-->", roll_no)
    template = template.replace(
        "<!--$img-src-->", image_source if image_source != None else "")
    template = template.replace("<!--$branch-->", branch_name)
    template = template.replace("<!--$grade_card-->", html_output)
    template = template.replace("<!--$date-->", cur_date_time)
    template = template.replace("<!--CGPA-->", str(CGPA))
    template = template.replace(
        "<!--$email-->", f"{roll_no.lower()}@iiitr.ac.in")
    print(f"{template=}")
    output_file.write(template)

print(
    f"You can change how the webpage looks by editing {os.getcwd()}/template.html")
driver = webdriver.Chrome()
driver.execute_script("window.open('', '_blank');")
driver.switch_to.window(driver.window_handles[1])
local_html_file_path = f"file:///{os.getcwd()}/output.html"
driver.get(local_html_file_path)

input("Make sure to print your report and then you can press any key to dispose browser session and exit.")

driver.quit()
