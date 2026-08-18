
<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 3/13/26
 * Time: 2:57 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
$ini='';
include 'assets/nsfproject/start/init.php';
include 'assets/nsfproject/start/noLoginNeeded.php';
use Matomo\Ini\IniReader;
use Nsfproject\helper\helper;
use Nsfproject\helper\logger;
use Nsfproject\models\pages;
use Nsfproject\helper\dbModel;
$logger = logger::getInstance();
$logger->displayUserMessage();
$logger->displaySuccessMessage();
$db=dbModel::getInstance();
$page=new pages($db);
if (isset($_GET['_focus']) && is_numeric($_GET['_focus'])) {
    $focus = $_GET['_focus'];
   $page->fetchPage($focus);
} else {
   $page->fetchPage('default');
}

echo helper::getFooter($ini);



