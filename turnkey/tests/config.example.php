<?php
/**
 * Test Configuration File
 *
 * This file defines constants needed for running unit tests.
 * Copy this file to tests/config.php and update with your test database credentials.
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

// Database Configuration for Tests
// Update these values with your test database credentials

define('DB_HOST', 'localhost');
define('DB_NAME', 'nsfproject_test');
define('DB_USER', 'root');
define('DB_PASS', 'password');
define('DB_PORT', '3306');

// Web Path Configuration
define('WEB_PATH', '/nsfproject');

// Project Root (automatically set in bootstrap.php)
if (!defined('PROJECT_ROOT')) {
    define('PROJECT_ROOT', dirname(__DIR__, 2) . '/html/nsfproject');
}

