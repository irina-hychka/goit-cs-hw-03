-- 1) Get all tasks for a specific user
SELECT * FROM tasks WHERE user_id = 1;

-- 2) Get tasks by a specific status
SELECT * FROM tasks
WHERE status_id = (SELECT id FROM status WHERE name = 'new');

-- 3) Update the status of a specific task
UPDATE tasks
SET status_id = (SELECT id FROM status WHERE name = 'in progress')
WHERE id = 1;

-- 4) List users who have no tasks
SELECT * FROM users u
WHERE u.id NOT IN (SELECT user_id FROM tasks);

-- 5) Insert a new task for a specific user
INSERT INTO tasks (title, description, status_id, user_id)
VALUES ('Нове завдання', 'Опис нового завдання', 1, 2);

-- 6) Get all tasks that are not completed
SELECT * FROM tasks
WHERE status_id != (SELECT id FROM status WHERE name = 'completed');

-- 7) Delete a specific task
DELETE FROM tasks WHERE id = 5;

-- 8) Find users by email domain/pattern
SELECT * FROM users
WHERE email LIKE '%@example.com';

-- 9) Update a user’s full name
UPDATE users
SET fullname = 'Нове Імя'
WHERE id = 1;

-- 10) Count tasks per status
SELECT s.name, COUNT(t.id)
FROM tasks t
JOIN status s ON t.status_id = s.id
GROUP BY s.name;

-- 11) Get tasks assigned to users with a specific email domain
SELECT t.*
FROM tasks t
JOIN users u ON t.user_id = u.id
WHERE u.email LIKE '%@example.net';

-- 12) Get tasks without a description
SELECT * FROM tasks
WHERE description IS NULL OR description = '';

-- 13) Users and their tasks currently in 'in progress'
SELECT u.fullname, t.title, t.description
FROM users u
JOIN tasks t ON u.id = t.user_id
JOIN status s ON t.status_id = s.id
WHERE s.name = 'in progress';

-- 14) Users and the number of their tasks
SELECT u.fullname, COUNT(t.id) AS tasks_count
FROM users u
LEFT JOIN tasks t ON u.id = t.user_id
GROUP BY u.id, u.fullname;
