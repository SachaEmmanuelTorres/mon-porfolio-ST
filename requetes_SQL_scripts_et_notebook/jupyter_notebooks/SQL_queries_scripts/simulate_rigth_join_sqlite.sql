SELECT customers.*,
	   orders.order_id
FROM customers
-- simulation de RIGTH JOIN
LEFT JOIN orders ON orders.customer_id = customers.id