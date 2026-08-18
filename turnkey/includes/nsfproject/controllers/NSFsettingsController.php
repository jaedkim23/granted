<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 3/13/26
 * Time: 1:46 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/


namespace Nsfproject\controllers;
require_once (__DIR__ . '/../vendor/autoload.php');
use Matomo\Ini\IniReader;
use Matomo\Ini\IniWriter;
use Matomo\Ini\IniReadingException;
use Matomo\Ini\IniWritingException;
use Exception;
use Nsfproject\helper\logger;



class NSFsettingsController
{
    private $config; //location of conf.ini
    private $exampleConfig; // location of example.ini (for setup)
    private $settings;

    public function __construct() {
        $this->config = __DIR__ . '/../conf/conf.ini';
        $this->exampleConfig = __DIR__ . '/../conf/example.ini';
        if (!file_exists($this->config)) {
            if (!file_exists($this->exampleConfig)) {
                throw new Exception('Your installation is incomplete. You are missing your configuration file, or the example configuration file.');
            } else {
                if (!copy($this->exampleConfig, $this->config)) {
                    throw new Exception('The webserver process is unable to write to the directory where the NSF Project files are stored. Write destination: ' . $this->config . '.');
                }
            }
        }
    }

    public function readConfig()
    {
        $reader = new IniReader();
        try {
            $this->settings = $reader->readFile($this->config);
        } catch (IniReadingException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage('Failed to read configuration file: ' . $e->getMessage());
            throw new Exception('Failed to read configuration file: ' . $e->getMessage());
        }
    }

    public function writeConfig() {
        $writer = new IniWriter();
        try {
            $writer->writeToFile($this->config, $this->settings);
        } catch (IniWritingException $e) {
            $logger = logger::getInstance();
            $logger->logErrorMessage('Failed to write configuration file: ' . $e->getMessage());
            $logger->logUserMessage('Unable to write configuration file. Please check the error log for details.');
           return(false);
        }
        return true;
    }

    public function validateConfigForm() {
        $errors = [];
        $logger = logger::getInstance();

        // Validate header section
        if (empty($_POST['header']['siteTitle'])) {
            $errors[] = 'Site title is required.';
        }

        if (empty($_POST['header']['logo'])) {
            $errors[] = 'Logo is required.';
        }

        if (empty($_POST['header']['schoolName'])) {
            $errors[] = 'School name is required.';
        }

        // Validate footer section
        if (!empty($_POST['footer']['emailSender']) && !filter_var($_POST['footer']['emailSender'], FILTER_VALIDATE_EMAIL)) {
            $errors[] = 'Footer email sender must be a valid email address.';
        }

        if (empty($_POST['footer']['copyright'])) {
            $errors[] = 'Copyright is required.';
        }

        if (empty($_POST['footer']['schoolName'])) {
            $errors[] = 'Footer school name is required.';
        }

        // Validate resourceLinks array
        if (isset($_POST['footer']['resourceLink']) && is_array($_POST['footer']['resourceLink'])) {
            foreach ($_POST['footer']['resourceLink'] as $index => $link) {
                if (!empty($link) && !preg_match('/^\[([^\]]+)\]\(([^)]+)\)$/', $link)) {
                    $errors[] = "Resource link " . ($index + 1) . " must be in Markdown format: [Text](URL)";
                }
            }
        }

        // Validate database section
        if (empty($_POST['database']['host'])) {
            $errors[] = 'Database host is required.';
        }

        if (empty($_POST['database']['dbname'])) {
            $errors[] = 'Database name is required.';
        }

        if (empty($_POST['database']['user'])) {
            $errors[] = 'Database user is required.';
        }

        if (isset($_POST['database']['port']) && !empty($_POST['database']['port']) && !is_numeric($_POST['database']['port'])) {
            $errors[] = 'Database port must be a number.';
        }

        // Validate includesdir section
        if (empty($_POST['includesdir']['includesdir'])) {
            $errors[] = 'Includes directory is required.';
        }

        // Log validation errors
        if (!empty($errors)) {
            foreach ($errors as $error) {
                $logger->logUserMessage($error);
            }
            $logger->writeErrors();
            return false;
        }

        return true;
    }

    public function getSettings()
    {
        return $this->settings;
    }

    public function updateSettingsFromForm() {
        $logger = logger::getInstance();

        try {
            // Start with current settings or empty array
            $newSettings = $this->settings ?? [];

            // Update header section
            $newSettings['header']['siteTitle'] = trim($_POST['header']['siteTitle'] ?? '');
            $newSettings['header']['logo'] = trim($_POST['header']['logo'] ?? '');
            $newSettings['header']['schoolName'] = trim($_POST['header']['schoolName'] ?? '');

            // Update footer section
            $newSettings['footer']['emailSender'] = trim($_POST['footer']['emailSender'] ?? '');
            $newSettings['footer']['copyright'] = trim($_POST['footer']['copyright'] ?? '');
            $newSettings['footer']['logo'] = trim($_POST['footer']['logo'] ?? '');
            $newSettings['footer']['schoolName'] = trim($_POST['footer']['schoolName'] ?? '');

            // Handle resourceLinks array - filter out empty values
            $resourceLinks = [];
            if (isset($_POST['footer']['resourceLink']) && is_array($_POST['footer']['resourceLink'])) {
                foreach ($_POST['footer']['resourceLink'] as $link) {
                    $trimmedLink = trim($link);
                    if (!empty($trimmedLink)) {
                        $resourceLinks[] = $trimmedLink;
                    }
                }
            }
            $newSettings['footer']['resourceLink'] = $resourceLinks;

            // Update database section
            $newSettings['database']['host'] = trim($_POST['database']['host'] ?? '');
            $newSettings['database']['port'] = trim($_POST['database']['port'] ?? '');
            $newSettings['database']['dbname'] = trim($_POST['database']['dbname'] ?? '');
            $newSettings['database']['user'] = trim($_POST['database']['user'] ?? '');
            $newSettings['database']['password'] = trim($_POST['database']['password'] ?? '');

            // Update CSS section
            $newSettings['CSS']['override'] = trim($_POST['CSS']['override'] ?? '');

            // Update includesdir section
            $newSettings['includesdir']['includesdir'] = trim($_POST['includesdir']['includesdir'] ?? '');

            // Update settings and write to file
            $this->settings = $newSettings;

        } catch (Exception $e) {
            $logger->logErrorMessage('Error updating settings from form: ' . $e->getMessage());
            $logger->logUserMessage('An error occurred while updating the configuration.');
            $logger->writeErrors();
            return false;
        }
        return true;
    }
}
