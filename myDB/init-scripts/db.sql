drop table if EXISTS testing;
CREATE TABLE testing(
    id INT NOT NULL AUTO_INCREMENT,
    name TINYTEXT NOT NULL,
    PRIMARY KEY(id)
    );
insert into testing (name) values ("testing 1");
insert into testing (name) values ("testing 2");
insert into testing (name) values ("testing 3");  