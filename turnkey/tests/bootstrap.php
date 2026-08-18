<?php
/**
 * PHPUnit Bootstrap File
 *
 * This file is executed before running tests and sets up the environment
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

// Get the base path
$basePath = dirname(__DIR__);

// Load composer autoloader
require_once $basePath . '/includes/composer.json' !== false
    ? $basePath . '/includes/nsfproject/vendor/autoload.php'
    : $basePath . '/vendor/autoload.php';

// Load test configuration if it exists
$configFile = $basePath . '/tests/config.php';
if (file_exists($configFile)) {
    require_once $configFile;
}

// Define constants that tests might need
if (!defined('PROJECT_ROOT')) {
    define('PROJECT_ROOT', $basePath . '/html/nsfproject');
}

if (!defined('WEB_PATH')) {
    define('WEB_PATH', '/nsfproject');
}

// Set up error reporting for tests
error_reporting(E_ALL);
ini_set('display_errors', '1');

