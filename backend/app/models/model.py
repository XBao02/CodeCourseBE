from datetime import datetime
from app.models import db 
# Lưu ý: Đảm bảo 'db' được import đúng từ nơi bạn khởi tạo SQLAlchemy app

# ==========================================================
# BẢNG LIÊN KẾT (MANY-TO-MANY)
# ==========================================================

# Liên kết Khóa học - Danh mục
course_categories = db.Table('course_categories',
    db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'), primary_key=True),
    db.Column('CategoryId', db.BigInteger, db.ForeignKey('Categories.Id'), primary_key=True)
)

# Liên kết Khóa học - Chủ đề (Topics)
course_topics = db.Table('course_topics',
    db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'), primary_key=True),
    db.Column('TopicId', db.BigInteger, db.ForeignKey('Topics.Id'), primary_key=True)
)

# Liên kết Khóa học - Khóa học (Tiên quyết - Prerequisites)
course_prerequisites = db.Table('course_prerequisites',
    db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'), primary_key=True),
    db.Column('PrerequisiteCourseId', db.BigInteger, db.ForeignKey('Courses.Id'), primary_key=True)
)

# ========================
# BẢNG NGƯỜI DÙNG
# ========================
class User(db.Model):
    __tablename__ = 'Users'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column('Email', db.String(190), unique=True, nullable=False)
    password_hash = db.Column('PasswordHash', db.String(255), nullable=False)
    full_name = db.Column('FullName', db.String(150), nullable=False)
    role = db.Column('Role', db.String(50), nullable=False, default='student')
    avatar_url = db.Column('AvatarUrl', db.String(255))
    is_active = db.Column('IsActive', db.Boolean, nullable=False, default=True)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    student = db.relationship('Student', backref='user', uselist=False)
    instructor = db.relationship('Instructor', backref='user', uselist=False)
    admin = db.relationship('Admin', backref='user', uselist=False)
    
    # Quan hệ chat
    sent_messages = db.relationship('Message', foreign_keys='Message.from_user_id', backref='from_user')
    received_messages = db.relationship('Message', foreign_keys='Message.to_user_id', backref='to_user')
    ai_sessions = db.relationship('AIChatSession', backref='user')
    
    # Quan hệ hành vi (AI Recommendation)
    interactions = db.relationship('UserInteraction', backref='user')

# ========================
# SINH VIÊN
# ========================
class Student(db.Model):
    __tablename__ = 'Students'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'), unique=True, nullable=False)
    birth_date = db.Column('BirthDate', db.Date)
    phone = db.Column('Phone', db.String(20))
    address = db.Column('Address', db.String(255))
    occupation = db.Column('Occupation', db.String(120))
    study_goal = db.Column('StudyGoal', db.Text)
    
    # [MỚI] Vector sở thích cho AI (Lưu JSON array)
    interest_vector = db.Column('InterestVector', db.JSON) 

    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    enrollments = db.relationship('Enrollment', backref='student', cascade="all, delete-orphan")
    lesson_progress = db.relationship('LessonProgress', backref='student')
    test_attempts = db.relationship('TestAttempt', backref='student')
    ai_analysis = db.relationship('AIAbilityAnalysis', backref='student')
    study_plans = db.relationship('StudyPlan', backref='student')
    invoices = db.relationship('Invoice', backref='student')
    
    # [MỚI] Quan hệ Recommendation System
    reviews = db.relationship('Review', backref='student')
    wishlist = db.relationship('Wishlist', backref='student')

# ========================
# GIẢNG VIÊN
# ========================
class Instructor(db.Model):
    __tablename__ = 'Instructors'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'), unique=True, nullable=False)
    expertise = db.Column('Expertise', db.String(255))
    biography = db.Column('Biography', db.Text)
    years_experience = db.Column('YearsExperience', db.Integer, default=0)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    courses = db.relationship('Course', backref='instructor', cascade="all, delete-orphan")

# ========================
# ADMIN
# ========================
class Admin(db.Model):
    __tablename__ = 'Admins'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'), unique=True, nullable=False)
    notes = db.Column('Notes', db.Text)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

