<?php
if (file_exists('assets/nsfproject/settings/settings.php')) {
    header('Location: setup4.php');
    exit;
}
include 'assets/nsfproject/header/setup-header.php';
?>
<body>
<h1>Welcome</h1>
<p>You have entered the setup to launch your college or university's research dashboard display system. </p>
<p>On the next screen you will be asked for some information on the filesystem that this site runs on, as well as some basic information about how you want this site to operate.</p>
<p>Please note, you will have the opportunity to add a CSS Override file in case you would like to customize your system further.</p>
<p>The list of information you will need is as follows: </p>
<ul>
    <li>The absolute path of the includes directory(do not place this in your webpath)</li>
        <li>What you want to title this site</li>
    <li>The URL for your logo</li>
    <li>Your school name</li>
    <li>A contact email address for this site (placed in the footer)</li>
    <li>The copyright statement for this site</li>
    <li>Any resources you would like to link to in the footer of your site</li>
    <li>Database Connection information includeing:
    <ol>
        <li>Database host name</li>
        <li>The port that the database program listens on (Mysql / mariadb typically is 3306)</li>
        <li>The database name you have chosen for this project</li>
        <li>The database user name for this project</li>
        <li>The database user password for accessing the database</li>
    </ol></li>
</ul>
<form action="setup2.php" method="post">
<label for="includesdir">To start,  we will need to know the Absolute Directory Path of where you have placed the includes directory. We recommend placing it at /var/www.</label>
    <div class="flex-container">
<input type="text" name="includesdir" id="includesdir" placeholder="Absolute path of includes directory" class="flex-input"  required>
    </div>
    <div>
    <input type="submit" value="Next" class="button">
    </div>
</form>
</body>
<?php
include 'assets/nsfproject/footer/setup-footer.php';
