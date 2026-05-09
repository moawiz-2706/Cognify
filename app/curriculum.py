"""Curriculum data for CS/SE/AI/DS/CYS degree programs."""

from typing import Dict, List, Any
from app.simple_models import Course, Semester


def get_curriculum() -> Dict[int, Semester]:
    """Get the complete curriculum for all semesters."""
    curriculum = {
        1: Semester(
            number=1,
            courses=[
                Course(code="CL1000", name="Introduction to Information and Communication Technology", credit_hours="0+1", semester=1),
                Course(code="CS1002", name="Programming Fundamentals", credit_hours="3+1", semester=1),
                Course(code="NS1001", name="Applied Physics", credit_hours="3+0", semester=1),
                Course(code="MT1003", name="Calculus and Analytical Geometry", credit_hours="3+0", semester=1),
                Course(code="SS1013", name="Ideology and Constitution of Pakistan", credit_hours="2+0", semester=1),
                Course(code="SS1012", name="Functional English", credit_hours="2+1", semester=1),
            ]
        ),
        2: Semester(
            number=2,
            courses=[
                Course(code="CS1004", name="Object Oriented Programming", credit_hours="3+1", semester=2),
                Course(code="SE1001", name="Introduction to Software Engineering", credit_hours="3+0", semester=2),
                Course(code="CS1005", name="Discrete Structures", credit_hours="3+0", semester=2),
                Course(code="EE1005", name="Digital Logic Design", credit_hours="3+1", semester=2),
                Course(code="MT1008", name="Multi Variable Calculus", credit_hours="3+0", semester=2),
            ]
        ),
        3: Semester(
            number=3,
            courses=[
                Course(code="CS2001", name="Data Structures", credit_hours="3+1", semester=3),
                Course(code="SE2001", name="Software Requirements Engineering", credit_hours="3+0", semester=3),
                Course(code="EE2003", name="Computer Organization and Assembly Language", credit_hours="3+1", semester=3),
                Course(code="MT1004", name="Linear Algebra", credit_hours="3+0", semester=3),
                Course(code="SS1007", name="Islamic Studies/Ethics", credit_hours="2+0", semester=3),
                Course(code="SS/MG", name="Elective-I", credit_hours="2+0", semester=3),
            ]
        ),
        4: Semester(
            number=4,
            courses=[
                Course(code="CS2005", name="Database Systems", credit_hours="3+1", semester=4),
                Course(code="MT2005", name="Probability and Statistics", credit_hours="3+0", semester=4),
                Course(code="SE2002", name="Software Design and Architecture", credit_hours="3+0", semester=4),
                Course(code="CS2006", name="Operating Systems", credit_hours="3+1", semester=4),
                Course(code="SS1014", name="Expository Writing / Communication & Presentation Skills", credit_hours="2+1", semester=4),
                Course(code="CSxxxx", name="Computing Internship", credit_hours="0+1", semester=4),
            ]
        ),
        5: Semester(
            number=5,
            courses=[
                Course(code="SE3004", name="Software Construction & Development", credit_hours="3+0", semester=5),
                Course(code="SE3002", name="Software Quality Engineering", credit_hours="3+0", semester=5),
                Course(code="CS2009", name="Design and Analysis of Algorithms", credit_hours="3+0", semester=5),
                Course(code="SS2007", name="Technical and Business Writing", credit_hours="3+0", semester=5),
                Course(code="SExxxx", name="SE Elective – I", credit_hours="3+0", semester=5),
            ]
        ),
        6: Semester(
            number=6,
            courses=[
                Course(code="CS3001", name="Computer Networks", credit_hours="3+1", semester=6),
                Course(code="SE4002", name="Fundamentals of Software Project Management", credit_hours="3+0", semester=6),
                Course(code="AI2002", name="Artificial Intelligence", credit_hours="3+1", semester=6),
                Course(code="SExxxx", name="SE Elective – II", credit_hours="3+0", semester=6),
                Course(code="SExxxx", name="SE Elective – III", credit_hours="3+0", semester=6),
            ]
        ),
        7: Semester(
            number=7,
            courses=[
                Course(code="SE4091", name="Final Year Project - I", credit_hours="0+3", semester=7),
                Course(code="CS3002", name="Information Security", credit_hours="3+0", semester=7),
                Course(code="CS3006", name="Parallel and Distributed Computing", credit_hours="3+0", semester=7),
                Course(code="SS3002", name="Civics and Community Engagement", credit_hours="2+0", semester=7),
                Course(code="SExxxx", name="SE Elective – IV", credit_hours="3+0", semester=7),
                Course(code="SExxxx", name="SE Elective – V", credit_hours="3+0", semester=7),
            ]
        ),
        8: Semester(
            number=8,
            courses=[
                Course(code="SE4091", name="Final Year Project - II", credit_hours="0+3", semester=8),
                Course(code="CS4001", name="Professional Practices", credit_hours="3+0", semester=8),
                Course(code="SS/MG", name="Elective-II", credit_hours="3+0", semester=8),
                Course(code="SExxxx", name="SE Elective – VI", credit_hours="3+0", semester=8),
                Course(code="MG4011", name="Entrepreneurship", credit_hours="3+0", semester=8),
                Course(code="SSxxxx", name="Computing Internship", credit_hours="0+1", semester=8),
            ]
        ),
    }
    return curriculum


def get_semester_courses(semester: int) -> List[Course]:
    """Get courses for a specific semester."""
    curriculum = get_curriculum()
    if semester in curriculum:
        return curriculum[semester].courses
    return []


def get_course_by_code(course_code: str) -> Course:
    """Get a course by its code."""
    curriculum = get_curriculum()
    for semester in curriculum.values():
        for course in semester.courses:
            if course.code == course_code:
                return course
    raise ValueError(f"Course {course_code} not found")

