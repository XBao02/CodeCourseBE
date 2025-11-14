
from flask_sqlalchemy import SQLAlchemy

# Single SQLAlchemy instance for the package
db = SQLAlchemy()

# Import model classes so they are available as `from app.models import Course, Student, ...`
from .model import (
    User, Student, Instructor, Admin, Course,
    CourseSection, Lesson, Enrollment, LessonProgress,
    Test, Question, Choice, QuestionTestCase, TestAttempt,
    CodeSubmission, Answer, AIAbilityAnalysis, StudyPlan,
    PlanItem, Message, Invoice, AIChatSession, AIChatMessage
)

__all__ = [
    'db', 'User', 'Student', 'Instructor', 'Admin', 'Course',
    'CourseSection', 'Lesson', 'Enrollment', 'LessonProgress',
    'Test', 'Question', 'Choice', 'QuestionTestCase', 'TestAttempt',
    'CodeSubmission', 'Answer', 'AIAbilityAnalysis', 'StudyPlan',
    'PlanItem', 'Message', 'Invoice', 'AIChatSession', 'AIChatMessage'
]

