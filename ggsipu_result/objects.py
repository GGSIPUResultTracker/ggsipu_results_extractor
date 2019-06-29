"""Module having classes for data storing.
"""

import json
from .util import JSONSerializable


class Subject(JSONSerializable):
    def __init__(self, paper_id, paper_code=None, name=None, credit=None, minor_max=None,
                 major_max=None, type=None, department=None, mode=None, kind=None, semester=None):
        self.paper_id = paper_id
        self.paper_code = paper_code
        self.name = name
        self.credit = credit
        self.minor_max = minor_max
        self.major_max = major_max
        self.type = type
        self.department = department
        self.mode = mode
        self.kind = kind
        self.semester = semester

    @staticmethod
    def pass_marks():
        # TODO: Temprariliy using hardcoded value, update it to scrap from pdf
        return 40

    @staticmethod
    def max_marks():
        # TODO: Temprariliy using hardcoded value, update it to scrap from pdf
        return 100

    def __str__(self):
        return "{self.paper_id}-{self.name}[{self.paper_code}]".format(self=self)

    def __eq__(self, other):
        return self.paper_id == other


class Marks(JSONSerializable):
    def __init__(self, paper_id, minor, major, total, grade=None, paper_credit=None):
        self.paper_id = paper_id
        self.minor = minor
        self.major = major
        self.total = total
        self.grade = grade
        self.paper_credit = paper_credit

    def __str__(self):
        return "[{self.paper_id}]({self.paper_credit}) Minor-{self.minor}, Major-{self.major}, Total-{self.total}".format(self=self)


class Result(JSONSerializable):

    def __init__(self, roll_num, semester, student_name=None, batch=None, marks=None):
        self.semester = semester
        self.roll_num = roll_num
        self.student_name = student_name
        self.batch = batch
        self.marks = marks if marks else {}

    def get_mark_drops(self):
        """Return marks where total in less than passing marks or None"""
        return self.get_marks(0, 39, True)

    def get_num_drops(self):
        """Get the num total failed."""
        return len(self.get_mark_drops())

    num_drops = property(lambda self: self.get_num_drops(), None, None)
    """
    Read-only property that accesses the
    get_num_drops()<Result.get_num_drops()> function.
    """
    
    def get_marks_by_paper(self, paper_id):
        return self.marks[paper_id]

    def get_marks(self, min_marks=0, max_marks=Subject.max_marks(), include_none=False):
        """ Return the marks whose total is more than eq 'min_marks' and more than eq 'max_marks'

            Args:
                min_marks: minimum marks
                max_marks: maximum marks
                include_none: Whether to include marks where total in None or not.

            Returns:
                List of filtered Marks objects.
        """
        marks = []
        for k, m in self.marks.items():
            if m.total:
                if min_marks <= m.total <= max_marks:
                    marks.append(m)
            else:
                if include_none and min_marks == 0:
                    marks.append(m)
        return marks

    def add_mark(self, paper_id, mark):
        if isinstance(paper_id, int):
            self.marks[paper_id] = mark
        else:
            raise TypeError("paper_id should be of int type")

    def get_cgpa(self):
        """Get the CGPA for tha marks"""

        grades = {'O': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 'C': 5, 'P': 4}
        total_credit = sum(
            m.paper_credit if m.paper_credit else 0 for m in self.get_marks())
        total = sum(grades.get(
            m.grade, 0) * m.paper_credit if m.total and m.paper_credit else 0 for m in self.get_marks())
        return round(total/total_credit, 2) if total and total_credit else 0

    cgpa = property(lambda self: self.get_cgpa(), None, None)
    """
    Read-only property that accesses the
    get_cgpa()<Result.get_cgpa()> function.
    """

    def __str__(self):
        return "Result(Sem {self.semester})[{self.roll_num}]{self.student_name}({self.batch}) [CGPA: {self.cgpa}]".format(self=self)


class Student(JSONSerializable):
    def __init__(self, roll_num, full_name=None, batch_year=None, programme_code=None,
                 programme_name=None, institution_code=None, institution_name=None):
        self.name = full_name
        self.id = roll_num
        self.batch = batch_year
        self.results = {}
        self.programme_code = programme_code
        self.programme_name = programme_name
        self.institution_code = institution_code
        self.institution_name = institution_name

    def iter_results(self):
        """Return generator object of all results.
        """
        for sem in self.results:
            yield self.results[sem]

    def get_result_by_sem(self, sem):
        return self.results[sem]

    def add_result(self, res, semester):
        """Add the result to results dict.

        If result for semester is already present then it ignores current.
        """
        if not semester in self.results:
            self.update_result(res, semester)
        # else:
        #     raise Exception("Result for semester {} is already present.".format(semester))

    def update_result(self, res, semester):
        """Update the result for given semester.
        """
        if isinstance(semester, int):
            self.results[semester] = res
        else:
            raise TypeError("semester should be of int type")

    def __str__(self):
        return "{self.name} - {self.id} [{self.batch}]".format(self=self)
