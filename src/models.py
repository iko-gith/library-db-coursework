from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, CheckConstraint, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Publisher(Base):
    """Издательство"""
    __tablename__ = 'publisher'

    id   = Column(Integer,     primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)

    editions = relationship("Edition", back_populates="publisher", cascade="all, delete-orphan")


class Author(Base):
    """Автор"""
    __tablename__ = 'author'

    id          = Column(Integer,     primary_key=True, autoincrement=True)
    last_name   = Column(String(100), nullable=False)
    first_name  = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)

    editions = relationship("Edition", secondary="edition_author", back_populates="authors")


class Edition(Base):
    """Издание"""
    __tablename__ = 'edition'

    id           = Column(Integer,     primary_key=True, autoincrement=True)
    title        = Column(String(255), nullable=False)
    publish_year = Column(Integer,     nullable=False)
    publisher_id = Column(Integer,     ForeignKey('publisher.id', ondelete='RESTRICT'), nullable=False)

    publisher    = relationship("Publisher", back_populates="editions")
    authors      = relationship("Author",      secondary="edition_author", back_populates="editions")
    copies       = relationship("BookCopy",    back_populates="edition", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="edition", cascade="all, delete-orphan")


from sqlalchemy import Table
edition_author = Table(
    'edition_author',
    Base.metadata,
    Column('edition_id', Integer, ForeignKey('edition.id', ondelete='CASCADE'), primary_key=True),
    Column('author_id',  Integer, ForeignKey('author.id', ondelete='CASCADE'), primary_key=True)
)


class StorageLocation(Base):
    """Место хранения"""
    __tablename__ = 'storage_location'

    id    = Column(Integer,    primary_key=True, autoincrement=True)
    hall  = Column(String(50), nullable=False)
    rack  = Column(String(50), nullable=False)
    shelf = Column(String(50), nullable=False)

    copies = relationship("BookCopy", back_populates="storage_location")


class Supplier(Base):
    """Поставщик"""
    __tablename__ = 'supplier'

    id    = Column(Integer,     primary_key=True, autoincrement=True)
    name  = Column(String(255), nullable=False)
    inn   = Column(String(12),  unique=True, nullable=False)
    phone = Column(String(20),  nullable=False)

    supplies = relationship("Supply", back_populates="supplier", cascade="all, delete-orphan")


class Supply(Base):
    """Поступление"""
    __tablename__ = 'supply'

    id           = Column(Integer,        primary_key=True, autoincrement=True)
    doc_number   = Column(String(50),     nullable=False)
    supply_date  = Column(Date,           nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    supplier_id  = Column(Integer,        ForeignKey('supplier.id', ondelete='RESTRICT'), nullable=False)

    supplier = relationship("Supplier", back_populates="supplies")
    copies   = relationship("BookCopy", back_populates="supply")


class BookCopy(Base):
    """Экземпляр (физ. копия)"""
    __tablename__ = 'book_copy'

    id               = Column(Integer,        primary_key=True, autoincrement=True)
    inventory_number = Column(String(100),    unique=True, nullable=False)
    status           = Column(String(30),     nullable=False, default='в фонде')
    price            = Column(Numeric(10, 2), nullable=False)
    
    edition_id          = Column(Integer, ForeignKey('edition.id', ondelete='RESTRICT'), nullable=False)
    storage_location_id = Column(Integer, ForeignKey('storage_location.id', ondelete='RESTRICT'), nullable=False)
    supply_id           = Column(Integer, ForeignKey('supply.id', ondelete='RESTRICT'), nullable=False)

    edition          = relationship("Edition", back_populates="copies")
    storage_location = relationship("StorageLocation", back_populates="copies")
    supply           = relationship("Supply", back_populates="copies")
    loans            = relationship("Loan", back_populates="book_copy", cascade="all, delete-orphan")


class Reader(Base):
    """Читатель"""
    __tablename__ = 'reader'

    id        = Column(Integer,     primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    phone     = Column(String(20),  nullable=False)
    email     = Column(String(100), nullable=True)

    library_card = relationship("LibraryCard", back_populates="reader", uselist=False, cascade="all, delete-orphan")


class LibraryCard(Base):
    """Читательский билет"""
    __tablename__ = 'library_card'

    id          = Column(Integer,    primary_key=True, autoincrement=True)
    card_number = Column(String(50), unique=True, nullable=False)
    issue_date  = Column(Date,       nullable=False)
    expiry_date = Column(Date,       nullable=False)
    reader_id   = Column(Integer,    ForeignKey('reader.id', ondelete='CASCADE'), unique=True, nullable=False)

    reader       = relationship("Reader",      back_populates="library_card")
    loans        = relationship("Loan",        back_populates="library_card", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="library_card", cascade="all, delete-orphan")


class Employee(Base):
    """Сотрудник"""
    __tablename__ = 'employee'

    id        = Column(Integer,     primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    position  = Column(String(100), nullable=False)

    loans = relationship("Loan", back_populates="employee")


class Loan(Base):
    """Выдача"""
    __tablename__ = 'loan'

    id          = Column(Integer, primary_key=True, autoincrement=True)
    issue_date  = Column(Date,    nullable=False)
    due_date    = Column(Date,    nullable=False)
    return_date = Column(Date,    nullable=True)

    book_copy_id    = Column(Integer, ForeignKey('book_copy.id', ondelete='RESTRICT'), nullable=False)
    library_card_id = Column(Integer, ForeignKey('library_card.id', ondelete='RESTRICT'), nullable=False)
    employee_id     = Column(Integer, ForeignKey('employee.id', ondelete='RESTRICT'), nullable=False)

    book_copy    = relationship("BookCopy",    back_populates="loans")
    library_card = relationship("LibraryCard", back_populates="loans")
    employee     = relationship("Employee",    back_populates="loans")
    fines        = relationship("Fine",        back_populates="loan", cascade="all, delete-orphan")


class Reservation(Base):
    """Бронирование"""
    __tablename__ = 'reservation'

    id               = Column(Integer,    primary_key=True, autoincrement=True)
    reservation_date = Column(Date,       nullable=False)
    valid_until      = Column(Date,       nullable=False)
    status           = Column(String(30), nullable=False, default='активна')

    library_card_id = Column(Integer, ForeignKey('library_card.id', ondelete='CASCADE'), nullable=False)
    edition_id      = Column(Integer, ForeignKey('edition.id', ondelete='CASCADE'), nullable=False)

    library_card = relationship("LibraryCard", back_populates="reservations")
    edition      = relationship("Edition", back_populates="reservations")


class Fine(Base):
    """Штраф"""
    __tablename__ = 'fine'

    id           = Column(Integer,        primary_key=True, autoincrement=True)
    reason       = Column(String(255),    nullable=False)
    amount       = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date,           nullable=True)

    loan_id = Column(Integer, ForeignKey('loan.id', ondelete='CASCADE'), nullable=False)

    loan = relationship("Loan", back_populates="fines")

class AppUser(Base):
    """Учетная запись пользователя"""
    __tablename__ = 'app_user'

    id            = Column(Integer,     primary_key=True, autoincrement=True)
    username      = Column(String(100), unique=True,      nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(50),  nullable=False)
    employee_id   = Column(Integer,     ForeignKey('employee.id', ondelete='CASCADE'), nullable=True)
    reader_id     = Column(Integer,     ForeignKey('reader.id', ondelete='CASCADE'), nullable=True)
