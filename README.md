# Schedule to iCalendar
This Python tool allows you to export schedules from [ESIIAB](https://esiiab.uclm.es/horarios/) to **.ics** format, letting you have a complete schedule for any course and group in your calendar.

The application fetches schedules directly from the official website using requests and BeautifulSoup to parse the HTML.


# Execution - Manual
## Clone repository
[Instructions on how to clone a repository](https://docs.github.com/es/repositories/creating-and-managing-repositories/cloning-a-repository)

## Create virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

## Install dependencies:    
`pip install -r requirements.txt`

## Run main.py
`python main.py`

# How to use?

## Mode 1: Complete group schedule
Exports the complete schedule for a specific group (e.g., "1º GRUPO A (10)").

## Mode 2: Custom subject selection
If you take subjects from different groups, you can individually select the subjects you need. The program will show you all subjects organized by year (1º, 2º, 3º, 4º) and you can mark the ones you take.

When running the program:
1. You'll be asked which mode you prefer (1 or 2)
2. **Mode 1**: Use arrows to select your group and press Enter
3. **Mode 2**: Mark the subjects you take with space, then press Enter to continue to the next year

## Export file
A file like "**3º GRUPO I (12).ics**" or "**My_Custom_Schedule.ics**" (in mode 2) is generated. Import the file to Google Calendar or transfer it to your phone and open it to have all your subjects in your calendar.

### Important notes:
- **First semester** subjects repeat until **January 31**
- **Second semester** subjects repeat until **May 31**
- The program automatically detects both semesters from the website

# Progress
## TODO
- [ ] Automatically get end of semester date according to current semester.
- [ ] Automatically get schedules for current year.
- [ ] Automatically get schedules for current semester.

## DONE
- [x] Add graphical interface.
- [X] Automate schedule extraction.
- [X] Implement for other calendars.
- [x] Replace Selenium with requests + BeautifulSoup
- [x] Add custom subject selection mode

