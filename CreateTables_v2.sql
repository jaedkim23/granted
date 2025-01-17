USE TEST2;
drop table if exists emp_cas;
CREATE TABLE emp_cas(
	db_id 		INT AUTO_INCREMENT PRIMARY KEY,
    emp_id			int,
    banner_id		int,
    first_name		VARCHAR(1023),
    middle_name		VARCHAR(1023),
    last_name		VARCHAR(1023),
    preferred_name	VARCHAR(1023),
    email			VARCHAR(1023),
    work_phone 		VARCHAR(255),
    has_tenure		INT,
    position		VARCHAR(255),
    department		VARCHAR(255),
    college			VARCHAR(255)
);  




insert into emp_cas (emp_id, banner_id) values (1,1);
select * from emp_cas;


CREATE TABLE wos_raw(
	id 		INT AUTO_INCREMENT PRIMARY KEY,
    uid		VARCHAR(255),
    title	VARCHAR(1023),
    types   VARCHAR(255),
    sourceTitle		varchar(1023),
    publishYear 	int,
    issue			varchar(255),
    wosStandard		VARCHAR(1023),
    displayName		VARCHAR(1023),
    doi				VARCHAR(255),
    issn			VARCHAR(255),
    eissn			VARCHAR(255)
);

select * from wos_raw;

-- delete from wos_raw;
-- drop table wos_raw;

select * from wos_raw where wosStandard like 'Kohl, J%';
select * from wos_raw limit 100;
select * from wos_raw where wosStandard like "Koenig, %";
select * from wos_raw where doi = "10.1037/a0023557";
select * from wos_raw where lower(title) like "are leader stereotypes masculine? a meta-analysis of three research paradigms%";

CREATE TABLE open_alex_raw(
	id 		INT AUTO_INCREMENT PRIMARY KEY,
    work_id		VARCHAR(255),
    work_title	VARCHAR(1023),
    work_display_name   VARCHAR(1023),
    work_publication_year 	int,
    work_publication_date	VARCHAR(255),
    author_id		VARCHAR(255),
    author_name		VARCHAR(1023),
	author_position		VARCHAR(255),
    institution_id		VARCHAR(255),
    institution_name		VARCHAR(255),
    institution_country_code	VARCHAR(255)
);  
select * from open_alex_raw order by id desc;
select * from open_alex_raw where author_id='https://openalex.org/A5052899967';
select * from open_alex_raw where work_id='https://openalex.org/W2950956680';

-- delete from open_alex_raw;
-- drop table open_alex_raw;
select * from open_alex_raw where work_id = "https://openalex.org/W3196601740";
select * from open_alex_raw where author_id = "https://openalex.org/A5060000907";

drop table if exists emp_cas; 
delete from emp_cas;

select * from emp_cas;
select * from open_alex_raw where author_id="https://openalex.org/A5086059547";
delete from open_alex_raw where work_id="https://openalex.org/W2950826797";
-- delete from emp_cas;
select * from open_alex_raw limit 10;
select * from emp_cas where last_name='Yin';

select * from wos_raw limit 10;
select * from wos_raw where uid = '000188531400006';

select * from wos_raw order by id desc;

drop table if exists id_lookup;
CREATE TABLE id_lookup(
	id 			INT AUTO_INCREMENT PRIMARY KEY,
    emp_id		int,
    wos_id		varchar(255) NULL,
    alex_id		varchar(255) NULL
);  

select * from id_lookup order by id desc;

drop table if exists wos_lookup_history;
CREATE TABLE wos_lookup_history(
	id 			INT AUTO_INCREMENT PRIMARY KEY,
    emp_id		int,
    wos_id		varchar(255) NULL,
    author_name	varchar(1023) NULL,
    search_term varchar(1023) NULL
); 

select * from wos_lookup_history;
select * from id_lookup;
select count(*) from id_lookup;
select * from emp_cas where last_name = "Yang";
select * from id_lookup where emp_id = 49933;
select * from emp_cas left join id_lookup on emp_cas.emp_id = id_lookup.emp_id where alex_id is null and wos_id is null;
select * from emp_cas where emp_id = 32596;
select emp_cas.emp_id, preferred_name, has_tenure, position, department, wos_id 
from emp_cas left join id_lookup on emp_cas.emp_id = id_lookup.emp_id where wos_id is null;

select * from emp_cas where last_name='Yin';
select * from id_lookup where emp_id=32596;

select * from wos_raw limit 10;

select * from id_lookup where emp_id = 32596;
delete from id_lookup where emp_id = 32596;

select * from id_lookup where alex_id is not null;
select count(*) from id_lookup;

select * from id_lookup order by id desc limit 10;
select * from id_lookup where emp_id = 11125;
select * from id_lookup;

select * from id_lookup order by id desc limit 10;

select * from emp_cas where emp_id=11125;

select * from id_lookup where emp_id=11125;

update id_lookup set wos_id='FWC-8344-2022' where emp_id = 11125;

select * from emp_cas where emp_id = 32596;
select emp_id, count(*) from emp_cas group by emp_id order by count(*) desc;

select * from id_lookup where emp_id = 32596;
select * from id_lookup where emp_id = 48717;
select * from emp_cas where emp_id = 27450;
select * from emp_cas where last_name like "Bell";
update id_lookup set wos_id='CDY-5675-2022' where emp_id = 48717; 

select * from emp_cas where last_name="Ellis";
select * from id_lookup where emp_id = 1796;


select * from emp_cas;
select * from id_lookup;
select * from wos_lookup_history;


select * from emp_cas;

CREATE TABLE emp_temp(
	temp_id 		INT AUTO_INCREMENT PRIMARY KEY,
    full_name		VARCHAR(1023),
    email			VARCHAR(1023)
);

CREATE TABLE emp_dept_match(
	match_id		INT auto_increment primary key,
    SUB_UNIT		VARCHAR(255)
);  

select * from emp_temp;
select * from id_lookup;
select * from wos_lookup_history;
select * from emp_cas;
select * from emp_dept_match;

