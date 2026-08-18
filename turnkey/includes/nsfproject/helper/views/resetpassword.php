<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/13/26
 * Time: 3:45 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/

use Nsfproject\helper\logger;

?>
<div class="reset-password-container">
    <h2>Reset Password</h2>

    <?php
        $logger=logger::getInstance();
        $logger->displayUserMessage();
    ?>

        <form method="post" action="<?php echo WEB_PATH.'/updatePassword.php';?>">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required><br>

            <label for="confirm_password">Confirm Password:</label>
            <input type="password" id="confirm_password" name="confirm_password" required><br>

            <input type="submit" name="submit" value="Reset Password">
        </form>
</div>

