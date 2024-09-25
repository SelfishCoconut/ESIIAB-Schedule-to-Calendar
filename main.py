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
    options = Options()
    options.add_argument("--headless=old")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.esiiab.uclm.es/grado/horarios.php?que=&curso=2024-25&submenu=2")

    path: str = "/html/body/table[2]/tbody/tr/td/table/tbody/tr/td[2]/table[5]/tbody/*"
    course: str = '3º'
    group: str = "GRUPO I"

    tables = driver.find_elements(By.XPATH, path)

    for title, table in zip(tables[0::2], tables[1::2]):
        if group.lower() in title.text.lower() and course.lower() in title.text.lower():
            create_events(parser(title.text, table))


def parser(title: str, table):
    start_time: str
    end_time: str
    name: str
    location: str
    day: str
    schedule = Schedule(title)

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

    create_ics_file(calendar, schedule.group.split(" - ")[0])


def create_event(day, lecture):
    start_date = [int(part) for part in datetime.today().strftime('%Y-%m-%d').split("-")]
    end_date = [int(part) for part in "2025-01-10".split("-")]

    start_hour, start_min = [int(part) for part in lecture.start_time.split(":")]
    end_hour, end_min = [int(part) for part in lecture.end_time.split(":")]

    day = translate_weekdays(day)

    event = Event()
    event.add('summary', lecture.name)
    event.add('dtstart', datetime(start_date[0], start_date[1], start_date[2], start_hour, start_min, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event.add('dtend', datetime(2024, 9, 25, end_hour, end_min, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event.add('rrule', {'FREQ': 'weekly', 'until': datetime(end_date[0], end_date[1], end_date[2]), 'by-day': day})
    event['location'] = vText('Escuela Politécnica Superior Albacete, {}'.format(lecture.location))

    return event


def create_ics_file(calendar: Calendar, filename: str):
    f = open(os.path.join(Path.cwd(), filename + ".ics"), 'wb')
    f.write(calendar.to_ical())
    f.close()


def translate_weekdays(day: str):
    if day == "Lunes":
        day = "mo"
    elif day == "Martes":
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