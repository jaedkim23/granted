<?php
/**
 * Unit Tests for Logger Class
 *
 * @category Testing
 * @package Nsfproject\Tests
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 */

namespace Nsfproject\Tests;

use PHPUnit\Framework\TestCase;
use Nsfproject\helper\logger;

class LoggerTest extends TestCase
{
    private logger $logger;

    protected function setUp(): void
    {
        // Reset singleton instance before each test
        $reflection = new \ReflectionClass('Nsfproject\helper\logger');
        $property = $reflection->getProperty('instance');
        $property->setAccessible(true);
        $property->setValue(null);

        $this->logger = logger::getInstance();
    }

    /**
     * Test that logger is a singleton
     */
    public function testLoggerIsSingleton(): void
    {
        $logger1 = logger::getInstance();
        $logger2 = logger::getInstance();

        $this->assertSame($logger1, $logger2);
    }

    /**
     * Test logging user messages
     */
    public function testLogUserMessage(): void
    {
        $message = 'Test user message';
        $this->logger->logUserMessage($message);

        $messages = $this->logger->getUserMessages();
        $this->assertContains($message, $messages);
    }

    /**
     * Test multiple user messages
     */
    public function testMultipleUserMessages(): void
    {
        $msg1 = 'First message';
        $msg2 = 'Second message';

        $this->logger->logUserMessage($msg1);
        $this->logger->logUserMessage($msg2);

        $messages = $this->logger->getUserMessages();
        $this->assertCount(2, $messages);
        $this->assertContains($msg1, $messages);
        $this->assertContains($msg2, $messages);
    }

    /**
     * Test logging error messages
     */
    public function testLogErrorMessage(): void
    {
        $errorMsg = 'Test error message';
        $this->logger->logErrorMessage($errorMsg);

        // Check that error was logged (via reflection since getter doesn't exist)
        $reflection = new \ReflectionClass($this->logger);
        $property = $reflection->getProperty('errors');
        $property->setAccessible(true);
        $errors = $property->getValue($this->logger);

        $this->assertContains($errorMsg, $errors);
    }

    /**
     * Test logging success messages
     */
    public function testLogSuccessMessage(): void
    {
        $successMsg = 'Operation successful';
        $this->logger->logSuccessMessage($successMsg);

        $messages = $this->logger->getSuccessMessages();
        $this->assertContains($successMsg, $messages);
    }

    /**
     * Test retrieving user messages
     */
    public function testGetUserMessages(): void
    {
        $this->logger->logUserMessage('Message 1');
        $this->logger->logUserMessage('Message 2');

        $messages = $this->logger->getUserMessages();
        $this->assertIsArray($messages);
        $this->assertCount(2, $messages);
    }

    /**
     * Test retrieving success messages
     */
    public function testGetSuccessMessages(): void
    {
        $this->logger->logSuccessMessage('Success 1');
        $this->logger->logSuccessMessage('Success 2');

        $messages = $this->logger->getSuccessMessages();
        $this->assertIsArray($messages);
        $this->assertCount(2, $messages);
    }

    /**
     * Test empty messages
     */
    public function testEmptyMessages(): void
    {
        $messages = $this->logger->getUserMessages();
        $this->assertIsArray($messages);
        $this->assertEmpty($messages);
    }

    /**
     * Test displayUserMessage clears messages
     */
    public function testDisplayUserMessageClearsMessages(): void
    {
        $this->logger->logUserMessage('Test message');

        // Capture output
        ob_start();
        $this->logger->displayUserMessage();
        ob_end_clean();

        $messages = $this->logger->getUserMessages();
        $this->assertEmpty($messages);
    }

    /**
     * Test displaySuccessMessage with data
     */
    public function testDisplaySuccessMessageOutput(): void
    {
        $this->logger->logSuccessMessage('Test success');

        ob_start();
        $this->logger->displaySuccessMessage();
        $output = ob_get_clean();

        $this->assertStringContainsString('success-messages', $output);
        $this->assertStringContainsString('Test success', $output);
    }

    /**
     * Test displayUserMessage with data
     */
    public function testDisplayUserMessageOutput(): void
    {
        $this->logger->logUserMessage('Test error');

        ob_start();
        $this->logger->displayUserMessage();
        $output = ob_get_clean();

        $this->assertStringContainsString('error', $output);
        $this->assertStringContainsString('Test error', $output);
    }
}

