drop table product;
drop table request;
drop table user;
drop table inspector;
drop table enterprise;
drop table register;
drop table market;

CREATE TABLE "user" (
	id varchar(20) NOT NULL,
	"name" varchar(20) NULL,
	e_mail varchar(30) NULL,
	CONSTRAINT "User_pkey" PRIMARY KEY (id)
);

CREATE TABLE enterprise (
	id varchar(20) NOT NULL,
	"name" varchar(20) NULL,
	e_mail varchar(30) NULL,
	CONSTRAINT enterprise_pkey PRIMARY KEY (id)
);

CREATE TABLE inspector (
	id varchar(20) NOT NULL,
	"name" varchar(20) NULL,
	e_mail varchar(30) NULL,
	introduce text NULL,
	CONSTRAINT inspector_pkey PRIMARY KEY (id)
);

CREATE TABLE register (
	id varchar(20) NOT NULL,
	"password" varchar NULL,
	"role" varchar(20) NULL,
	CONSTRAINT chk_password_length CHECK ((length((password)::text) > 7)),
	CONSTRAINT register_pkey PRIMARY KEY (id)
);

CREATE TABLE request (
	request_product_id varchar(20) NOT NULL,
	client_id varchar(20) NULL,
	inspector_id varchar(20) NULL,
	request_message text NULL,
	request_complete bool NULL DEFAULT false,
	CONSTRAINT request_pk PRIMARY KEY (request_product_id),
	CONSTRAINT request_inspector_id_fkey FOREIGN KEY (inspector_id) REFERENCES inspector(id),
	CONSTRAINT request_request_product_id_fkey FOREIGN KEY (request_product_id) REFERENCES product(product_id)
);

CREATE TABLE product (
	product_id varchar(20) NOT NULL,
	enterprise_id varchar(20) NULL,
	product_name varchar(20) NULL,
	product_description text NULL,
	category varchar(20) NOT NULL,
	phase_owner varchar(20) NULL,
	price int4 NULL,
	certification bool NULL DEFAULT false,
	CONSTRAINT chk_category_not_null CHECK ((category IS NOT NULL)),
	CONSTRAINT product_pkey PRIMARY KEY (product_id),
	CONSTRAINT product_price_check CHECK (((price >= 0) AND (price <= 10000000))),
	CONSTRAINT product_enterpriseid_fkey FOREIGN KEY (enterprise_id) REFERENCES enterprise(id),
	CONSTRAINT product_phase_owner_fkey FOREIGN KEY (phase_owner) REFERENCES "user"(id)
);

CREATE TABLE market (
	product_id varchar(20) NULL,
	enrollment_date date NULL,
	CONSTRAINT market_product_id_fkey FOREIGN KEY (product_id) REFERENCES product(product_id)
);

CREATE ROLE "user" WITH 
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	NOLOGIN
	NOREPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1;

CREATE ROLE enterprise WITH 
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	NOLOGIN
	NOREPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1;

CREATE ROLE inspector WITH 
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	NOLOGIN
	NOREPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1;


GRANT INSERT, SELECT ON TABLE request TO "user";
GRANT SELECT, UPDATE ON TABLE "user" TO "user";
GRANT SELECT ON TABLE enterprise TO "user";
GRANT SELECT ON TABLE inspector TO "user";
GRANT DELETE, SELECT ON TABLE market TO "user";
GRANT SELECT, UPDATE ON TABLE register TO "user";
GRANT SELECT, UPDATE ON TABLE product TO "user";


GRANT INSERT, SELECT ON TABLE request TO enterprise;
GRANT SELECT ON TABLE "user" TO enterprise;
GRANT SELECT, UPDATE ON TABLE enterprise TO enterprise;
GRANT SELECT ON TABLE inspector TO enterprise;
GRANT INSERT, SELECT ON TABLE market TO enterprise;
GRANT SELECT, UPDATE ON TABLE register TO enterprise;
GRANT INSERT, SELECT ON TABLE product TO enterprise;

GRANT SELECT, UPDATE ON TABLE request TO inspector;
GRANT SELECT ON TABLE "user" TO inspector;
GRANT SELECT ON TABLE enterprise TO inspector;
GRANT SELECT, UPDATE ON TABLE inspector TO inspector;
GRANT SELECT ON TABLE market TO inspector;
GRANT SELECT, UPDATE ON TABLE register TO inspector;
GRANT SELECT, UPDATE ON TABLE product TO inspector;