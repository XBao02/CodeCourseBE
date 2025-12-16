
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
from .payment import Payment
from .placement_test import PlacementTest
from .skill_profile import SkillProfile
from .learning_path import LearningPath
from .learning_path_item import LearningPathItem
from .placement_question import PlacementQuestion
from .placement_question_bank import PlacementQuestionBank

__all__ = [
    'db', 'User', 'Student', 'Instructor', 'Admin', 'Course',
    'CourseSection', 'Lesson', 'Enrollment', 'LessonProgress',
    'Test', 'Question', 'Choice', 'QuestionTestCase', 'TestAttempt',
    'CodeSubmission', 'Answer', 'AIAbilityAnalysis', 'StudyPlan',
    'PlanItem', 'Message', 'Invoice', 'AIChatSession', 'AIChatMessage',
    'PlacementTest', 'SkillProfile', 'LearningPath', 'LearningPathItem',
    'PlacementQuestion', 'PlacementQuestionBank', 'Payment',
]
