<?php
/**
 * Unit Tests for Pages Model
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

namespace Nsfproject\Tests;

use PHPUnit\Framework\TestCase;
use Nsfproject\models\pages;
use Nsfproject\helper\dbModel;
use PHPUnit\Framework\MockObject\MockObject;

class PagesTest extends TestCase
{
    private pages $pages;
    private MockObject $dbMock;

    protected function setUp(): void
    {
        $this->dbMock = $this->createMock(dbModel::class);
        $this->pages = new pages($this->dbMock);
    }

    /**
     * Test setting and getting title
     */
    public function testSetAndGetTitle(): void
    {
        $title = 'Test Page Title';
        $this->pages->setTitle($title);

        $this->assertEquals($title, $this->pages->getTitle());
    }

    /**
     * Test setting and getting parent ID
     */
    public function testSetAndGetParentid(): void
    {
        $parentid = 5;
        $this->pages->setParentid($parentid);

        $this->assertEquals($parentid, $this->pages->getParentid());
    }

    /**
     * Test setting and getting active status
     */
    public function testSetAndGetActive(): void
    {
        $this->pages->setActive(1);
        $this->assertEquals(1, $this->pages->getActive());

        $this->pages->setActive(0);
        $this->assertEquals(0, $this->pages->getActive());
    }

    /**
     * Test setting and getting secure status
     */
    public function testSetAndGetSecure(): void
    {
        $this->pages->setSecure(1);
        $this->assertEquals(1, $this->pages->getSecure());

        $this->pages->setSecure(0);
        $this->assertEquals(0, $this->pages->getSecure());
    }

    /**
     * Test setting and getting embed content
     */
    public function testSetAndGetEmbed(): void
    {
        $embed = '<iframe src="https://example.com"></iframe>';
        $this->pages->setEmbed($embed);

        $this->assertEquals($embed, $this->pages->getEmbed());
    }

    /**
     * Test setting and getting page content
     */
    public function testSetAndGetContent(): void
    {
        $content = 'This is page content';
        $this->pages->setContent($content);

        $this->assertEquals($content, $this->pages->getContent());
    }

    /**
     * Test empty parentid (null)
     */
    public function testNullParentid(): void
    {
        $this->pages->setParentid(null);
        $this->assertNull($this->pages->getParentid());
    }

    /**
     * Test empty embed content
     */
    public function testEmptyEmbed(): void
    {
        $this->pages->setEmbed('');
        $this->assertEquals('', $this->pages->getEmbed());
    }

    /**
     * Test empty page content
     */
    public function testEmptyContent(): void
    {
        $this->pages->setContent('');
        $this->assertEquals('', $this->pages->getContent());
    }

    /**
     * Test all properties together
     */
    public function testAllPropertiesTogether(): void
    {
        $this->pages->setTitle('Complete Page');
        $this->pages->setParentid(2);
        $this->pages->setActive(1);
        $this->pages->setSecure(0);
        $this->pages->setEmbed('<iframe></iframe>');
        $this->pages->setContent('Page content here');

        $this->assertEquals('Complete Page', $this->pages->getTitle());
        $this->assertEquals(2, $this->pages->getParentid());
        $this->assertEquals(1, $this->pages->getActive());
        $this->assertEquals(0, $this->pages->getSecure());
        $this->assertEquals('<iframe></iframe>', $this->pages->getEmbed());
        $this->assertEquals('Page content here', $this->pages->getContent());
    }

    /**
     * Test validateaddeditpageform - valid data
     */
    public function testValidateFormValidData(): void
    {
        $_POST['title'] = 'Valid Title';
        $_POST['active'] = 1;
        $_POST['secure'] = 0;

        $result = pages::validateaddeditpageform();
        $this->assertTrue($result);

        unset($_POST['title'], $_POST['active'], $_POST['secure']);
    }

    /**
     * Test validateaddeditpageform - missing title
     */
    public function testValidateFormMissingTitle(): void
    {
        $_POST['title'] = '';
        $_POST['active'] = 1;
        $_POST['secure'] = 0;

        $result = pages::validateaddeditpageform();
        $this->assertFalse($result);

        unset($_POST['title'], $_POST['active'], $_POST['secure']);
    }

    /**
     * Test validateaddeditpageform - invalid active value
     */
    public function testValidateFormInvalidActive(): void
    {
        $_POST['title'] = 'Title';
        $_POST['active'] = 2; // Invalid, should be 0 or 1
        $_POST['secure'] = 0;

        $result = pages::validateaddeditpageform();
        $this->assertFalse($result);

        unset($_POST['title'], $_POST['active'], $_POST['secure']);
    }

    /**
     * Test validateaddeditpageform - invalid secure value
     */
    public function testValidateFormInvalidSecure(): void
    {
        $_POST['title'] = 'Title';
        $_POST['active'] = 1;
        $_POST['secure'] = 'yes'; // Invalid, should be numeric 0 or 1

        $result = pages::validateaddeditpageform();
        $this->assertFalse($result);

        unset($_POST['title'], $_POST['active'], $_POST['secure']);
    }

    /**
     * Test validateaddeditpageform - numeric parentid passes
     *
     * Note: parentid is not validated by the form validation function,
     * only title, active, and secure are validated
     */
    public function testValidateFormWithParentidNotValidated(): void
    {
        $_POST['title'] = 'Child Page';
        $_POST['parentid'] = 'abc'; // Not validated - passes anyway
        $_POST['active'] = 1;
        $_POST['secure'] = 0;

        $result = pages::validateaddeditpageform();
        // parentid is not validated in the form validation function
        $this->assertTrue($result);

        unset($_POST['title'], $_POST['parentid'], $_POST['active'], $_POST['secure']);
    }

    /**
     * Test title as string type
     */
    public function testTitleIsString(): void
    {
        $this->pages->setTitle('String Title');
        $this->assertIsString($this->pages->getTitle());
    }

    /**
     * Test active as integer
     */
    public function testActiveIsInteger(): void
    {
        $this->pages->setActive(1);
        $this->assertIsInt($this->pages->getActive());
    }

    /**
     * Test secure as integer
     */
    public function testSecureIsInteger(): void
    {
        $this->pages->setSecure(0);
        $this->assertIsInt($this->pages->getSecure());
    }

    /**
     * Test constructor sets dbh
     */
    public function testConstructorSetsDbh(): void
    {
        $pages = new pages($this->dbMock);
        $this->assertNotNull($pages);
    }

    /**
     * Test getting database reference
     */
    public function testGetDB(): void
    {
        $result = $this->pages->getDB();
        $this->assertSame($this->dbMock, $result);
    }

    /**
     * Test special characters in title
     */
    public function testSpecialCharactersInTitle(): void
    {
        $title = 'Page & Title <with> "Special" Characters\'';
        $this->pages->setTitle($title);

        $this->assertEquals($title, $this->pages->getTitle());
    }

    /**
     * Test large content value
     */
    public function testLargeContentValue(): void
    {
        $largeContent = str_repeat('This is content. ', 100);
        $this->pages->setContent($largeContent);

        $this->assertEquals($largeContent, $this->pages->getContent());
    }

    /**
     * Test validateaddeditpageform - valid with numeric parentid
     */
    public function testValidateFormValidParentid(): void
    {
        $_POST['title'] = 'Child Page';
        $_POST['parentid'] = 5;
        $_POST['active'] = 1;
        $_POST['secure'] = 0;

        $result = pages::validateaddeditpageform();
        $this->assertTrue($result);

        unset($_POST['title'], $_POST['parentid'], $_POST['active'], $_POST['secure']);
    }
}


