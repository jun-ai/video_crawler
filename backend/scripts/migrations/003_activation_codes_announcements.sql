-- =====================================================
-- 迁移脚本：激活码 + 公告 + 用户状态字段
-- 执行方式：手动在 MySQL 中运行
-- =====================================================

-- 1. 激活码表
CREATE TABLE IF NOT EXISTS `activation_codes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(50) NOT NULL UNIQUE,
    `is_used` TINYINT(1) DEFAULT 0,
    `used_by` INT NULL,
    `used_at` DATETIME NULL,
    `max_uses` INT DEFAULT 1,
    `use_count` INT DEFAULT 0,
    `created_by` INT NULL,
    `expires_at` DATETIME NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX `ix_activation_codes_code` (`code`),
    INDEX `ix_activation_codes_id` (`id`),
    CONSTRAINT `fk_activation_codes_used_by` FOREIGN KEY (`used_by`) REFERENCES `users`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 公告表
CREATE TABLE IF NOT EXISTS `announcements` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(200) NOT NULL,
    `content` TEXT NOT NULL,
    `type` VARCHAR(20) DEFAULT 'info',
    `priority` INT DEFAULT 0,
    `is_active` TINYINT(1) DEFAULT 1,
    `created_by` INT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX `ix_announcements_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 用户表新增字段
ALTER TABLE `users`
    ADD COLUMN `activation_code_id` INT NULL AFTER `is_active`,
    ADD COLUMN `status` VARCHAR(20) DEFAULT 'approved' AFTER `activation_code_id`,
    ADD COLUMN `activated_at` DATETIME NULL AFTER `status`;
