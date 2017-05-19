
## Looking for the rare postal code after cleaning with python before

SELECT tags.value, COUNT(*) as num
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
	  SELECT * FROM ways_tags) tags
WHERE tags.key = 'postcode' 
OR tags.key = 'postal_code'
GROUP BY tags.value 
ORDER BY num 
LIMIT 20;

## FIXING POSTAL CODE ONE BY ONE 

SELECT id 
FROM ways_tags 
WHERE key='postcode' 
AND value = '001963';


SELECT * FROM ways_tags WHERE id=429260650 and type='addr';

## UPDATE THE POSTAL CODE WITH THE CORRECTED VALUE 
UPDATE ways_tags 
SET value = '00193' 
WHERE id ='429260650' 
AND key = 'postcode'; 


## SAME PROCESS BIT FOR NODES TAGS 
SELECT id 
FROM nodes_tags 
WHERE key='postcode' 
AND value = '0747';

SELECT * FROM nodes_tags WHERE id=4790951322 and type='addr';

UPDATE nodes_tags 
SET value = '00195' 
WHERE id ='4790951322' 
AND key = 'postcode'; 


## MOST FREEQUENT POSTAL CODE 

SELECT tags.value, COUNT(*) as num
FROM (SELECT * FROM nodes_tags 
	  UNION ALL 
	  SELECT * FROM ways_tags) tags
WHERE tags.key = 'postcode' 
OR tags.key = 'postal_code'
GROUP BY tags.value 
ORDER BY num DESC
LIMIT 10;

## CITY WITH HIGER FREQUENCY 

SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key == 'city'
GROUP BY tags.value
ORDER BY count DESC
LIMIT 20;



## Count Unique USERS uid 

SELECT COUNT(DISTINCT(users.uid)) as count 
FROM (SELECT uid FROM ways UNION ALL SELECT uid FROM nodes) users;


# Count of nodes and ways 

SELECT COUNT(*) as count
FROM nodes;


SELECT COUNT(*) as count
FROM ways; 



## Numer of users that apper just one time , i will use the code writter befor and usinf it for FROM 

SELECT COUNT(*)
FROM (SELECT users.user ,  COUNT(*) as count 
FROM (SELECT user FROM ways UNION ALL SELECT user FROM nodes) users
GROUP BY users.user
HAVING count = 1) zero;

### Top 20 amenities 

SELECT value, COUNT(*) as count
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY count DESC
LIMIT 20;

###  BEST cuisine for retaurant, bar and cafe

SELECT nodes_tags.value, COUNT(*) as count
FROM nodes_tags ,(SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') as restaurant
WHERE nodes_tags.id=restaurant.id
AND nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY count DESC
LIMIT 5;






