<?php
/**
 * Unit Tests for User Model
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

namespace Nsfproject\Tests;

use PHPUnit\Framework\TestCase;
use Nsfproject\models\user;
use Nsfproject\helper\dbModel;
use PHPUnit\Framework\MockObject\MockObject;

class UserTest extends TestCase
{
    private user $user;
    private MockObject $dbMock;

    protected function setUp(): void
    {
        // Create a mock for dbModel
        $this->dbMock = $this->createMock(dbModel::class);
        $this->user = new user($this->dbMock);
    }

    /**
     * Test setting and getting ID
     */
    public function testSetAndGetId(): void
    {
        $testId = 123;
        $this->user->setId($testId);

        $this->assertEquals($testId, $this->user->getId());
    }

    /**
     * Test setting and getting email
     */
    public function testSetAndGetEmail(): void
    {
        $testEmail = 'test@example.com';
        $this->user->setEmail($testEmail);

        $this->assertEquals($testEmail, $this->user->getEmail());
    }

    /**
     * Test setting and getting first name
     */
    public function testSetAndGetFirst(): void
    {
        $testFirst = 'John';
        $this->user->setFirst($testFirst);

        $this->assertEquals($testFirst, $this->user->getFirst());
    }

    /**
     * Test setting and getting last name
     */
    public function testSetAndGetLast(): void
    {
        $testLast = 'Doe';
        $this->user->setLast($testLast);

        $this->assertEquals($testLast, $this->user->getLast());
    }

    /**
     * Test setting and getting level
     */
    public function testSetAndGetLevel(): void
    {
        $testLevel = 'admin';
        $this->user->setLevel($testLevel);

        $this->assertEquals($testLevel, $this->user->getLevel());
    }

    /**
     * Test ID type
     */
    public function testIdIsInteger(): void
    {
        $this->user->setId(456);
        $this->assertIsInt($this->user->getId());
    }

    /**
     * Test email type
     */
    public function testEmailIsString(): void
    {
        $this->user->setEmail('test@domain.com');
        $this->assertIsString($this->user->getEmail());
    }

    /**
     * Test first name type
     */
    public function testFirstIsString(): void
    {
        $this->user->setFirst('Jane');
        $this->assertIsString($this->user->getFirst());
    }

    /**
     * Test last name type
     */
    public function testLastIsString(): void
    {
        $this->user->setLast('Smith');
        $this->assertIsString($this->user->getLast());
    }

    /**
     * Test level type
     */
    public function testLevelIsString(): void
    {
        $this->user->setLevel('user');
        $this->assertIsString($this->user->getLevel());
    }

    /**
     * Test multiple property setters
     */
    public function testMultiplePropertySetters(): void
    {
        $this->user->setId(1);
        $this->user->setEmail('user@test.com');
        $this->user->setFirst('First');
        $this->user->setLast('Last');
        $this->user->setLevel('admin');

        $this->assertEquals(1, $this->user->getId());
        $this->assertEquals('user@test.com', $this->user->getEmail());
        $this->assertEquals('First', $this->user->getFirst());
        $this->assertEquals('Last', $this->user->getLast());
        $this->assertEquals('admin', $this->user->getLevel());
    }

    /**
     * Test fetchUsers returns array
     */
    public function testFetchUsersReturnsArray(): void
    {
        // Mock the database behavior
        $mockPDO = $this->createMock(\PDO::class);
        $mockStatement = $this->createMock(\PDOStatement::class);

        $mockData = [
            ['id' => 1, 'email' => 'user1@test.com', 'first' => 'John', 'last' => 'Doe', 'level' => 'user'],
            ['id' => 2, 'email' => 'user2@test.com', 'first' => 'Jane', 'last' => 'Smith', 'level' => 'admin']
        ];

        $mockStatement->expects($this->once())
            ->method('fetchAll')
            ->willReturn($mockData);

        $mockPDO->expects($this->once())
            ->method('prepare')
            ->willReturn($mockStatement);

        $this->dbMock->expects($this->once())
            ->method('getDB')
            ->willReturn($mockPDO);

        $result = $this->user->fetchUsers();

        $this->assertIsArray($result);
        $this->assertCount(2, $result);
    }

    /**
     * Test that constructor sets dbh
     */
    public function testConstructorSetsDbh(): void
    {
        $user = new user($this->dbMock);
        $this->assertNotNull($user);
    }

    /**
     * Test email validation format
     */
    public function testEmailValidationFormat(): void
    {
        $validEmails = [
            'test@example.com',
            'user.name@example.co.uk',
            'name+tag@example.com'
        ];

        foreach ($validEmails as $email) {
            $this->assertTrue(
                filter_var($email, FILTER_VALIDATE_EMAIL) !== false,
                "Email '$email' should be valid"
            );
        }
    }

    /**
     * Test invalid email formats
     */
    public function testInvalidEmailFormats(): void
    {
        $invalidEmails = [
            'invalid.email',
            '@example.com',
            'user@',
            'user@.com'
        ];

        foreach ($invalidEmails as $email) {
            $this->assertFalse(
                filter_var($email, FILTER_VALIDATE_EMAIL) !== false,
                "Email '$email' should be invalid"
            );
        }
    }

    /**
     * Test property persistence
     */
    public function testPropertyPersistence(): void
    {
        $id = 99;
        $email = 'persist@test.com';
        $first = 'Persistent';
        $last = 'User';
        $level = 'moderator';

        $this->user->setId($id);
        $this->user->setEmail($email);
        $this->user->setFirst($first);
        $this->user->setLast($last);
        $this->user->setLevel($level);

        // Verify properties persist
        for ($i = 0; $i < 3; $i++) {
            $this->assertEquals($id, $this->user->getId());
            $this->assertEquals($email, $this->user->getEmail());
            $this->assertEquals($first, $this->user->getFirst());
            $this->assertEquals($last, $this->user->getLast());
            $this->assertEquals($level, $this->user->getLevel());
        }
    }
}