# ========================
# [MỚI] DANH MỤC (CATEGORIES)
# ========================
class Category(db.Model):
    __tablename__ = 'Categories'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column('Name', db.String(100), nullable=False)
    slug = db.Column('Slug', db.String(100), unique=True, nullable=False)
    parent_id = db.Column('ParentId', db.BigInteger, db.ForeignKey('Categories.Id'))
    
    # Quan hệ đệ quy (Category cha - con)
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    topics = db.relationship('Topic', backref='category')

# ========================
# [MỚI] CHỦ ĐỀ (TOPICS)
# ========================
class Topic(db.Model):
    __tablename__ = 'Topics'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column('Name', db.String(100), nullable=False)
    slug = db.Column('Slug', db.String(100), unique=True, nullable=False)
    category_id = db.Column('CategoryId', db.BigInteger, db.ForeignKey('Categories.Id'), nullable=False)

# ========================
# KHÓA HỌC (ĐÃ CẬP NHẬT)
# ========================
class Course(db.Model):
    __tablename__ = 'Courses'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    instructor_id = db.Column('InstructorID', db.BigInteger, db.ForeignKey('Instructors.Id'), nullable=False)
    title = db.Column('Title', db.String(180), nullable=False)
    slug = db.Column('Slug', db.String(200), unique=True, nullable=False)
    image_url = db.Column('ImageUrl', db.String(500), nullable=True)
    description = db.Column('Description', db.Text)
    level = db.Column('Level', db.String(50), nullable=False, default='beginner')
    language = db.Column('Language', db.String(64), nullable=False, default='general')
    price = db.Column('Price', db.Numeric(12, 2), nullable=False, default=0.00)
    currency = db.Column('Currency', db.String(3), nullable=False, default='VND')
    is_public = db.Column('IsPublic', db.Boolean, nullable=False, default=False)
    # [MỚI] Vector đặc trưng khóa học cho AI
    embedding_vector = db.Column('EmbeddingVector', db.JSON)

    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Quan hệ cũ
    sections = db.relationship('CourseSection', backref='course')
    enrollments = db.relationship('Enrollment', backref='course')
    invoices = db.relationship('Invoice', backref='course')
    
    # [MỚI] Quan hệ cho hệ thống Gợi ý
    categories = db.relationship('Category', secondary=course_categories, backref='courses')
    topics = db.relationship('Topic', secondary=course_topics, backref='courses')
    reviews = db.relationship('Review', backref='course')
    
    # Khóa học tiên quyết (Self-referential Many-to-Many)
    prerequisites = db.relationship(
        'Course', 
        secondary=course_prerequisites,
        primaryjoin=(course_prerequisites.c.CourseId == id),
        secondaryjoin=(course_prerequisites.c.PrerequisiteCourseId == id),
        backref='required_for'
    )

# ========================
# [MỚI] TƯƠNG TÁC NGƯỜI DÙNG
# ========================
class UserInteraction(db.Model):
    __tablename__ = 'UserInteractions'
    
    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'), nullable=False)
    entity_id = db.Column('EntityId', db.BigInteger, nullable=False) # ID của Course hoặc Lesson
    entity_type = db.Column('EntityType', db.String(50), default='course') # 'course', 'lesson'
    interaction_type = db.Column('InteractionType', db.String(50), nullable=False) # 'view', 'click', 'search', 'wishlist_add'
    duration_seconds = db.Column('DurationSeconds', db.Integer, default=0)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

# ========================
# [MỚI] ĐÁNH GIÁ & REVIEW
# ========================
class Review(db.Model):
    __tablename__ = 'Reviews'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    course_id = db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'), nullable=False)
    student_id = db.Column('StudentId', db.BigInteger, db.ForeignKey('Students.Id'), nullable=False)
    rating = db.Column('Rating', db.Integer, nullable=False) # 1-5
    comment = db.Column('Comment', db.Text)
    sentiment_score = db.Column('SentimentScore', db.Numeric(4, 3)) # Điểm cảm xúc từ AI (-1 đến 1)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

