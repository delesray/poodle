-- passwords = pass
-- insert admin
INSERT INTO `poodle`.`accounts` (`account_id`, `email`, `password`, `role`)
VALUES (1, 'a@a.com', '$2b$12$ctdJK7aLqFyhN50AE7aVgu/zRcMBLLgWKdkILjyTwPxx0.MuQIaTK', 'admin');
INSERT INTO `poodle`.`admins` (`admin_id`)
VALUES (1);

-- insert teachers
INSERT INTO `poodle`.`accounts` (`account_id`, `email`, `password`, `role`)
VALUES (2, 't2@t2.com', '$2b$12$ctdJK7aLqFyhN50AE7aVgu/zRcMBLLgWKdkILjyTwPxx0.MuQIaTK', 'teacher');
INSERT INTO `poodle`.`teachers` (`teacher_id`, `first_name`, `last_name`)
VALUES (2, 't2', 't2');

INSERT INTO `poodle`.`accounts` (`account_id`, `email`, `password`, `role`)
VALUES (3, 't3@t3.com', '$2b$12$ctdJK7aLqFyhN50AE7aVgu/zRcMBLLgWKdkILjyTwPxx0.MuQIaTK', 'teacher');
INSERT INTO `poodle`.`teachers` (`teacher_id`, `first_name`, `last_name`)
VALUES (3, 't3', 't3');

-- insert students
INSERT INTO `poodle`.`accounts` (`account_id`, `email`, `password`, `role`)
VALUES (4, 's4@s4.com', '$2b$12$ctdJK7aLqFyhN50AE7aVgu/zRcMBLLgWKdkILjyTwPxx0.MuQIaTK', 'student');
INSERT INTO `poodle`.`students` (`student_id`, `first_name`, `last_name`)
VALUES (4, 's4', 's4');

INSERT INTO `poodle`.`accounts` (`account_id`, `email`, `password`, `role`)
VALUES (5, 's5@s5.com', '$2b$12$ctdJK7aLqFyhN50AE7aVgu/zRcMBLLgWKdkILjyTwPxx0.MuQIaTK', 'student');
INSERT INTO `poodle`.`students` (`student_id`, `first_name`, `last_name`)
VALUES (5, 's5', 's5');



-- Insert Courses for t2 (account_id: 2, teacher_id: 2)
INSERT INTO `poodle`.`courses` (`title`, `description`, `objectives`, `owner_id`, `is_premium`)
VALUES ('Python Basics', 'Learn the fundamentals of Python programming.',
        'Get comfortable with variables, data types, control flow, and functions.', 2, 0),
       ('Intro to Web Development', 'Build your first web page using HTML and CSS.',
        'Master basic web page structure, styling, and interactivity.', 2, 1);

-- Insert Sections for Course 1 (course_id: 1)
INSERT INTO `poodle`.`sections` (`title`, `content_type`, `description`, `course_id`)
VALUES ('Introduction', 'text', 'Welcome and course overview.', 1),
       ('Basic Syntax', 'text', 'Variables and keywords', 1);

-- Insert Sections for Course 2 (course_id: 2)
INSERT INTO `poodle`.`sections` (`title`, `content_type`, `description`, `course_id`)
VALUES ('HTML Fundamentals', 'text', 'Learn the building blocks of web pages.', 2),
       ('CSS Styling', 'text', 'Add style and interactivity with CSS.', 2);

-- Insert Courses for t3 (account_id: 3, teacher_id: 3)
INSERT INTO `poodle`.`courses` (`title`, `description`, `objectives`, `owner_id`, `is_premium`)
VALUES ('JavaScript for Beginners', 'Get started with interactive web development.',
        'Learn variables, functions, and DOM manipulation basics.', 3, 1);

-- Insert Sections for Course 3 (course_id: 3)
INSERT INTO `poodle`.`sections` (`title`, `content_type`, `description`, `course_id`)
VALUES ('Introduction to Javascript', 'text', 'Welcome and course overview.', 3),
       ('Variables & Data Types', 'text', 'Mastering variables and data storage.', 3),
       ('Control Flow Statements', 'text', 'Learn how to control program flow.', 3);

-- insert tags
INSERT INTO `poodle`.`tags` (`name`)
VALUES ('python'),
       ('backend'),
       ('js'),
       ('frontend'),
       ('webdev'),
       ('git');

-- relate some tags
INSERT INTO `poodle`.`courses_tags` (`course_id`, `tag_id`)
VALUES (1,1),(1,2),(2,5),(3,3),(3,4);

-- enroll 2 students to course 1
INSERT INTO `poodle`.`students_courses` (`student_id`, `course_id`) VALUES ('4', '1');
INSERT INTO `poodle`.`students_courses` (`student_id`, `course_id`) VALUES ('5', '1');
