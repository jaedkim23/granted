-- -------------------------------------------------------------
-- TablePlus 6.8.6(662)
--
-- https://tableplus.com/
--
-- Database: nsfproject
-- Generation Time: 2026-04-28 17:16:53.5420
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


DROP TABLE IF EXISTS `adminpages`;
CREATE TABLE `adminpages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(50) NOT NULL,
  `parentid` int(11) DEFAULT NULL,
  `url` varchar(100) DEFAULT NULL,
  `active` tinyint(1) DEFAULT 1,
  `is_default` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `pages`;
CREATE TABLE `pages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(50) NOT NULL,
  `parentid` int(11) DEFAULT NULL,
  `embed` text DEFAULT NULL,
  `content` text DEFAULT NULL,
  `active` tinyint(1) DEFAULT 1,
  `secure` tinyint(1) DEFAULT NULL,
  `is_default` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `password_resets`;
CREATE TABLE `password_resets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(100) DEFAULT NULL,
  `token` char(50) DEFAULT NULL,
  `expires` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `first` varchar(100) NOT NULL,
  `last` varchar(100) NOT NULL,
  `level` varchar(50) NOT NULL,
  `passwordhash` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `adminpages` (`id`, `title`, `parentid`, `url`, `active`, `is_default`) VALUES
(4, 'users', NULL, 'user', 1, 0),
(5, 'add', 4, 'user/add', 1, 0),
(8, 'pages', NULL, 'pages', 1, 0),
(9, 'add', 8, 'pages/add', 1, 0),
(10, 'view', 4, 'user', 1, 0),
(11, 'view', 8, 'pages', 1, 0),
(12, 'Configuration', NULL, 'conf', 1, 0),
(13, 'view', 12, 'conf', 1, 0),
(14, 'edit', 12, 'conf/edit', 1, 0);

INSERT INTO `pages` (`id`, `title`, `parentid`, `embed`, `content`, `active`, `secure`, `is_default`) VALUES
(14, 'HERD Dashboard', NULL, '<div class=\'tableauPlaceholder\' id=\'viz1776887557824\' style=\'position: relative\'><noscript><a href=\'#\'><img alt=\'HERD_Data_Dashboard \' src=\'https://public.tableau.com/static/images/HE/HERDDashboard/HERD_Data_Dashboard/1_rss.png\' style=\'border: none\' /></a></noscript><object class=\'tableauViz\'  style=\'display:none;\'><param name=\'host_url\' value=\'https%3A%2F%2Fpublic.tableau.com%2F\' /> <param name=\'embed_code_version\' value=\'3\' /> <param name=\'site_root\' value=\'\' /><param name=\'name\' value=\'HERDDashboard/HERD_Data_Dashboard\' /><param name=\'tabs\' value=\'no\' /><param name=\'toolbar\' value=\'yes\' /><param name=\'static_image\' value=\'https://public.tableau.com/static/images/HE/HERDDashboard/HERD_Data_Dashboard/1.png\' /> <param name=\'animate_transition\' value=\'yes\' /><param name=\'display_static_image\' value=\'yes\' /><param name=\'display_spinner\' value=\'yes\' /><param name=\'display_overlay\' value=\'yes\' /><param name=\'display_count\' value=\'yes\' /><param name=\'language\' value=\'en-US\' /></object></div>                <script type=\'text/javascript\'>                    var divElement = document.getElementById(\'viz1776887557824\');                    var vizElement = divElement.getElementsByTagName(\'object\')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.minWidth=\'715px\';vizElement.style.maxWidth=\'1300px\';vizElement.style.width=\'100%\';vizElement.style.height=\'1827px\';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.minWidth=\'715px\';vizElement.style.maxWidth=\'1300px\';vizElement.style.width=\'100%\';vizElement.style.height=\'1827px\';} else { vizElement.style.width=\'100%\';vizElement.style.height=\'1827px\';}                     var scriptElement = document.createElement(\'script\');                    scriptElement.src = \'https://public.tableau.com/javascripts/api/viz_v1.js\';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>', '<p>This is some content that you can choose to add if you want to. &nbsp;It will appear at the top of the page, above any embed that is included.&nbsp;</p>\r\n<h2>Headings are available!&nbsp;</h2>', 1, 0, 1),
(18, 'R&D Expenditures', NULL, '<div class=\'tableauPlaceholder\' id=\'viz1776979377840\' style=\'position: relative\'><noscript><a href=\'#\'><img alt=\'HERD_Data_Dashboard \' src=\'https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;HE&#47;HERDDashboard&#47;HERD_Data_Dashboard&#47;1_rss.png\' style=\'border: none\' /></a></noscript><object class=\'tableauViz\'  style=\'display:none;\'><param name=\'host_url\' value=\'https%3A%2F%2Fpublic.tableau.com%2F\' /> <param name=\'embed_code_version\' value=\'3\' /> <param name=\'site_root\' value=\'\' /><param name=\'name\' value=\'HERDDashboard&#47;HERD_Data_Dashboard\' /><param name=\'tabs\' value=\'no\' /><param name=\'toolbar\' value=\'yes\' /><param name=\'static_image\' value=\'https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;HE&#47;HERDDashboard&#47;HERD_Data_Dashboard&#47;1.png\' /> <param name=\'animate_transition\' value=\'yes\' /><param name=\'display_static_image\' value=\'yes\' /><param name=\'display_spinner\' value=\'yes\' /><param name=\'display_overlay\' value=\'yes\' /><param name=\'display_count\' value=\'yes\' /><param name=\'language\' value=\'en-US\' /></object></div>                <script type=\'text/javascript\'>                    var divElement = document.getElementById(\'viz1776979377840\');                    var vizElement = divElement.getElementsByTagName(\'object\')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.minWidth=\'715px\';vizElement.style.maxWidth=\'1300px\';vizElement.style.width=\'100%\';vizElement.style.height=\'1827px\';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.minWidth=\'715px\';vizElement.style.maxWidth=\'1300px\';vizElement.style.width=\'100%\';vizElement.style.height=\'1827px\';} else { vizElement.style.width=\'100%\';vizElement.style.height=\'1827px\';}                     var scriptElement = document.createElement(\'script\');                    scriptElement.src = \'https://public.tableau.com/javascripts/api/viz_v1.js\';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>', '<h2>R&amp;D Expenditures</h2>\r\n<p>&nbsp;</p>', 1, 1, 0),
(19, 'test page', 14, '', '<h2>Test page no embed.</h2>\r\n<p>use this page for other things such as an about page, or a listing of participants.&nbsp;</p>', 1, 0, 0);

INSERT INTO `users` (`id`, `email`, `first`, `last`, `level`, `passwordhash`) VALUES
(15, 'admin@admin.com', 'delete once', 'you have an account', 'admin', '$2y$10$eXE3WfNSXi5kpEikpJPdsuFa5tLVwK1L3w3oc3fjapvQ5yewUv1H.');



/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;