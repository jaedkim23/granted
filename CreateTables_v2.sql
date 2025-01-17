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

drop table if exists id_lookup;
CREATE TABLE id_lookup(
	id 			INT AUTO_INCREMENT PRIMARY KEY,
    emp_id		int,
    wos_id		varchar(255) NULL,
    alex_id		varchar(255) NULL
);  

drop table if exists wos_lookup_history;
CREATE TABLE wos_lookup_history(
	id 			INT AUTO_INCREMENT PRIMARY KEY,
    emp_id		int,
    wos_id		varchar(255) NULL,
    author_name	varchar(1023) NULL,
    search_term varchar(1023) NULL
); 
