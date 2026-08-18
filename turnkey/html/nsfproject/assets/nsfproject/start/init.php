<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/10/26
 * Time: 2:06 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
session_start();
define('PROJECT_ROOT', realpath(__DIR__ .'/../../..' ));

if (!file_exists(PROJECT_ROOT . '/assets/nsfproject/settings/settings.php')) {
    header('Location: setup.php');
    exit;
} else {
    include PROJECT_ROOT . '/assets/nsfproject/settings/settings.php';
}