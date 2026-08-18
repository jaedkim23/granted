<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/9/26
 * Time: 2:54 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/

namespace Nsfproject\helper;

use PDO;
use PDOException;
use Exception;

class dbModel
{
    private static ?dbModel $instance = null;
    public PDO $db;
    private bool $dbconnection = false;

    private function __construct() {
        if (!$this->connectDB()) {
            throw new Exception('Fatal Error: Unable to connect to database!');
        }
    }
    protected function connectDB() {
        if (!$this->dbconnection) {
            $host = DB_HOST;
            $user = DB_USER;
            $pass = DB_PASS;
            $port = DB_PORT;
            $db = DB_NAME;

            // Detect database type and configure accordingly
            if ($host === ':memory:') {
                // SQLite for testing
                $conn_str = 'sqlite::memory:';
                $atributes = array(
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
                );
            } elseif (strpos($host, 'postgres') !== false || !empty($port) && $port == '5432') {
                // PostgreSQL
                $conn_str = "pgsql:host=$host;port=$port;dbname=$db";
                $atributes = array(
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
                );
            } else {
                // MySQL/MariaDB (default)
                $atributes = array(
                    PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8",
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
                );
                $conn_str = 'mysql:host=' . $host . ';dbname=' . $db . ';port=' . $port;
            }

            try {
                $this->db = new PDO($conn_str, $user, $pass, $atributes);
            } catch (PDOException $e) {
                $logger=logger::getInstance();
                $logger->logErrorMessage("Unable to connect to the database.");
                $logger->logErrorMessage('---- Connection error ----> ' . $e->getMessage());
                $logger->writeErrors();
                return false;
            }
            $this->dbconnection = true;
        }
        return true;
    }

    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new dbModel();
        }
        return self::$instance;
    }
    public function getDB(): PDO {
        return $this->db;
    }

    private function currentHost(){
        $allowed_hosts = [
            "webapi.sandiego.edu",
            "staging-webapi.sandiego.edu",
            "build-webapi.sandiego.edu",
            "localhost",
            "localhost-webapi.sandiego.edu"
        ];

        $url = "//" . $_SERVER['HTTP_HOST'];
        $host = parse_url($url, PHP_URL_HOST);
        $matched_host = array_search($host, $allowed_hosts);

        if($matched_host !== false){
            return $allowed_hosts[$matched_host];
        } else {
            return $allowed_hosts[0];
        }
    }

    function activeEnv($currentHost){

        $activeEnv = null;

        if (isset($currentHost) && !empty($currentHost)) {
            switch ($currentHost) {
                case 'localhost-webapi.sandiego.edu':
                    $activeEnv = "local";
                    break;
                case 'build-webapi.sandiego.edu':
                    $activeEnv = "build";
                    break;
                case 'staging-webapi.sandiego.edu':
                    $activeEnv = "staging";
                    break;
                default:
                    $activeEnv = "prod";
            }
        }

        return $activeEnv;
    }


}