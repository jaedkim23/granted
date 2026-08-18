<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 3/13/26
 * Time: 3:38 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SITETITLE</title>
    <link rel="stylesheet" href= "<?php echo WEB_PATH?>/assets/nsfproject/css/site.css">
    <OVERRIDECSS>
</head>
<body>

<header class="site-header">
	<div class="site-header__inner">
		<a class="site-header__brand" href="<?php echo WEB_PATH?>" aria-label="Home">
			<img class="site-header__logo" src="LOGO" alt="SCHOOLNAME">
			<span class="site-header__org">SCHOOLNAME</span>
		</a>

		<h1 class="site-header__title">NSF Project Dashboard</h1>

		<div class="site-header__account">
			<?php
			if (isset($_SESSION['first'])) {
				echo "Welcome  {$_SESSION['first']} {$_SESSION['last']}";
				echo "<a href='". WEB_PATH . "/logout.php'>Logout</a>";
				if(isset($_SESSION['return'])) {
					unset($_SESSION['return']);
				}
			} else {
				echo "<a class='btn btn--ghost' href='".WEB_PATH . "/login.php?return={$_SERVER['PHP_SELF']}'>Login</a>";
			}
			?>


		</div>
	</div>
</header>
<nav class="site-nav" aria-label="Primary">
    NAVIGATION
</nav>
<div class="site-content"> <!--Main body opener.  Main body closer is in regular-footer.php -->
