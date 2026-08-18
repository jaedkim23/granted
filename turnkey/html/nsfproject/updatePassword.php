<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/16/26
 * Time: 4:12 PM
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
if (!isset($_SESSION['token'])) {
    header(header: "location:". WEB_PATH . "/login");
}
use Matomo\Ini\IniReader;
use Nsfproject\helper\helper;
use Nsfproject\helper\logger;
use Nsfproject\helper\dbModel;
use Nsfproject\models\user;
$logger=logger::getInstance();
$errors = [];
$success = false;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $password = $_POST['password'] ?? '';
    $confirm_password = $_POST['confirm_password'] ?? '';

    if (empty($password)) {
        $errors[] = 'Password is required.';
        $logger->logUserMessage('Password is required.');
    }
    if (empty($confirm_password)) {
        $errors[] = 'Confirm password is required.';
        $logger->logUserMessage('Confirm password is required.');
    }
    if ($password !== $confirm_password) {
        $errors[] = 'Passwords do not match.';
        $logger->logUserMessage('Passwords do not match.');
    }

    if (empty($errors)) {
        $success = true;
        $dbh = \Nsfproject\helper\dbModel::getInstance();
        $user=new \Nsfproject\models\user($dbh);
        if ($user->updatePassword($_SESSION['token'], $password)) {
            if ($user->validateUser($_SESSION['token'], $password)) {
                $user->setSession();
                unset($_SESSION['token']);
            }

            $logger->displaySuccessMessage();

            ?>
            <p>You will be redirected in 10 seconds.</p>
            <script>
                setTimeout(function() {
                    window.location.href = "<?php echo WEB_PATH; ?>/";
                }, 10000);
            </script>
            <?php
            helper::getFooter($ini);
            exit;
        }
    }else {
        helper::updatePasswordform();
    }
} else {
    helper::updatePasswordform();
}
helper::getFooter($ini);
?>