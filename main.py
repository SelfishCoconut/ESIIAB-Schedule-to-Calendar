from selenium import webdriver
from selenium.webdriver.common.by import By

from Timetable import Schedule, Lecture


def main():
    driver = webdriver.Chrome()
    driver.get("https://www.esiiab.uclm.es/grado/horarios.php?que=&curso=2024-25&submenu=2")

    path: str = "/html/body/table[2]/tbody/tr/td/table/tbody/tr/td[2]/table[5]/tbody"
    course: int = 3
    group: str = "GRUPO I"

    parent_element = driver.find_element(By.XPATH, path)

    # Find all child elements within the parent element
    child_elements = parent_element.find_elements(By.XPATH, "./*")

    # Initialize an empty dictionary
    elements_dict = {}

    for i in range(2,len(child_elements),2):
        title = child_elements[i].text
        parser(child_elements[i+1])

    # Iterate over the child elements and store them in the dictionary
    for i in range(2, len(child_elements), 2):
        key = child_elements[i].text
        rows = child_elements[i+1].find_elements(By.XPATH, "./td/table/tbody/*")

        value = child_elements[i + 1].text if i + 1 < len(child_elements) else None
        elements_dict[key] = value

    # Print the dictionary
    print(elements_dict)

def parser(table):
    start_time: str
    end_time: str
    name: str
    location: str
    day: str
    schedule = Schedule()

    table = table.find_elements(By.XPATH, "./td/table/tbody/*")
    week = table[0].find_elements(By.XPATH, "./*")[0:len(table[0].find_elements(By.XPATH, "./*"))]
    for i in range(1,len(table)):
        row = table[i].find_elements(By.XPATH, "./*")
        start_time, end_time = row[0].text.split("\n")
        for day in range(1, len(row)):
            if(row[day].text):
                name, location = row[day].text.split("\n")
            else:
                name = ""
                location = ""
            schedule.add_lecture_to_day(week[day].text, Lecture(name, location, start_time, end_time))
    return schedule

if __name__ == "__main__":
    main()
