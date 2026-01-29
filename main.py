import os
import platform
from pathlib import Path
import re

import cutie
import requests
from bs4 import BeautifulSoup

from icalendar import vText, Calendar, Event
import datetime as dt
from datetime import datetime, date
import zoneinfo

from Timetable import Schedule, Lecture


class Subject:
    """Represents a single subject with its schedule information"""
    def __init__(self, name, location, day, start_time, end_time, course_group, semester):
        self.name = name
        self.location = location
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.course_group = course_group
        self.semester = semester
    
    def __repr__(self):
        return f"{self.name} - {self.day} {self.start_time}-{self.end_time} ({self.location})"


def main():
    print("Loading...")
    
    # Fetch the HTML from the URL
    url = "https://esiiab.uclm.es/horarios/"
    response = requests.get(url, timeout=10)
    response.encoding = 'utf-8'
    
    if response.status_code != 200:
        print(f"Error loading page: {response.status_code}")
        return
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Clear screen (cross-platform)
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    # Find all tables - each schedule table comes after a header text
    tables = soup.find_all('table')
    
    courses = []
    course_data = []
    
    # The schedule headers appear as text directly before tables
    # Pattern: Match schedules like "1º GRUPO A (10) - 1 Semestre" or "3º Aspectos Prof. Inf. - 2 Semestre"
    # More flexible pattern to catch all variations
    schedule_pattern = re.compile(r'(\d+º\s+[^-]+ - \d+ Semestre)')
    
    # Get all text and split to find patterns
    page_text = soup.get_text()
    
    # Find all schedule headers in the text
    for match in schedule_pattern.finditer(page_text):
        group_name = match.group(1).strip()
        courses.append(group_name)
    
    # Now match each course with its table
    # The tables are in the same order as the course names
    if len(courses) > len(tables):
        print(f"Warning: Found {len(courses)} groups but only {len(tables)} tables")
    
    # Filter tables that are actually timetables (they have day columns)
    valid_tables = []
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 1:
            header = rows[0]
            header_text = header.get_text()
            # Check if it's a timetable (contains day names)
            if any(day in header_text for day in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']):
                valid_tables.append(table)
    
    # Match courses with valid tables
    for i, (course, table) in enumerate(zip(courses, valid_tables)):
        course_data.append((course, table))
    
    if not courses:
        print("No schedules found on the page")
        return
    
    # Ask user if they want full schedule or custom selection
    print("\nWhat would you like to do?")
    print("1. Export complete schedule for a group")
    print("2. Select individual subjects from different groups")
    
    try:
        choice = input("\nChoose option (1 or 2): ").strip()
    except EOFError:
        choice = "1"
    
    if choice == "2":
        # Custom subject selection mode
        all_subjects = parse_all_subjects(course_data)
        selected_subjects = custom_subject_selection(all_subjects)
        if selected_subjects:
            create_custom_calendar(selected_subjects)
    else:
        # Original full schedule mode
        course = menu(courses)
        
        # Find the selected course and parse its schedule
        for title, table in course_data:
            if course in title:
                create_events(parser(title, table))
    
    print("Done! Calendar file created successfully :)")
    # Open file explorer (cross-platform)
    if platform.system() == 'Windows':
        os.system('explorer .')
    elif platform.system() == 'Darwin':  # macOS
        os.system('open .')
    else:  # Linux
        os.system('xdg-open .')


def menu(courses: list):
    print("Hello! Choose a group to get the corresponding calendar (use arrows to move and Enter "
          "to select)")
    flag = "0"
    captions = []
    for index, course in enumerate(courses):
        if course[1] != flag:
            flag = course[1]
            captions.append(index)
            courses.insert(index, "")
            index += 1

    chosen_option = courses[cutie.select(courses, caption_indices=captions, selected_index=8)]
    print("Option selected correctly, processing...")
    return chosen_option


def parser(title: str, table):
    """Parse a BeautifulSoup table object into a Schedule object"""
    schedule = Schedule(title)
    
    # Get all rows from the table
    rows = table.find_all('tr')
    
    if len(rows) < 2:
        return schedule
    
    # First row contains the days of the week
    header_row = rows[0]
    days = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
    
    # Skip the first column (time) and get the day names
    day_names = days[1:] if len(days) > 1 else []
    
    # Process each subsequent row (time slots)
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        
        if len(cells) < 2:
            continue
        
        # First cell contains the time
        time_cell = cells[0].get_text(strip=True)
        
        # Parse time - format is "8:159:45" or "8:15\n9:45" or "8:15 9:45"
        # Try splitting by space or newline first
        time_parts = time_cell.replace('\n', ' ').split()
        
        if len(time_parts) >= 2:
            start_time = time_parts[0]
            end_time = time_parts[1]
        else:
            # Time is concatenated like "8:159:45"
            # Use regex to split on time pattern
            time_pattern = r'(\d{1,2}:\d{2})'
            matches = re.findall(time_pattern, time_cell)
            if len(matches) >= 2:
                start_time = matches[0]
                end_time = matches[1]
            else:
                continue
        
        # Process each day's cell
        for day_idx, cell in enumerate(cells[1:]):
            if day_idx >= len(day_names):
                break
                
            day_name = day_names[day_idx]
            cell_text = cell.get_text(strip=True)
            
            if cell_text and cell_text != '':
                # Parse lecture info
                # Format can be "Subject NameLOCATION" or "Subject Name\nLOCATION"
                lines = cell_text.split('\n')
                
                if len(lines) >= 2:
                    # Subject name and location on separate lines
                    name = lines[0].strip()
                    location = lines[1].strip()
                else:
                    # Single line - need to extract location
                    # Look for patterns like AULA, SOFTW., Lab., Elect., HW
                    text = lines[0].strip()
                    
                    # Common location patterns
                    location_patterns = [
                        r'(AULA [\d.]+)$',
                        r'(SOFTW\. \d+)$',
                        r'(Lab\. [^$]+)$',
                        r'(Elect\.[^$]+)$',
                        r'(HW \d+)$',
                        r'(Aula [^$]+)$',
                    ]
                    
                    name = text
                    location = "To be determined"
                    
                    for pattern in location_patterns:
                        match = re.search(pattern, text)
                        if match:
                            location = match.group(1)
                            name = text[:match.start()].strip()
                            break
                    
                    # If no pattern matched, try to split on common location prefixes
                    if location == "To be determined":
                        for prefix in ['AULA', 'SOFTW.', 'Lab.', 'Elect.', 'HW', 'Aula']:
                            if prefix in text:
                                idx = text.rfind(prefix)
                                name = text[:idx].strip()
                                location = text[idx:].strip()
                                break
                
                if name and name != location:
                    schedule.add_lecture_to_day(day_name, Lecture(name, location, start_time, end_time))
    
    return schedule


def parse_all_subjects(course_data):
    """Parse all subjects from all courses and organize them"""
    all_subjects = {}
    
    for title, table in course_data:
        # Extract course year (1º, 2º, 3º, 4º)
        course_year_match = re.match(r'(\d+º)', title)
        if not course_year_match:
            continue
        
        course_year = course_year_match.group(1)
        
        # Determine semester
        if '1 Semestre' in title or 'Primer Cuatrimestre' in title:
            semester = '1'
        elif '2 Semestre' in title or 'Segundo Cuatrimestre' in title:
            semester = '2'
        else:
            semester = '1'
        
        # Parse the table
        rows = table.find_all('tr')
        if len(rows) < 2:
            continue
        
        # Get day names from header
        header_row = rows[0]
        days = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        day_names = days[1:] if len(days) > 1 else []
        
        # Parse each time slot
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            # Parse time
            time_cell = cells[0].get_text(strip=True)
            time_parts = time_cell.replace('\n', ' ').split()
            
            if len(time_parts) >= 2:
                start_time = time_parts[0]
                end_time = time_parts[1]
            else:
                time_pattern = r'(\d{1,2}:\d{2})'
                matches = re.findall(time_pattern, time_cell)
                if len(matches) >= 2:
                    start_time = matches[0]
                    end_time = matches[1]
                else:
                    continue
            
            # Parse each day's subjects
            for day_idx, cell in enumerate(cells[1:]):
                if day_idx >= len(day_names):
                    break
                
                day_name = day_names[day_idx]
                cell_text = cell.get_text(strip=True)
                
                if cell_text and cell_text != '':
                    # Parse subject name and location
                    lines = cell_text.split('\n')
                    
                    if len(lines) >= 2:
                        name = lines[0].strip()
                        location = lines[1].strip()
                    else:
                        text = lines[0].strip()
                        location_patterns = [
                            r'(AULA [\d.]+)$',
                            r'(SOFTW\. \d+)$',
                            r'(Lab\. [^$]+)$',
                            r'(Elect\.[^$]+)$',
                            r'(HW \d+)$',
                            r'(Aula [^$]+)$',
                        ]
                        
                        name = text
                        location = "To be determined"
                        
                        for pattern in location_patterns:
                            match = re.search(pattern, text)
                            if match:
                                location = match.group(1)
                                name = text[:match.start()].strip()
                                break
                        
                        if location == "To be determined":
                            for prefix in ['AULA', 'SOFTW.', 'Lab.', 'Elect.', 'HW', 'Aula']:
                                if prefix in text:
                                    idx = text.rfind(prefix)
                                    name = text[:idx].strip()
                                    location = text[idx:].strip()
                                    break
                    
                    if name and name != location:
                        subject = Subject(name, location, day_name, start_time, end_time, title, semester)
                        
                        # Organize by course year
                        if course_year not in all_subjects:
                            all_subjects[course_year] = {}
                        if name not in all_subjects[course_year]:
                            all_subjects[course_year][name] = []
                        all_subjects[course_year][name].append(subject)
    
    return all_subjects


def custom_subject_selection(all_subjects):
    """Allow user to select individual subjects organized by course"""
    print("\n" + "="*60)
    print("CUSTOM SUBJECT SELECTION")
    print("="*60)
    
    selected_subjects = []
    
    # Determine which semester(s) to show based on current date
    today = date.today()
    first_semester_end = date(2026, 1, 31)
    second_semester_end = date(2026, 5, 31)
    
    # If we're still in first semester, show both semesters
    # Otherwise, show only current semester
    if today <= first_semester_end:
        show_semesters = ['1', '2']  # Show both
        print("📅 Showing both semesters (currently in first semester)\n")
    elif today <= second_semester_end:
        show_semesters = ['2']  # Show only second semester
        print("📅 Showing second semester subjects only\n")
    else:
        show_semesters = ['1', '2']  # Academic year ended, show all
        print("📅 Showing all semesters\n")
    
    # Sort course years
    course_years = sorted(all_subjects.keys())
    
    # Select year by year to avoid scrolling issues
    for course_year in course_years:
        subjects = all_subjects[course_year]
        
        # Filter subjects by semester
        filtered_subjects = {}
        for subject_name, subject_list in subjects.items():
            # Keep subject if any instance is in the allowed semesters
            if any(subj.semester in show_semesters for subj in subject_list):
                filtered_subjects[subject_name] = subject_list
        
        subject_names = sorted(filtered_subjects.keys())
        
        if not subject_names:
            continue
        
        print(f"\n{course_year} Year - {len(subject_names)} subjects available")
        print("Mark the subjects you take (use space to mark, Enter to continue):")
        
        try:
            # Use cutie for multi-select
            selected_indices = cutie.select_multiple(
                subject_names,
                caption_indices=[],
                hide_confirm=True,
                minimal_count=0
            )
            
            # Add all instances of selected subjects
            for idx in selected_indices:
                subject_name = subject_names[idx]
                selected_subjects.extend(filtered_subjects[subject_name])
        
        except (KeyboardInterrupt, EOFError):
            print("\nSelection cancelled")
            return []
    
    if selected_subjects:
        print(f"\n✓ You have selected {len(selected_subjects)} class sessions")
    else:
        print("\n✗ No subjects selected")
    
    return selected_subjects


def create_custom_calendar(subjects):
    """Create a calendar from selected subjects"""
    calendar = Calendar()
    calendar.add('prodid', '-//My calendar product//mxm.dk//')
    calendar.add('version', '2.0')
    
    # Group subjects by name to avoid duplicates
    unique_subjects = {}
    for subject in subjects:
        key = (subject.name, subject.day, subject.start_time, subject.end_time, subject.location)
        if key not in unique_subjects:
            unique_subjects[key] = subject
    
    print(f"\nGenerating calendar with {len(unique_subjects)} unique classes...")
    
    for subject in unique_subjects.values():
        # Determine end date based on semester
        if subject.semester == '1':
            end_date = [2026, 1, 31]
        else:
            end_date = [2026, 5, 31]
        
        # Create lecture object for compatibility
        lecture = Lecture(subject.name, subject.location, subject.start_time, subject.end_time)
        event = create_event(subject.day, lecture, end_date)
        calendar.add_component(event)
    
    # Create filename
    filename = "My_Custom_Schedule"
    create_ics_file(calendar, filename)


def create_events(schedule: Schedule):
    calendar = Calendar()

    calendar.add('prodid', '-//My calendar product//mxm.dk//')
    calendar.add('version', '2.0')
    
    # Determine end date based on semester
    # First semester (1 Semestre) ends late January
    # Second semester (2 Semestre) ends late May/early June
    if '1 Semestre' in schedule.group or 'Primer Cuatrimestre' in schedule.group:
        # First semester ends January 31, 2026
        end_date = [2026, 1, 31]
    elif '2 Semestre' in schedule.group or 'Segundo Cuatrimestre' in schedule.group:
        # Second semester ends May 31, 2026
        end_date = [2026, 5, 31]
    else:
        # Default to May 31, 2026 for year-long courses
        end_date = [2026, 5, 31]
    
    for day, lectures in schedule.week.items():
        for lecture in lectures:
            calendar.add_component(create_event(day, lecture, end_date))

    create_ics_file(calendar, schedule.group.split(" - ")[0])


def create_event(day, lecture, semester_end_date):
    day, num = translate_weekdays(day)
    first_date = next_weekday(datetime.today(), num)

    start_date = [int(part) for part in first_date.strftime('%Y-%m-%d').split("-")]
    end_date = semester_end_date

    start_hour, start_min = [int(part) for part in lecture.start_time.split(":")]
    end_hour, end_min = [int(part) for part in lecture.end_time.split(":")]


    event = Event()
    event.add('summary', lecture.name)
    event.add('dtstart', datetime(start_date[0], start_date[1], start_date[2], start_hour, start_min, 0,
                                  tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
    event.add('dtend', datetime(start_date[0], start_date[1], start_date[2], end_hour, end_min, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")))
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
    print("File created: " + filename)


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
