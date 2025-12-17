-- Simulating FULL OUTER JOIN using UNION
SELECT orders.order_id, orders.customer_id, customers.name
FROM orders
LEFT JOIN customers ON orders.customer_id = customers.id
UNION
SELECT orders.order_id, orders.customer_id, customers.name
FROM customers
-- simulate RIGTH JOIN
LEFT JOIN orders ON customers.id = orders.customer_id;