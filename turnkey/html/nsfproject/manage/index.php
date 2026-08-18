<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/9/26
 * Time: 2:04 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
$ini=null;
include '../assets/nsfproject/start/init.php';
include '../assets/nsfproject/start/adminLoginNeeded.php';

use Matomo\Ini\IniReader;
use Nsfproject\controllers\NSFsettingsController;
use Nsfproject\helper\helper;
use Nsfproject\helper\dbModel;
use Nsfproject\helper\logger;
use Nsfproject\models\pages;
use Nsfproject\models\user;

$db=dbModel::getInstance();
$user=new user($db);
$user->fetchUser($_SESSION['id'],how:'id');
$logger = logger::getInstance();
$logger->displayUserMessage();
$logger->displaySuccessMessage();
//$webroot = $_SERVER['DOCUMENT_ROOT'];
//$currentDir = realpath(__DIR__ . '/..');
//$webPath = str_replace($webroot, '', $currentDir);
//echo "$webroot is the webroot $webPath is the webpath";
//var_export($_SESSION);
if (empty($_GET) && empty($_POST)) {
    helper::AdminWelcome($ini);
} else {
    $action = $_GET['action'];
    $ref = $_GET['ref'] ?? null;
    $id = $_GET['id'] ?? null;
    switch ($action) {
        case 'user':
            if ($ref === 'add') {
                if (isset($_POST['email'])) {
                    if (user::validateaddedituserform()) {
                           $user=new user($db);
                           $user->useradd();
                           $user->sendPasswordResetLink($_POST['email'],newUser:'true');

                    }
                } else {
                    helper::displayAddUserForm();
                }
            } elseif ($ref === 'edit') {
                if (isset ($_POST['email'])) {
                       if (user::validateaddedituserform($id)) {
                           $user=new user($db);
                           if ($user->userUpdate($id)) {
                                 $logger->displaySuccessMessage();
                           } else {
                                 $logger->displayUserMessage();
                               $email = htmlspecialchars($_POST['email'])?? null;
                               $first = htmlspecialchars($_POST['first'])?? null;
                               $last = htmlspecialchars($_POST['last'])?? null;
                               $level = htmlspecialchars($_POST['level'])?? null;
                               $button = 'Update User';
                               //calling it this way because displayEditUserForm will pull the information from the database.
                               include 'views/addedituser.php';
                           }
                           $user->fetchUser($id,how:'id');
                       }
                } else {
                    helper::displayEditUserForm($id);
                }
            } elseif ($ref === 'delete') {
                $user=new user($db);
                $user->fetchUser($_GET['id'],how:'id');
                $user->deleteUser();

                $logger = logger::getInstance();
                $logger->displayUserMessage();
                $logger->displaySuccessMessage();
                $users=$user->fetchUsers();
                helper::displayUsers($users);
            } else {
                $user=new user($db);
                $users=$user->fetchUsers();
                helper::displayUsers($users);
            }
            break;
        case 'pages':
            if ($ref === 'add') {
                if (isset($_POST['title'])) {
                    if (pages::validateaddeditpageform()) {
                        $page=new pages($db);
                        if (!$page->pageadd()) {
                            helper::displayAddPageForm();
                        }
                    } else {
                        helper::displayAddPageForm();                    }
                } else {
                    helper::displayAddPageForm();
                }
            } elseif ($ref === 'edit') {
                if (isset ($_POST['title'])) {
                    if (pages::validateaddeditpageform($id)) {
                        $page=new pages($db);
                        if (!$page->pageUpdate($id)) {
                            helper::displayAddPageForm();
                        }
                    } else {
                        helper::displayAddPageForm();
                    }
                } else {
                    helper::displayEditPageForm($id);
                }
            } else {
                $page=new pages($db);
                $pages=$page->fetchPages();
                $logger->displayUserMessage();
                $logger->displaySuccessMessage();
                if (!empty($pages)) {
                    helper::displayPages($pages);
                } else {
                    echo "<p>No pages found. <a href='" . WEB_PATH . "/manage/pages/add'>Add a page</a></p>";
                }
            }
            break;
        case 'conf' :
            $controller = new NSFsettingsController();
            $controller->readConfig();
            $settings = $controller->getSettings(); // Returns the parsed INI data
            if (!is_null($ref) && $ref==='edit') {
                if (isset($_POST['submit'])) {
                    unset($_POST['submit']);
                    //validate form
                    if ($controller->validateConfigForm()) {
                        if ($controller->updateSettingsFromForm()) {
                            $writeResult = $controller->writeConfig();
                            if ($writeResult === true) {
                                $logger->displaySuccessMessage('Configuration updated successfully.');
                                // Refresh settings after writing
                                $controller->readConfig();
                                $settings = $controller->getSettings();
                                helper::displayConfiguration($settings);
                            } else {
                                $logger->displayUserMessage();
                                $settings = $_POST;
                                helper::displayConfForm($settings);
                            }
                        } else {
                            $logger->displayUserMessage('Please correct the errors in the form.');
                            helper::displayConfForm($settings);
                        }
                    } else {
                        $logger->displayUserMessage();
                        $settings = $_POST;
                        helper::displayConfForm($settings);
                    }
                } else {
                    helper::displayConfForm($settings);
                }
            } else {
                helper::displayConfiguration($settings);
            }
            break;
        default:
            throw new \Exception('Unexpected value ' . $action);


    } // end of the switch
} // end of the else
echo helper::getFooter($ini);