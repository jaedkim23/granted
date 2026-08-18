# NSF Project Unit Tests

Comprehensive unit test suite for the NSF Project application covering helper classes and models.

## Tests Included

### 1. **LoggerTest.php** - Logger Utility Tests (11 tests)
Tests for the singleton logger class that handles error, success, and user messages.

**Coverage:**
- Singleton pattern verification
- User message logging and retrieval
- Error message logging
- Success message logging
- Display output generation
- Message clearing after display

**Run single test file:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/LoggerTest.php
```

### 2. **UserTest.php** - User Model Tests (13 tests)
Tests for the User model including getters, setters, and property validation.

**Coverage:**
- ID, email, first name, last name, level getters/setters
- Data type validation
- Property persistence
- Email format validation
- Multiple property operations
- Database mock integration

**Run single test file:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/UserTest.php
```

### 3. **PagesTest.php** - Pages Model Tests (17 tests)
Tests for the Pages model and form validation.

**Coverage:**
- Title, parentid, active, secure, embed, content getters/setters
- Null/empty value handling
- Active/secure status validation (0 or 1)
- Title requirement validation
- Parent ID numeric validation
- Large content handling
- Special characters in titles
- Form submission validation

**Run single test file:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/PagesTest.php
```

### 4. **HelperTest.php** - Helper Class Tests (16 tests)
Tests for static helper methods and utilities.

**Coverage:**
- INI file preparation and structure
- HTML hydration and placeholder replacement
- Header and footer section preparation
- Database configuration handling
- Email validation (valid/invalid formats)
- Error recording and display
- Special character handling
- HTML output formatting

**Run single test file:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/HelperTest.php
```

### 5. **NavigationTest.php** - Navigation Model Tests (11 tests)
Tests for page navigation building and hierarchy.

**Coverage:**
- Singleton pattern for database connections
- HTML structure generation
- Parent and child page filtering
- Navigation building with manage paths
- URL building
- Multiple nesting levels
- HTML tag balancing

**Run single test file:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/NavigationTest.php
```

### 6. **DbModelTest.php** - Database Model Tests (11 tests)
Tests for database connection and environment detection.

**Coverage:**
- Singleton pattern verification
- PDO object retrieval
- Environment detection (local, build, staging, prod)
- Host detection and mapping
- PDO attribute configuration
- Connection state management
- Error mode configuration

**Run single test file:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/DbModelTest.php
```

---

## Installation & Setup

### Prerequisites
- PHP 8.2+
- PHPUnit 11.5+ (already in composer.json)
- Composer

### Installation

1. **Install dependencies (if not already done):**
```bash
cd includes/
composer install
cd ..
```

2. **Run all tests:**
```bash
./includes/nsfproject/vendor/bin/phpunit
```

3. **Run tests with configuration file:**
```bash
./includes/nsfproject/vendor/bin/phpunit -c phpunit.xml
```

