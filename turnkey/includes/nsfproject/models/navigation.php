<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/10/26
 * Time: 4:22 PM
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
use Nsfproject\helper\logger;

class navigation
{
    private dbModel $db;
    private string $table;
    private array $navigation;
    const INACTIVE_STATUS = 0;

    public function __construct($dbh) {
        $this->db = $dbh;
        if (strstr($_SERVER['PHP_SELF'],'manage')) {
            $this->table='adminpages';
        } else {
            $this->table='pages';
        }
    }


    public function getPages($secure) {
        $sql="SELECT * FROM {$this->table} WHERE active='1'";
        $end=" ORDER BY id ASC";
        if (!$secure) {
             $sql.=" AND secure=".navigation::INACTIVE_STATUS;
        }
        $sql .= $end;
       // error_log($sql);
        try {
            $stmt = $this->db->db->prepare($sql);
            $stmt->execute();
            $this->navigation=$stmt->fetchAll();
        } catch (\PDOException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Database error retrieving pages: " . $e->getMessage());
            $logger->writeErrors();
            $this->navigation=array();
            return false;
        } catch (\Exception $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage("Error retrieving pages: " . $e->getMessage());
            $logger->writeErrors();
            $this->navigation=array();
          return false;
        }
        return true;
    }

    public function buildNestedNavigation() {
        $manage='';
        if (strstr($_SERVER['PHP_SELF'],'manage')) {
            $manage='/manage';
        }
        $pages = $this->navigation;
        $nav = "<ul>
                   <li><a href='".WEB_PATH . "{$manage}/'>Home</a>";

        $parentPages = array_filter($pages, function($page) {
            return $page['parentid'] === null;
        });
       // error_log(var_export($parentPages, true));
        foreach ($parentPages as $parent) {
            $childPages = array_filter($pages, function($page) use ($parent) {
                return $page['parentid'] == $parent['id'];
            });
            if ($parent['is_default']===0) {
                $url = $this->buildURL($parent);
                $nav .= "<li><a href=\"" . WEB_PATH . "$manage/{$url}\">{$parent['title']}</a>";
            }
         //   error_log(var_export($childPages, true));
            if (!empty($childPages)) {
                $nav .= '<ul>';
                foreach ($childPages as $child) {
                    $url = $this->buildURL($child);
                    $nav .= "<li><a href=\"". WEB_PATH. "$manage/{$url}\">{$child['title']}</a></li>";
                }
                $nav .= '</ul>';
            }
            $nav .= '</li>';
        }
        $nav .= '</ul>';
        return $nav;
    }

    private function buildURL($page) {
        if (isset($page['url'])) {
            return $page['url'];
        }
        $url='pages/'.$page['id'];
        return $url;
    }
}