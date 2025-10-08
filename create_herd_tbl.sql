drop table if exists herd_exp;
CREATE TABLE herd_exp (
	tb1_id 				SERIAL PRIMARY KEY,
	year				int not null,
	fund_source			VARCHAR not null,
	amount				numeric,
	herd_tbl			int not null
);

select * from herd_exp;

drop table if exists institution;
CREATE TABLE institution (
	inst_id 		SERIAL		PRIMARY KEY,
	inst_name		VARCHAR		NOT NULL,
	last_update		DATE		NOT NULL
);
SELECT * FROM institution;
select * from institution where inst_name like 'U. South %';
SELECT CURRENT_DATE;

drop table if exists herd21;
CREATE TABLE herd21 (
	tb21_id				SERIAL PRIMARY KEY,
	inst_id				INT NOT NULL,
	year				INT NOT NULL,
	value				NUMERIC NULL
);
SELECT * FROM herd21;
select * from herd21 where inst_id=76;

drop table if exists herd_rank;
CREATE TABLE herd_rank (
	rank_id				SERIAL PRIMARY KEY,
	inst_id				INT NOT NULL,
	year				INT NOT NULL,
	rank				INT	NULL
);
SELECT * FROM herd_rank;
select * from herd_rank where inst_id=2;

drop table if exists herd_fund_source;
CREATE TABLE herd_fund_source (
	tbl_hfs_id				SERIAL PRIMARY KEY,
	inst_id				INT NOT NULL,
	year				INT NOT NULL,
	fund_source			VARCHAR 	NULL,
	value				NUMERIC     NULL
);
select * from herd_fund_source where year=2021 order by tbl_hfs_id;