# ========================
# [MỚI] DANH SÁCH YÊU THÍCH
# ========================
class Wishlist(db.Model):
    __tablename__ = 'Wishlists'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column('StudentId', db.BigInteger, db.ForeignKey('Students.Id'), nullable=False)
    course_id = db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'), nullable=False)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)


# ========================
# PHẦN HỌC
# ========================
class CourseSection(db.Model):
    __tablename__ = 'CourseSections'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    course_id = db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'), nullable=False)
    title = db.Column('Title', db.String(180), nullable=False)
    sort_order = db.Column('SortOrder', db.Integer, default=0)

    lessons = db.relationship('Lesson', backref='section')

# ========================
# BÀI HỌC
# ========================
class Lesson(db.Model):
    __tablename__ = 'Lessons'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    section_id = db.Column('SectionId', db.BigInteger, db.ForeignKey('CourseSections.Id'), nullable=False)
    title = db.Column('Title', db.String(180), nullable=False)
    type = db.Column('Type', db.String(50), nullable=False, default='video')
    content = db.Column('Content', db.Text)
    video_url = db.Column('VideoUrl', db.String(255))
    duration_seconds = db.Column('DurationSeconds', db.Integer)
    sort_order = db.Column('SortOrder', db.Integer, default=0)
    is_preview = db.Column('IsPreview', db.Boolean, default=False)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

    tests = db.relationship('Test', backref='lesson')
    progress = db.relationship('LessonProgress', backref='lesson')

# ========================
# ĐĂNG KÝ KHÓA HỌC
# ========================
class Enrollment(db.Model):
    __tablename__ = 'Enrollments'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column('StudentId', db.BigInteger, db.ForeignKey('Students.Id'), nullable=False)
    course_id = db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'), nullable=False)
    status = db.Column('Status', db.String(50), nullable=False, default='pending')
    progress_percent = db.Column('ProgressPercent', db.Integer, default=0)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

# ========================
# TIẾN ĐỘ BÀI HỌC
# ========================
class LessonProgress(db.Model):
    __tablename__ = 'LessonProgress'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column('StudentId', db.BigInteger, db.ForeignKey('Students.Id'), nullable=False)
    lesson_id = db.Column('LessonId', db.BigInteger, db.ForeignKey('Lessons.Id'), nullable=False)
    status = db.Column('Status', db.String(50), default='not_started')
    score = db.Column('Score', db.Numeric(6, 2))
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True))

# ========================
# TEST
# ========================
class Test(db.Model):
    __tablename__ = 'Tests'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column('Title', db.String(180), nullable=False)
    is_placement = db.Column('IsPlacement', db.Boolean, default=False)
    lesson_id = db.Column('LessonId', db.BigInteger, db.ForeignKey('Lessons.Id'))
    time_limit_minutes = db.Column('TimeLimitMinutes', db.Integer, default=0)
    attempts_allowed = db.Column('AttemptsAllowed', db.Integer, default=1)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

    questions = db.relationship('Question', backref='test')
    attempts = db.relationship('TestAttempt', backref='test')

# ========================
# CÂU HỎI
# ========================
class Question(db.Model):
    __tablename__ = 'Questions'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    test_id = db.Column('TestId', db.BigInteger, db.ForeignKey('Tests.Id'), nullable=False)
    type = db.Column('Type', db.String(50), nullable=False, default='single_choice')
    content = db.Column('Content', db.Text, nullable=False)
    points = db.Column('Points', db.Integer, default=1)
    sort_order = db.Column('SortOrder', db.Integer, default=0)

    choices = db.relationship('Choice', backref='question')
    test_cases = db.relationship('QuestionTestCase', backref='question')
    answers = db.relationship('Answer', backref='question')
    code_submissions = db.relationship('CodeSubmission', backref='question')

