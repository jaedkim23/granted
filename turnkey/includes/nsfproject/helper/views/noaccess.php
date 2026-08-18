<?php
/**
 * Created by PHPStorm
 * User: bteague
 * Date: 4/27/26
 * Time: 4:58 PM
 * PHP Version: 7.4+
 *
 * @category
 * @package
 * @author   Bryan Teague <bryant@sandiego.edu>
 * @license  https://github.sandiego.edu.com/ GPL
 * @link     https://github.sandiego.edu.com/
 **/
?>
<h2>You must be logged in to view this page.</h2>
<p>You will be redirected to login in 5 seconds.</p>
<script>
    setTimeout(function() {
        window.location.href = "<?php echo WEB_PATH; ?>/login.php?return=<?PHP echo $_SERVER['REQUEST_URI']?>";
    }, 5000);
</script>