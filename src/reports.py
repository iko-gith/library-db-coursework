import sys
from pathlib import Path
import csv
import json
from datetime import datetime
from sqlalchemy import create_engine, func, desc, case
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.config import config
from src.models import Loan, BookCopy, Edition, Reader, LibraryCard, Fine, Supplier, Supply, StorageLocation

class LibraryReports:
    def __init__(self):
        engine       = create_engine(config.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        self.session = SessionLocal()

    def close(self):
        self.session.close()

    def _get_header(self, report_name: str, params: dict = None):
        return {
            "report_name":  report_name,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "parameters":   params or {},
            "generated_by": "Системный администратор / Библиотекарь"
        }

    def report_debtors(self, export_format=None):
        today = datetime.now().date()
        results = (
            self.session.query(
                Loan.id,
                Reader.full_name,
                Reader.phone,
                Edition.title,
                Loan.due_date,
                (today - Loan.due_date).label('days_overdue')
            )
            .join(LibraryCard,                Loan.library_card_id == LibraryCard.id)
            .join(Reader,                     LibraryCard.reader_id == Reader.id)
            .join(BookCopy,                   Loan.book_copy_id == BookCopy.id)
            .join(Edition,                    BookCopy.edition_id == Edition.id)
            .filter(Loan.return_date == None, Loan.due_date < today)
            .all()
        )

        data = [
            {
                "loan_id":      r.id,
                "reader_name":  r.full_name,
                "phone":        r.phone,
                "book_title":   r.title,
                "due_date":     str(r.due_date),
                "days_overdue": r.days_overdue
            }
            for r in results
        ]
        
        report = {"header": self._get_header("Список должников"), "data": data}
        return self._export(report, "debtors", export_format)

    def report_popular_editions(self, limit=10, export_format=None):
        results = (
            self.session.query(
                Edition.title,
                func.count(Loan.id).label('loan_count')
            )
            .join(BookCopy, BookCopy.edition_id == Edition.id)
            .join(Loan,     Loan.book_copy_id == BookCopy.id)
            .group_by(Edition.id, Edition.title)
            .order_by(desc('loan_count'))
            .limit(limit)
            .all()
        )

        data   = [{"title": r.title, "loan_count": r.loan_count} for r in results]
        report = {"header": self._get_header(f"Топ {limit} востребованных изданий", {"limit": limit}), "data": data}
        return self._export(report, "popular_editions", export_format)

    def report_storage_load(self, export_format=None):
        results = (
            self.session.query(
                StorageLocation.hall,
                StorageLocation.rack,
                StorageLocation.shelf,
                func.count(BookCopy.id).label('total_copies'),
                func.sum(case((BookCopy.status == 'выдан', 1), else_=0)).label('issued_copies')
            )
            .outerjoin(BookCopy,          BookCopy.storage_location_id == StorageLocation.id)
            .group_by(StorageLocation.id, StorageLocation.hall, StorageLocation.rack, StorageLocation.shelf)
            .all()
        )

        data = [
            {
                "hall":          r.hall,
                "rack":          r.rack,
                "shelf":         r.shelf,
                "total_copies":  r.total_copies or 0,
                "issued_copies": int(r.issued_copies or 0),
                "free_copies":   (r.total_copies or 0) - int(r.issued_copies or 0)
            }
            for r in results
        ]
        report = {"header": self._get_header("Загруженность фонда по местам хранения"), "data": data}
        return self._export(report, "storage_load", export_format)

    def report_supplies_by_supplier(self, export_format=None):
        results = (
            self.session.query(
                Supplier.name,
                func.count(Supply.id).label('supply_count'),
                func.sum(Supply.total_amount).label('total_sum')
            )
            .join(Supply, Supply.supplier_id == Supplier.id)
            .group_by(Supplier.id, Supplier.name)
            .all()
        )

        data = [
            {
                "supplier_name": r.name,
                "supply_count":  r.supply_count,
                "total_sum":     float(r.total_sum or 0)
            }
            for r in results
        ]
        report = {"header": self._get_header("Поступления по поставщикам"), "data": data}
        return self._export(report, "supplies_by_supplier", export_format)

    def report_reader_history(self, card_number: str, export_format=None):
        results = (
            self.session.query(
                Loan.issue_date,
                Loan.due_date,
                Loan.return_date,
                Edition.title,
                BookCopy.inventory_number
            )
            .join(LibraryCard, Loan.library_card_id == LibraryCard.id)
            .join(BookCopy,    Loan.book_copy_id == BookCopy.id)
            .join(Edition,     BookCopy.edition_id == Edition.id)
            .filter(LibraryCard.card_number == card_number)
            .all()
        )

        data = [
            {
                "issue_date":       str(r.issue_date),
                "due_date":         str(r.due_date),
                "return_date":      str(r.return_date) if r.return_date else "Не возвращена",
                "book_title":       r.title,
                "inventory_number": r.inventory_number
            }
            for r in results
        ]
        report = {"header": self._get_header("История выдач читателя", {"card_number": card_number}), "data": data}
        return self._export(report, f"reader_history_{card_number}", export_format)

    def _export(self, report_dict, filename_prefix, export_format):
        if export_format == 'json':
            filename = f"{filename_prefix}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, ensure_ascii=False, indent=4)
            print(f"Отчет сохранен в JSON: {filename}")
            return filename

        elif export_format == 'csv':
            filename = f"{filename_prefix}.csv"
            if not report_dict["data"]:
                print(f"Отчет {filename_prefix} пуст")
                return None
            
            keys = report_dict["data"][0].keys()
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(report_dict["data"])
            print(f"Отчет сохранен в CSV: {filename}")
            return filename
        
        return report_dict

if __name__ == "__main__":
    rep = LibraryReports()
    rep.report_debtors(export_format='json')
    rep.report_popular_editions(limit=5, export_format='csv')
    rep.report_storage_load(export_format='json')
    rep.report_supplies_by_supplier(export_format='json')
    rep.report_reader_history(card_number='1', export_format='json')

    rep.close()
