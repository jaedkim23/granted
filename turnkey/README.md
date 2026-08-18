# nsfproject
NSF Project standalone website to display research information

## Database files
Database files are seeded with 2 example pages,  the HERD dashboard, publicly available, and the R&D research page which is currently set to secure, meaning you must be logged in to see it. You can change the secure setting to false to make it public.  

The database files are also seeded with a single admin user that should be removed once you have created your own admin user, see [Admin Login](#admin-login) for credentials.

## Setup
1. Download a copy of the repository.
2. Create a database and user with appropriate permissions.
3. Place the Includes directory in a location on your server that is not in the webpath, but PHP is able to access. (Check your php.ini file for open_base_dir settings if you are unsure where this is.) Please note: the includes directory is required to be the directory that contains the nsfproject folder.
4. Confirm that apache can write to the following directories:  nsfproject/assets/nsfproject/settings/ and includes/nsfproject/conf/.  This is needed for the setup process to write the necessary configuration files, and for the project to function properly.
   1. You will need to download the composer.phar file from https://getcomposer.org/download/ and place it in your includes folder.
   2. cd to your includes folder, then run 
```php composer.phar install  --optimize-autoloader --no-dev``` from the command line to install the necessary dependencies into includes/nsfproject/vendor, and to build your autoloader.  All of which is needed for the project to function. This step does not need to be done on the server, but it is recommended to do so, as it will save time and bandwidth on the server.  If you do not have access to the command line on your server, you can run this command on your local machine, and then upload the includes/nsfproject/vendor directory to your server.
4. Place the nsfproject folder in the webpath of your server.  Please note, the nsfproject folder is needed.
   1. If you place the nsfproject folder below the toplevel of the webpath (directly in the HTML directory), you will need to update the .htaccess file to include the webpath (from the html folder to the nsfproject folder) to the nsfproject folder in the RewriteBase directive.  For example, if you place the nsfproject folder in a subdirectory called "nsf", you would change the RewriteBase directive to "RewriteBase /nsf/nsfproject/".  If you place the nsfproject folder directly in the HTML directory, you can leave the RewriteBase directive as is.
5. point your browser to your server and webpath, and you should see page one of the setup process.  Follow the instructions to complete the setup.  You will need to provide the database credentials you created in step 2, and the location of the Includes directory from step 3.
6. You will be given the opportunity to remove the setup files after the setup is complete, it is recommended to do so for security reasons.  
7. Once the setup is complete, you can log in to the admin dashboard using the credentials provided in the database files, see [Admin Login](#admin-login) for credentials.  From there you can create new pages, edit existing pages, and manage users.

## Users
This project supports regular users and admin users.  Regular users can view pages that are set to secure.  Admin users can view all pages, and can also create, edit, and delete pages, as well as manage users.  It is recommended to create a new admin user and delete the default admin user for security reasons.
### Passsword reset link / Password set email 
We utilize a token based system for password resets and password set emails.  When a user requests a password reset, they will be sent an email with a link to reset their password.  The link will contain a token that is valid for 1 hour.  If the token is expired, the user will need to request a new password reset email.  The same process is used for setting a password for a new user.  The user will be sent an email with a link to set their password, and the link will contain a token that is valid for 24 hours.  If the token is expired, the user will need to request a new password set email.

## Pages
Pages can be set to secure or public, and you can set one page to be the homepage.  If a user tries to access a secure page without being logged in, they will be redirected to the login page.  Once they log in, they will be redirected back to the page they were trying to access.

## CSS Overrides
Located in the css directory is a file called overrides.css.  This file is loaded after the default CSS files, and can be used to override any of the default styles.  This file is not included in the setup process, so you will need to modify the file as needed, setting your colors, fonts, and other styles to match your branding. If needed, you can also adjust the header-height, if your logo is a different shape, and the max-width of the site.  

## Admin login:
<span id='admin-login'></span>

* email: admin@admin.com
* password: hvG+$D@set