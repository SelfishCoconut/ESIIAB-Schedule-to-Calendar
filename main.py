import os
from pathlib import Path

import cutie
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from icalendar import vText, Calendar, Event
import datetime as dt
from datetime import datetime
import zoneinfo

from Timetable import Schedule, Lecture


def main():
    print("Cargando...")
    options = Options()
    options.add_argument("--headless=old")
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.esiiab.uclm.es/grado/horarios.php?que=&curso=2024-25&submenu=2")

    path: str = "/html/body/table[2]/tbody/tr/td/table/tbody/tr/td[2]/table[5]/tbody/*"
    os.system('cls')

    tables = driver.find_elements(By.XPATH, path)

    courses = []
    for course in tables[2::2]:
        courses.append(course.text.split(" - ")[0])

    course = menu(courses)

    for title, table in zip(tables[0::2], tables[1::2]):
        if course in title.text:
            create_events(parser(title.text, table))
    print("Creo que todo ha salido bien :)")
    os.system('start .')


def menu(courses: list):
    print("Hola! Elige un curso para obtener el calendario correspondiente (usa las flechas para moverte y Enter "
          "para seleccionar)")
    flag = "0"
    captions = []
    for index, course in enumerate(courses):
        if course[1] != flag:
            flag = course[1]
            captions.append(index)
            courses.insert(index, "")
            index += 1

    chosen_option = courses[cutie.select(courses, caption_indices=captions, selected_index=8)]
    print("Opción elegida correctamente, procesando...")
    return chosen_option


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
                try:
                    name, location = row[day].text.split("\n")
                except:
                    continue
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
    day, num = translate_weekdays(day)
    first_date = next_weekday(datetime.today(), num)

    start_date = [int(part) for part in first_date.strftime('%Y-%m-%d').split("-")]
    end_date = [int(part) for part in "2025-01-10".split("-")]

    start_hour, start_min = [int(part) for part in lecture.start_time.split(":")]
    end_hour, end_min = [int(part) for part in lecture.end_time.split(":")]


    event = Event()
    event.add('summary', lecture.name)
    event.add('dtstart', datetime(start_date[0], start_date[1], start_date[2], start_hour, start_min, 0,
                                  tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event.add('dtend', datetime(2024, 9, 25, end_hour, end_min, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event.add('rrule',
              {'FREQ': 'weekly', 'until': datetime(end_date[0], end_date[1], end_date[2]), 'byday': day.upper()})
    event['location'] = vText('Escuela Politécnica Superior Albacete, {}'.format(lecture.location))

    return event


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    return d + dt.timedelta(days_ahead)

def create_ics_file(calendar: Calendar, filename: str):
    f = open(os.path.join(Path.cwd(), filename + ".ics"), 'wb')
    f.write(calendar.to_ical())
    f.close()
    print("Archivo creado, se llama " + filename)


def translate_weekdays(day: str):
    num: int
    if day == "Lunes":
        day = "mo"
        num = 0
    elif day == "Martes":
        day = "tu"
        num = 1
    elif day == "Miércoles":
        day = "we"
        num = 2
    elif day == "Jueves":
        day = "th"
        num = 3
    elif day == "Viernes":
        day = "fr"
        num = 4
    return day, num


if __name__ == "__main__":
    main()
