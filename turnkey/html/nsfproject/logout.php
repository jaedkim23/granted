<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/10/26
 * Time: 3:12 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
session_start();
session_destroy();
header('Location: index.php');