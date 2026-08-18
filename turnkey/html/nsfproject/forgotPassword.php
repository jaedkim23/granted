<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/13/26
 * Time: 2:16 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
include 'assets/nsfproject/start/init.php';
include 'assets/nsfproject/start/noLoginNeeded.php';
use Matomo\Ini\IniReader;
use Nsfproject\helper\helper;
use Nsfproject\helper\logger;
use Nsfproject\helper\dbModel;
use Nsfproject\models\user;
/*
Step 1:  check if user is in DB.
Step 2:  if user is in DB, generate a random token and save it to the DB with an expiration time.
Step 3:  send an email to the user with a link to reset their password, including the token as a parameter.
Step 4:  when the user clicks the link, verify the token and expiration time. If valid, allow the user to reset their password.
Step 5:  after the password is reset, invalidate the token so it cannot be used again.
*/
if (isset($_GET['token'])) {
    $token = $_GET['token'];
    $dbh = dbModel::getInstance();
    $user = new user($dbh);
    $email = $user->checkToken($token);
    if ($email !== false) {
        echo "$email is email <br>";
        $_SESSION['token'] = $email;
        helper::updatePasswordform();
    } else {
        $logger = logger::getInstance();
        $logger->logUserMessage('Token invalid. Please try the reset password link again.');
        $logger->displayUserMessage();
    }
}

echo helper::getFooter($ini);




