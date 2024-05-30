-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema poodle
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema poodle
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `poodle` ;
USE `poodle` ;

-- -----------------------------------------------------
-- Table `poodle`.`accounts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`accounts` (
  `account_id` INT(11) NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(30) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  `role` ENUM('admin', 'student', 'teacher') NOT NULL,
  `is_deactivated` TINYINT(1) NULL DEFAULT 0,
  PRIMARY KEY (`account_id`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`admins`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`admins` (
  `admin_id` INT(11) NOT NULL,
  PRIMARY KEY (`admin_id`),
  CONSTRAINT `admins_ibfk_1`
    FOREIGN KEY (`admin_id`)
    REFERENCES `poodle`.`accounts` (`account_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`teachers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`teachers` (
  `teacher_id` INT(11) NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `phone_number` VARCHAR(30) NULL DEFAULT NULL,
  `linked_in` VARCHAR(200) NULL DEFAULT NULL,
  `profile_picture` BLOB NULL DEFAULT NULL,
  PRIMARY KEY (`teacher_id`),
  CONSTRAINT `teachers_ibfk_1`
    FOREIGN KEY (`teacher_id`)
    REFERENCES `poodle`.`accounts` (`account_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`courses`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`courses` (
  `course_id` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(50) NOT NULL,
  `description` VARCHAR(250) NOT NULL,
  `objectives` VARCHAR(250) NOT NULL,
  `owner_id` INT(11) NOT NULL,
  `is_premium` TINYINT(1) NULL DEFAULT 0,
  `is_hidden` TINYINT(1) NULL DEFAULT 0,
  `home_page_picture` BLOB NULL DEFAULT NULL,
  `rating` FLOAT NULL DEFAULT NULL,
  `people_rated` INT(11) NULL DEFAULT 0,
  PRIMARY KEY (`course_id`),
  UNIQUE INDEX `title` (`title` ASC) VISIBLE,
  INDEX `owner_id` (`owner_id` ASC) VISIBLE,
  CONSTRAINT `courses_ibfk_1`
    FOREIGN KEY (`owner_id`)
    REFERENCES `poodle`.`teachers` (`teacher_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`tags`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`tags` (
  `tag_id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`tag_id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`courses_tags`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`courses_tags` (
  `course_id` INT(11) NOT NULL,
  `tag_id` INT(11) NOT NULL,
  PRIMARY KEY (`course_id`, `tag_id`),
  INDEX `tag_id` (`tag_id` ASC) VISIBLE,
  CONSTRAINT `courses_tags_ibfk_1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`),
  CONSTRAINT `courses_tags_ibfk_2`
    FOREIGN KEY (`tag_id`)
    REFERENCES `poodle`.`tags` (`tag_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`sections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`sections` (
  `section_id` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(45) NOT NULL,
  `content_type` ENUM('video', 'image', 'text', 'quiz') NOT NULL,
  `external_link` VARCHAR(500) NULL DEFAULT NULL,
  `description` VARCHAR(250) NULL DEFAULT NULL,
  `course_id` INT(11) NOT NULL,
  PRIMARY KEY (`section_id`),
  INDEX `course_id` (`course_id` ASC) VISIBLE,
  CONSTRAINT `sections_ibfk_1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`students`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students` (
  `student_id` INT(11) NOT NULL,
  `first_name` VARCHAR(50) NOT NULL,
  `last_name` VARCHAR(50) NOT NULL,
  `profile_picture` BLOB NULL DEFAULT NULL,
  `is_premium` TINYINT(1) NULL DEFAULT 0,
  PRIMARY KEY (`student_id`),
  CONSTRAINT `students_ibfk_1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`accounts` (`account_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`students_courses`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students_courses` (
  `student_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `status` INT(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`student_id`, `course_id`),
  INDEX `course_id` (`course_id` ASC) VISIBLE,
  CONSTRAINT `students_courses_ibfk_1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`students` (`student_id`),
  CONSTRAINT `students_courses_ibfk_2`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`students_ratings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students_ratings` (
  `student_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `rating` FLOAT NOT NULL,
  PRIMARY KEY (`student_id`, `course_id`),
  INDEX `course_id` (`course_id` ASC) VISIBLE,
  CONSTRAINT `students_ratings_ibfk_1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`students` (`student_id`),
  CONSTRAINT `students_ratings_ibfk_2`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poodle`.`students_sections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students_sections` (
  `student_id` INT(11) NOT NULL,
  `section_id` INT(11) NOT NULL,
  PRIMARY KEY (`student_id`, `section_id`),
  INDEX `section_id` (`section_id` ASC) VISIBLE,
  CONSTRAINT `students_sections_ibfk_1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`students` (`student_id`),
  CONSTRAINT `students_sections_ibfk_2`
    FOREIGN KEY (`section_id`)
    REFERENCES `poodle`.`sections` (`section_id`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
