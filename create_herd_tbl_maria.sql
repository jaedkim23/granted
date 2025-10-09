drop table if exists herd_exp;
CREATE TABLE herd_exp (
	tb1_id 				INT PRIMARY KEY AUTO_INCREMENT,
	year					int not null,
	fund_source			VARCHAR(255) not null,
	amount				numeric,
	herd_tbl				int not null
);
select * from herd_exp;

drop table if exists institution;
CREATE TABLE institution (
	inst_id 			INT 			PRIMARY KEY AUTO_INCREMENT,
	inst_name		VARCHAR(255)		NOT NULL,
	last_update		DATE			NOT NULL
);
SELECT * FROM institution;

drop table if exists herd21;
CREATE TABLE herd21 (
	tb21_id				INT PRIMARY KEY AUTO_INCREMENT,
	inst_id				INT NOT NULL,
	year					INT NOT NULL,
	value					NUMERIC NULL
);
SELECT * FROM herd21;

drop table if exists herd_rank;
CREATE TABLE herd_rank (
	rank_id				INT PRIMARY KEY AUTO_INCREMENT,
	inst_id				INT NOT NULL,
	YEAR					INT NOT NULL,
	RANK					INT	NULL
);
SELECT * FROM herd_rank;

drop table if exists herd_fund_source;
CREATE TABLE herd_fund_source (
	tbl_hfs_id			INT PRIMARY KEY AUTO_INCREMENT,
	inst_id				INT 				NOT NULL,
	YEAR					INT 				NOT NULL,
	fund_source			VARCHAR(255) 	NULL,
	VALUE					NUMERIC     	NULL
);
select * from herd_fund_source;