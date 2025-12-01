drop table if exists institution;
CREATE TABLE institution (
	inst_id 			INT 			PRIMARY KEY AUTO_INCREMENT,
	inst_name		VARCHAR(255)		NOT NULL,
	last_update		DATE			NOT NULL
);
SELECT * FROM institution;

drop table if exists herd_exp;
CREATE TABLE herd_exp (
	exp_id 				INT PRIMARY KEY AUTO_INCREMENT,
	inst_id				INT NOT NULL,
	year				int not null,
	value				NUMERIC NULL,
	FOREIGN KEY (inst_id) REFERENCES institution(inst_id)
);
select * from herd_exp;

drop table if exists herd_rank;
CREATE TABLE herd_rank (
	rank_id				INT PRIMARY KEY AUTO_INCREMENT,
	inst_id				INT NOT NULL,
	YEAR					INT NOT NULL,
	RANK					INT	NULL,
	FOREIGN KEY (inst_id) REFERENCES institution(inst_id)
);
SELECT * FROM herd_rank;

drop table if exists herd_fund_source_cat;
CREATE TABLE herd_fund_source_cat (
	fund_source_id			INT PRIMARY KEY AUTO_INCREMENT,
	fund_source				VARCHAR(255) 	NULL,
	last_update				DATE		NOT NULL
);
select * from herd_fund_source_cat;

drop table if exists herd_fund_source;
CREATE TABLE herd_fund_source (
	tbl_hfs_id			INT PRIMARY KEY AUTO_INCREMENT,
	inst_id				INT 				NOT NULL,
	fund_source_id		INT				 	NOT NULL,
	YEAR				INT 				NOT NULL,
	VALUE					NUMERIC     	NULL,
	FOREIGN KEY (inst_id) REFERENCES institution(inst_id),
	FOREIGN KEY (fund_source_id) REFERENCES herd_fund_source_cat(fund_source_id)
);
select * from herd_fund_source;

drop table if exists herd_field;
CREATE TABLE herd_field (
	field_id				INT PRIMARY KEY AUTO_INCREMENT,
	field_name				VARCHAR(255) 			NOT NULL,
	last_update				DATE				NOT NULL
);
select * from herd_field;

drop table if exists herd_fund_field;
CREATE TABLE herd_fund_field (
	tbl_field_id					INT PRIMARY KEY AUTO_INCREMENT,
	inst_id					INT 				NOT NULL,
	field_id				INT					NOT NULL,
	YEAR					INT 				NOT NULL,
	VALUE					NUMERIC     	NULL,
	FOREIGN KEY (inst_id) REFERENCES institution(inst_id),
	FOREIGN KEY (field_id) REFERENCES herd_field(field_id)
);
select * from herd_fund_field;


drop table if exists herd_headcount_cat;
CREATE TABLE herd_headcount_cat (
	headcount_cat_id		INT PRIMARY KEY AUTO_INCREMENT,
	headcount_cat			VARCHAR(255) 			NOT NULL,
	last_update				DATE				NOT NULL
);
select * from herd_headcount_cat;


drop table if exists herd_headcount;
CREATE TABLE herd_headcount (
	tbl_headcount_id			INT PRIMARY KEY AUTO_INCREMENT,
	headcount_cat_id			INT NOT NULL,
	inst_id						INT NOT NULL,
	fte							INT NULL,
	YEAR						INT 		NOT NULL,
	VALUE						NUMERIC    	NULL,
	FOREIGN KEY (inst_id) REFERENCES institution(inst_id),
	FOREIGN KEY (headcount_cat_id) REFERENCES herd_headcount_cat(headcount_cat_id)
);
select * from herd_headcount;


drop table if exists herd_state;
CREATE TABLE herd_state (
	state_id				INT PRIMARY KEY AUTO_INCREMENT,
	state_name				VARCHAR(255) 			NOT NULL,
	last_update				DATE				NOT NULL
);
select * from herd_state;

drop table if exists herd_headcount_state;
CREATE TABLE herd_headcount_state (
	tbl_headcount_state_id			INT PRIMARY KEY AUTO_INCREMENT,
	headcount_cat_id			INT NOT NULL,
	state_id						INT NOT NULL,
	fte							INT NULL,
	YEAR						INT 		NOT NULL,
	VALUE						NUMERIC    	NULL,
	FOREIGN KEY (state_id) REFERENCES herd_state(state_id),
	FOREIGN KEY (headcount_cat_id) REFERENCES herd_headcount_cat(headcount_cat_id)
);
select * from herd_headcount_state;