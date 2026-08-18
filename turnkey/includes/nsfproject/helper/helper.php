<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/8/26
 * Time: 2:10 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/

namespace Nsfproject\helper;
use Nsfproject\controllers\NSFsettingsController;
use Nsfproject\helper\logger;
use Nsfproject\helper\dbModel;
use Nsfproject\models\navigation;
use Nsfproject\models\pages;
use PDO;

class helper
{
    var $error=array();
    public static $pepper = "8#7*0B9#16Ee1BiD9P122)a5@!7j(2MV";
    public static $forgotPasswordLink = WEB_PATH . "/forgotPassword.php?token=";
    public static function prepareIniFile($array)
    {
//        array(
//    'Section1'=>array(
//          'value1'=>'hello',
//          'value2'=>'world',
//      ),
//      'Section2'=>array(
//          'value3'=>'foo',
//         )
//      );
        $inifile=array(
            'header'=>array(
                'siteTitle'=>$array['siteTitle'],
                'logo'=>$array['logo'],
                'schoolName'=>$array['schoolName'],
            ),
            'footer'=>array(
                'emailSender'=>$array['emailSender'],
                'copyright'=>$array['copyright'],
                'logo'=>$array['logo'],
                'schoolName'=>$array['schoolName'],
                'resourceLink'=>$array['resourceLink'],
            ),
            'database'=>array(
                'host'=>$array['host'],
                'port'=>$array['port'],
                'dbname'=>$array['dbname'],
                'user'=>$array['user'],
                'password'=>$array['password'],
            ),
            'CSS'=>array(
                'override'=>$array['override'],
            ),
            'includesdir'=>array(
                'includesdir'=>$array['includesdir'],
            )
        );
        return $inifile;
    }

    public static function hydrateHTML($HTML, $part, $array) {
        $headerVars=$array[$part];
        if ($part === 'footer') {
            $resourceLinks=self::prepareResourceLinks($array['footer']['resourceLink']);
            $updatedHeader=str_replace('MYRESOURCELINKS', $resourceLinks, $HTML);
            unset($headerVars['resourceLink']);
            $updatedHeader= str_replace(array_keys($headerVars), array_values($headerVars), $updatedHeader);
        } else {
            $keys=array_map('strtoupper', array_keys($headerVars));
            $updatedHeader = str_replace($keys, array_values($headerVars), $HTML);
        }
        return $updatedHeader;
    }

    private static function prepareResourceLinks($array) {
        $links = [];
        foreach ($array as $value) {

// Your Markdown input
            $markdown = $value;

            /**
             * The Regex Pattern:
             * \[([^\]]+)\] -> Matches text inside square brackets (Capture Group 1)
             * \(([^)]+)\)  -> Matches the URL inside parentheses (Capture Group 2)
             */
            $pattern = '/\[([^\]]+)\]\(([^)]+)\)/';

            /**
             * The Replacement Template:
             * $2 corresponds to the URL (Group 2)
             * $1 corresponds to the Link Text (Group 1)
             */
            $replacement = '<a href="$2">$1</a>';

// Perform the replacement
            $html_link = preg_replace($pattern, $replacement, $markdown);
            $links[]=$html_link;
// Result: <a href="https://www.sandiego.edu/">University of San Diego</a>

        }
        $return='<ul class="site-footer__links">'."\n";
        foreach ($links as $link) {
            $return .= "<li>$link</li>\n";
        }
        $return.="</ul>\n";
        return $return;
    }

    public static function getHeader($ini) {
        ob_start();
        include PROJECT_ROOT . '/assets/nsfproject/header/regular-header.php';
        $header = ob_get_clean();
        $finishedHeader=\Nsfproject\helper\helper::hydrateHTML($header,'header',$ini);
        $dbh=dbModel::getInstance();
        $nav=new navigation($dbh);
        $secure=false;
        if (isset($_SESSION['email'])) {
            $secure=true;
        }
        $nav->getPages($secure);
        $mynav=$nav->buildNestedNavigation();
        $finishedHeader = str_replace('NAVIGATION', $mynav, $finishedHeader);
        if (isset($ini['CSS']['override']) && !empty($ini['CSS']['override'])) {
            $finishedHeader = str_replace('<OVERRIDECSS>', '<link rel="stylesheet" href="' . $ini['CSS']['override'] . '">', $finishedHeader);
        } else {
            $finishedHeader = str_replace('<OVERRIDECSS>', '', $finishedHeader);
        }
        return $finishedHeader;
    }

