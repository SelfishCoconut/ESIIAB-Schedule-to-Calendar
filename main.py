import os
from pathlib import Path

import cutie
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from icalendar import vText, Calendar, Event
from datetime import datetime
import zoneinfo

import pandas as pd

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

#    course = menu(courses)

    schedules = []

    for title, table in zip(tables[2::2], tables[3::2]):
        schedules.append(parser(title.text, table))

    parser_xlsx("", schedules)

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


def parser_xlsx(filename: str, schedules):
    df = pd.read_excel('asignaturas.xlsx')
    grouped = df.groupby('Exp')

    for exp, group in grouped:
        my_schedule = Schedule(str(exp))
        for _, row in group.iterrows():
            for schedule in schedules:
                if str(row['Gr']) in schedule.group:
                    for day, lectures in schedule.week.items():
                        for lecture in lectures:
                            if lecture.name.lower() == row['Asignatura'].lower():
                                print(f"Day: {day}, Name: {lecture.name}, Start: {lecture.start_time}, End: {lecture.end_time}")
                                my_schedule.add_lecture_to_day(day, lecture)

        create_events(my_schedule)



def get_subject(schedules, Subjects, Groups):
    pass


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


def create_events(schedule: Schedule, filename=None):
    calendar = Calendar()

    calendar.add('prodid', '-//My calendar product//mxm.dk//')
    calendar.add('version', '1.0')
    for day, lectures in schedule.week.items():
        for lecture in lectures:
            calendar.add_component(create_event(day, lecture))
    if filename is None:
        create_ics_file(calendar, schedule.group.split(" - ")[0])
    else:
        create_ics_file(calendar, filename)


def create_event(day, lecture):
    start_date = [int(part) for part in datetime.today().strftime('%Y-%m-%d').split("-")]
    end_date = [int(part) for part in "2025-01-10".split("-")]

    start_hour, start_min = [int(part) for part in lecture.start_time.split(":")]
    end_hour, end_min = [int(part) for part in lecture.end_time.split(":")]

    day = translate_weekdays(day)

    event = Event()
    event.add('summary', lecture.name)
    event.add('dtstart', datetime(start_date[0], start_date[1], start_date[2], start_hour, start_min, 0,
                                  tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event.add('dtend', datetime(2024, 9, 25, end_hour, end_min, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event.add('rrule', {'FREQ': 'weekly', 'until': datetime(end_date[0], end_date[1], end_date[2]), 'by-day': day})
    event['location'] = vText('Escuela Politécnica Superior Albacete, {}'.format(lecture.location))

    return event


def create_ics_file(calendar: Calendar, filename: str):
    f = open(os.path.join(Path.cwd(), filename + ".ics"), 'wb')
    f.write(calendar.to_ical())
    f.close()
    print("Archivo creado, se llama " + filename)


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
