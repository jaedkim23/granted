<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/9/26
 * Time: 3:46 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/

namespace Nsfproject\models;

use Nsfproject\helper\dbModel;
use Nsfproject\helper\helper;
use Nsfproject\helper\logger;

class user
{
    private int $id;
    private string $email;
    private string $first;
    private string $last;
    private string $level;
    private dbModel $dbh;
    private string $passwordHash;


    public function __construct(dbModel $dbh)
    {
        $this->dbh = $dbh;
    }

    public function getId(): int
    {
        return $this->id;
    }

    public function setId(int $id): void
    {
        $this->id = $id;
    }

    public function getEmail(): string
    {
        return $this->email;
    }

    public function setEmail(string $email): void
    {
        $this->email = $email;
    }

    public function getFirst(): string
    {
        return $this->first;
    }

    public function setFirst(string $first): void
    {
        $this->first = $first;
    }

    public function getLast(): string
    {
        return $this->last;
    }

    public function setLast(string $last): void
    {
        $this->last = $last;
    }

    public function getLevel(): string
    {
        return $this->level;
    }
    public function setLevel(string $level): void
    {
        $this->level = $level;
    }

    private function pepperPassword($password) {
        $pepperedPassword=hash_hmac("sha256",$password, helper::$pepper);

        $this->passwordHash=password_hash($pepperedPassword,PASSWORD_DEFAULT);
    }

    public function useradd() {
        $problem=false;
        try {
            $email=$_POST['email'];
            $password=$_POST['password']??'temppassword';
            $first=$_POST['first'];
            $last=$_POST['last'];
            $level=$_POST['level']??'user';
            $this->pepperPassword($password);
            $sql = "INSERT INTO users (email, passwordhash, first, last, level) VALUES (?, ?, ?, ?, ?)";
            $dbh = $this->dbh;
            $stmt = $dbh->getDB()->prepare($sql);
            $stmt->execute([$email, $this->passwordHash, $first, $last, $level]);
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error adding user: " . $e->getMessage());
            $logger->logUserMessage('Database error adding user: ' . $e->getMessage());
            $logger->writeErrors();
            $problem=true;
            helper::displayAddUserForm();
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error adding user: " . $e->getMessage());
            $logger->logUserMessage('Error adding user: '.$e->getMessage());
            $logger->writeErrors();
            $problem=true;
            helper::displayAddUserForm();
        }
        if (!$problem) {
            $logger = logger::getInstance();
            $logger->logSuccessMessage("User added successfully: " . $email);
            $logger->displaySuccessMessage();
        }
    }

    /**
     * @param int $id
     * @return bool
     */
    public function userUpdate(int $id):bool {
        try {
            $dbh = $this->dbh;
            $email=$_POST['email'];
            $first=$_POST['first'];
            $last=$_POST['last'];
            $level=$_POST['level'];
            $sql = "update users set email=?, first=?, last=?, level=? where id=?";
            $stmt = $dbh->getDB()->prepare($sql);
            $stmt->execute([$email, $first, $last, $level, $id]);
            $dbh = null;
            $logger = logger::getInstance();
            $logger->logSuccessMessage("User updated successfully: " . $email);
            return true;
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error updating user: " . $e->getMessage());
            $logger->logUserMessage("Database error updating user.");
            $logger->writeErrors();
            return false;
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error updating user: " . $e->getMessage());
            $logger->logUserMessage("Error updating user.");
            $logger->writeErrors();
            return false;
        }
    }

    /**
     * @param string $email
     * @param string $password
     * @return bool
     */
    public function validateUser(string $email, string $password):bool {
        $sql = "SELECT * FROM users WHERE email=?";
        $dbh = $this->dbh;
        $stmt = $dbh->getDB()->prepare($sql);
        $stmt->execute([$email]);
        $user = $stmt->fetch();
        $dbh = null;
        if ($user) {
            $pepperedPassword=hash_hmac("sha256",$password, helper::$pepper);
            if (password_verify($pepperedPassword, $user['passwordhash'])) {
                $this->first=$user['first'];
                $this->last=$user['last'];
                $this->level=$user['level'];
                $this->email=$user['email'];
                $this->id=$user['id'];
                return true;
            }
        }
        return false;
    }

