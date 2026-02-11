CREATE TABLE bank (
    age INT,
    job VARCHAR(50),
    marital VARCHAR(20),
    education VARCHAR(30),
    defaulted VARCHAR(10),
    balance DECIMAL(10,2),
    housing VARCHAR(10),
    loan VARCHAR(10),
    contact VARCHAR(20),
    day INT,
    month VARCHAR(10),
    duration INT,
    campaign INT,
    pdays INT,
    previous INT,
    poutcome VARCHAR(20),
    y VARCHAR(10)
);

INSERT INTO bank VALUES
(30,'unemployed','married','primary','no',1787.00,'no','no','cellular',19,'oct',79,1,-1,0,'unknown','no'),
(33,'services','married','secondary','no',4789.00,'yes','yes','cellular',11,'may',220,1,339,4,'failure','no'),
(35,'management','single','tertiary','no',1350.00,'yes','no','cellular',16,'apr',185,1,330,1,'failure','no'),
(30,'technician','married','tertiary','no',1476.00,'yes','yes','unknown',3,'jun',199,4,339,4,'other','yes');

