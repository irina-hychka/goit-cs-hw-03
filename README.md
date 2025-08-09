# Homework: Introduction to Database Management Systems

## Task 1 — PostgreSQL Task Management System

**Objective:**  
Create a database for a task management system using PostgreSQL.  
The database must contain tables for **users**, **task statuses**, and **tasks** themselves.  
Perform the necessary queries within the task management database.

### Implementation
1. Created database tables according to the given structure requirements.  
2. The `email` field in the `users` table and the `name` field in the `status` table are **unique**.  
3. Implemented **cascade deletion** so that deleting a user automatically removes all their related tasks.  
4. Added a **table creation script** (`create_tables.py`).  
5. Implemented a **`seed.py` script** in Python that populates the database with random data using the [Faker](https://faker.readthedocs.io/) library.  
6. Created and executed all required SQL queries in the task management system database.  

---

## Task 2 — MongoDB CRUD with PyMongo

**Objective:**  
Develop a Python script that uses the **PyMongo** library to perform basic CRUD operations in MongoDB.

### Implementation
1. Created the MongoDB database and designed the required document structure.  
2. Implemented all necessary CRUD operations (**Create**, **Read**, **Update**, **Delete**).  
3. Added exception handling for possible database operation errors.  
4. Wrote clear, well-structured, and commented Python functions.  

---

## Technologies Used
- **PostgreSQL**  
- **MongoDB**  
- **Python 3.x**  
- [psycopg2](https://www.psycopg.org/)  
- [PyMongo](https://pymongo.readthedocs.io/)  
- [Faker](https://faker.readthedocs.io/)  
- [python-dotenv](https://pypi.org/project/python-dotenv/)  

---

## How to Run

### PostgreSQL Setup
1. Ensure PostgreSQL is installed and running.  
2. Create a `.env` file in the project root with the following variables:
   ```env
   DB_NAME=your_database_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```
3. Run the table creation script:
   ```bash
   python create_tables.py
   ```
4. Seed the database with test data:
   ```bash
   python seed.py
   ```

### MongoDB Setup
1. Ensure MongoDB is installed locally or accessible via Docker.  
2. Update the connection URI in the script if needed.  
3. Run the CRUD operations script:
   ```bash
   python main.py
   ```
