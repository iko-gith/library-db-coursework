import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import config
from src.models import Base, Edition, Author, Reader, Loan, BookCopy

def test_connection():
    engine       = create_engine(config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session      = SessionLocal()

    try:
        editions_count = session.query(Edition).count()
        print(f"Изданий в базе: {editions_count}")

        readers_count = session.query(Reader).count()
        print(f"Читателей в базе: {readers_count}")

        loans_count = session.query(Loan).count()
        print(f"Записей о выдачах книг: {loans_count}")

        print("\nАвторы и книги:")
        authors = session.query(Author).all()
        for author in authors:
            book_titles = [e.title for e in author.editions]
            print(f"- {author.last_name} {author.first_name}: {', '.join(book_titles) if book_titles else 'нет книг'}")

        latest_loan = session.query(Loan).order_by(Loan.id.desc()).first()
        if latest_loan:
            print("\nПоследняя выдачи из базы:")
            print(f"- ID выдачи:               {latest_loan.id}")
            print(f"- Дата выдачи:             {latest_loan.issue_date}")
            print(f"- Срок возврата:           {latest_loan.due_date}")
            print(f"- Читатель (ID билета):    {latest_loan.library_card.card_number}")
            print(f"- Инвентарный номер книги: {latest_loan.book_copy.inventory_number}")
            print(f"- Статус возврата:         {'Возвращена (' + str(latest_loan.return_date) + ')'
                                                if latest_loan.return_date else 'На руках'}")

    except Exception as e:
        print(f"Ошибка при проверке: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_connection()
