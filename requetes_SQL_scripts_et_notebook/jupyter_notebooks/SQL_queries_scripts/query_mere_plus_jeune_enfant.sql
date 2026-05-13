SELECT p.name AS mother_name, 
       MIN(c.age) AS youngest_child_age
FROM people p
JOIN people c ON c.motherId = p.id
GROUP BY p.name;