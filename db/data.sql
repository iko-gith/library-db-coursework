TRUNCATE TABLE employee RESTART IDENTITY CASCADE;
INSERT INTO employee (full_name, position) VALUES
('Орешкин Даниил',     'Администратор системы'),
('Смирнов Алексей',    'Библиотекарь');

TRUNCATE TABLE publisher RESTART IDENTITY CASCADE;
INSERT INTO publisher (name, city) VALUES
('Наука',         'Москва'),
('Питер',         'Санкт-Петербург'),
('БХВ-Петербург', 'Санкт-Петербург'),
('Эксмо',         'Москва');

TRUNCATE TABLE author RESTART IDENTITY CASCADE;
INSERT INTO author (last_name, first_name, middle_name) VALUES
('Клеппман', 'Мартин',    NULL),
('Дейт',     'Кристофер', 'Джон'),
('Кормен',   'Томас',     'Хенрик');

TRUNCATE TABLE edition RESTART IDENTITY CASCADE;
INSERT INTO edition (title, publish_year, publisher_id) VALUES
('Программирование, масштабирование, поддержка', 2018, 2),
('Введение в системы баз данных',                2005, 3),
('Алгоритмы. Построение и анализ',               2015, 1);

TRUNCATE TABLE edition_author RESTART IDENTITY CASCADE;
INSERT INTO edition_author (edition_id, author_id) VALUES
(1, 1),
(2, 2),
(3, 3);

TRUNCATE TABLE storage_location RESTART IDENTITY CASCADE;
INSERT INTO storage_location (hall, rack, shelf) VALUES
('Зал №1 (Техническая литература)',    'Стеллаж А-1', 'Полка 3'),
('Зал №2 (Учебные пособия)',           'Стеллаж Б-2', 'Полка 1'),
('Зал №3 (Художественная литература)', 'Стеллаж В-4', 'Полка 2');

TRUNCATE TABLE supplier RESTART IDENTITY CASCADE;
INSERT INTO supplier (name, inn, phone) VALUES
('ООО "Книготорг"',              '770123456789', '+7 (495) 123-45-67'),
('АО "Издательский дом "Книга"', '780298765432', '+7 (812) 987-65-43');

TRUNCATE TABLE supply RESTART IDENTITY CASCADE;
INSERT INTO supply (doc_number, supply_date, total_amount, supplier_id) VALUES
('Накладная-101', '2026-01-15', 15000.00, 1),
('Накладная-102', '2026-02-20', 28500.50, 2);

TRUNCATE TABLE reader RESTART IDENTITY CASCADE;
INSERT INTO reader (full_name, phone, email) VALUES
('Тестовый Читатель Обычный', '+7 (999) 111-22-33', 'reader@test.com');

TRUNCATE TABLE library_card RESTART IDENTITY CASCADE;
INSERT INTO library_card (card_number, issue_date, expiry_date, reader_id) VALUES
('CARD-2026-0001', '2026-01-10', '2027-01-10', 1);

TRUNCATE TABLE book_copy RESTART IDENTITY CASCADE;
INSERT INTO book_copy (inventory_number, status, price, edition_id, storage_location_id, supply_id) VALUES
('INV-00001', 'в фонде', 1200.00, 1, 1, 1),
('INV-00002', 'в фонде', 1500.00, 1, 1, 1),
('INV-00003', 'в фонде', 950.00, 2, 2, 2),
('INV-00004', 'в фонде', 2500.00, 3, 2, 2);