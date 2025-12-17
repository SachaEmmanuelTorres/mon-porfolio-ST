CREATE TABLE products (
	id INTEGER,
	name TEXT,
	price INTEGER  CHECK (price > 0),
	stock INTEGER,
	PRIMARY KEY(ID)
	

); 