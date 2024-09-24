class Lecture:

    start_time: str
    end_time: str
    name: str
    location: str

    def __init__(self, name: str, location: str, start_time: str, end_time: str):
        self.name = name
        self.location = location
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f"{self.subject} ({self.start_time}-{self.end_time}) at {self.location}"

class Day:
    def __init__(self):
        self.lectures = []

    def add_lecture(self, lecture):
        self.lectures.append(lecture)

    def __repr__(self):
        return "\n".join([str(lecture) for lecture in self.lectures])


class Schedule:
    def __init__(self):
        self.week = {
            "Lunes": Day(),
            "Martes": Day(),
            "Miércoles": Day(),
            "Jueves": Day(),
            "Viernes": Day()
        }

    def add_lecture_to_day(self, day, lecture):
        if day in self.week:
            self.week[day].add_lecture(lecture)

    def __repr__(self):
        schedule_str = ""
        for day, lectures in self.week.items():
            schedule_str += f"{day}:\n{lectures}\n"
        return schedule_str