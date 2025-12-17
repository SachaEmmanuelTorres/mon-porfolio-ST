-- Mettre à jour les âges des parents
UPDATE people SET age = 40 WHERE id = 1;  -- John
UPDATE people SET age = 38 WHERE id = 2;  -- Jane

-- Mettre à jour les âges des enfants
UPDATE people SET age = 10 WHERE id = 3;  -- Alice
UPDATE people SET age = 8 WHERE id = 4;   -- Bob