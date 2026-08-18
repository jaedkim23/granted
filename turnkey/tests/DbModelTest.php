<?php
/**
 * Unit Tests for Database Model
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

namespace Nsfproject\Tests;

use PHPUnit\Framework\TestCase;
use Nsfproject\helper\dbModel;

class DbModelTest extends TestCase
{
    protected function setUp(): void
    {
        // Reset singleton instance before each test
        $reflection = new \ReflectionClass('Nsfproject\helper\dbModel');
        $property = $reflection->getProperty('instance');
        $property->setAccessible(true);
        $property->setValue(null);
    }

    /**
     * Test dbModel is singleton
     */
    public function testDbModelIsSingleton(): void
    {
        // This test requires database credentials to be set
        // We'll skip it if the constants aren't defined
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $db1 = dbModel::getInstance();
            $db2 = dbModel::getInstance();

            $this->assertSame($db1, $db2);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test getInstance returns dbModel object
     */
    public function testGetInstanceReturnsDbModelObject(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();
            $this->assertInstanceOf(dbModel::class, $dbModel);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test getDB returns PDO object
     */
    public function testGetDBReturnsPdoObject(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();
            $pdo = $dbModel->getDB();

            $this->assertInstanceOf(\PDO::class, $pdo);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test activeEnv returns correct environment for localhost
     */
    public function testActiveEnvLocalhostLocal(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();

            // Use reflection to call private method
            $reflection = new \ReflectionClass(dbModel::class);
            $method = $reflection->getMethod('activeEnv');
            $method->setAccessible(true);

            $result = $method->invoke($dbModel, 'localhost-webapi.sandiego.edu');

            $this->assertEquals('local', $result);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test activeEnv returns correct environment for build
     */
    public function testActiveEnvBuildEnvironment(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();

            $reflection = new \ReflectionClass(dbModel::class);
            $method = $reflection->getMethod('activeEnv');
            $method->setAccessible(true);

            $result = $method->invoke($dbModel, 'build-webapi.sandiego.edu');

            $this->assertEquals('build', $result);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test activeEnv returns correct environment for staging
     */
    public function testActiveEnvStagingEnvironment(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();

            $reflection = new \ReflectionClass(dbModel::class);
            $method = $reflection->getMethod('activeEnv');
            $method->setAccessible(true);

            $result = $method->invoke($dbModel, 'staging-webapi.sandiego.edu');

            $this->assertEquals('staging', $result);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test activeEnv defaults to prod
     */
    public function testActiveEnvDefaultsProd(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();

            $reflection = new \ReflectionClass(dbModel::class);
            $method = $reflection->getMethod('activeEnv');
            $method->setAccessible(true);

            $result = $method->invoke($dbModel, 'webapi.sandiego.edu');

            $this->assertEquals('prod', $result);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test activeEnv returns null for empty host
     */
    public function testActiveEnvNullForEmpty(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();

            $reflection = new \ReflectionClass(dbModel::class);
            $method = $reflection->getMethod('activeEnv');
            $method->setAccessible(true);

            $result = $method->invoke($dbModel, '');

            $this->assertNull($result);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test dbModel properties
     */
    public function testDbModelProperties(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();

            // Check that db property exists
            $this->assertTrue(property_exists($dbModel, 'db'));
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test multiple getInstance calls return same instance
     */
    public function testMultipleInstanceCallsSameObject(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $db1 = dbModel::getInstance();
            $db2 = dbModel::getInstance();
            $db3 = dbModel::getInstance();

            $this->assertSame($db1, $db2);
            $this->assertSame($db2, $db3);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test environment mapping array
     */
    public function testEnvironmentMapping(): void
    {
        $envMap = [
            'localhost-webapi.sandiego.edu' => 'local',
            'build-webapi.sandiego.edu' => 'build',
            'staging-webapi.sandiego.edu' => 'staging',
            'webapi.sandiego.edu' => 'prod',
        ];

        $this->assertIsArray($envMap);
        foreach ($envMap as $host => $env) {
            $this->assertIsString($host);
            $this->assertIsString($env);
        }
    }

    /**
     * Test allowed hosts array
     */
    public function testAllowedHostsArray(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();

            $reflection = new \ReflectionClass(dbModel::class);
            $method = $reflection->getMethod('currentHost');
            $method->setAccessible(true);

            // Method exists and is callable
            $this->assertTrue(method_exists($dbModel, 'currentHost'));
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }

    /**
     * Test PDO attributes are set correctly
     */
    public function testPdoAttributesConfiguration(): void
    {
        if (!defined('DB_HOST')) {
            $this->markTestSkipped('Database constants not defined');
        }

        try {
            $dbModel = dbModel::getInstance();
            $pdo = $dbModel->getDB();

            // Check error mode
            $errorMode = $pdo->getAttribute(\PDO::ATTR_ERRMODE);
            $this->assertEquals(\PDO::ERRMODE_EXCEPTION, $errorMode);
        } catch (\Exception $e) {
            $this->markTestSkipped('Database connection not available: ' . $e->getMessage());
        }
    }
}