    public static function getFooter($ini) {
        ob_start();
        include PROJECT_ROOT . '/assets/nsfproject/footer/regular-footer.php';
        $footer=ob_get_clean();
        $finishedFooter=\Nsfproject\helper\helper::hydrateHTML($footer,'footer',$ini);
        return $finishedFooter;
    }

    public function recordError($message) {
        $this->error[] = $message;
    }

    public function writeError() {
        $report='';
        foreach ($this->error as $error) {
            $report.='<p class="error">'.$error."</p>\n";
        }
        return $report;
    }

    public static function setWebPath($currentDir) {
        $webroot = $_SERVER['DOCUMENT_ROOT'];

        $computedWebPath = str_replace($webroot, '', $currentDir);
        // Fix for Windows systems (backslash vs forward slash)
        // Uncomment this line if you are using Windows and experiencing issues with backslashes in the path
       # $computedWebPath = str_replace('\\', '/', $computedWebPath);

// Ensure it starts with a slash but doesn't end with one
        #$computedWebPath = '/' . trim($computedWebPath, '/');

// Define the constant
        define('WEB_PATH', $computedWebPath);

    }

    private static function checkIfTableExists($dbh,$table) {
        // Detect database type
        $driver = $dbh->getAttribute(PDO::ATTR_DRIVER_NAME);

        if ($driver === 'pgsql') {
            // PostgreSQL
            $sql = "SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :tableName
            )";
            $params = ['tableName' => $table];
        } elseif ($driver === 'sqlite') {
            // SQLite
            $sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=:tableName";
            $params = ['tableName' => $table];
        } else {
            // MySQL/MariaDB
            $sql = "select count(*) from information_schema.tables where table_schema = :dbName and table_name = :tableName";
            $params = ['dbName' => 'nsfproject', 'tableName' => $table];
        }

        $query = $dbh->prepare($sql);
        $query->execute($params);

