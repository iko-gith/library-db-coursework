import sys
from pathlib import Path
import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.config import config

fake = Faker('ru_RU')

def generate_test_data():
    conn = psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )
    cursor = conn.cursor()

    print("Генерация тестовых данных")

    try:
        # 1. Читатели
        print(f"Создание {config.NUM_READERS} читателей...")
        reader_ids = []
        for _ in range(config.NUM_READERS):
            full_name = fake.name()
            phone = fake.phone_number()
            email = fake.email()

            cursor.execute(
                "INSERT INTO reader (full_name, phone, email) VALUES (%s, %s, %s) RETURNING id;",
                (full_name, phone, email)
            )
            r_id = cursor.fetchone()[0]
            reader_ids.append(r_id)

            card_number = f"CARD-2026-{fake.unique.random_number(digits=5, fix_len=True)}"
            issue_date = fake.date_between(start_date='-1y', end_date='today')
            expiry_date = issue_date + timedelta(days=365)

            cursor.execute(
                """INSERT INTO library_card (card_number, issue_date, expiry_date, reader_id)
                   VALUES (%s, %s, %s, %s);""",
                (card_number, issue_date, expiry_date, r_id)
            )

        cursor.execute("SELECT id FROM book_copy;")
        book_copy_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM employee;")
        employee_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM library_card;")
        card_ids = [row[0] for row in cursor.fetchall()]

        cursor.execute("SELECT id FROM edition;")
        edition_ids = [row[0] for row in cursor.fetchall()]

        if not book_copy_ids or not employee_ids or not card_ids:
            print("Ошибка: Сначала выполните data.sql, чтобы в базе были книги, сотрудники и билеты!")
            return


        print(f"Генерация выдач ({config.NUM_LOANS} записей)...")
        for _ in range(config.NUM_LOANS):
            issue_date = fake.date_between(start_date='-6m', end_date='today')
            due_date = issue_date + timedelta(days=config.DEFAULT_LOAN_DAYS)

            is_returned = random.choice([True, True, False])
            return_date = None
            if is_returned:
                return_date = issue_date + timedelta(days=random.randint(5, 25))

            book_copy_id = random.choice(book_copy_ids)
            card_id = random.choice(card_ids)
            employee_id = random.choice(employee_ids)

            cursor.execute(
                """INSERT INTO loan (issue_date, due_date, return_date, book_copy_id, library_card_id, employee_id)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;""",
                (issue_date, due_date, return_date, book_copy_id, card_id, employee_id)
            )
            loan_id = cursor.fetchone()[0]

            if return_date and return_date > due_date:
                days_late = (return_date - due_date).days
                fine_amount = days_late * config.FINE_RATE_PER_DAY
                cursor.execute(
                    """INSERT INTO fine (reason, amount, payment_date, loan_id)
                       VALUES (%s, %s, %s, %s);""",
                    ("Просрочка возврата книги", fine_amount, return_date, loan_id)
                )


        print(f"Генерация бронирований ({config.NUM_RESERVATIONS} записей)...")
        statuses = ['активна', 'выполнена', 'отменена', 'истекла']
        for _ in range(config.NUM_RESERVATIONS):
            res_date = fake.date_between(start_date='-6m', end_date='today')
            valid_until = res_date + timedelta(days=3)
            status = random.choice(statuses)
            card_id = random.choice(card_ids)
            edition_id = random.choice(edition_ids)

            cursor.execute(
                """INSERT INTO reservation (reservation_date, valid_until, status, library_card_id, edition_id)
                   VALUES (%s, %s, %s, %s, %s);""",
                (res_date, valid_until, status, card_id, edition_id)
            )

        conn.commit()
        print("Успешно сгенерировано")

    except Exception as e:
        conn.rollback()
        print(f"Ошибка при генерации данных\n {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    generate_test_data()
