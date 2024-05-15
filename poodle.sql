-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema poodle
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema poodle
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `poodle` DEFAULT CHARACTER SET latin1 ;
USE `poodle` ;

-- -----------------------------------------------------
-- Table `poodle`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`users` (
  `user_id` INT(11) NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(45) NOT NULL,
  `first_name` VARCHAR(45) NOT NULL,
  `last_name` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  `profile_picture` BLOB NOT NULL,
  `is_admin` TINYINT(4) NOT NULL DEFAULT 0,
  `is_deleted` TINYINT(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`teachers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`teachers` (
  `phone_number` VARCHAR(45) NULL DEFAULT NULL,
  `linkedin_account` VARCHAR(45) NULL DEFAULT NULL,
  `user_id` INT(11) NOT NULL,
  PRIMARY KEY (`user_id`),
  INDEX `fk_teachers_users1_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_teachers_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `poodle`.`users` (`user_id`)
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
  `is_premium` TINYINT(4) NOT NULL DEFAULT 0,
  `is_hidden` TINYINT(4) NOT NULL DEFAULT 0,
  `home_page_picture` BLOB NULL DEFAULT NULL,
  `rating` INT(11) NULL DEFAULT NULL,
  `owner_id` INT(11) NOT NULL,
  PRIMARY KEY (`course_id`),
  UNIQUE INDEX `title_UNIQUE` (`title` ASC) VISIBLE,
  INDEX `fk_courses_teachers1_idx` (`owner_id` ASC) VISIBLE,
  CONSTRAINT `fk_courses_teachers1`
    FOREIGN KEY (`owner_id`)
    REFERENCES `poodle`.`teachers` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`course_sections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`course_sections` (
  `section_id` INT(11) NOT NULL,
  `title` VARCHAR(45) NOT NULL,
  `content` VARCHAR(45) NOT NULL,
  `description` VARCHAR(45) NULL DEFAULT NULL,
  `external_link` VARCHAR(200) NULL DEFAULT NULL,
  `course_id` INT(11) NOT NULL,
  PRIMARY KEY (`section_id`),
  UNIQUE INDEX `title_UNIQUE` (`title` ASC) VISIBLE,
  INDEX `fk_course_sections_courses1_idx` (`course_id` ASC) VISIBLE,
  CONSTRAINT `fk_course_sections_courses1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`courses_teachers`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`courses_teachers` (
  `course_id` INT(11) NOT NULL,
  `teacher_id` INT(11) NOT NULL,
  PRIMARY KEY (`course_id`, `teacher_id`),
  INDEX `fk_courses_has_teachers_teachers1_idx` (`teacher_id` ASC) VISIBLE,
  INDEX `fk_courses_has_teachers_courses1_idx` (`course_id` ASC) VISIBLE,
  CONSTRAINT `fk_courses_has_teachers_courses1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_courses_has_teachers_teachers1`
    FOREIGN KEY (`teacher_id`)
    REFERENCES `poodle`.`teachers` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`expertise_areas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`expertise_areas` (
  `area_id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`area_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`expertise_areas_courses`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`expertise_areas_courses` (
  `expertise_area_id` INT(11) NOT NULL,
  `course_id` INT(11) NOT NULL,
  PRIMARY KEY (`expertise_area_id`, `course_id`),
  INDEX `fk_expertise_areas_has_courses_courses1_idx` (`course_id` ASC) VISIBLE,
  INDEX `fk_expertise_areas_has_courses_expertise_areas1_idx` (`expertise_area_id` ASC) VISIBLE,
  CONSTRAINT `fk_expertise_areas_has_courses_courses1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_expertise_areas_has_courses_expertise_areas1`
    FOREIGN KEY (`expertise_area_id`)
    REFERENCES `poodle`.`expertise_areas` (`area_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`students`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students` (
  `student_id` INT(11) NOT NULL,
  PRIMARY KEY (`student_id`),
  INDEX `fk_students_users1_idx` (`student_id` ASC) VISIBLE,
  CONSTRAINT `fk_students_users1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`users` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `poodle`.`students_courses`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `poodle`.`students_courses` (
  `course_id` INT(11) NOT NULL,
  `progress` INT(11) NULL DEFAULT NULL,
  `student_id` INT(11) NOT NULL,
  `rating` INT(11) NOT NULL,
  PRIMARY KEY (`course_id`, `student_id`),
  INDEX `fk_students_has_courses_courses1_idx` (`course_id` ASC) VISIBLE,
  INDEX `fk_students_courses_students1_idx` (`student_id` ASC) VISIBLE,
  CONSTRAINT `fk_students_courses_students1`
    FOREIGN KEY (`student_id`)
    REFERENCES `poodle`.`students` (`student_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_students_has_courses_courses1`
    FOREIGN KEY (`course_id`)
    REFERENCES `poodle`.`courses` (`course_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
