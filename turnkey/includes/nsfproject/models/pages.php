<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/21/26
 * Time: 3:44 PM
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
use function PHPUnit\Framework\isNull;

class pages
{
    private $dbh;
    private $title;
    private $parentid;
    private $active;
    private $secure;
    private $embed;
    private $content;
    private $default;

    public function __construct($dbh)
    {
        $this->dbh = $dbh;
    }

    public function setTitle($title)
    {
        $this->title = $title;
    }

    public function setParentid($parentid)
    {
        $this->parentid = $parentid;
    }

    public function setActive($active)
    {
        $this->active = $active;
    }

    public function setSecure($secure)
    {
        $this->secure = $secure;
    }

    public function setEmbed($embed)
    {
        $this->embed = $embed;
    }

    public function setContent($content)
    {
        $this->content = $content;
    }

    public function getDB()
    {
        return $this->dbh;
    }

    public function getTitle()
    {
        return $this->title;
    }

    public function getParentid()
    {
        return $this->parentid;
    }

    public function getActive()
    {
        return $this->active;
    }

    public function getSecure()
    {
        return $this->secure;
    }

    public function getEmbed()
    {
        return $this->embed;
    }
    public function getDefault()
    {
        return $this->default;
    }
    public function setDefault($default)
    {
        $this->default = $default;
    }

    public function getContent()
    {
        return $this->content;
    }

    public function pageadd() {
        $problem = false;
        try {
            $title = $_POST['title'];
            $parentid = is_numeric($_POST['parentid']) ? $_POST['parentid'] : null;
            $active = $_POST['active'] ?? 0;
            $secure = $_POST['secure'] ?? 0;
            $embed = $_POST['embed'] ?? '';
            $content = $_POST['content'] ?? '';
            $default = $_POST['is_default'] ?? '0';

            $sql = "INSERT INTO pages (title, parentid, active, secure, embed, content, is_default) VALUES (?, ?, ?, ?, ?, ?,?)";
            $dbh = $this->dbh;
            $stmt = $dbh->getDB()->prepare($sql);
            $mycontent=[$title, $parentid, $active, $secure, $embed, $content, $default];
            $stmt->execute($mycontent);
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error adding page: " . $e->getMessage() . " Query: $sql, prepared values: " . var_export($mycontent,true));
            $logger->logUserMessage('Database error adding page: ' . $e->getMessage());
            $logger->writeErrors();
            $problem = true;
            helper::displayAddPageForm();
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error adding page: " . $e->getMessage());
            $logger->logUserMessage('Error adding page: ' . $e->getMessage());
            $logger->writeErrors();
            $problem = true;
            helper::displayAddPageForm();
        }
        if (!$problem) {
            $logger = logger::getInstance();
            $logger->logSuccessMessage("Page added successfully: " . $title);
            $logger->displaySuccessMessage();
            return true;
        }
        return false;
    }

    public function pageUpdate($id) {
        $problem = false;
        try {
            $title = $_POST['title'];
            $parentid = is_numeric($_POST['parentid']) ? $_POST['parentid'] : null;
            $active = $_POST['active'] ?? 0;
            $secure = $_POST['secure'] ?? 0;
            $embed = $_POST['embed'] ?? '';
            $content = $_POST['content'] ?? '';
            $default = $_POST['is_default'] ?? '0';
            $sql = "update pages set title=?, parentid=?, active=?, secure=?, embed=?, content=?, is_default=? where id=?";
            $dbh = $this->dbh;
            $stmt = $dbh->getDB()->prepare($sql);
            $mycontent=[$title, $parentid, $active, $secure, $embed, $content, $default, $id];
            $stmt->execute($mycontent);
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error adding page: " . $e->getMessage() . " Query: $sql, prepared values: " . var_export($mycontent,true));
            $logger->logUserMessage('Database error updating page: ' . $e->getMessage());
            $logger->writeErrors();
            $problem = true;
            helper::displayAddPageForm();
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error updating page: " . $e->getMessage());
            $logger->logUserMessage('Error updating page: ' . $e->getMessage());
            $logger->writeErrors();
            $problem = true;
            helper::displayAddPageForm();
        }
        if (!$problem) {
            $logger = logger::getInstance();
            $logger->logSuccessMessage("Page updated successfully: " . $title);
            $logger->displaySuccessMessage();
            return true;
        }
        return false;
    }

    public static function validateaddeditpageform($id = null) {
        $logger = logger::getInstance();
        $title = $_POST['title'] ?? null;
        $parentid = is_numeric($_POST['parentid']) ? $_POST['parentid'] : null;
        $active = $_POST['active'] ?? null;
        $secure = $_POST['secure'] ?? null;
        $embed = $_POST['embed'] ?? null;
        $content = $_POST['content'] ?? null;

        if (empty($title)) {
            $logger->logUserMessage('Title is required.');
            return false;
        }
        if (!is_null($parentid) && !is_numeric($parentid)) {
            $logger->logUserMessage('Parent ID must be a number.');
            return false;
        }

        if (!is_numeric($active) || !in_array($active, [0, 1])) {
            $logger->logUserMessage('Active must be Yes or No.');
            return false;
        }
        if (!is_numeric($secure) || !in_array($secure, [0, 1])) {
            $logger->logUserMessage('Secure must be Yes or No.');
            return false;
        }
        // embed and content can be empty strings, no validation needed
        return true;
    }

    public function fetchPage($id, $doDisplay=true) {
        $dbh = $this->dbh;
        if ($id === 'default') {
            $id=1;
            $sql = "SELECT * FROM pages WHERE is_default = ? LIMIT 1";
        } else {
            $sql = "SELECT * FROM pages WHERE id = ? LIMIT 1";
        }
        $stmt = $dbh->getDB()->prepare($sql);
        $stmt->execute([$id]);
        $page = $stmt->fetch();
        if ($doDisplay) {
            helper::displayPage($page);
        } else {
            $this->id=$page['id'];
            $this->title=$page['title'];
            $this->parentid=$page['parentid'];
            $this->active=$page['active'];
            $this->secure=$page['secure'];
            $this->embed=$page['embed'];
            $this->content=$page['content'];
            $this->default=$page['is_default'];
        }

    }

    public function fetchPages() {
        $dbh=$this->dbh;
        $sql = "select id, title, embed,content,active,secure,is_default,parentid from pages order by id asc";
        try {
            $stmt = $dbh->getDB()->prepare($sql);
            $stmt->execute();
            $pages = $stmt->fetchAll();
            return $pages;
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error retrieving pages: " . $e->getMessage() . " Query: $sql");
            $logger->logUserMessage('Database error retrieving pages: ' . $e->getMessage());
            $logger->writeErrors();
            return [];
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error retrieving pages: " . $e->getMessage());
            $logger->logUserMessage('Error retrieving pages: ' . $e->getMessage());
            $logger->writeErrors();
            return [];
        }
    }
}