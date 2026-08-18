<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/10/26
 * Time: 11:55 AM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/


if (!isset($_SESSION['email'])) {
    header('Location: /nsfproject/login.php?return='.$_SERVER['REQUEST_URI']);
}


if (file_exists(PROJECT_ROOT.'/setup.php')) {
    $error='Your setup.php still exists.  This is a security issue. Please remove the setup files as you have already configured your system manually, or visit <a href="' . WEB_PATH.'setup4.php">system setup step 4</a>';
}

use Matomo\Ini\IniReader;
use Nsfproject\helper\helper;
use Nsfproject\helper\logger;

$logger = logger::getInstance();
$helper = new helper();
if (isset($error) && !empty($error)) {
    error_log("recording the settings error: $error");
    $logger->logUserMessage($error);
}

$currentDir = realpath(__DIR__ . '/../../..');
helper::setWebPath($currentDir);

if (isset($inifilelocation)) {
    $reader=new IniReader();
    $ini = $reader->readFile($inifilelocation);
    helper::setDatabaseConnect($ini);
    echo helper::getHeader($ini);
}
else {
    exit('Settings file incomplete. Missing the $inifilelocation variable. Please run the setup process to create the settings file.');
}
$logger->displayUserMessage();
$logger->displaySuccessMessage();