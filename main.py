import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from icalendar import vText, Calendar, Event
from datetime import datetime
import zoneinfo

from Timetable import Schedule, Lecture

def main():
    chrome_options = Options()
    #    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.esiiab.uclm.es/grado/horarios.php?que=&curso=2024-25&submenu=2")

    path: str = "/html/body/table[2]/tbody/tr/td/table/tbody/tr/td[2]/table[5]/tbody"
    course: str = '3º'
    group: str = "GRUPO I"

    parent_element = driver.find_element(By.XPATH, path)
    child_elements = parent_element.find_elements(By.XPATH, "./*")

    for i in range(2, len(child_elements), 2):
        title = child_elements[i].text
        if group.lower() in title.lower() and course.lower() in title.lower():
            create_events(parser(child_elements[i + 1]))


def parser(table):
    start_time: str
    end_time: str
    name: str
    location: str
    day: str
    schedule = Schedule()

    table = table.find_elements(By.XPATH, "./td/table/tbody/*")
    week = table[0].find_elements(By.XPATH, "./*")[0:len(table[0].find_elements(By.XPATH, "./*"))]
    for i in range(1, len(table)):
        row = table[i].find_elements(By.XPATH, "./*")
        start_time, end_time = row[0].text.split("\n")
        for day in range(1, len(row)):
            if row[day].text:
                name, location = row[day].text.split("\n")
                schedule.add_lecture_to_day(week[day].text, Lecture(name, location, start_time, end_time))
    return schedule


def create_events(schedule: Schedule):
    calendar = Calendar()

    calendar.add('prodid', '-//My calendar product//mxm.dk//')
    calendar.add('version', '1.0')
    for day, lectures in schedule.week.items():
        for lecture in lectures:
            calendar.add_component(create_event(day, lecture))

    create_ics_file(calendar, "calendario.ics")


def create_event(day, lecture):
    start_date = [int(part) for part in datetime.today().strftime('%Y-%m-%d').split("-")]
    end_date = [int(part) for part in "2025-01-10".split("-")]

    start_hour, start_min = [int(part) for part in lecture.start_time.split(":")]
    end_hour, end_min = [int(part) for part in lecture.end_time.split(":")]

    event = Event()
    event.add('summary', lecture.name)
    event.add('dtstart', datetime(start_date[0], start_date[1], start_date[2], start_hour, start_min, 0,
                                  tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event.add('dtend', datetime(2024, 9, 25, end_hour, end_min, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event['location'] = vText('Escuela Politécnica Superior Albacete, {}'.format(lecture.location))

    day = translate_weekdays(day)
    event.add('rrule', {'FREQ': 'weekly', 'until': datetime(end_date[0], end_date[1], end_date[2]), 'by-day': day})

    return event


def create_ics_file(calendar: Calendar, filename: str):
    # Write to disk
    directory = Path.cwd() / 'MyCalendar'
    directory.mkdir(parents=True, exist_ok=False)

    f = open(os.path.join(directory, filename), 'wb')
    f.write(calendar.to_ical())
    f.close()


def translate_weekdays(day: str):
    if day == "Lunes":
        day = "mo"
    elif day == "Mattes":
        day = "tu"
    elif day == "Miércoles":
        day = "we"
    elif day == "Jueves":
        day = "th"
    elif day == "Viernes":
        day = "fr"
    return day


if __name__ == "__main__":
    main()
