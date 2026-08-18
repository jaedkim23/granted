<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 3/13/26
 * Time: 4:27 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/


include 'assets/nsfproject/header/setup-header.php';

$includesdir=$_POST["includesdir"]??null;
rtrim ($includesdir,"/");
$autoloaddir=$includesdir . DIRECTORY_SEPARATOR . 'includes'.DIRECTORY_SEPARATOR.'nsfproject' . DIRECTORY_SEPARATOR . 'vendor' . DIRECTORY_SEPARATOR . 'autoload.php';

if (is_dir($includesdir . DIRECTORY_SEPARATOR . 'includes'.DIRECTORY_SEPARATOR.'nsfproject')) {
    require_once $autoloaddir;
} else {
    ?>
    <form action="setup2.php" method="post">
<label for="includesdir">We checked your <?php echo $includesdir?>, but could not load the autoloader.  Please check the absolute path you provided, and try again.<br> Reminder: It is where you placed the includes directory.</label>
    <div class="flex-container">
<input type="text" name="includesdir" id="includesdir" placeholder="Absolute path of includes directory" class="flex-input" value="<?php echo $includesdir?>" required>
    </div>
    <div>
    <input type="submit" value="Next" class="button">
    </div>
</form>
<?php
    include 'assets/nsfproject/footer/setup-footer.php';
    exit;
}
use Matomo\Ini\IniReader;
use Matomo\Ini\IniWriter;
use Matomo\Ini\IniReadingException;
use Matomo\Ini\IniWritingException;
use Nsfproject\helper\setupForm;

$iniread= new IniReader();
$array = $iniread->readFile($includesdir . DIRECTORY_SEPARATOR . 'includes'.DIRECTORY_SEPARATOR.'nsfproject'.DIRECTORY_SEPARATOR.'conf'.DIRECTORY_SEPARATOR.'example.ini');
?>
<h1>Congratulations Just a few more questions and your site will be ready to launch!</h1>

<?php
$form = new setupForm($array,$includesdir);
$form->buildSetupForm();
$form->display('setup3.php');

include 'assets/nsfproject/footer/setup-footer.php';

