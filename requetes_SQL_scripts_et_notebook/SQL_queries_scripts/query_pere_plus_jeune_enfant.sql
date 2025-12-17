SELECT p.name AS father_name, 
	   MIN(c.age) AS youngest_child_age
FROM people p
JOIN people c ON c.fatherId = p.id
GROUP BY p.name;