-- =============================================================
-- Business Listings Dashboard – Database Schema
-- MySQL 8.0  |  charset: utf8mb4  |  collation: utf8mb4_unicode_ci
-- =============================================================

CREATE DATABASE IF NOT EXISTS `listings_db`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `listings_db`;

CREATE TABLE IF NOT EXISTS `listing_master` (
    `id`            INT             NOT NULL AUTO_INCREMENT,
    `business_name` VARCHAR(255)    NOT NULL,
    `category`      VARCHAR(150)    NOT NULL DEFAULT 'Unknown',
    `city`          VARCHAR(100)    NOT NULL DEFAULT 'Unknown',
    `address`       TEXT            DEFAULT NULL,
    `phone`         VARCHAR(30)     DEFAULT NULL,
    `source`        VARCHAR(50)     NOT NULL DEFAULT 'Unknown',
    `image_url`     VARCHAR(500)    DEFAULT NULL,
    `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`id`),

    -- Prevent exact duplicates at the DB level; INSERT IGNORE uses this.
    -- city/source are NOT NULL ('Unknown' default) so the key also catches rows without them.
    UNIQUE KEY `uq_name_city_source` (`business_name`(150), `city`, `source`),

    -- Indexes for aggregation queries used by /api/stats/* endpoints
    INDEX `idx_category` (`category`),
    INDEX `idx_city`     (`city`),
    INDEX `idx_source`   (`source`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
