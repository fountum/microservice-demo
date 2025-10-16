CREATE USER "access"@"%" IDENTIFIED BY "funnygames";

CREATE DATABASE auth_db;
USE auth_db;

CREATE TABLE `Users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE DATABASE sales_data;
USE sales_data;
CREATE TABLE `Sales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `trace_id` varchar(36) NOT NULL,
  `customers` int NOT NULL,
  `cookies_sold` int NOT NULL,
  `income` float NOT NULL,
  `reported_time` datetime NOT NULL,
  `date_created` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

GRANT ALL PRIVILEGES ON auth_db.* TO "access"@"%";
GRANT ALL PRIVILEGES ON sales_data.* TO "access"@"%";
FLUSH PRIVILEGES; 