# ========================
# LỰA CHỌN
# ========================
class Choice(db.Model):
    __tablename__ = 'Choices'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    question_id = db.Column('QuestionId', db.BigInteger, db.ForeignKey('Questions.Id'), nullable=False)
    content = db.Column('Content', db.Text, nullable=False)
    is_correct = db.Column('IsCorrect', db.Boolean, default=False)
    sort_order = db.Column('SortOrder', db.Integer, default=0)
    
    @property
    def text(self):
        """Alias for content to support both field names"""
        return self.content

# ========================
# TEST CASE CHO CÂU HỎI LẬP TRÌNH
# ========================
class QuestionTestCase(db.Model):
    __tablename__ = 'QuestionTestCases'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    question_id = db.Column('QuestionId', db.BigInteger, db.ForeignKey('Questions.Id'), nullable=False)
    input = db.Column('Input', db.Text)
    expected_output = db.Column('ExpectedOutput', db.Text)
    is_hidden = db.Column('IsHidden', db.Boolean, default=True)
    weight = db.Column('Weight', db.Integer, default=1)
    sort_order = db.Column('SortOrder', db.Integer, default=0)

# ========================
# LẦN LÀM BÀI
# ========================
class TestAttempt(db.Model):
    __tablename__ = 'TestAttempts'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    test_id = db.Column('TestId', db.BigInteger, db.ForeignKey('Tests.Id'), nullable=False)
    student_id = db.Column('StudentId', db.BigInteger, db.ForeignKey('Students.Id'), nullable=False)
    attempt_number = db.Column('AttemptNumber', db.Integer, default=1)
    start_time = db.Column('StartTime', db.DateTime(timezone=True), nullable=False)
    submit_time = db.Column('SubmitTime', db.DateTime(timezone=True))
    total_score = db.Column('TotalScore', db.Numeric(6, 2))
    suggested_level = db.Column('SuggestedLevel', db.String(50))
    ai_comment = db.Column('AIComment', db.Text)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

    code_submissions = db.relationship('CodeSubmission', backref='attempt')
    answers = db.relationship('Answer', backref='attempt')

# ========================
# NỘP CODE
# ========================
class CodeSubmission(db.Model):
    __tablename__ = 'CodeSubmissions'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    attempt_id = db.Column('AttemptId', db.BigInteger, db.ForeignKey('TestAttempts.Id'), nullable=False)
    question_id = db.Column('QuestionId', db.BigInteger, db.ForeignKey('Questions.Id'), nullable=False)
    submitted_code = db.Column('SubmittedCode', db.Text, nullable=False)
    language = db.Column('Language', db.String(50), default='python')
    execution_result = db.Column('ExecutionResult', db.Text)
    tests_passed = db.Column('TestsPassed', db.Integer, default=0)
    total_tests = db.Column('TotalTests', db.Integer, default=0)
    auto_score = db.Column('AutoScore', db.Numeric(6, 2))
    ai_feedback = db.Column('AIFeedback', db.Text)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

# ========================
# CÂU TRẢ LỜI
# ========================
class Answer(db.Model):
    __tablename__ = 'Answers'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    attempt_id = db.Column('AttemptId', db.BigInteger, db.ForeignKey('TestAttempts.Id'), nullable=False)
    question_id = db.Column('QuestionId', db.BigInteger, db.ForeignKey('Questions.Id'), nullable=False)
    choice_id = db.Column('ChoiceId', db.BigInteger, db.ForeignKey('Choices.Id'))
    answer_text = db.Column('AnswerText', db.Text)
    score_given = db.Column('ScoreGiven', db.Numeric(6, 2))

# ========================
# PHÂN TÍCH NĂNG LỰC AI
# ========================
class AIAbilityAnalysis(db.Model):
    __tablename__ = 'AIAbilityAnalysis'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column('StudentId', db.BigInteger, db.ForeignKey('Students.Id'), nullable=False)
    test_id = db.Column('TestId', db.BigInteger, db.ForeignKey('Tests.Id'), nullable=False)
    level = db.Column('Level', db.String(50))
    avg_score = db.Column('AvgScore', db.Numeric(6, 2))
    skill_scores = db.Column('SkillScores', db.Text)
    course_recommendation = db.Column('CourseRecommendation', db.Text)
    path_recommendation = db.Column('PathRecommendation', db.Text)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

