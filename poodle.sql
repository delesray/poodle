-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema poodle
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `poodle` DEFAULT CHARACTER SET latin1 ;
USE `poodle` ;

-- -----------------------------------------------------
-- Table `poodle`.`accounts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`accounts` (
  `account_id` INT(11) NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(45) NOT NULL,
  `password` VARCHAR(200) NOT NULL,
  `role` ENUM('admin', 'teacher', 'student') NOT NULL,
  PRIMARY KEY (`account_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`admins`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`admins` (
  `admin_id` INT(11) NOT NULL,
  PRIMARY KEY (`admin_id`),
  INDEX `fk_admins_accounts_idx` (`admin_id` ASC) VISIBLE,
  CONSTRAINT `fk_admins_accounts`
    FOREIGN KEY (`admin_id`)
    REFERENCES `poodle`.`accounts` (`account_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`teachers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`teachers` (
  `teacher_id` INT(11) NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `phone_number` VARCHAR(45) NULL DEFAULT NULL,
  `linkedin` VARCHAR(45) NULL DEFAULT NULL,
  `profile_picture` BLOB NULL DEFAULT NULL,
  `is_deactivated` TINYINT(4) NULL DEFAULT NULL,
  PRIMARY KEY (`teacher_id`),
  INDEX `fk_teachers_accounts1_idx` (`teacher_id` ASC) VISIBLE,
  CONSTRAINT `fk_teachers_accounts1`
    FOREIGN KEY (`teacher_id`)
    REFERENCES `poodle`.`accounts` (`account_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`courses`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`courses` (
  `course_id` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(45) NOT NULL,
  `description` TEXT NOT NULL,
  `objectives` TEXT NOT NULL,
  `owner_id` INT(11) NOT NULL,
  `is_premium` TINYINT(4) NULL DEFAULT 0,
  `is_hidden` TINYINT(4) NULL DEFAULT 0,
  `home_page_picture` BLOB NULL DEFAULT NULL,
  `rating` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  UNIQUE INDEX `title_UNIQUE` (`title` ASC) VISIBLE,
  INDEX `fk_courses_teachers1_idx` (`owner_id` ASC) VISIBLE,
  CONSTRAINT `fk_courses_teachers1`
    FOREIGN KEY (`owner_id`)
    REFERENCES `poodle`.`teachers` (`teacher_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`tags`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`tags` (
  `tag_id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`tag_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`courses_tags`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`courses_tags` (
  `course_id` INT(11) NOT NULL,
  `tag_id` INT(11) NOT NULL,
  PRIMARY KEY (`course_id`, `tag_id`),
  INDEX `fk_courses_has_tags_tags1_idx` (`tag_id` ASC) VISIBLE,
  INDEX `fk_courses_has_tags_courses1_idx` (`course_id` ASC) VISIBLE,
  CONSTRAINT `fk_courses_has_tags_courses1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_courses_has_tags_tags1`
    FOREIGN KEY (`tag_id`)
    REFERENCES `poodle`.`tags` (`tag_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`sections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`sections` (
  `section_id` INT(11) NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(45) NOT NULL,
  `content` TEXT NOT NULL,
  `description` VARCHAR(45) NULL DEFAULT NULL,
  `external_link` VARCHAR(200) NULL DEFAULT NULL,
  `course_id` INT(11) NOT NULL,
  PRIMARY KEY (`section_id`),
  INDEX `fk_sections_courses1_idx` (`course_id` ASC) VISIBLE,
  CONSTRAINT `fk_sections_courses1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`students`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students` (
  `student_id` INT(11) NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `profile_picture` BLOB NULL DEFAULT NULL,
  `is_premium` TINYINT(4) NULL DEFAULT 0,
  `is_deactivated` TINYINT(4) NULL DEFAULT 0,
  PRIMARY KEY (`student_id`),
  INDEX `fk_students_accounts1_idx` (`student_id` ASC) VISIBLE,
  CONSTRAINT `fk_students_accounts1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`accounts` (`account_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`students_progress`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students_progress` (
  `student_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `progress` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`student_id`, `course_id`),
  INDEX `fk_students_has_courses1_courses1_idx` (`course_id` ASC) VISIBLE,
  INDEX `fk_students_has_courses1_students1_idx` (`student_id` ASC) VISIBLE,
  CONSTRAINT `fk_students_has_courses1_courses1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_students_has_courses1_students1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`students` (`student_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`students_rating`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students_rating` (
  `student_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  `rating` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`student_id`, `course_id`),
  INDEX `fk_students_has_courses_courses1_idx` (`course_id` ASC) VISIBLE,
  INDEX `fk_students_has_courses_students1_idx` (`student_id` ASC) VISIBLE,
  CONSTRAINT `fk_students_has_courses_courses1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_students_has_courses_students1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`students` (`student_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`students_sections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students_sections` (
  `student_id` INT(11) NOT NULL,
  `section_id` INT(11) NOT NULL,
  PRIMARY KEY (`student_id`, `section_id`),
  INDEX `fk_students_has_sections_sections1_idx` (`section_id` ASC) VISIBLE,
  INDEX `fk_students_has_sections_students1_idx` (`student_id` ASC) VISIBLE,
  CONSTRAINT `fk_students_has_sections_sections1`
    FOREIGN KEY (`section_id`)
    REFERENCES `poodle`.`sections` (`section_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_students_has_sections_students1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`students` (`student_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
