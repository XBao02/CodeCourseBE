from app import create_app
from app.utils.seed import seed_default_instructor
from app.models import db
from app.models.model import Course, Instructor


def slugify(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
        .replace(",", "")
        .replace(".", "")
    )


def build_course_entries():
    languages = [
        "python",
        "javascript",
        "java",
        "typescript",
        "c",
        "cpp",
        "csharp",
        "go",
        "rust",
        "php",
        "ruby",
        "kotlin",
        "swift",
        "web_frontend",
        "react",
        "vue",
        "angular",
        "svelte",
        "nodejs",
        "django",
        "flask",
        "laravel",
        "android",
        "ios",
        "flutter",
        "sql",
        "machine_learning",
        "deep_learning",
        "data_analysis",
        "devops",
        "cloud",
    ]

    meta = {
        "python": "Python",
        "javascript": "JavaScript",
        "java": "Java",
        "typescript": "TypeScript",
        "c": "C",
        "cpp": "C++",
        "csharp": "C#",
        "go": "Go",
        "rust": "Rust",
        "php": "PHP",
        "ruby": "Ruby",
        "kotlin": "Kotlin",
        "swift": "Swift",
        "web_frontend": "Web Frontend",
        "react": "React",
        "vue": "Vue.js",
        "angular": "Angular",
        "svelte": "Svelte",
        "nodejs": "Node.js",
        "django": "Django",
        "flask": "Flask",
        "laravel": "Laravel",
        "android": "Android",
        "ios": "iOS",
        "flutter": "Flutter",
        "sql": "SQL",
        "machine_learning": "Machine Learning",
        "deep_learning": "Deep Learning",
        "data_analysis": "Data Analysis",
        "devops": "DevOps",
        "cloud": "Cloud",
    }

    beginner_templates = [
        "{label} Basics",
        "Introduction to {label}",
        "{label} Fundamentals",
        "{label} Starter Kit",
        "{label} Essentials",
    ]
    intermediate_templates = [
        "Advanced {label} Programming",
        "{label} Deep Concepts",
        "{label} Performance Techniques",
    ]
    advanced_templates = [
        "{label} Mastery",
        "{label} Expert Techniques",
    ]

    descriptions = {
        "beginner": (
            "Khóa học giúp bạn làm quen với các khái niệm cốt lõi của {label}, từ cú pháp cơ bản đến cấu trúc chương trình đầu tiên."
        ),
        "intermediate": (
            "Đào sâu những mô hình nâng cao và best practice để xây dựng ứng dụng {label} hiệu quả hơn."
        ),
        "advanced": (
            "Thực hành các kỹ thuật chuyên sâu, tối ưu và mở rộng quy mô cho các dự án {label} lớn."
        ),
    }

    courses = []
    for lang in languages:
        label = meta.get(lang, lang.replace("_", " ").title())
        for template in beginner_templates:
            title = template.format(label=label)
            courses.append(
                {
                    "title": title,
                    "description": descriptions["beginner"].format(label=label),
                    "level": "beginner",
                    "language": lang,
                    "slug": slugify(title),
                }
            )
        for template in intermediate_templates:
            title = template.format(label=label)
            courses.append(
                {
                    "title": title,
                    "description": descriptions["intermediate"].format(label=label),
                    "level": "intermediate",
                    "language": lang,
                    "slug": slugify(title),
                }
            )
        for template in advanced_templates:
            title = template.format(label=label)
            courses.append(
                {
                    "title": title,
                    "description": descriptions["advanced"].format(label=label),
                    "level": "advanced",
                    "language": lang,
                    "slug": slugify(title),
                }
            )

    return courses


def seed_courses():
    seed_default_instructor()
    instructor = Instructor.query.first()
    if not instructor:
        return
    courses_data = build_course_entries()
    for data in courses_data:
        if Course.query.filter_by(slug=data["slug"]).first():
            continue
        course = Course(
            instructor_id=instructor.id,
            title=data["title"],
            description=data["description"],
            level=data["level"],
            language=data["language"],
            slug=data["slug"],
            image_url="https://placehold.co/600x400",
            price=0,
            currency="USD",
            is_public=True,
        )
        db.session.add(course)
    db.session.commit()


def run():
    app = create_app()
    with app.app_context():
        seed_courses()


if __name__ == "__main__":
    run()
