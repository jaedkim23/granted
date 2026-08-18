-- PostgreSQL compatible schema for NSF Project
-- Generated for cross-database compatibility

-- Drop tables if they exist (PostgreSQL syntax)
DROP TABLE IF EXISTS adminpages CASCADE;
DROP TABLE IF EXISTS pages CASCADE;
DROP TABLE IF EXISTS password_resets CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Admin pages table
CREATE TABLE adminpages (
    id SERIAL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    parentid INTEGER,
    url VARCHAR(100),
    active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false
);

-- Pages table
CREATE TABLE pages (
    id SERIAL PRIMARY KEY,
    title VARCHAR(50) NOT NULL,
    parentid INTEGER,
    embed TEXT,
    content TEXT,
    active BOOLEAN DEFAULT true,
    secure BOOLEAN DEFAULT false,
    is_default BOOLEAN DEFAULT false
);

-- Password resets table
CREATE TABLE password_resets (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100),
    token CHAR(50),
    expires TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    first VARCHAR(100) NOT NULL,
    last VARCHAR(100) NOT NULL,
    level VARCHAR(50) NOT NULL,
    passwordhash VARCHAR(255)
);

-- Insert sample admin pages with specific IDs
INSERT INTO adminpages (id, title, parentid, url, active, is_default) VALUES
(4, 'users', NULL, 'user', true, false),
(5, 'add', 4, 'user/add', true, false),
(8, 'pages', NULL, 'pages', true, false),
(9, 'add', 8, 'pages/add', true, false),
(10, 'view', 4, 'user', true, false),
(11, 'view', 8, 'pages', true, false),
(12, 'Configuration', NULL, 'conf', 1, 0),
(13, 'view', 12, 'conf', 1, 0),
(14, 'edit', 12, 'conf/edit', 1, 0);

-- Insert sample pages with specific IDs
INSERT INTO pages (id, title, parentid, embed, content, active, secure, is_default) VALUES
(14, 'HERD Dashboard', NULL, '<div class=''tableauPlaceholder'' id=''viz1776887557824'' style=''position: relative''><noscript><a href=''#''><img alt=''HERD_Data_Dashboard '' src=''https://public.tableau.com/static/images/HE/HERDDashboard/HERD_Data_Dashboard/1_rss.png'' style=''border: none'' /></a></noscript><object class=''tableauViz''  style=''display:none;''><param name=''host_url'' value=''https%3A%2F%2Fpublic.tableau.com%2F'' /> <param name=''embed_code_version'' value=''3'' /> <param name=''site_root'' value='''' /><param name=''name'' value=''HERDDashboard/HERD_Data_Dashboard'' /><param name=''tabs'' value=''no'' /><param name=''toolbar'' value=''yes'' /><param name=''static_image'' value=''https://public.tableau.com/static/images/HE/HERDDashboard/HERD_Data_Dashboard/1.png'' /> <param name=''animate_transition'' value=''yes'' /><param name=''display_static_image'' value=''yes'' /><param name=''display_spinner'' value=''yes'' /><param name=''display_overlay'' value=''yes'' /><param name=''display_count'' value=''yes'' /><param name=''language'' value=''en-US'' /></object></div>                <script type=''text/javascript''>                    var divElement = document.getElementById(''viz1776887557824'');                    var vizElement = divElement.getElementsByTagName(''object'')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.minWidth=''715px'';vizElement.style.maxWidth=''1300px'';vizElement.style.width=''100%'';vizElement.style.height=''1827px'';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.minWidth=''715px'';vizElement.style.maxWidth=''1300px'';vizElement.style.width=''100%'';vizElement.style.height=''1827px'';} else { vizElement.style.width=''100%'';vizElement.style.height=''1827px'';}                     var scriptElement = document.createElement(''script'');                    scriptElement.src = ''https://public.tableau.com/javascripts/api/viz_v1.js'';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>', '<p>This is some content that you can choose to add if you want to. &nbsp;It will appear at the top of the page, above any embed that is included.&nbsp;</p>
<h2>Headings are available!&nbsp;</h2>', true, false, true),
(18, 'R&D Expenditures', NULL, '<div class=''tableauPlaceholder'' id=''viz1776979377840'' style=''position: relative''><noscript><a href=''#''><img alt=''HERD_Data_Dashboard '' src=''https://public.tableau.com/static/images/HE/HERDDashboard/HERD_Data_Dashboard/1_rss.png'' style=''border: none'' /></a></noscript><object class=''tableauViz''  style=''display:none;''><param name=''host_url'' value=''https%3A%2F%2Fpublic.tableau.com%2F'' /> <param name=''embed_code_version'' value=''3'' /> <param name=''site_root'' value='''' /><param name=''name'' value=''HERDDashboard/HERD_Data_Dashboard'' /><param name=''tabs'' value=''no'' /><param name=''toolbar'' value=''yes'' /><param name=''static_image'' value=''https://public.tableau.com/static/images/HE/HERDDashboard/HERD_Data_Dashboard/1.png'' /> <param name=''animate_transition'' value=''yes'' /><param name=''display_static_image'' value=''yes'' /><param name=''display_spinner'' value=''yes'' /><param name=''display_overlay'' value=''yes'' /><param name=''display_count'' value=''yes'' /><param name=''language'' value=''en-US'' /></object></div>                <script type=''text/javascript''>                    var divElement = document.getElementById(''viz1776979377840'');                    var vizElement = divElement.getElementsByTagName(''object'')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.minWidth=''715px'';vizElement.style.maxWidth=''1300px'';vizElement.style.width=''100%'';vizElement.style.height=''1827px'';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.minWidth=''715px'';vizElement.style.maxWidth=''1300px'';vizElement.style.width=''100%'';vizElement.style.height=''1827px'';} else { vizElement.style.width=''100%'';vizElement.style.height=''1827px'';}                     var scriptElement = document.createElement(''script'');                    scriptElement.src = ''https://public.tableau.com/javascripts/api/viz_v1.js'';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>', '<h2>R&amp;D Expenditures</h2>
<p>&nbsp;</p>', true, true, false),
(19, 'test page', 14, '', '<h2>Test page no embed.</h2>
<p>use this page for other things such as an about page, or a listing of participants.&nbsp;</p>', true, false, false);

-- Insert sample user with specific ID
INSERT INTO users (id, email, first, last, level, passwordhash) VALUES
(15, 'admin@admin.com', 'delete once', 'you have an account', 'admin', '$2y$10$eXE3WfNSXi5kpEikpJPdsuFa5tLVwK1L3w3oc3fjapvQ5yewUv1H.');
