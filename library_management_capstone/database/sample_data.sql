USE library_management_db;
INSERT INTO admins(username,password_hash) VALUES
('admin','pbkdf2:sha256:600000$demo$e5f2a8d3f4a1d5b8c7e6f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0');

INSERT INTO categories(category_name) VALUES
('Computer Science'),('Fiction'),('Science'),('History'),('Business');

INSERT INTO publishers(publisher_name,city) VALUES
('Pearson','Delhi'),('Penguin Random House','New Delhi'),('O Reilly Media','California'),
('HarperCollins','Gurugram'),('Oxford University Press','Oxford');

INSERT INTO authors(author_name,country) VALUES
('Ramez Elmasri','USA'),('Abraham Silberschatz','USA'),('Robert C. Martin','USA'),
('J.K. Rowling','UK'),('George Orwell','UK'),('Yuval Noah Harari','Israel'),
('Stephen Hawking','UK'),('Martin Kleppmann','UK'),('Paulo Coelho','Brazil'),
('James Clear','USA');

INSERT INTO books(isbn,title,publisher_id,category_id,published_year) VALUES
('9780133970777','Fundamentals of Database Systems',1,1,2015),
('9780073523323','Database System Concepts',1,1,2019),
('9780132350884','Clean Code',1,1,2008),
('9780747532743','Harry Potter and the Philosopher''s Stone',2,2,1997),
('9780451524935','1984',4,2,1949),
('9780062316097','Sapiens',4,4,2015),
('9780553380163','A Brief History of Time',2,3,1998),
('9781491903995','Designing Data-Intensive Applications',3,1,2017),
('9780061122415','The Alchemist',4,2,1993),
('9780735211292','Atomic Habits',4,5,2018);

INSERT INTO book_authors(book_id,author_id) VALUES
(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10);

INSERT INTO members(member_no,full_name,email,phone,joined_on,status) VALUES
('MEM001','Aarav Sharma','aarav@example.com','9876500001',CURDATE(),'ACTIVE'),
('MEM002','Priya Verma','priya@example.com','9876500002',CURDATE(),'ACTIVE'),
('MEM003','Kabir Singh','kabir@example.com','9876500003',CURDATE(),'ACTIVE'),
('MEM004','Ananya Gupta','ananya@example.com','9876500004',CURDATE(),'ACTIVE'),
('MEM005','Ishaan Mehta','ishaan@example.com','9876500005',CURDATE(),'ACTIVE'),
('MEM006','Meera Kapoor','meera@example.com','9876500006',CURDATE(),'ACTIVE'),
('MEM007','Rohan Das','rohan@example.com','9876500007',CURDATE(),'ACTIVE'),
('MEM008','Sara Khan','sara@example.com','9876500008',CURDATE(),'ACTIVE'),
('MEM009','Dev Patel','dev@example.com','9876500009',CURDATE(),'ACTIVE'),
('MEM010','Nisha Rao','nisha@example.com','9876500010',CURDATE(),'ACTIVE');

INSERT INTO book_copies(book_id,accession_no,status)
SELECT b.book_id, CONCAT('ACC-',b.book_id,'-',n.n), 'AVAILABLE'
FROM books b CROSS JOIN
(SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3) n;

INSERT INTO loans(member_id,copy_id,issue_date,due_date,status)
VALUES
(1,1,DATE_SUB(CURDATE(),INTERVAL 20 DAY),DATE_SUB(CURDATE(),INTERVAL 6 DAY),'ISSUED'),
(2,4,DATE_SUB(CURDATE(),INTERVAL 4 DAY),DATE_ADD(CURDATE(),INTERVAL 10 DAY),'ISSUED'),
(3,7,DATE_SUB(CURDATE(),INTERVAL 30 DAY),DATE_SUB(CURDATE(),INTERVAL 16 DAY),'RETURNED'),
(1,10,DATE_SUB(CURDATE(),INTERVAL 60 DAY),DATE_SUB(CURDATE(),INTERVAL 46 DAY),'RETURNED');

UPDATE book_copies SET status='ISSUED' WHERE copy_id IN (1,4);
UPDATE loans SET return_date=DATE_SUB(CURDATE(),INTERVAL 15 DAY) WHERE loan_id=3;
UPDATE book_copies SET status='AVAILABLE' WHERE copy_id=7;
INSERT INTO fines(loan_id,amount,paid_amount,status,created_on)
VALUES(1,30,0,'UNPAID',CURDATE()),(3,25,25,'PAID',CURDATE());

INSERT INTO reservations(member_id,book_id,reserved_on,status)
VALUES(4,1,CURDATE(),'PENDING'),(5,8,CURDATE(),'PENDING');

INSERT INTO digital_resources(title,resource_type,url,description,added_on) VALUES
('Introduction to SQL','EBOOK','https://dev.mysql.com/doc/','MySQL official documentation',CURDATE()),
('Database Research Journal','JOURNAL','https://www.acm.org/','Research resource example',CURDATE());