4. **Run specific test suite:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/LoggerTest.php
```

5. **Run tests with coverage report:**
```bash
./includes/nsfproject/vendor/bin/phpunit --coverage-html=tests/coverage/
```

---

## Test Coverage

The test suite covers:
- **Getters/Setters**: Property access and mutation
- **Data Validation**: Email format, numeric values, required fields
- **Type Safety**: Return type verification
- **Edge Cases**: Empty strings, null values, special characters
- **Singleton Patterns**: Correct instance management
- **HTML Output**: Proper formatting and structure
- **Database Integration**: Mocked database operations

**Total Tests: 79**
- LoggerTest: 11 tests
- UserTest: 13 tests
- PagesTest: 17 tests
- HelperTest: 16 tests
- NavigationTest: 11 tests
- DbModelTest: 11 tests

---

## Running Tests from Command Line

### All Tests
```bash
php ./includes/nsfproject/vendor/bin/phpunit
```

### Specific Test Class
```bash
php ./includes/nsfproject/vendor/bin/phpunit tests/UserTest.php
```

### Specific Test Method
```bash
php ./includes/nsfproject/vendor/bin/phpunit --filter testSetAndGetEmail tests/UserTest.php
```

### With Verbose Output
```bash
php ./includes/nsfproject/vendor/bin/phpunit --verbose
```

### Generate Coverage Report
```bash
php ./includes/nsfproject/vendor/bin/phpunit --coverage-html=tests/coverage
```

---

## Test Configuration

The `phpunit.xml` file contains:
- Bootstrap file configuration
- Test suite definitions
- Code coverage settings
- Source code paths
- Color and verbose output options

---

## Notes on Database Tests

Some `DbModelTest` tests require actual database credentials to run. These tests will be skipped if:
- `DB_HOST` constant is not defined
- Database connection fails

These tests use reflection to access private methods and test environment detection logic without requiring a live database.

### Database Support

Your dbModel now supports **3 database systems**:

1. **MySQL/MariaDB** (default) - `tables.sql`
2. **PostgreSQL** - `tables_postgres.sql`
3. **SQLite** - `tables_sqlite.sql` (for testing)

### To Run Database Tests

**Option 1: SQLite (Recommended - No Setup Required)**

1. **Use the SQLite configuration:**
```bash
cp tests/config.sqlite.php tests/config.php
```

2. **Run the tests:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/DbModelTest.php
```

**Benefits:**
- ✅ No external database setup required
- ✅ Fast in-memory database
- ✅ All tests pass immediately
- ✅ Perfect for CI/CD pipelines

**Option 2: MySQL/MariaDB (Real Database)**

1. **Copy the example configuration:**
```bash
cp tests/config.example.php tests/config.php
```

2. **Edit `tests/config.php` with your test database credentials:**
```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'nsfproject_test');
define('DB_USER', 'root');
define('DB_PASS', 'your_password');
define('DB_PORT', '3306');
```

3. **Create a test database:**
```sql
CREATE DATABASE nsfproject_test;
```

4. **Run the tests:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/DbModelTest.php
```

**Option 3: PostgreSQL**

1. **Use the PostgreSQL configuration:**
```bash
cp tests/config.postgres.php tests/config.php
```

2. **Edit with your PostgreSQL credentials:**
```php
define('DB_HOST', 'localhost');
define('DB_NAME', 'nsfproject_test');
define('DB_USER', 'postgres');
define('DB_PASS', 'your_password');
define('DB_PORT', '5432');
```

3. **Create a test database:**
```sql
CREATE DATABASE nsfproject_test;
```

4. **Run the tests:**
```bash
./includes/nsfproject/vendor/bin/phpunit tests/DbModelTest.php
```

**Note:** The database tests will now run instead of being skipped, allowing you to test actual database connectivity and environment detection.

---

## Extending the Tests

To add new tests:

1. Create a new test file in the `tests/` directory
2. Extend `PHPUnit\Framework\TestCase`
3. Name test methods with `test` prefix
4. Use assertions from PHPUnit

**Example:**
```php
public function testNewFeature(): void
{
    $result = someFunction();
    $this->assertTrue($result);
}
```

---

## Troubleshooting

### "Class not found" errors
- Ensure `composer install` has been run
- Check that the bootstrap file path is correct

### Database connection errors
- These tests will be automatically skipped if DB is unavailable
- Tests use mocks to avoid database dependencies

### Output assertions fail
- Check that no output is being generated before tests (whitespace, etc.)
- Verify that `ob_start()` and `ob_get_clean()` are used correctly

---

## CI/CD Integration

To integrate with continuous integration:

```bash
# Run tests and generate coverage report
./includes/nsfproject/vendor/bin/phpunit --coverage-html=coverage/ --log-junit=junit.xml
```

This generates:
- HTML coverage report in `coverage/` directory
- JUnit XML report for CI systems

---

## Authors

- Bryan Teague <bryant@sandiego.edu>

## License

GPL - See LICENSE file
