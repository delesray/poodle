create table accounts
(
    account_id int auto_increment
        primary key,
    email      varchar(30)                          not null,
    password   varchar(200)                         not null,
    role       enum ('admin', 'student', 'teacher') not null
);

create table admins
(
    admin_id int not null
        primary key,
    constraint admins_ibfk_1
        foreign key (admin_id) references accounts (account_id)
);

create table students
(
    student_id      int         not null
        primary key,
    first_name      varchar(50) not null,
    last_name       varchar(50) not null,
    profile_picture blob        null,
    is_premium      tinyint(1)  null,
    is_deactivated  tinyint(1)  null,
    constraint students_ibfk_1
        foreign key (student_id) references accounts (account_id)
);

create table tags
(
    tag_id int auto_increment
        primary key,
    name   varchar(45) not null
);

create table teachers
(
    teacher_id      int          not null
        primary key,
    first_name      varchar(50)  not null,
    last_name       varchar(50)  not null,
    phone_number    varchar(30)  null,
    linked_in       varchar(200) null,
    profile_picture blob         null,
    is_deactivated  tinyint(1)   null,
    constraint teachers_ibfk_1
        foreign key (teacher_id) references accounts (account_id)
);

create table courses
(
    id                int auto_increment
        primary key,
    title             varchar(50)  not null,
    description       varchar(250) not null,
    objectives        varchar(250) not null,
    owner_id          int          not null,
    is_premium        tinyint(1)   null,
    is_hidden         tinyint(1)   null,
    home_page_picture blob         null,
    rating            int          not null,
    constraint title
        unique (title),
    constraint courses_ibfk_1
        foreign key (owner_id) references teachers (teacher_id)
);

create index owner_id
    on courses (owner_id);

create table courses_tags
(
    course_id int not null,
    tag_id    int not null,
    primary key (course_id, tag_id),
    constraint courses_tags_ibfk_1
        foreign key (course_id) references courses (id),
    constraint courses_tags_ibfk_2
        foreign key (tag_id) references tags (tag_id)
);

create index tag_id
    on courses_tags (tag_id);

create table sections
(
    section_id    int auto_increment
        primary key,
    title         varchar(45)                             null,
    content       enum ('video', 'image', 'text', 'quiz') null,
    description   varchar(250)                            null,
    external_link varchar(500)                            null,
    course_id     int                                     null,
    constraint sections_ibfk_1
        foreign key (course_id) references courses (id)
);

create index course_id
    on sections (course_id);

create table students_progress
(
    student_id int not null,
    course_id  int not null,
    progress   int not null,
    primary key (student_id, course_id),
    constraint students_progress_ibfk_1
        foreign key (student_id) references students (student_id),
    constraint students_progress_ibfk_2
        foreign key (course_id) references courses (id)
);

create index course_id
    on students_progress (course_id);

create table students_rating
(
    student_id int not null,
    course_id  int not null,
    rating     int not null,
    primary key (student_id, course_id),
    constraint students_rating_ibfk_1
        foreign key (student_id) references students (student_id),
    constraint students_rating_ibfk_2
        foreign key (course_id) references courses (id)
);

create index course_id
    on students_rating (course_id);

create table students_sections
(
    student_id int not null,
    section_id int not null,
    primary key (student_id, section_id),
    constraint students_sections_ibfk_1
        foreign key (student_id) references students (student_id),
    constraint students_sections_ibfk_2
        foreign key (section_id) references sections (section_id)
);

create index section_id
    on students_sections (section_id);


