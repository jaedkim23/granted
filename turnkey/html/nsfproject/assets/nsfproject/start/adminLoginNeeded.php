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
use Matomo\Ini\IniReader;
use Nsfproject\helper\helper;
use Nsfproject\helper\logger;

$currentDir = realpath(__DIR__ . '/../../..');
helper::setWebPath($currentDir);

if (!isset($_SESSION['email'])) {
    header('Location:'.WEB_PATH .'/login.php?return='.$_SERVER['REQUEST_URI']);
    exit;
}

if (!isset($_SESSION['level']) || $_SESSION['level'] != 'admin') {
//    var_export($_SESSION);
//    exit('Access Denied to Administrative Area');
    header('Location: '.WEB_PATH .'/?error=Access Denied to Administrative Area');
    exit;

}
if (file_exists(PROJECT_ROOT.'/setup.php')) {
    $error='Your setup.php still exists.  This is a security issue. Please remove the setup files as you have already configured your system manually, or visit <a href="'.WEB_PATH.'/setup4.php">system setup step 4</a>';
}

$logger = logger::getInstance();

if (isset($error) && !empty($error)) {
    error_log("recording the settings error: $error");
    $logger->logUserMessage($error);
}


$helper = new helper();
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