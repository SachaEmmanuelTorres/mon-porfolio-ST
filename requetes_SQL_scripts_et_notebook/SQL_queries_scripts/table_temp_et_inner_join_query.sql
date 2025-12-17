-- WITH test_temp_table AS (
-- 	SELECT orders.order_id, orders.customer_id, customers.name
-- 	FROM orders
-- 	INNER JOIN customers ON orders.customer_id = customers.id
-- 	)
-- 	SELECT * FROM test_temp_table;
-- 	la table temporaire est inutile et couteuse dans ce cas 
SELECT orders.order_id, orders.customer_id, customers.name
FROM orders
INNER JOIN customers ON orders.customer_id = customers.id