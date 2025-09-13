-- Remove spaces and replace NULL with 'unknown' (or your preferred default)


SHOW TABLES;
DESCRIBE bank_marketing;
SELECT COUNT(*) FROM bank_marketing;
-- Job categories
SELECT job, COUNT(*) FROM bank_marketing GROUP BY job;

-- Marital status
SELECT marital, COUNT(*) FROM bank_marketing GROUP BY marital;

-- Education
SELECT education, COUNT(*) FROM bank_marketing GROUP BY education;

-- Contact type
SELECT contact, COUNT(*) FROM bank_marketing GROUP BY contact;


SET SQL_SAFE_UPDATES = 0;

UPDATE bank_marketing
SET job = TRIM(IFNULL(job, 'unknown'));

UPDATE bank_marketing
SET marital = TRIM(IFNULL(marital, 'unknown'));

UPDATE bank_marketing
SET education = TRIM(IFNULL(education, 'unknown'));

UPDATE bank_marketing
SET contact = TRIM(IFNULL(contact, 'unknown'));


-- Job categories
SELECT job, COUNT(*) FROM bank_marketing GROUP BY job;

-- Marital status
SELECT marital, COUNT(*) FROM bank_marketing GROUP BY marital;

-- Education
SELECT education, COUNT(*) FROM bank_marketing GROUP BY education;

-- Contact type
SELECT contact, COUNT(*) FROM bank_marketing GROUP BY contact;

