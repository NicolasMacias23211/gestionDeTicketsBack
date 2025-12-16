-- Script para convertir campos ID a AUTO_INCREMENT
-- Ejecutar este script en MySQL antes de aplicar las migraciones de Django

USE `e-seus`;

-- Modificar tabla services
ALTER TABLE `services` 
MODIFY COLUMN `id-services` INT NOT NULL AUTO_INCREMENT;

-- Modificar tabla closing-codes
ALTER TABLE `closing-codes` 
MODIFY COLUMN `id-closing-code` INT NOT NULL AUTO_INCREMENT;

-- Modificar tabla ans
ALTER TABLE `ans` 
MODIFY COLUMN `id-ans` INT NOT NULL AUTO_INCREMENT;

-- Modificar tabla status
ALTER TABLE `status` 
MODIFY COLUMN `id-status` INT NOT NULL AUTO_INCREMENT;

-- Verificar cambios
SHOW CREATE TABLE services;
SHOW CREATE TABLE `closing-codes`;
SHOW CREATE TABLE ans;
SHOW CREATE TABLE status;
