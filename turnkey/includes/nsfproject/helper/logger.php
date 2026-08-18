<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 3/13/26
 * Time: 2:05 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/

namespace Nsfproject\helper;

class logger
{
    private static ?\Nsfproject\helper\logger $instance = null;
    private array $messages = [];
    private array $errors = [];
    private array $success = [];

//    private function __construct() {
//        return self::getInstance();
//    }

    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new logger();
        }
        return self::$instance;
    }

    public function logUserMessage($message) {
        $this->messages[] = $message;
    }

//    public function logSuccessMessage($message) {
//        $this->success[] = $message;
//    }

    public function logErrorMessage($message) {
        $this->errors[] = $message;
    }
    public function writeErrors() {
        foreach ($this->errors as $error) {
            error_log($error);
        }
    }

    public function logSuccessMessage($message) {
        $this->success[] = $message;
    }

    public function getSuccessMessages() {
        return $this->success;
    }

    public function getUserMessages() {
        return $this->messages;
    }

//    public function getErrors() {
//        return implode(', ', $this->errors);
//    }

//    public function getSuccessMessages() {
//        return implode(', ', $this->success);
//    }

    public function displaySuccessMessage() {
        if (!empty($this->success)) : ?>
            <ul class="success-messages">
                <?php foreach ($this->success as $error): ?>
                    <li><?php echo htmlspecialchars($error); ?></li>
                <?php endforeach; ?>
            </ul>
        <?php endif;
    }
    public function displayUserMessage() {
        if (!empty($this->messages)) : ?>
            <ul class="error">
                <?php foreach ($this->messages as $error): ?>
                    <li><?php echo $error; ?></li>
                <?php endforeach; ?>
            </ul>
        <?php endif;
        $this->messages=[];
    }
}
