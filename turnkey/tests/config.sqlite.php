<?php
/**
 * Test Configuration File - SQLite Version
 *
 * This version uses SQLite in-memory database for testing.
 * No external database setup required.
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

// SQLite in-memory database for testing (no setup required)
define('DB_HOST', ':memory:');
define('DB_NAME', 'nsfproject_test');
define('DB_USER', '');
define('DB_PASS', '');
define('DB_PORT', '');

// Web Path Configuration
define('WEB_PATH', '/nsfproject');

// Project Root (automatically set in bootstrap.php)
if (!defined('PROJECT_ROOT')) {
    define('PROJECT_ROOT', dirname(__DIR__, 2) . '/html/nsfproject');
}