        if ($driver === 'sqlite') {
            return $query->fetchColumn() !== false;
        } else {
            return $query->fetchColumn() > 0;
        }
    }

    public static function loadSql($dbh,$sqlfile = null) {
        $usercheck=self::checkIfTableExists($dbh,'users');
        $adminpagescheck=self::checkIfTableExists($dbh,'adminpages');
        $pagescheck=self::checkIfTableExists($dbh,'pages');
        $password_resetscheck=self::checkIfTableExists($dbh,'password_resets');
        if ($usercheck || $adminpagescheck || $pagescheck || $password_resetscheck) {
            $logger=logger::getInstance();
            $logger->logUserMessage("One or more tables already exist in the database.  Please drop the existing tables before running the setup. Database was NOT setup");
            $logger->logErrorMessage("One or more tables already exist in the database.  Please drop the existing tables before running the setup.");
            $logger->writeErrors();
            return false;
        }

        // Auto-detect appropriate SQL file if not provided
        if ($sqlfile === null) {
            $driver = $dbh->getAttribute(PDO::ATTR_DRIVER_NAME);
            if ($driver === 'pgsql') {
                $sqlfile = __DIR__ . '/../conf/tables_postgres.sql';
            } elseif ($driver === 'sqlite') {
                $sqlfile = __DIR__ . '/../conf/tables_sqlite.sql';
            } else {
                $sqlfile = __DIR__ . '/../conf/tables.sql';
            }
        }

        if (!file_exists($sqlfile)) {
            $logger=logger::getInstance();
            $logger->logUserMessage("SQL file not found: $sqlfile");
            $logger->logErrorMessage("SQL file not found: $sqlfile");
            $logger->writeErrors();
            return false;
        }

        $sql = file_get_contents($sqlfile);
        try {
            $dbh->exec($sql);
            return true;
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logUserMessage("Database error setting up database: " . $e->getMessage());
            $logger->logErrorMessage("Database error setting up database: " . $e->getMessage());
            $logger->writeErrors();
            return false;
        }
    }

    public static function AdminWelcome($ini) {
        include 'views/adminwelcome.php';
    }

    public static function setDatabaseConnect($ini) {
        define('DB_HOST',$ini['database']['host']);
        define('DB_NAME',$ini['database']['dbname']);
        define('DB_USER',$ini['database']['user']);
        define('DB_PASS',$ini['database']['password']);
        define('DB_PORT',$ini['database']['port']);

    }

    public static function displayAddUserForm() {
        $logger=logger::getInstance();
        $email = htmlspecialchars($_POST['email']?? null);
        $first = htmlspecialchars($_POST['first']?? null);
        $last = htmlspecialchars($_POST['last']?? null);
        $level = htmlspecialchars($_POST['level']?? null);
        $button = 'Add User';

        include 'views/addedituser.php';

    }

    public static function displayEditUserForm($id) {

        $logger=logger::getInstance();
        $dbh=dbModel::getInstance();
        $user=new \Nsfproject\models\user($dbh);
        $user->fetchUser($id,how:'id');
        $email = htmlspecialchars($user->getEmail())?? null;
        $first = htmlspecialchars($user->getFirst())?? null;
        $last = htmlspecialchars($user->getLast())?? null;
        $level = htmlspecialchars($user->getLevel())?? null;
        $button = 'Update User';
        include 'views/addedituser.php';

    }

    public static function displayAddPageForm() {
        $logger=logger::getInstance();
        $title = htmlspecialchars($_POST['title']?? null);
        $parentid = is_numeric($_POST['parentid']??null) ? $_POST['parentid'] : null;
        $embed = $_POST['embed']?? null;
        $content = $_POST['content']??null;
        $active = htmlspecialchars($_POST['active']??null);
        $secure = htmlspecialchars($_POST['secure']??null);
        $is_default = htmlspecialchars($_POST['is_default']??null);
        $button = 'Add Page';
        $logger->displayUserMessage();
        include 'views/addeditpage.php';
    }

    public static function displayEditPageForm($id) {
        $logger=logger::getInstance();
        $dbh=dbModel::getInstance();
        $pages=new pages($dbh);
        $pages->fetchPage($id, doDisplay:false);
        $title = htmlspecialchars($pages->getTitle())?? null;
        $parentid = htmlspecialchars($pages->getParentid())?? null;
        $embed = $pages->getEmbed()?? null;
        $content = $pages->getContent()??null;
        $active = htmlspecialchars($pages->getActive())?? null;
        $secure = htmlspecialchars($pages->getSecure())?? null;
        $is_default = $pages->getDefault()?? null;
        $button = 'Update Page';
        include 'views/addeditpage.php';

    }

    public static function sendPasswordResetEmail($user,$token,$newUser) {
        $email = $user['email'] ?? '';
        $first = $user['first'] ?? '';
        $last = $user['last'] ?? '';
        $id = $user['id'] ?? '';
        $url = self::$forgotPasswordLink . $token;
        $url = 'https://'.$_SERVER['SERVER_NAME'] . $url;
        //todo:  look at what is needed to make the headers non-static.
        $controller=new NSFsettingsController();
        $controller->readConfig();
        $ini=$controller->getSettings();
        $fromemail=$ini['footer']['emailSender'];
        $siteName=$ini['header']['siteTitle'];
        $from = $siteName . ' ' . '<'.$fromemail.'>';
        $headers = [
            'From'     => $from,
            'X-Mailer' => 'PHP/' . phpversion()
        ];
        if (!$newUser) {
            $subject = $siteName . ' - Password Reset';
            $message = <<<EOL
Hello {$first} {$last},
You or someone else has requested to reset your password.  If you did not generate this request, you can ignore this email.
If you requested a password reset, please visit {$url} to reset your password.  This token is only valid for one (1) hour only.

Thank you.
{$siteName} team
EOL;
        } else {
            $subject = $siteName . ' - Set Password';
            $message = <<<EOL
Hello {$first} {$last},
An account has been created for you on the {$siteName} application.  Please visit {$url} to set your password and access the application. This token is only valid for one (1) hour only. if the time has passed, you may reset your password using the forgot password link on the site. 

Thank you.
{$siteName} team
EOL;
        }
        mail($email, $subject, $message, $headers);
    }

    public static function updatePasswordform() {
        include 'views/resetpassword.php';
    }

    public static function displayUsers($users) {
        include 'views/display_users.php';
    }

    public static function displayPage($page) {
        $content = $page['content'] ?? null;
        $embed = $page['embed'] ?? null;
        if ($page['secure'] && !(isset($_SESSION['id']))) {
            include 'views/noaccess.php';
            return;
        }
        include 'views/displayPage.php';
    }

    public static function displayPages($pages) {
        include 'views/displayPageList.php';
    }

    public static function displayConfForm($ini) {
        include 'views/confform.php';
    }

    public static function displayConfiguration($ini) {
        include 'views/configuration.php';
    }
}