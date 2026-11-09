


DROP TABLE IF EXISTS publisher CASCADE;
CREATE TABLE publisher (
    id   SERIAL       PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS author CASCADE;
CREATE TABLE author (
    id          SERIAL       PRIMARY KEY,
    last_name   VARCHAR(100) NOT NULL,
    first_name  VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100)
);

DROP TABLE IF EXISTS edition CASCADE;
CREATE TABLE edition (
    id           SERIAL       PRIMARY KEY,
    title        VARCHAR(255) NOT NULL,
    publish_year INT          NOT NULL 
                 CHECK (publish_year > 1400 
                    AND publish_year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    publisher_id INT          NOT NULL 
                 REFERENCES publisher(id) 
                 ON DELETE RESTRICT
);
CREATE INDEX idx_edition_publisher ON edition(publisher_id);

DROP TABLE IF EXISTS edition_author CASCADE;
CREATE TABLE edition_author (
    edition_id INT NOT NULL 
               REFERENCES edition(id) 
               ON DELETE CASCADE,
    author_id  INT NOT NULL 
               REFERENCES author(id) 
               ON DELETE CASCADE,
    PRIMARY KEY (edition_id, author_id)
);
CREATE INDEX idx_edition_author_edition ON edition_author(edition_id);
CREATE INDEX idx_edition_author_author  ON edition_author(author_id);

DROP TABLE IF EXISTS storage_location CASCADE;
CREATE TABLE storage_location (
    id    SERIAL      PRIMARY KEY,
    hall  VARCHAR(50) NOT NULL,
    rack  VARCHAR(50) NOT NULL,
    shelf VARCHAR(50) NOT NULL
);

DROP TABLE IF EXISTS supplier CASCADE;
CREATE TABLE supplier (
    id    SERIAL       PRIMARY KEY,
    name  VARCHAR(255) NOT NULL,
    inn   VARCHAR(12)  NOT NULL UNIQUE,
    phone VARCHAR(20)  NOT NULL
);

DROP TABLE IF EXISTS supply CASCADE;
CREATE TABLE supply (
    id           SERIAL         PRIMARY KEY,
    doc_number   VARCHAR(50)    NOT NULL,
    supply_date  DATE           NOT NULL 
                 DEFAULT CURRENT_DATE,
    total_amount NUMERIC(12, 2) NOT NULL 
                 CHECK (total_amount >= 0),
    supplier_id  INT            NOT NULL 
                 REFERENCES supplier(id) 
                 ON DELETE RESTRICT
);
CREATE INDEX idx_supply_supplier ON supply(supplier_id);

DROP TABLE IF EXISTS book_copy CASCADE;
CREATE TABLE book_copy (
    id                  SERIAL         PRIMARY KEY,
    inventory_number    VARCHAR(100)   NOT NULL UNIQUE,
    status              VARCHAR(30)    NOT NULL 
                        DEFAULT 'в фонде' 
                        CHECK (status IN ('в фонде', 'выдан', 'утрачен', 'списан')),
    price               NUMERIC(10, 2) NOT NULL 
                        CHECK (price >= 0),
    edition_id          INT            NOT NULL 
                        REFERENCES edition(id) 
                        ON DELETE RESTRICT,
    storage_location_id INT            NOT NULL 
                        REFERENCES storage_location(id) 
                        ON DELETE RESTRICT,
    supply_id           INT            NOT NULL 
                        REFERENCES supply(id) 
                        ON DELETE RESTRICT
);
CREATE INDEX idx_book_copy_edition ON book_copy(edition_id);
CREATE INDEX idx_book_copy_location ON book_copy(storage_location_id);
CREATE INDEX idx_book_copy_supply ON book_copy(supply_id);

DROP TABLE IF EXISTS reader CASCADE;
CREATE TABLE reader (
    id        SERIAL       PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone     VARCHAR(20)  NOT NULL,
    email     VARCHAR(100)
);

DROP TABLE IF EXISTS library_card CASCADE;
CREATE TABLE library_card (
    id          SERIAL      PRIMARY KEY,
    card_number VARCHAR(50) NOT NULL UNIQUE,
    issue_date  DATE        NOT NULL 
                DEFAULT CURRENT_DATE,
    expiry_date DATE        NOT NULL,
    reader_id   INT         NOT NULL UNIQUE 
                REFERENCES reader(id) 
                ON DELETE CASCADE,
    CONSTRAINT check_expiry_date CHECK (expiry_date > issue_date)
);
CREATE INDEX idx_library_card_reader ON library_card(reader_id);

DROP TABLE IF EXISTS employee CASCADE;
CREATE TABLE employee (
    id        SERIAL       PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    position  VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS loan CASCADE;
CREATE TABLE loan (
    id              SERIAL PRIMARY KEY,
    issue_date      DATE   NOT NULL 
                    DEFAULT CURRENT_DATE,
    due_date        DATE   NOT NULL,
    return_date     DATE,
    book_copy_id    INT    NOT NULL 
                    REFERENCES book_copy(id) 
                    ON DELETE RESTRICT,
    library_card_id INT    NOT NULL 
                    REFERENCES library_card(id) 
                    ON DELETE RESTRICT,
    employee_id     INT    NOT NULL 
                    REFERENCES employee(id) 
                    ON DELETE RESTRICT,
    CONSTRAINT check_return_date CHECK (return_date IS NULL OR return_date >= issue_date)
);
CREATE INDEX idx_loan_book_copy ON loan(book_copy_id);
CREATE INDEX idx_loan_library_card ON loan(library_card_id);
CREATE INDEX idx_loan_employee ON loan(employee_id);

DROP TABLE IF EXISTS reservation CASCADE;
CREATE TABLE reservation (
    id               SERIAL      PRIMARY KEY,
    reservation_date DATE        NOT NULL 
                     DEFAULT CURRENT_DATE,
    valid_until      DATE        NOT NULL,
    status           VARCHAR(30) NOT NULL 
                     DEFAULT 'активна' 
                     CHECK (status IN ('активна', 'выполнена', 'отменена', 'истекла')),
    library_card_id  INT         NOT NULL 
                     REFERENCES library_card(id) 
                     ON DELETE CASCADE,
    edition_id       INT         NOT NULL 
                     REFERENCES edition(id) 
                     ON DELETE CASCADE
);
CREATE INDEX idx_reservation_card ON reservation(library_card_id);
CREATE INDEX idx_reservation_edition ON reservation(edition_id);

DROP TABLE IF EXISTS fine CASCADE;
CREATE TABLE fine (
    id           SERIAL         PRIMARY KEY,
    reason       VARCHAR(255)   NOT NULL,
    amount       NUMERIC(10, 2) NOT NULL 
                 CHECK (amount > 0),
    payment_date DATE,
    loan_id      INT            NOT NULL 
                 REFERENCES loan(id) 
                 ON DELETE CASCADE
);
CREATE INDEX idx_fine_loan ON fine(loan_id);