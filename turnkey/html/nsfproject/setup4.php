<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/8/26
 * Time: 4:03 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/

if (!empty($_POST)) {
    if (isset($_POST['deleteSetup'])) {

        $files_to_delete = [
            'setup.php',
            'setup2.php',
            'setup3.php',
            'setup4.php'
        ];

        foreach ($files_to_delete as $file) {
            if (file_exists($file)) {
                unlink($file);
            }
        }

    }
    header("Location: manage/user/add");
    exit;
} else {
    include 'assets/nsfproject/header/setup-header.php';
    echo "<h2> You have completed setup without deleting your setup files. It is highly recommended that you do that.</h2>\n";
    echo "<form action='setup4.php' method='post'>\n";
    echo "<div><label for='deleteSetup'>Would you like to delete your setup files now?</label>\n";
    echo "<input type='checkbox' name='deleteSetup' id='deleteSetup' value='yes'> YES </div>\n";
    echo "<input class='button' type='submit' name='submit' id='deleteSetup' value='submit'>\n";
    echo "</form>\n";
    include 'assets/nsfproject/footer/setup-footer.php';
}

