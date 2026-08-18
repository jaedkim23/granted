<?php
/**
 * Unit Tests for Navigation Model
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

namespace Nsfproject\Tests;

use PHPUnit\Framework\TestCase;
use Nsfproject\models\navigation;
use Nsfproject\helper\dbModel;
use PHPUnit\Framework\MockObject\MockObject;

class NavigationTest extends TestCase
{
    private navigation $navigation;
    private MockObject $dbMock;

    protected function setUp(): void
    {
        // Mock the $_SERVER global to avoid direct access
        $_SERVER['PHP_SELF'] = '/index.php';

        $this->dbMock = $this->createMock(dbModel::class);
        $this->navigation = new navigation($this->dbMock);
    }

    protected function tearDown(): void
    {
        // Clean up $_SERVER
        unset($_SERVER['PHP_SELF']);
    }

    /**
     * Test navigation constructor with regular path
     */
    public function testConstructorWithRegularPath(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        $nav = new navigation($this->dbMock);
        $this->assertNotNull($nav);
    }

    /**
     * Test navigation constructor with manage path
     */
    public function testConstructorWithManagePath(): void
    {
        $_SERVER['PHP_SELF'] = '/manage/index.php';

        $nav = new navigation($this->dbMock);
        $this->assertNotNull($nav);
    }

    /**
     * Test buildNestedNavigation returns string
     */
    public function testBuildNestedNavigationReturnsString(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        // Set navigation data directly using reflection
        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, []);

        $result = $this->navigation->buildNestedNavigation();

        $this->assertIsString($result);
    }

    /**
     * Test buildNestedNavigation includes home link
     */
    public function testBuildNestedNavigationIncludesHome(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, []);

        // Mock WEB_PATH constant
        if (!defined('WEB_PATH')) {
            define('WEB_PATH', '/test');
        }

        $result = $this->navigation->buildNestedNavigation();

        $this->assertStringContainsString('Home', $result);
    }

    /**
     * Test buildNestedNavigation with parent pages
     */
    public function testBuildNestedNavigationWithParentPages(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        if (!defined('WEB_PATH')) {
            define('WEB_PATH', '/test');
        }

        $pages = [
            [
                'id' => 1,
                'title' => 'Parent Page',
                'parentid' => null,
                'url' => 'parent-page'
            ]
        ];

        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, $pages);

        $result = $this->navigation->buildNestedNavigation();

        $this->assertStringContainsString('Parent Page', $result);
    }

    /**
     * Test buildNestedNavigation with nested child pages
     */
    public function testBuildNestedNavigationWithChildPages(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        if (!defined('WEB_PATH')) {
            define('WEB_PATH', '/test');
        }

        $pages = [
            [
                'id' => 1,
                'title' => 'Parent',
                'parentid' => null,
                'url' => 'parent'
            ],
            [
                'id' => 2,
                'title' => 'Child',
                'parentid' => 1,
                'url' => 'child'
            ]
        ];

        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, $pages);

        $result = $this->navigation->buildNestedNavigation();

        $this->assertStringContainsString('Parent', $result);
        $this->assertStringContainsString('Child', $result);
        $this->assertStringContainsString('<ul>', $result);
    }

    /**
     * Test buildNestedNavigation HTML structure
     */
    public function testBuildNestedNavigationHtmlStructure(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        if (!defined('WEB_PATH')) {
            define('WEB_PATH', '/');
        }

        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, []);

        $result = $this->navigation->buildNestedNavigation();

        // Check for basic HTML structure
        $this->assertStringContainsString('<ul>', $result);
        $this->assertStringContainsString('</ul>', $result);
        $this->assertStringContainsString('<li>', $result);
        $this->assertStringContainsString('</li>', $result);
        $this->assertStringContainsString('<a href=', $result);
    }

    /**
     * Test getPages with mock database
     *
     * @note This test is skipped as it requires direct database property access
     *       The actual getPages method functionality is tested via integration
     */
    public function testGetPackagesWithMockDatabase(): void
    {
        $this->markTestSkipped('Database integration test - requires database setup');
    }

    /**
     * Test buildNestedNavigation with manage path
     */
    public function testBuildNestedNavigationWithManagePath(): void
    {
        $_SERVER['PHP_SELF'] = '/manage/index.php';

        if (!defined('WEB_PATH')) {
            define('WEB_PATH', '/');
        }

        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, []);

        $result = $this->navigation->buildNestedNavigation();

        // Should contain manage path
        $this->assertStringContainsString('manage', $result);
    }

    /**
     * Test buildNestedNavigation filters parent pages correctly
     */
    public function testBuildNestedNavigationFiltersParents(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        if (!defined('WEB_PATH')) {
            define('WEB_PATH', '/');
        }

        $pages = [
            [
                'id' => 1,
                'title' => 'Parent 1',
                'parentid' => null,
                'url' => 'parent1'
            ],
            [
                'id' => 2,
                'title' => 'Parent 2',
                'parentid' => null,
                'url' => 'parent2'
            ],
            [
                'id' => 3,
                'title' => 'Child',
                'parentid' => 1,
                'url' => 'child'
            ]
        ];

        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, $pages);

        $result = $this->navigation->buildNestedNavigation();

        $this->assertStringContainsString('Parent 1', $result);
        $this->assertStringContainsString('Parent 2', $result);
        $this->assertStringContainsString('Child', $result);
    }

    /**
     * Test multiple levels of nesting
     */
    public function testMultipleLevelsOfNesting(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        if (!defined('WEB_PATH')) {
            define('WEB_PATH', '/');
        }

        $pages = [
            [
                'id' => 1,
                'title' => 'Root',
                'parentid' => null,
                'url' => 'root'
            ],
            [
                'id' => 2,
                'title' => 'Level 1',
                'parentid' => 1,
                'url' => 'level1'
            ]
        ];

        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, $pages);

        $result = $this->navigation->buildNestedNavigation();

        $this->assertStringContainsString('Root', $result);
        $this->assertStringContainsString('Level 1', $result);
    }

    /**
     * Test buildNestedNavigation returns valid HTML
     */
    public function testBuildNestedNavigationValidHtml(): void
    {
        $_SERVER['PHP_SELF'] = '/index.php';

        if (!defined('WEB_PATH')) {
            define('WEB_PATH', '/');
        }

        $reflection = new \ReflectionClass($this->navigation);
        $property = $reflection->getProperty('navigation');
        $property->setAccessible(true);
        $property->setValue($this->navigation, []);

        $result = $this->navigation->buildNestedNavigation();

        // Count opening and closing tags
        $openCount = substr_count($result, '<ul>');
        $closeCount = substr_count($result, '</ul>');

        $this->assertEquals($openCount, $closeCount);
    }
}


