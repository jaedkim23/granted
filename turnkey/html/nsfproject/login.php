<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/10/26
 * Time: 11:48 AM
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

$logger = logger::getInstance();

if (isset($_GET['return'])) {
    $_SESSION['return'] = $_GET['return'];
}
if (!empty($_POST) && $_POST['submit'] == 'Login' && isset($_POST['email'])) {
    $email = filter_var(trim($_POST['email']), FILTER_SANITIZE_EMAIL);
    $password = $_POST['password'];
    $dbh=dbModel::getInstance();
    $user = new user($dbh);
    if ($user->validateUser($email, $password)) {
        $user->setSession();

        $logger->writeErrors();
        if (isset($_SESSION['return'])) {
            $return = $_SESSION['return'];
            unset($_SESSION['return']);
            header("Location: $return");
        } else {
            header("Location: ". WEB_PATH . "/");
            exit;
        }
    } else {
        $logger->logErrorMessage("Login failed for email: $email");
        $logger->writeErrors();
        echo "<p class='error'>Invalid email or password. Please try again.</p>";
    }
} else if (!empty($_POST) && $_POST['submit'] == 'Send Reset Link' && isset($_POST['email'])) {
    $email = filter_var(trim($_POST['email']), FILTER_SANITIZE_EMAIL);
    $dbh= dbModel::getInstance();
    $user = new user($dbh);
    if ($user->sendPasswordResetLink($email)) {
        echo "<p class='success'>A password reset link has been sent to your email if it exists in our system.</p>";
    } else {
        $logger->logErrorMessage("Password reset requested for non-existent email: $email");
        $logger->writeErrors();
        echo "<p class='error'>If the email exists in our system, a password reset link has been sent.</p>";
    }
}
?>

<?php
$forgotPassword = isset($_GET['forgotPassword']) && $_GET['forgotPassword'] === '1';
?>

<div class="login-container">
     <?php if ($forgotPassword): ?>
        <h2>Reset Password</h2>
        <form method="post">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required><br>

            <input type="submit" name="submit" value="Send Reset Link">
        </form>
        <p><a href="login.php">Back to Login</a></p>
    <?php else: ?>
        <h2>Login</h2>
        <form method="post">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required><br>

            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br>

            <input type="submit" name="submit" value="Login">
        </form>
        <p><a href="login.php?forgotPassword=1">Forgot Password?</a></p>
    <?php endif; ?>
</div>

<?php

echo helper::getFooter($ini);
?>