    public function sendPasswordResetLink($email,$newUser=false) {
        $problem=false;
        $dbh = $this->dbh;
        $sql = "SELECT * FROM users WHERE email=?";
        $dbh = $this->dbh;
        $stmt = $dbh->getDB()->prepare($sql);
        $stmt->execute([$email]);
        $user = $stmt->fetch();
        $dbh = null;
        if ($user) {
            $token = bin2hex(random_bytes(16));
            $expires = date('Y-m-d H:i:s', time() + 3600);
            try {
                $sql = "INSERT INTO password_resets (email, token, expires) VALUES (?, ?, ?)";
                $dbh = $this->dbh;
                $stmt = $dbh->getDB()->prepare($sql);
                $stmt->execute([$email, $token, $expires]);
                helper::sendPasswordResetEmail($user, $token,$newUser);
            } catch (\PDOException $e) {
                $logger = logger::getInstance();
                $logger->logErrorMessage("Database error sending password reset link: " . $e->getMessage());
                $logger->logUserMessage('Database error sending password reset link: ' . $e->getMessage());
                $logger->writeErrors();
                return false;
            } catch (\Exception $e) {
                $logger = logger::getInstance();
                $logger->logErrorMessage("Error sending password reset link: " . $e->getMessage());
                $logger->logUserMessage('Error sending password reset link: '.$e->getMessage());
                $logger->writeErrors();
                return false;
            }

        }
        return true;
    }
    public function updatePassword($email, $password) {
        try {
            $this->pepperPassword($password);
            $sql = "UPDATE users SET passwordhash=? WHERE email=?";
            $dbh = $this->dbh;
            $stmt = $dbh->getDB()->prepare($sql);
            $stmt->execute([$this->passwordHash, $email]);
            $dbh = null;
            $logger = logger::getInstance();
            $logger->logSuccessMessage("Password updated successfully: " . $email);
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error updating password: " . $e->getMessage());
            $logger->logUserMessage("Database error updating password.");
            $logger->writeErrors();
            return false;
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error updating password: " . $e->getMessage());
            $logger->logUserMessage("Error updating password");
            $logger->writeErrors();
            return false;
        }
        return true;
    }

    public function checkToken($token) {
        $dbh = $this->dbh;
        $sql = "SELECT * FROM password_resets WHERE token=? and expires >= now()";
        $stmt = $dbh->getDB()->prepare($sql);
        $stmt->execute([$token]);
        $user = $stmt->fetch();
        $dbh = null;
        if ($user) {
            return $user['email'];
        }
        return false;
    }

    public function setSession() {
        $_SESSION['email'] = $this->getEmail();
        //error_log($this->getEmail() . " " . $this->getFirst() . " " . $this->getLast() . "email, first and last");
        $_SESSION['first'] = $this->getFirst();
        $_SESSION['last'] = $this->getLast();
        $_SESSION['level'] = $this->getLevel();
        $_SESSION['id'] = $this->getId();
        //error_log('Session has been set to the above');
    }

    public function fetchUsers() {
        $dbh = $this->dbh;
        $sql = "select id, email, first, last, level from users order by last asc";
        $stmt = $dbh->getDB()->prepare($sql);
        $stmt->execute();
        $users = $stmt->fetchAll();
        $dbh = null;
        return $users;
    }

    public function deleteUser() {
        try {
            $dbh = $this->dbh;
            $sql = "DELETE FROM users WHERE id=?";
            $stmt = $dbh->getDB()->prepare($sql);
            $stmt->execute([$this->id]);
            $dbh = null;
            $logger = logger::getInstance();
            $logger->logSuccessMessage("User deleted successfully: " . $this->email);
            return true;
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error deleting user: " . $e->getMessage());
            $logger->logUserMessage("Database error deleting user.");
            $logger->writeErrors();
            return false;
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error deleting user: " . $e->getMessage());
            $logger->logUserMessage("Error deleting user.");
            $logger->writeErrors();
            return false;
        }
    }

    public function fetchUser($id,$how='id') {
        try {
            $dbh = $this->dbh;
            $sql = "select id, email, first, last, level from users where $how=?";
            $stmt = $dbh->getDB()->prepare($sql);
            $stmt->execute([$id]);
            $user = $stmt->fetch();
            $dbh = null;
            $this->setEmail($user['email']);
            $this->setFirst($user['first']);
            $this->setLast($user['last']);
            $this->setLevel($user['level']);
            $this->setid($user['id']);
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error fetching user: " . $e->getMessage());
            $logger->logUserMessage("Database error fetching user.");
            $logger->writeErrors();
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error fetching user: " . $e->getMessage());
            $logger->logUserMessage("Error fetching user.");
            $logger->writeErrors();
        }
    }

    public static function validateaddedituserform($id=null) {

        $problem = false;
        $logger = logger::getInstance();

        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            $email = trim($_POST['email'] ?? '');
            $first = trim($_POST['first'] ?? '');
            $last = trim($_POST['last'] ?? '');
            $level = trim($_POST['level'] ?? '');

            if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
                $problem = true;
                $logger->logUserMessage('Valid email is required.');
            }
            if (empty($first)) {
                $problem = true;
                $logger->logUserMessage('First name is required.');
            }
            if (empty($last)) {
                $problem = true;
                $logger->logUserMessage('Last name is required.');
            }
            if (empty($level)) {
                $problem = true;
                $logger->logUserMessage('Level is required.');
            }

            if (!$problem) {
                return true;
            } else {
                $logger->writeErrors();
                if ($_POST['submit'] ==='Add User') {
                    helper::displayAddUserForm();
                } else {
                    helper::displayEditUserForm($id);
                }
                // include 'views/addedituser.php';
                return false;
            }
        }
        return true;
    }
}