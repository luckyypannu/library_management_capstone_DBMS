# Intelligent Library and Digital Resource Management System

## Abstract
The project is a relational database application for managing physical books, digital resources, memberships, circulation, reservations and late-return penalties. It uses Flask as the application layer and MySQL as the relational database.

## Problem Statement
Manual library operations can make it difficult to track available copies, borrowing history, overdue items and penalties. The proposed system centralizes these records and supports accurate retrieval and reporting.

## Objectives
- Maintain structured book, author, publisher and member records.
- Track physical copies and their availability.
- Record issue and return transactions.
- Identify overdue loans and calculate late fees.
- Store digital resource links.
- Generate usage reports using SQL.

## Scope
This academic prototype supports librarian/admin workflows. It is intended for local demonstration and can be extended with member self-service, email reminders, barcode scanning and production deployment.

## Technology
HTML, CSS, JavaScript, Python Flask and MySQL 8.

## Database design
See `ER_DIAGRAM.md` and `../database/schema.sql`. The schema separates books from copies, and authors from books through a junction table to reduce duplication and support many-to-many relationships.

## Normalization notes
- 1NF: each field stores a single atomic value; author names are not stored as comma-separated lists.
- 2NF: the junction table `book_authors` has a composite key and no non-key attribute depending on only part of that key.
- 3NF: publisher, category and author details are held in separate tables rather than repeated in each book row.
- BCNF: the principal entity tables use candidate keys (such as ISBN, member number and email) as determinants. Review any additional business-specific functional dependencies before claiming a formal BCNF proof.

## SQL coverage
The `database/queries.sql` file demonstrates joins, subqueries, UNION, MySQL-compatible INTERSECT/EXCEPT alternatives, views, CTEs and window functions. `schema.sql` includes indexes and constraints.

## Business rules
- A standard loan period is 14 days.
- Late fee is ₹5 per day.
- A copy can be issued only when its status is AVAILABLE.
- Only ACTIVE members may borrow books.
- The issue and return operations use transactions.

## Testing checklist
1. Log in with the configured administrator.
2. Add a book and verify its row and copies in MySQL.
3. Register a member.
4. Issue an available copy and verify the loan and copy status.
5. Return the book and verify status restoration.
6. Return an overdue book in a test dataset and verify fine creation.
7. Verify reports for overdue and popular books.
8. Try duplicate ISBN, member number and email values and confirm constraints reject them.

## Limitations and future scope
Reservations are recorded but automatic reservation queue fulfillment is not implemented. Add role-based permissions, password reset, audit logs, pagination, automated reservation allocation, barcode scanning and deployment hardening in future versions.
