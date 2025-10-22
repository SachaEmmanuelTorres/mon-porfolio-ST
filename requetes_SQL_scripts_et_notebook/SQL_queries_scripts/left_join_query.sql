SELECT customers.*,
	   orders.order_id
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id
