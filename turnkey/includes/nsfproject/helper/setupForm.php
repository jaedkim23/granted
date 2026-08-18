<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/7/26
 * Time: 3:11 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/

namespace Nsfproject\helper;

class setupForm
{
    var $form;
    var $translate=array(
        'siteTitle'=>'Site Title',
        'schoolName'=>'School Name',
        'resourceLink'=>'Resource Link',
        'override'=>'CSS Override file name',
        'includesdir'=>'Includes Directory'
    );
    var $header;
    var $footer;
    var $database;
    var $CSS;
    var $includesdir;
/* setupform works with the Ini file, example output from readini:
array ( 'header' =>
            array ( 'siteTitle' => 'NSF Project Dashboard',
                    'logo' => 'https://www.sandiego.edu/assets/global/images/sandiego-logo.png',
                    'schoolName' => 'University of San Diego', ),
        'footer' =>
            array ( 'email' => 'bryant@sandiego.edu',
                    'copyright' => 'Copyright 2024 University of San Diego. All rights reserved.',
                    'logo' => '',
                    'schoolName' => '',
                    'resourceLink' =>
                        array ( 0 => '[University of San Diego](https://www.sandiego.edu/)', ), ),
        'database' =>
            array ( 'host' => 'simmons.sandiego.edu',
                    'port' => 3306,
                    'dbname' => 'nsfproject',
                    'user' => 'nsfproject',
                    'password' => '6o6lglnkpF$0', ),
        'CSS' => array ( 'override' => '', ), )
*/
    public function __construct($array,$includesdir) {
        if ($this->validateArray($array)) {
            $this->header = $array['header'];
            $this->footer = $array['footer'];
            $this->database = $array['database'];
            $this->CSS = $array['CSS'];
            if (!empty($array['includesdir']['includesdir'])) {
                $this->includesdir = $array['includesdir'];
            } else {
                $this->includesdir=['includesdir'=>$includesdir];
            }

        } else {
            throw new \InvalidArgumentException("Invalid configuration array provided to setupForm.");
        }
    }

    private function validateArray($array) {
        if (!is_array($array)) {
            return false;
        }
        $requiredSections = ['header', 'footer', 'database', 'CSS'];
        foreach ($requiredSections as $section) {
            if (!isset($array[$section])) {
                return false;
            }
        }
        return true;
    }
    
    private function labelInput($displaykey, $formvalue, $key,$required=true) {
        $return = "<div class='labelInput'>";
        $return .="<label for='{$key}'>{$displaykey}</label>\r\n";
        $return .="<input type='text' name='{$key}' value='{$formvalue}' ".($required?"required":"")."/>\r\n";
        $return .="</div>";
        return $return;
    }

    private function labelTextArea($formkey, $formvalue)
    {
        $return = "<div class= 'labelInput'>";
        $return .="<label for='{$formkey}'>{$formkey}</label>\r\n";
        $return .="<textarea id='{$formkey}'  name='{$formkey}'>{$formvalue}</textarea>\r\n";
        $return .="</div>";
        return $return;
    }

    public function buildSetupForm() {
        // This method would generate the HTML form based on the properties of the class.
        $this->form='<fieldset><legend>Header Settings</legend>' . "\r\n";
        foreach($this->header as $key => $value) {
            $formkey=$this->translate[$key]??$key;
            $formvalue=$value;
            $this->form .= $this->labelInput($formkey, $formvalue,$key);
        }
        $this->form .="</fieldset>\r\n";
        $this->form .='<fieldset><legend>Footer Settings</legend>' . "\r\n";
        foreach($this->footer as $key => $value) {
            $formkey=$this->translate[$key]??$key;
            if ($key === 'resourceLink') {
                $mykey=$key . "[]";
                foreach ($value as $link) {
                    $formvalue=$link;
                    $this->form .= $this->labelInput($formkey, $formvalue,$mykey);
                }
                $this->form .= "<p>You will be able to add more resource links after completing setup.</p>\r\n";
            } else {
                $formvalue = $value;
                $this->form .= $this->labelInput($formkey, $formvalue,$key);
            }
        }
        $this->form .="</fieldset>\r\n";
        $this->form .='<fieldset><legend>Database Connection Settings</legend>' . "\r\n";
        foreach ($this->database as $key => $value) {
            $formkey=$this->translate[$key]??$key;
            $formvalue=$value;
            $this->form .= $this->labelInput($formkey, $formvalue,$key);

        }
        $this->form .="</fieldset>\r\n";
        $this->form.='<fieldset><legend>Includes Directory Location</legend>' . "\r\n";
        foreach($this->includesdir as $key => $value) {
            $formkey=$this->translate[$key]??$key;
            $formvalue=$value;
            $this->form .= $this->labelInput($formkey, $formvalue,$key);
        }
        $this->form .="</fieldset>\r\n";
        $this->form .='<fieldset><legend>CSS Override File</legend>' . "\r\n";
        foreach ($this->CSS as $key => $value) {
            $formkey=$this->translate[$key]??$key;
            $formvalue=$value;
            $this->form .= $this->labelInput($formkey, $formvalue,$key,false);
            $this->form .= "<p>This should be the webpath to where you have placed your CSS override file.  For example, if you have placed your CSS override file in the css directory of this project, you would enter '/nsfproject/assets/nsfproject/css/yourfilename.css'.</p>\r\n";
        }
        $this->form .="</fieldset>\r\n";
    }

    public function display($url) {
        echo "<form action='{$url}' method='post'>\r\n";
        echo $this->form;
        echo "<button class='button' type='submit'>Submit Information</button>\r\n";
        echo "</form>\r\n";
    }
}