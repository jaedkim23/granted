<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/7/26
 * Time: 3:41 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
/**
 * 1. Validate the Database connection, and if valid, create tables.
 * 2. Write the config to the proper ini file (conf.ini)
 * 3. If no problems detected above, load the "final header" and "final footer" with create admin user dialog.
 *  4. If problems, load the setup header / footer and resolve the database issue.
 */

// validate connection information
$host = $_POST['host'];
$port = $_POST['port'];
$dbname = $_POST['dbname'];
$user = $_POST['user'];
$password = $_POST['password'];
$includesdir=($_POST["includesdir"]??null);

try {
    $pdo=new PDO("mysql:host=$host;port=$port;dbname=$dbname", $user, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $dbconnection=true;
} catch (PDOException $e) {
    $dbconnection=false;
}
if ($dbconnection) {
    $autoloaddir = $includesdir . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'nsfproject' . DIRECTORY_SEPARATOR . 'vendor' . DIRECTORY_SEPARATOR . 'autoload.php';

    $inifilelocation = $includesdir . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'nsfproject' . DIRECTORY_SEPARATOR . 'conf' . DIRECTORY_SEPARATOR . 'conf.ini';
    $sqlfileLocation = $includesdir . DIRECTORY_SEPARATOR . 'includes' . DIRECTORY_SEPARATOR . 'nsfproject' . DIRECTORY_SEPARATOR . 'conf' . DIRECTORY_SEPARATOR . 'tables.sql';

    $fileContents = "<?php \r\n require_once '{$autoloaddir}';\r\n";
    $fileContents .= '$inifilelocation=' . "'" . $inifilelocation . "';\r\n";
    $foundError = false;
    $error = '';

    $result = file_put_contents('assets/nsfproject/settings/settings.php', $fileContents);
    if ($result === false) {
        $error .= '<p class="error">Error writing settings file: ' . "</p>\n";
        $foundError = true;
    }


    try {
        require_once $autoloaddir;
        // $iniwriter = \Matomo\Ini\IniWriter::class;
        $iniwriter = new \Matomo\Ini\IniWriter();
        $ini = \Nsfproject\helper\helper::prepareIniFile($_POST);
        $iniwriter->writeToFile($inifilelocation, $ini);
    } catch (Exception $e) {
        $error .= '<p class="error">Error writing conf.ini file: ' . $e->getMessage() . "</p>\n";
        $foundError = true;
    }


    //do this later
    if (!$foundError) {
        $loadsqlReturn=\Nsfproject\helper\helper::loadSql($pdo,$sqlfileLocation);
        include 'assets/nsfproject/start/init.php';
        include 'assets/nsfproject/start/noLoginNeeded.php';
        $logger=\Nsfproject\helper\logger::getInstance();
        $logger->displayUserMessage();
        $logger->displaySuccessMessage();
        if ($loadsqlReturn) {
            echo "<h2>Completed writing the files!</h2>\n";
            echo "<form action='setup4.php' method='post'>\n";
            echo "<div><label for='deleteSetup'>Would you like to delete your setup files now?</label>\n";
            echo "<input type='checkbox' name='deleteSetup' id='deleteSetup' value='yes'> YES </div>\n";
            echo "<input class='button' type='submit' name='submit' id='deleteSetup' value='submit'>\n";
            echo "</form>\n";
        } else {
            echo "<h2>There was an error loading the SQL file. Please review the errors, resolve and hit reload to continue setup.</h2>\n";
        }
        $finishedFooter=\Nsfproject\helper\helper::getFooter($ini);
        echo $finishedFooter;
        exit;
    }
}
use Nsfproject\helper\setupForm;
$ini = \Nsfproject\helper\helper::prepareIniFile($_POST);
include 'assets/nsfproject/header/setup-header.php';
echo "<h2>Please correct the following errors:</h2>\n";
echo "$error\n";
$form = new setupForm($ini,$includesdir);
$form->buildSetupForm();
$form->display('setup3.php');
include 'assets/nsfproject/footer/setup-footer.php';