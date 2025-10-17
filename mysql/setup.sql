CREATE USER IF NOT EXISTS 'sales'@'%' IDENTIFIED BY 'funnygames';
CREATE USER IF NOT EXISTS 'auth'@'%' IDENTIFIED BY 'WORMSandDIRTandSAND';

CREATE DATABASE IF NOT EXISTS auth_db;
CREATE DATABASE IF NOT EXISTS sales_data;

USE auth_db;
CREATE TABLE IF NOT EXISTS `Users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

USE sales_data;
CREATE TABLE IF NOT EXISTS `sales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `trace_id` varchar(36) NOT NULL,
  `customers` int NOT NULL,
  `cookies_sold` int NOT NULL,
  `income` float NOT NULL,
  `reported_time` datetime NOT NULL,
  `date_created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

GRANT ALL PRIVILEGES ON auth_db.* TO 'auth'@'%';
GRANT ALL PRIVILEGES ON sales_data.* TO 'sales'@'%';
FLUSH PRIVILEGES;