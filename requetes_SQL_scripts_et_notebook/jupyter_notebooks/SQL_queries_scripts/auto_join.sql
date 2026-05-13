-- AUTO JOIN (self-join example)
SELECT c1.id AS customer_id_1, 
	   c1.name AS customer_name_1, 
	   c2.id AS customer_id_2, 
	   c2.name AS customer_name_2
FROM customers c1
INNER JOIN customers c2 ON c1.id == c2.id;
-- INNER JOIN customers c2 ON c1.id != c2.id;