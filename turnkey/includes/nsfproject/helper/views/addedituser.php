<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/9/26
 * Time: 3:33 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
?>
<form method="post">
    <?php
    $logger->displayUserMessage();
    ?>
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required value="<?php echo $email; ?>"><br>

    <label for="first">First Name:</label>
    <input type="text" id="first" name="first" required value="<?php echo $first; ?>"><br>

    <label for="last">Last Name:</label>
    <input type="text" id="last" name="last" required value="<?php echo $last; ?>"><br>
    <label for="level">User level:</label>
    <select name="level" id="level">
        <option value="">-- Please choose an option --</option>
        <option value="user" <?php if ($level === 'user') echo "selected";?>>Viewer</option>
        <option value="admin" <?php if ($level === 'admin') echo 'selected';?>>Administrator</option>
    </select>
    <input type="submit" value="<?php echo $button; ?>">
</form>
