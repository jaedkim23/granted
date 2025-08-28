USE test1;

DROP TABLE IF EXISTS smse_ft;
CREATE TABLE smse_ft(
	smse_id			INT AUTO_INCREMENT PRIMARY KEY,
	emp_id			int,
    banner_id		int,
    first_name		VARCHAR(1023),
    middle_name		VARCHAR(1023),
    last_name		VARCHAR(1023),
    position		VARCHAR(255),
    department		VARCHAR(255)
);
SELECT * FROM smse_ft;

DROP TABLE IF EXISTS org_map;
CREATE TABLE org_map(
	orgmap_id			INT AUTO_INCREMENT PRIMARY KEY,
    position			VARCHAR(255),
    supervisory_org		VARCHAR(255),
    department			VARCHAR(255),
    college				VARCHAR(255)
);
SELECT * FROM ORG_MAP where college = 'School of Business';


DROP TABLE IF EXISTS fac_tbl CASCADE;
DROP TABLE IF EXISTS nonfac_tbl;
DROP TABLE IF EXISTS emp_orgs;
DROP TABLE IF EXISTS id_lookup;
DROP TABLE IF EXISTS wos_tbl;
DROP TABLE IF EXISTS wos_lookup_history;
drop table if exists open_alex_tbl;
drop table if exists emp_tbl;

CREATE TABLE emp_tbl(
	res_id 		INT AUTO_INCREMENT PRIMARY KEY,
    emp_id			int,
    banner_id		int,
    first_name		VARCHAR(1023),
    middle_name		VARCHAR(1023),
    last_name		VARCHAR(1023),
    preferred_name	VARCHAR(1023),
    email			VARCHAR(1023),
    work_phone 		VARCHAR(255)
);
select * from emp_tbl;
DROP TABLE IF EXISTS fac_tbl;
CREATE TABLE fac_tbl ( 
	fac_id			INT AUTO_INCREMENT PRIMARY KEY,
    res_id			int not null,
    position		VARCHAR(255),
    department		VARCHAR(255),
    college			VARCHAR(255),
    has_tenure		int,
    FOREIGN KEY (res_id) REFERENCES emp_tbl(res_id)
);  

DROP TABLE IF EXISTS nonfac_tbl;
CREATE TABLE nonfac_tbl (
	nonfac_id			INT AUTO_INCREMENT PRIMARY KEY,
    res_id				int not null,
    position			VARCHAR(255),
    supervisory_org		VARCHAR(255),
    college				VARCHAR(255),
    FOREIGN KEY (res_id) REFERENCES emp_tbl(res_id)
);

DROP TABLE IF EXISTS emp_orgs;
CREATE TABLE emp_orgs (
	emp_org_id			INT AUTO_INCREMENT PRIMARY KEY,
    res_id				int not null,
    banner_id 			int,
    full_name			VARCHAR(1023),
    email				VARCHAR(255),
    unit				VARCHAR(255),
    FOREIGN KEY (res_id) REFERENCES emp_tbl(res_id)
);
SELECT * FROM emp_orgs;

drop table if exists id_lookup;
CREATE TABLE id_lookup(
	lookup_id 	INT AUTO_INCREMENT PRIMARY KEY,
    res_id		int,
    wos_id		varchar(255) NULL,
    alex_id		varchar(255) NULL,
    FOREIGN KEY (res_id) REFERENCES emp_tbl(res_id)    
);  

drop table if exists wos_lookup_history;
CREATE TABLE wos_lookup_history(
	wos_lookup_id 			INT AUTO_INCREMENT PRIMARY KEY,
    res_id		int,
    wos_id		varchar(255) NULL,
    author_name	varchar(1023) NULL,
    search_term varchar(1023) NULL,
    foreign key (res_id) references emp_tbl(res_id)
); 

drop table if exists wos_tbl CASCADE;
CREATE TABLE wos_tbl (
	wos_rec_id 		INT AUTO_INCREMENT PRIMARY KEY,
    work_id 		VARCHAR(255) NULL,
    title			VARCHAR(1023) NULL,
    source			VARCHAR(1023) NULL,
    publish_year	INT,
    doi				VARCHAR(1023) NULL,
    issn			VARCHAR(1023) NULL,
	eissn			VARCHAR(1023) NULL
); 

