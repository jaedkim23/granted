<?php
/**
 * Test Configuration File - PostgreSQL Version
 *
 * This version uses PostgreSQL for testing.
 * Requires PostgreSQL server to be running.
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

// PostgreSQL database for testing
define('DB_HOST', 'localhost');
define('DB_NAME', 'nsfproject_test');
define('DB_USER', 'postgres');
define('DB_PASS', 'password');
define('DB_PORT', '5432');

// Web Path Configuration
define('WEB_PATH', '/nsfproject');

// Project Root (automatically set in bootstrap.php)
if (!defined('PROJECT_ROOT')) {
    define('PROJECT_ROOT', dirname(__DIR__, 2) . '/html/nsfproject');
}

