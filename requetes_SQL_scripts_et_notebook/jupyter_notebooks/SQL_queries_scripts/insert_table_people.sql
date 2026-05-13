INSERT INTO people (id, name, fatherId, motherId) VALUES
(1, 'John', NULL, NULL),  -- Père
(2, 'Jane', NULL, NULL),  -- Mère
(3, 'Alice', 1, 2),  -- Enfant 1 avec John comme père et Jane comme mère
(4, 'Bob', 1, 2);    -- Enfant 2 avec John comme père et Jane comme mère