# ========================
# KẾ HOẠCH HỌC TẬP
# ========================
class StudyPlan(db.Model):
    __tablename__ = 'StudyPlans'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    student_id = db.Column('StudentId', db.BigInteger, db.ForeignKey('Students.Id'), nullable=False)
    created_by = db.Column('CreatedBy', db.String(20), default='ai')
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

    plan_items = db.relationship('PlanItem', backref='plan')

# ========================
# CHI TIẾT KẾ HOẠCH
# ========================
class PlanItem(db.Model):
    __tablename__ = 'PlanItems'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    plan_id = db.Column('PlanId', db.BigInteger, db.ForeignKey('StudyPlans.Id'), nullable=False)
    course_id = db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'))
    lesson_id = db.Column('LessonId', db.BigInteger, db.ForeignKey('Lessons.Id'))
    target_level = db.Column('TargetLevel', db.String(50))
    deadline = db.Column('Deadline', db.Date)
    sort_order = db.Column('SortOrder', db.Integer, default=0)
    status = db.Column('Status', db.String(50), default='not_started')

# ========================
# TIN NHẮN
# ========================
class Message(db.Model):
    __tablename__ = 'Messages'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    channel = db.Column('Channel', db.String(20), default='direct')
    from_user_id = db.Column('FromUserId', db.BigInteger, db.ForeignKey('Users.Id'), nullable=False)
    to_user_id = db.Column('ToUserId', db.BigInteger, db.ForeignKey('Users.Id'))
    course_id = db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'))
    lesson_id = db.Column('LessonId', db.BigInteger, db.ForeignKey('Lessons.Id'))
    content = db.Column('Content', db.Text, nullable=False)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)
    read_at = db.Column('ReadAt', db.DateTime(timezone=True))

# ========================
# HÓA ĐƠN
# ========================
class Invoice(db.Model):
    __tablename__ = 'Invoices'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    invoice_number = db.Column('InvoiceNumber', db.String(40), unique=True, nullable=False)
    student_id = db.Column('StudentId', db.BigInteger, db.ForeignKey('Students.Id'), nullable=False)
    course_id = db.Column('CourseId', db.BigInteger, db.ForeignKey('Courses.Id'), nullable=False)
    amount = db.Column('Amount', db.Numeric(12, 2), nullable=False)
    currency = db.Column('Currency', db.String(3), default='VND')
    payment_method = db.Column('PaymentMethod', db.String(20), default='online')
    payment_status = db.Column('PaymentStatus', db.String(20), default='pending')
    reference_code = db.Column('ReferenceCode', db.String(120))
    issued_at = db.Column('IssuedAt', db.DateTime(timezone=True), nullable=False)
    paid_at = db.Column('PaidAt', db.DateTime(timezone=True))
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

# ========================
# PHIÊN CHAT AI
# ========================
class AIChatSession(db.Model):
    __tablename__ = 'AIChatSessions'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'), nullable=False)
    session_type = db.Column('SessionType', db.String(100), default='general_ai_chat')
    description = db.Column('Description', db.Text)
    status = db.Column('Status', db.String(50), default='active')
    message_count = db.Column('MessageCount', db.Integer, default=0)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column('UpdatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

    messages = db.relationship('AIChatMessage', backref='session')

# ========================
# TIN NHẮN CHAT AI
# ========================
class AIChatMessage(db.Model):
    __tablename__ = 'AIChatMessages'

    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column('SessionId', db.BigInteger, db.ForeignKey('AIChatSessions.Id'), nullable=False)
    sent_by = db.Column('SentBy', db.String(20), default='user')
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'))
    content = db.Column('Content', db.Text, nullable=False)
    message_type = db.Column('MessageType', db.String(50), default='text')
    emotion = db.Column('Emotion', db.String(50))
    tokens_used = db.Column('TokensUsed', db.Integer, default=0)
    sent_at = db.Column('SentAt', db.DateTime(timezone=True), default=datetime.utcnow)
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)