DROP TABLE IF EXISTS wos_work_tbl CASCADE;
CREATE TABLE wos_work_tbl (
	wos_work_id		INT AUTO_INCREMENT PRIMARY KEY,
	wos_rec_id		INT,
	res_id			INT,
	FOREIGN KEY (res_id) REFERENCES emp_tbl(res_id),
	FOREIGN KEY (wos_rec_id) REFERENCES wos_tbl(wos_rec_id)
);


drop table if exists open_alex_tbl CASCADE;
CREATE TABLE open_alex_tbl (
	open_alex_rec_id 		INT AUTO_INCREMENT PRIMARY KEY,
    res_id					INT,
    work_id 				VARCHAR(255) NULL,
    title					VARCHAR(1023) NULL,
    source					VARCHAR(1023) NULL,
    publish_year			INT
);    


DROP TABLE IF EXISTS open_alex_work_tbl CASCADE;
CREATE TABLE open_alex_work_tbl (
	open_alex_work_id		INT AUTO_INCREMENT PRIMARY KEY,
	open_alex_rec_id		INT,
	res_id					INT,
	foreign key (res_id) references emp_tbl(res_id),
	foreign key (open_alex_rec_id) references open_alex_tbl(open_alex_rec_id)
);

select distinct E.first_name, E.last_name, E.res_id, wos_id, alex_id from emp_tbl E 
inner join id_lookup I on E.res_id = I.res_id;  

select * from wos_work_tbl;
select * from wos_work_tbl;
select * from wos_tbl;
select * from id_lookup;
select distinct E.first_name, E.last_name, E.res_id, wos_id, alex_id from emp_tbl E 
inner join wos_work_tbl WT on WT.res_id = E.res_id 
inner join wos_tbl W on WT.wos_rec_id=W.wos_rec_id 
inner join id_lookup I on I.res_id=WT.res_id where last_name='Morse';

select * from wos_tbl where res_id = 607;
select * from id_lookup;
select * from wos_tbl where res_id = 182;

select * from emp_orgs;


select * from wos_lookup_history;
select * from id_lookup;
select * from emp_tbl order by res_id desc;
select * from fac_tbl;
select * from wos_tbl order by wos_rec_id desc;
select * from open_alex_tbl order by open_alex_rec_id desc;
SELECT * FROM wos_tbl WHERE res_id = '1473' AND work_id = '001320214900011';

SELECT E.res_id, emp_id, banner_id, first_name, middle_name, last_name, preferred_name, email, position, department, college, has_tenure 
        FROM emp_tbl E INNER JOIN fac_tbl F ON E.res_id = F.res_id;
        
SELECT * FROM fac_tbl WHERE RES_ID = 801;
select * from emp_tbl where res_id = 801;
select * from nonfac_tbl where res_id=801;
select * from org_map;
select * from smse_ft;

SELECT res_id, wos_id, alex_id, COUNT(*)
FROM id_lookup
GROUP BY res_id, wos_id, alex_id
HAVING COUNT(*) > 1;

WITH ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY res_id, wos_id, alex_id
           ORDER BY res_id
         ) AS rn
  FROM id_lookup
)
DELETE FROM id_lookup
WHERE res_id IN (
  SELECT res_id FROM ranked WHERE rn > 1
);

select count(*) from id_lookup;

select * from emp_tbl where last_name='Morse';
select * from fac_tbl where res_id = 182;
select * from id_lookup where res_id = 182;
select * from emp_tbl where res_id=182;

select * from wos_tbl;
select * from wos_work_tbl;

select distinct title, A.wos_rec_id, B.res_id, C.first_name, C.last_name 
from wos_tbl A inner join wos_work_tbl B on A.wos_rec_id = B.wos_rec_id
inner join emp_tbl C on C.res_id = B.res_id order by 2 desc;

select * from wos_work_tbl where res_id = 182;

select * from id_lookup where res_id in (select res_id from id_lookup group by res_id having count(*)>1);

