from passlib.context import CryptContext
from database import SessionLocal, engine
from models import (
    Base,
    User,
    Employer,
    Faculty,
    Category,
    Skill,
    Vacancy,
    VacancySkill,
    ApplicationStatus,
)

# начальные данные для демонстрации

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_database(db):
    # не засеиваем повторно
    if db.query(User).count() > 0:
        return

    # факультеты
    faculties = [
        Faculty(name="Информатика и вычислительная техника"),
        Faculty(name="Экономика и управление"),
        Faculty(name="Юриспруденция"),
        Faculty(name="Менеджмент"),
    ]
    db.add_all(faculties)
    db.flush()

    # категории вакансий
    categories = [
        Category(name="IT и разработка"),
        Category(name="Административная работа"),
        Category(name="Исследования"),
        Category(name="Преподавание"),
        Category(name="Стажировка"),
    ]
    db.add_all(categories)
    db.flush()

    # навыки
    skills = [
        Skill(name="Python"),
        Skill(name="Excel"),
        Skill(name="Word"),
        Skill(name="Английский язык"),
        Skill(name="Коммуникации"),
        Skill(name="Аналитика"),
        Skill(name="Программирование"),
        Skill(name="Дизайн"),
    ]
    db.add_all(skills)
    db.flush()

    # статусы заявок
    statuses = [
        ApplicationStatus(name="На рассмотрении"),
        ApplicationStatus(name="Просмотрено"),
        ApplicationStatus(name="Принято"),
        ApplicationStatus(name="Отклонено"),
    ]
    db.add_all(statuses)
    db.flush()

    # пользователи-работодатели
    employer_users = [
        User(
            email="techstart@company.ru",
            hashed_password=pwd_context.hash("password123"),
            name="ООО ТехноСтарт",
            role="employer",
        ),
        User(
            email="dekanat@uni.ru",
            hashed_password=pwd_context.hash("password123"),
            name="Деканат ФИТ",
            role="employer",
        ),
        User(
            email="research@uni.ru",
            hashed_password=pwd_context.hash("password123"),
            name="Исследовательский центр",
            role="employer",
        ),
    ]
    db.add_all(employer_users)
    db.flush()

    # профили работодателей
    employers = [
        Employer(
            user_id=employer_users[0].id,
            company_name="ООО ТехноСтарт",
            description="IT-компания, разрабатываем мобильные приложения и веб-сервисы",
            website="https://techstart.ru",
        ),
        Employer(
            user_id=employer_users[1].id,
            company_name="Деканат факультета информатики",
            description="Административный отдел факультета информационных технологий",
        ),
        Employer(
            user_id=employer_users[2].id,
            company_name="Исследовательский центр университета",
            description="Проводим научные исследования в области математики и информатики",
        ),
    ]
    db.add_all(employers)
    db.flush()

    # вакансии
    vacancies_data = [
        dict(
            employer_id=employers[0].id,
            category_id=categories[0].id,
            title="Стажёр Python-разработчик",
            description="Ищем студента 3-4 курса для стажировки в команду бэкенд-разработки. "
            "Будешь работать с FastAPI, SQLAlchemy, PostgreSQL. "
            "Гибкий график, возможность совмещать с учёбой.",
            employment_type="internship",
            salary_from=15000,
            salary_to=25000,
            skill_ids=[0, 6],  # Python, Программирование
        ),
        dict(
            employer_id=employers[0].id,
            category_id=categories[0].id,
            title="Помощник frontend-разработчика",
            description="Требуется студент для помощи в разработке пользовательских интерфейсов. "
            "Знание HTML, CSS, JavaScript приветствуется. Обучение на месте.",
            employment_type="part_time",
            salary_from=12000,
            salary_to=18000,
            skill_ids=[6, 7],  # Программирование, Дизайн
        ),
        dict(
            employer_id=employers[1].id,
            category_id=categories[1].id,
            title="Помощник секретаря деканата",
            description="Помощь в оформлении документов, работа с базами данных студентов, "
            "приём посетителей. Частичная занятость, 4 часа в день.",
            employment_type="part_time",
            salary_from=10000,
            salary_to=12000,
            skill_ids=[1, 2, 4],  # Excel, Word, Коммуникации
        ),
        dict(
            employer_id=employers[1].id,
            category_id=categories[3].id,
            title="Ассистент преподавателя по математике",
            description="Проверка домашних заданий студентов первого курса, "
            "помощь на практических занятиях. Требуется отличное знание математического анализа.",
            employment_type="part_time",
            salary_from=8000,
            salary_to=10000,
            skill_ids=[4, 5],  # Коммуникации, Аналитика
        ),
        dict(
            employer_id=employers[2].id,
            category_id=categories[2].id,
            title="Исследовательский стажёр — машинное обучение",
            description="Участие в научном проекте по разработке алгоритмов классификации данных. "
            "Публикация результатов в журнале. Требуется знание Python и основ ML.",
            employment_type="internship",
            salary_from=20000,
            salary_to=30000,
            skill_ids=[0, 5, 6],  # Python, Аналитика, Программирование
        ),
        dict(
            employer_id=employers[2].id,
            category_id=categories[2].id,
            title="Лаборант кафедры информатики",
            description="Техническое обслуживание компьютерного класса, помощь преподавателям "
            "в организации лабораторных работ.",
            employment_type="part_time",
            salary_from=9000,
            salary_to=11000,
            skill_ids=[1, 6],  # Excel, Программирование
        ),
        dict(
            employer_id=employers[0].id,
            category_id=categories[4].id,
            title="Стажёр по тестированию ПО",
            description="Ручное тестирование веб-приложений, написание тест-кейсов, "
            "работа с баг-трекером. Отличный старт для начинающих QA-инженеров.",
            employment_type="internship",
            salary_from=15000,
            salary_to=20000,
            skill_ids=[5, 4],  # Аналитика, Коммуникации
        ),
        dict(
            employer_id=employers[1].id,
            category_id=categories[1].id,
            title="Оператор базы данных",
            description="Ввод и обработка данных в системе управления учебным процессом. "
            "Работа с Excel-таблицами, формирование отчётов.",
            employment_type="full_time",
            salary_from=18000,
            salary_to=22000,
            skill_ids=[1, 2],  # Excel, Word
        ),
        dict(
            employer_id=employers[2].id,
            category_id=categories[2].id,
            title="Аналитик данных (стажёр)",
            description="Обработка и анализ результатов социологических исследований. "
            "Подготовка аналитических отчётов, визуализация данных.",
            employment_type="internship",
            salary_from=16000,
            salary_to=24000,
            skill_ids=[1, 3, 5],  # Excel, Английский, Аналитика
        ),
        dict(
            employer_id=employers[0].id,
            category_id=categories[0].id,
            title="Разработчик мобильных приложений (практика)",
            description="Разработка функций для Android-приложения компании. "
            "Работа с Kotlin или Java, знание основ мобильной разработки.",
            employment_type="internship",
            salary_from=20000,
            salary_to=35000,
            skill_ids=[6, 0],  # Программирование, Python
        ),
    ]

    skill_objects = db.query(Skill).all()

    for v_data in vacancies_data:
        skill_ids = v_data.pop("skill_ids")
        vacancy = Vacancy(**v_data)
        db.add(vacancy)
        db.flush()

        for sid in skill_ids:
            if sid < len(skill_objects):
                vs = VacancySkill(vacancy_id=vacancy.id, skill_id=skill_objects[sid].id)
                db.add(vs)

    db.commit()
    print("База данных заполнена начальными данными")


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()
