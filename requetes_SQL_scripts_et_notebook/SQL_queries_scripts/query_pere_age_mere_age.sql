-- Nom du pere et âge minimum de ses enfants
SELECT 
    p1.name AS father_name, 
-- 	p2.name AS child_name,
    MIN(p2.age) AS min_child_age
FROM people p1
JOIN people p2  ON p1.id = p2.fatherId
GROUP BY p1.name

UNION

-- Nom de la mère et âge minimum de ses enfants
SELECT 
    p1.name AS mother_name, 
-- 	p2.name AS child_name,
    MIN(p2.age) AS min_child_age
FROM people p1
JOIN people p2 ON p1.id = p2.motherId
GROUP BY p1.name;