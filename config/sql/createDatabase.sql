-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
-- -----------------------------------------------------
-- Schema e-seus
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `e-seus` DEFAULT CHARACTER SET utf8mb4 ;
USE `e-seus` ;

-- -----------------------------------------------------
-- Table `e-seus`.`clients`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`clients` (
  `client-name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`client-name`),
  UNIQUE INDEX `client-name_UNIQUE` (`client-name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`services`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`services` (
  `id-services` INT NOT NULL,
  `service-name` VARCHAR(45) NULL,
  `service-description` VARCHAR(100) NULL,
  `estimated-solution-time` TIME NULL,
  PRIMARY KEY (`id-services`),
  UNIQUE INDEX `service-name_UNIQUE` (`service-name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`roles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`roles` (
  `rol-name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(100) NULL,
  PRIMARY KEY (`rol-name`),
  UNIQUE INDEX `rol-name_UNIQUE` (`rol-name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`e-users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`e-users` (
  `network-user` VARCHAR(45) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `middle-name` VARCHAR(45) NULL,
  `last-name` VARCHAR(45) NOT NULL,
  `second-last-name` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  `phone` VARCHAR(45) NULL,
  `user-client-name` VARCHAR(45) NOT NULL,
  `id-services` INT NOT NULL,
  `rol-name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`network-user`),
  INDEX `fk_users_clients1_idx` (`user-client-name` ASC) VISIBLE,
  INDEX `fk_users_services1_idx` (`id-services` ASC) VISIBLE,
  INDEX `fk_e-users_roles1_idx` (`rol-name` ASC) VISIBLE,
  CONSTRAINT `fk_users_clients1`
    FOREIGN KEY (`user-client-name`)
    REFERENCES `e-seus`.`clients` (`client-name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_services1`
    FOREIGN KEY (`id-services`)
    REFERENCES `e-seus`.`services` (`id-services`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_e-users_roles1`
    FOREIGN KEY (`rol-name`)
    REFERENCES `e-seus`.`roles` (`rol-name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`ticket-priority`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`ticket-priority` (
  `priority-name` VARCHAR(45) NOT NULL,
  `priority-description` VARCHAR(100) NULL,
  PRIMARY KEY (`priority-name`),
  UNIQUE INDEX `priority-name_UNIQUE` (`priority-name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`programs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`programs` (
  `program-name` VARCHAR(45) NOT NULL,
  `client-name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`program-name`),
  INDEX `fk_programs_clients_idx` (`client-name` ASC) VISIBLE,
  CONSTRAINT `fk_programs_clients`
    FOREIGN KEY (`client-name`)
    REFERENCES `e-seus`.`clients` (`client-name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`sub-programs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`sub-programs` (
  `sub-program-name` VARCHAR(45) NOT NULL,
  `program-name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`sub-program-name`),
  INDEX `fk_sub-programs_programs1_idx` (`program-name` ASC) VISIBLE,
  CONSTRAINT `fk_sub-programs_programs1`
    FOREIGN KEY (`program-name`)
    REFERENCES `e-seus`.`programs` (`program-name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`closing-codes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`closing-codes` (
  `id-closing-code` INT NOT NULL,
  `closing-code-name` VARCHAR(45) NULL,
  `closing-code-description` VARCHAR(100) NULL,
  PRIMARY KEY (`id-closing-code`),
  UNIQUE INDEX `closing-code-name_UNIQUE` (`closing-code-name` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`ans`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`ans` (
  `id-ans` INT NOT NULL,
  `ans-name` VARCHAR(45) NOT NULL,
  `ans-description` VARCHAR(100) NULL,
  PRIMARY KEY (`id-ans`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`users` (
  `network-user` VARCHAR(45) NOT NULL,
  `mail` VARCHAR(50) NULL,
  `phone` VARCHAR(45) NULL,
  PRIMARY KEY (`network-user`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`status` (
  `status-id` INT NOT NULL,
  `status-name` VARCHAR(45) NOT NULL,
  `status-description` VARCHAR(100) NULL,
  PRIMARY KEY (`status-id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`tickets`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`tickets` (
  `id-ticket` INT NOT NULL,
  `ticket-title` VARCHAR(45) NOT NULL,
  `ticket-description` VARCHAR(250) NOT NULL,
  `ticket-attachments` VARCHAR(250) NULL,
  `ticket-service` INT NOT NULL,
  `ticket-priority` VARCHAR(45) NOT NULL,
  `ticket--closing-code` INT NULL,
  `ticket-ans` INT NOT NULL,
  `reporter-user` VARCHAR(45) NOT NULL,
  `create-at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update-at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `assigned-to` VARCHAR(45) NULL,
  `closing date` DATETIME NULL,
  `estimated-closing-date` DATETIME NULL,
  `status-id` INT NOT NULL,
  `sub-program-name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id-ticket`),
  INDEX `fk_tickets_services1_idx` (`ticket-service` ASC) VISIBLE,
  INDEX `fk_tickets_ticket-priority1_idx` (`ticket-priority` ASC) VISIBLE,
  INDEX `fk_tickets_closing-codes1_idx` (`ticket--closing-code` ASC) VISIBLE,
  INDEX `fk_tickets_ans1_idx` (`ticket-ans` ASC) VISIBLE,
  INDEX `fk_tickets_users1_idx` (`reporter-user` ASC) VISIBLE,
  INDEX `fk_tickets_status1_idx` (`status-id` ASC) VISIBLE,
  INDEX `fk_tickets_sub-programs1_idx` (`sub-program-name` ASC) VISIBLE,
  CONSTRAINT `fk_tickets_services1`
    FOREIGN KEY (`ticket-service`)
    REFERENCES `e-seus`.`services` (`id-services`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tickets_ticket-priority1`
    FOREIGN KEY (`ticket-priority`)
    REFERENCES `e-seus`.`ticket-priority` (`priority-name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tickets_closing-codes1`
    FOREIGN KEY (`ticket--closing-code`)
    REFERENCES `e-seus`.`closing-codes` (`id-closing-code`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tickets_ans1`
    FOREIGN KEY (`ticket-ans`)
    REFERENCES `e-seus`.`ans` (`id-ans`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tickets_users1`
    FOREIGN KEY (`reporter-user`)
    REFERENCES `e-seus`.`users` (`network-user`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tickets_status1`
    FOREIGN KEY (`status-id`)
    REFERENCES `e-seus`.`status` (`status-id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_tickets_sub-programs1`
    FOREIGN KEY (`sub-program-name`)
    REFERENCES `e-seus`.`sub-programs` (`sub-program-name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`reported-times`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`reported-times` (
  `id-reported-times` INT NOT NULL,
  `date-reported` DATETIME NOT NULL,
  `reported-time` TIME NOT NULL,
  `id-ticket` INT NOT NULL,
  `create-at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update-at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id-reported-times`),
  INDEX `fk_reported-times_tickets1_idx` (`id-ticket` ASC) VISIBLE,
  CONSTRAINT `fk_reported-times_tickets1`
    FOREIGN KEY (`id-ticket`)
    REFERENCES `e-seus`.`tickets` (`id-ticket`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `e-seus`.`notes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `e-seus`.`notes` (
  `id-note` INT NOT NULL,
  `note` TEXT NOT NULL,
  `visible-to-client` TINYINT(1) NOT NULL DEFAULT 0,
  `create-at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update-at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `id-ticket` INT NOT NULL,
  PRIMARY KEY (`id-note`),
  INDEX `fk_notes_tickets1_idx` (`id-ticket` ASC) VISIBLE,
  CONSTRAINT `fk_notes_tickets1`
    FOREIGN KEY (`id-ticket`)
    REFERENCES `e-seus`.`tickets` (`id-ticket`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
