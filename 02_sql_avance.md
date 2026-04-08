# Expert SQL — Préparation Morgan Stanley HackerRank

> **Objectif** : Réviser les concepts SQL avancés pour un test de 60 minutes axé sur l'entrepôt de données Snowflake, les transformations et l'optimisation de requêtes.

---

## 1. Fonctions de fenêtrage (Window Functions)

### Définitions

Les fonctions de fenêtrage effectuent un calcul sur un ensemble de lignes liées à la ligne courante, **sans regrouper** les résultats. Contrairement à `GROUP BY`, chaque ligne conserve son identité.

**Syntaxe générale :**
```sql
fonction() OVER (
    [PARTITION BY col1, col2]
    [ORDER BY col3]
    [ROWS|RANGE BETWEEN début AND fin]
)
```

#### Fonctions de classement

| Fonction | Description |
|----------|-------------|
| `ROW_NUMBER()` | Numéro séquentiel unique (1, 2, 3...) même en cas d'égalité |
| `RANK()` | Rang avec trous en cas d'égalité (1, 2, 2, 4) |
| `DENSE_RANK()` | Rang sans trous en cas d'égalité (1, 2, 2, 3) |
| `NTILE(n)` | Divise les lignes en n groupes égaux |

#### Fonctions d'agrégation fenêtrées

```sql
SUM(montant) OVER (PARTITION BY departement ORDER BY date_embauche)
AVG(salaire) OVER (PARTITION BY departement)
COUNT(*) OVER ()  -- compte total
MIN(salaire) OVER (PARTITION BY departement)
MAX(salaire) OVER (PARTITION BY departement)
```

#### Fonctions de décalage

| Fonction | Description |
|----------|-------------|
| `LAG(col, n, default)` | Valeur de la ligne n rangs **avant** |
| `LEAD(col, n, default)` | Valeur de la ligne n rangs **après** |
| `FIRST_VALUE(col)` | Première valeur de la fenêtre |
| `LAST_VALUE(col)` | Dernière valeur de la fenêtre (attention au frame par défaut!) |

#### Frames (ROWS BETWEEN / RANGE BETWEEN)

```sql
-- Frame par défaut quand ORDER BY est présent :
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW

-- Exemples courants :
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW     -- du début jusqu'à la ligne courante
ROWS BETWEEN 2 PRECEDING AND CURRENT ROW              -- 3 dernières lignes
ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING       -- de la ligne courante à la fin
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING -- toute la partition
ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING               -- ligne précédente + courante + suivante
```

> **Piège courant** : `LAST_VALUE` avec le frame par défaut ne retourne PAS la dernière ligne de la partition. Il faut spécifier `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.

### Exemples détaillés

```sql
-- Données sample
CREATE TABLE employes (
    id INT,
    nom VARCHAR(50),
    departement VARCHAR(30),
    salaire DECIMAL(10,2),
    date_embauche DATE
);

INSERT INTO employes VALUES
(1, 'Alice',   'Finance',  75000, '2020-01-15'),
(2, 'Bob',     'Finance',  82000, '2019-06-01'),
(3, 'Charlie', 'Finance',  75000, '2021-03-20'),
(4, 'Diana',   'IT',       90000, '2018-09-10'),
(5, 'Eve',     'IT',       95000, '2020-11-05'),
(6, 'Frank',   'IT',       88000, '2021-07-15'),
(7, 'Grace',   'RH',       65000, '2019-02-28'),
(8, 'Henry',   'RH',       70000, '2020-08-12');
```

**Exemple 1 : Classement des salaires par département**
```sql
SELECT
    nom,
    departement,
    salaire,
    ROW_NUMBER() OVER (PARTITION BY departement ORDER BY salaire DESC) AS row_num,
    RANK()       OVER (PARTITION BY departement ORDER BY salaire DESC) AS rang,
    DENSE_RANK() OVER (PARTITION BY departement ORDER BY salaire DESC) AS dense_rang
FROM employes;

-- Résultat (Finance) :
-- Bob      | Finance | 82000 | 1 | 1 | 1
-- Alice    | Finance | 75000 | 2 | 2 | 2
-- Charlie  | Finance | 75000 | 3 | 2 | 2   ← ROW_NUMBER différent, RANK et DENSE_RANK identiques
```

**Exemple 2 : Cumul et comparaison avec la ligne précédente**
```sql
SELECT
    nom,
    departement,
    salaire,
    SUM(salaire) OVER (PARTITION BY departement ORDER BY date_embauche
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumul_salaire,
    LAG(salaire, 1, 0) OVER (PARTITION BY departement ORDER BY date_embauche) AS salaire_precedent,
    salaire - LAG(salaire, 1, 0) OVER (PARTITION BY departement ORDER BY date_embauche) AS diff
FROM employes
ORDER BY departement, date_embauche;
```

**Exemple 3 : Moyenne mobile sur 3 périodes**
```sql
SELECT
    nom,
    date_embauche,
    salaire,
    AVG(salaire) OVER (ORDER BY date_embauche
                       ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moyenne_mobile_3
FROM employes;
```

### Exercices

**Exercice 1** : Pour chaque département, afficher le nom de l'employé, son salaire, et le pourcentage que représente son salaire par rapport au total du département.

<details>
<summary>Solution</summary>

```sql
SELECT
    nom,
    departement,
    salaire,
    ROUND(salaire * 100.0 / SUM(salaire) OVER (PARTITION BY departement), 2) AS pct_dept
FROM employes
ORDER BY departement, pct_dept DESC;
```
</details>

**Exercice 2** : Afficher pour chaque employé la différence entre son salaire et le salaire le plus élevé de son département.

<details>
<summary>Solution</summary>

```sql
SELECT
    nom,
    departement,
    salaire,
    MAX(salaire) OVER (PARTITION BY departement) - salaire AS ecart_max
FROM employes;
```
</details>

**Exercice 3** : Classer les employés en 3 groupes (terciles) selon leur salaire global, puis afficher le groupe de chaque employé.

<details>
<summary>Solution</summary>

```sql
SELECT
    nom,
    salaire,
    NTILE(3) OVER (ORDER BY salaire) AS tercile
FROM employes;
```
</details>

**Exercice 4** : Pour chaque employé, afficher son salaire, le salaire de l'employé embauché juste avant lui dans le même département (LAG), et le salaire de celui embauché juste après (LEAD).

<details>
<summary>Solution</summary>

```sql
SELECT
    nom,
    departement,
    date_embauche,
    salaire,
    LAG(salaire)  OVER (PARTITION BY departement ORDER BY date_embauche) AS salaire_avant,
    LEAD(salaire) OVER (PARTITION BY departement ORDER BY date_embauche) AS salaire_apres
FROM employes;
```
</details>

**Exercice 5** : Pour chaque département, afficher le premier et le dernier employé embauché (par nom) en utilisant FIRST_VALUE et LAST_VALUE.

<details>
<summary>Solution</summary>

```sql
SELECT DISTINCT
    departement,
    FIRST_VALUE(nom) OVER (PARTITION BY departement ORDER BY date_embauche
                           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS premier_embauche,
    LAST_VALUE(nom)  OVER (PARTITION BY departement ORDER BY date_embauche
                           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS dernier_embauche
FROM employes;
```
</details>

---

## 2. CTEs (Common Table Expressions)

### Définitions

Une CTE est une expression de table temporaire définie avec `WITH` qui existe uniquement le temps de la requête. Elle améliore la lisibilité et permet la réutilisation.

**CTE simple :**
```sql
WITH cte_nom AS (
    SELECT ...
)
SELECT * FROM cte_nom;
```

**CTEs multiples :**
```sql
WITH
    cte1 AS (SELECT ...),
    cte2 AS (SELECT ... FROM cte1)  -- cte2 peut référencer cte1
SELECT * FROM cte2;
```

**CTE récursive** (pour hiérarchies, séries, graphes) :
```sql
WITH RECURSIVE cte AS (
    -- Membre ancre (cas de base)
    SELECT ... WHERE condition_initiale
    UNION ALL
    -- Membre récursif
    SELECT ... FROM cte WHERE condition_arret
)
SELECT * FROM cte;
```

> **Note Snowflake** : Snowflake utilise `WITH RECURSIVE` comme PostgreSQL.

### Exemples détaillés

**Données sample pour hiérarchie :**
```sql
CREATE TABLE employes_hierarchie (
    id INT,
    nom VARCHAR(50),
    manager_id INT,
    titre VARCHAR(50)
);

INSERT INTO employes_hierarchie VALUES
(1, 'CEO Martin',    NULL, 'CEO'),
(2, 'VP Finance',    1,    'Vice-Président'),
(3, 'VP IT',         1,    'Vice-Président'),
(4, 'Dir Compta',    2,    'Directeur'),
(5, 'Dir Dev',       3,    'Directeur'),
(6, 'Analyste Jean', 4,    'Analyste'),
(7, 'Dev Sophie',    5,    'Développeur'),
(8, 'Dev Marc',      5,    'Développeur');
```

**Exemple 1 : Hiérarchie complète avec niveau**
```sql
WITH RECURSIVE hierarchie AS (
    -- Ancre : le CEO (pas de manager)
    SELECT id, nom, manager_id, titre, 1 AS niveau, nom AS chemin
    FROM employes_hierarchie
    WHERE manager_id IS NULL

    UNION ALL

    -- Récursion : les subordonnés
    SELECT e.id, e.nom, e.manager_id, e.titre,
           h.niveau + 1,
           h.chemin || ' > ' || e.nom
    FROM employes_hierarchie e
    JOIN hierarchie h ON e.manager_id = h.id
)
SELECT * FROM hierarchie ORDER BY chemin;

-- Résultat :
-- 1 | CEO Martin    | NULL | CEO            | 1 | CEO Martin
-- 2 | VP Finance    | 1    | Vice-Président | 2 | CEO Martin > VP Finance
-- 4 | Dir Compta    | 2    | Directeur      | 3 | CEO Martin > VP Finance > Dir Compta
-- 6 | Analyste Jean | 4    | Analyste       | 4 | CEO Martin > VP Finance > Dir Compta > Analyste Jean
```

**Exemple 2 : Générer une série de dates**
```sql
WITH RECURSIVE dates AS (
    SELECT DATE '2026-01-01' AS dt
    UNION ALL
    SELECT DATEADD(DAY, 1, dt)
    FROM dates
    WHERE dt < DATE '2026-01-31'
)
SELECT dt FROM dates;
```

**Exemple 3 : CTEs multiples pour analyse**
```sql
WITH
    ventes_mensuelles AS (
        SELECT
            DATE_TRUNC('MONTH', date_vente) AS mois,
            SUM(montant) AS total_mensuel
        FROM ventes
        GROUP BY DATE_TRUNC('MONTH', date_vente)
    ),
    stats AS (
        SELECT
            AVG(total_mensuel) AS moyenne,
            STDDEV(total_mensuel) AS ecart_type
        FROM ventes_mensuelles
    )
SELECT
    vm.mois,
    vm.total_mensuel,
    s.moyenne,
    CASE
        WHEN vm.total_mensuel > s.moyenne + s.ecart_type THEN 'Au-dessus'
        WHEN vm.total_mensuel < s.moyenne - s.ecart_type THEN 'En-dessous'
        ELSE 'Normal'
    END AS classification
FROM ventes_mensuelles vm
CROSS JOIN stats s;
```

### Exercices

**Exercice 1** : Avec la table `employes_hierarchie`, trouver tous les subordonnés directs et indirects du VP IT (id=3).

<details>
<summary>Solution</summary>

```sql
WITH RECURSIVE subord AS (
    SELECT id, nom, manager_id, titre
    FROM employes_hierarchie
    WHERE manager_id = 3

    UNION ALL

    SELECT e.id, e.nom, e.manager_id, e.titre
    FROM employes_hierarchie e
    JOIN subord s ON e.manager_id = s.id
)
SELECT * FROM subord;
```
</details>

**Exercice 2** : Générer la suite de Fibonacci jusqu'à 100 avec une CTE récursive.

<details>
<summary>Solution</summary>

```sql
WITH RECURSIVE fib AS (
    SELECT 0 AS a, 1 AS b
    UNION ALL
    SELECT b, a + b FROM fib WHERE b < 100
)
SELECT a AS fibonacci FROM fib;
```
</details>

**Exercice 3** : Calculer le cumul des ventes par produit en utilisant des CTEs (pas de window function).

<details>
<summary>Solution</summary>

```sql
WITH ventes_data AS (
    SELECT produit_id, date_vente, montant
    FROM ventes
),
cumul AS (
    SELECT
        v1.produit_id,
        v1.date_vente,
        v1.montant,
        (SELECT SUM(v2.montant)
         FROM ventes_data v2
         WHERE v2.produit_id = v1.produit_id
         AND v2.date_vente <= v1.date_vente) AS cumul
    FROM ventes_data v1
)
SELECT * FROM cumul ORDER BY produit_id, date_vente;
```
</details>

**Exercice 4** : Avec une CTE, identifier les employés dont le salaire est supérieur à la moyenne de leur département.

<details>
<summary>Solution</summary>

```sql
WITH moy_dept AS (
    SELECT departement, AVG(salaire) AS salaire_moyen
    FROM employes
    GROUP BY departement
)
SELECT e.nom, e.departement, e.salaire, m.salaire_moyen
FROM employes e
JOIN moy_dept m ON e.departement = m.departement
WHERE e.salaire > m.salaire_moyen;
```
</details>

**Exercice 5** : Écrire une CTE récursive pour décomposer un nombre en puissances de 2 (ex: 13 = 8+4+1).

<details>
<summary>Solution</summary>

```sql
WITH RECURSIVE decomp AS (
    SELECT 13 AS reste, FLOOR(LOG(2, 13))::INT AS puissance
    UNION ALL
    SELECT reste - POWER(2, puissance)::INT,
           FLOOR(LOG(2, reste - POWER(2, puissance)::INT))::INT
    FROM decomp
    WHERE reste - POWER(2, puissance)::INT > 0
)
SELECT POWER(2, puissance)::INT AS valeur FROM decomp;
```
</details>

---

## 3. Sous-requêtes avancées

### Définitions

**Sous-requête non corrélée** : Exécutée une seule fois, indépendamment de la requête externe.
```sql
SELECT * FROM employes WHERE salaire > (SELECT AVG(salaire) FROM employes);
```

**Sous-requête corrélée** : Exécutée pour chaque ligne de la requête externe, référence des colonnes de la requête externe.
```sql
SELECT * FROM employes e
WHERE salaire > (SELECT AVG(salaire) FROM employes WHERE departement = e.departement);
```

**Opérateurs :**
- `EXISTS` : Vrai si la sous-requête retourne au moins une ligne
- `IN` : Vrai si la valeur est dans l'ensemble retourné
- `ANY/SOME` : Vrai si la comparaison est vraie pour au moins une valeur
- `ALL` : Vrai si la comparaison est vraie pour toutes les valeurs

### Exemples détaillés

```sql
-- EXISTS : Départements qui ont au moins un employé avec salaire > 80000
SELECT DISTINCT departement
FROM employes e1
WHERE EXISTS (
    SELECT 1 FROM employes e2
    WHERE e2.departement = e1.departement
    AND e2.salaire > 80000
);

-- NOT EXISTS : Employés qui ne sont managers de personne
SELECT e.nom
FROM employes_hierarchie e
WHERE NOT EXISTS (
    SELECT 1 FROM employes_hierarchie sub
    WHERE sub.manager_id = e.id
);

-- ALL : Employé avec le salaire le plus élevé (sans MAX)
SELECT nom, salaire
FROM employes
WHERE salaire >= ALL (SELECT salaire FROM employes);

-- Sous-requête dans FROM (table dérivée)
SELECT dept_stats.departement, dept_stats.nb_employes
FROM (
    SELECT departement, COUNT(*) AS nb_employes, AVG(salaire) AS avg_sal
    FROM employes
    GROUP BY departement
) dept_stats
WHERE dept_stats.avg_sal > 75000;

-- Sous-requête dans SELECT (scalar subquery)
SELECT
    nom,
    salaire,
    (SELECT AVG(salaire) FROM employes e2
     WHERE e2.departement = e1.departement) AS avg_dept
FROM employes e1;
```

### Exercices

**Exercice 1** : Trouver les employés qui gagnent plus que tous les employés du département RH (utiliser ALL).

<details>
<summary>Solution</summary>

```sql
SELECT nom, salaire
FROM employes
WHERE salaire > ALL (
    SELECT salaire FROM employes WHERE departement = 'RH'
);
```
</details>

**Exercice 2** : Trouver le deuxième salaire le plus élevé par département en utilisant une sous-requête corrélée.

<details>
<summary>Solution</summary>

```sql
SELECT e1.departement, e1.nom, e1.salaire
FROM employes e1
WHERE 1 = (
    SELECT COUNT(DISTINCT e2.salaire)
    FROM employes e2
    WHERE e2.departement = e1.departement
    AND e2.salaire > e1.salaire
);
```
</details>

**Exercice 3** : Afficher les départements dont le salaire moyen est supérieur au salaire moyen global, en utilisant une sous-requête dans HAVING.

<details>
<summary>Solution</summary>

```sql
SELECT departement, AVG(salaire) AS avg_salaire
FROM employes
GROUP BY departement
HAVING AVG(salaire) > (SELECT AVG(salaire) FROM employes);
```
</details>

---

## 4. MERGE / UPSERT

### Définitions

`MERGE` combine INSERT, UPDATE et DELETE en une seule instruction. Essentiel pour les patterns de Data Engineering : synchronisation de données, SCD (Slowly Changing Dimensions).

**Syntaxe complète :**
```sql
MERGE INTO table_cible t
USING table_source s
ON t.cle = s.cle
WHEN MATCHED AND s.flag = 'D' THEN DELETE
WHEN MATCHED THEN UPDATE SET t.col1 = s.col1, t.col2 = s.col2
WHEN NOT MATCHED THEN INSERT (col1, col2) VALUES (s.col1, s.col2);
```

### Exemples détaillés

**Données sample :**
```sql
-- Table dimension client (cible)
CREATE TABLE dim_client (
    client_id INT PRIMARY KEY,
    nom VARCHAR(100),
    ville VARCHAR(50),
    segment VARCHAR(20),
    date_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO dim_client VALUES
(1, 'Dupont SA',    'Paris',    'Gold',   '2025-01-01'),
(2, 'Martin Corp',  'Lyon',     'Silver', '2025-01-01'),
(3, 'Bernard Inc',  'Marseille','Bronze', '2025-01-01');

-- Données source (staging)
CREATE TABLE stg_client (
    client_id INT,
    nom VARCHAR(100),
    ville VARCHAR(50),
    segment VARCHAR(20)
);

INSERT INTO stg_client VALUES
(1, 'Dupont SA',     'Paris',     'Platinum'),  -- segment changé
(2, 'Martin Corp',   'Bordeaux',  'Silver'),    -- ville changée
(4, 'Nouveau Client','Toulouse',  'Bronze');     -- nouveau
```

**Exemple 1 : MERGE SCD Type 1 (écrasement)**
```sql
MERGE INTO dim_client t
USING stg_client s
ON t.client_id = s.client_id
WHEN MATCHED THEN
    UPDATE SET
        t.nom = s.nom,
        t.ville = s.ville,
        t.segment = s.segment,
        t.date_maj = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (client_id, nom, ville, segment, date_maj)
    VALUES (s.client_id, s.nom, s.ville, s.segment, CURRENT_TIMESTAMP);
```

**Exemple 2 : MERGE SCD Type 2 (historisation)**
```sql
-- Table avec historique
CREATE TABLE dim_client_scd2 (
    sk_client INT AUTOINCREMENT,      -- surrogate key
    client_id INT,                     -- business key
    nom VARCHAR(100),
    ville VARCHAR(50),
    segment VARCHAR(20),
    date_debut DATE,
    date_fin DATE DEFAULT '9999-12-31',
    est_courant BOOLEAN DEFAULT TRUE
);

-- Étape 1 : Fermer les enregistrements qui ont changé
MERGE INTO dim_client_scd2 t
USING stg_client s
ON t.client_id = s.client_id AND t.est_courant = TRUE
WHEN MATCHED AND (t.nom != s.nom OR t.ville != s.ville OR t.segment != s.segment) THEN
    UPDATE SET
        t.date_fin = CURRENT_DATE - 1,
        t.est_courant = FALSE;

-- Étape 2 : Insérer les nouvelles versions + nouveaux clients
INSERT INTO dim_client_scd2 (client_id, nom, ville, segment, date_debut, date_fin, est_courant)
SELECT s.client_id, s.nom, s.ville, s.segment, CURRENT_DATE, '9999-12-31', TRUE
FROM stg_client s
LEFT JOIN dim_client_scd2 t
    ON s.client_id = t.client_id AND t.est_courant = TRUE
WHERE t.client_id IS NULL;  -- Pas de version courante = nouveau ou vient d'être fermé
```

### Exercices

**Exercice 1** : Écrire un MERGE qui synchronise une table `dim_produit` depuis `stg_produit`, en mettant à jour le prix et la catégorie si changés, et en insérant les nouveaux produits.

<details>
<summary>Solution</summary>

```sql
MERGE INTO dim_produit t
USING stg_produit s
ON t.produit_id = s.produit_id
WHEN MATCHED AND (t.prix != s.prix OR t.categorie != s.categorie) THEN
    UPDATE SET t.prix = s.prix, t.categorie = s.categorie, t.date_maj = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (produit_id, nom, prix, categorie, date_maj)
    VALUES (s.produit_id, s.nom, s.prix, s.categorie, CURRENT_TIMESTAMP);
```
</details>

**Exercice 2** : Écrire un MERGE avec clause DELETE pour supprimer les enregistrements marqués avec `flag_suppression = 'Y'` dans la source.

<details>
<summary>Solution</summary>

```sql
MERGE INTO dim_client t
USING stg_client_full s
ON t.client_id = s.client_id
WHEN MATCHED AND s.flag_suppression = 'Y' THEN DELETE
WHEN MATCHED THEN
    UPDATE SET t.nom = s.nom, t.ville = s.ville, t.segment = s.segment
WHEN NOT MATCHED AND s.flag_suppression != 'Y' THEN
    INSERT (client_id, nom, ville, segment)
    VALUES (s.client_id, s.nom, s.ville, s.segment);
```
</details>

**Exercice 3** : Implémenter un SCD Type 2 complet avec MERGE pour une table `dim_employe` (champs : employe_id, nom, poste, salaire).

<details>
<summary>Solution</summary>

```sql
-- Étape 1 : Fermer les anciens enregistrements modifiés
MERGE INTO dim_employe t
USING stg_employe s
ON t.employe_id = s.employe_id AND t.est_courant = TRUE
WHEN MATCHED AND (t.poste != s.poste OR t.salaire != s.salaire) THEN
    UPDATE SET t.date_fin = CURRENT_DATE - 1, t.est_courant = FALSE;

-- Étape 2 : Insérer les nouvelles versions
INSERT INTO dim_employe (employe_id, nom, poste, salaire, date_debut, date_fin, est_courant)
SELECT s.employe_id, s.nom, s.poste, s.salaire, CURRENT_DATE, '9999-12-31', TRUE
FROM stg_employe s
WHERE NOT EXISTS (
    SELECT 1 FROM dim_employe t
    WHERE t.employe_id = s.employe_id
    AND t.est_courant = TRUE
    AND t.poste = s.poste
    AND t.salaire = s.salaire
);
```
</details>

---

## 5. Agrégations avancées

### Définitions

#### ROLLUP
Génère des sous-totaux hiérarchiques. `GROUP BY ROLLUP(a, b)` produit : (a,b), (a), ().

#### CUBE
Génère toutes les combinaisons possibles. `GROUP BY CUBE(a, b)` produit : (a,b), (a), (b), ().

#### GROUPING SETS
Spécifie exactement les groupements voulus.

```sql
-- ROLLUP : sous-totaux hiérarchiques
SELECT departement, titre, SUM(salaire)
FROM employes
GROUP BY ROLLUP(departement, titre);

-- CUBE : toutes les combinaisons
SELECT departement, titre, SUM(salaire)
FROM employes
GROUP BY CUBE(departement, titre);

-- GROUPING SETS : groupements spécifiques
SELECT departement, titre, SUM(salaire)
FROM employes
GROUP BY GROUPING SETS ((departement, titre), (departement), ());
```

#### GROUPING() — Distinguer les NULL de regroupement
```sql
SELECT
    CASE WHEN GROUPING(departement) = 1 THEN 'TOTAL' ELSE departement END AS dept,
    CASE WHEN GROUPING(titre) = 1 THEN 'TOUS' ELSE titre END AS titre,
    SUM(salaire) AS total_salaire
FROM employes
GROUP BY ROLLUP(departement, titre);
```

#### PIVOT / UNPIVOT (Snowflake)
```sql
-- PIVOT : lignes → colonnes
SELECT *
FROM ventes_mensuelles
PIVOT (SUM(montant) FOR mois IN ('Jan', 'Feb', 'Mar'))
AS p (produit, jan_ventes, feb_ventes, mar_ventes);

-- UNPIVOT : colonnes → lignes
SELECT *
FROM rapport_pivot
UNPIVOT (montant FOR mois IN (jan_ventes, feb_ventes, mar_ventes));
```

### Exercices

**Exercice 1** : Créer un rapport avec ROLLUP montrant : le total des salaires par (département, titre), par département, et le grand total.

<details>
<summary>Solution</summary>

```sql
SELECT
    COALESCE(departement, '--- TOTAL ---') AS departement,
    COALESCE(titre, '--- Sous-total ---') AS titre,
    COUNT(*) AS nb_employes,
    SUM(salaire) AS total_salaire
FROM employes e
JOIN employes_hierarchie eh ON e.id = eh.id
GROUP BY ROLLUP(departement, titre)
ORDER BY departement NULLS LAST, titre NULLS LAST;
```
</details>

**Exercice 2** : Utiliser CUBE pour créer une analyse croisée département × année d'embauche avec somme des salaires.

<details>
<summary>Solution</summary>

```sql
SELECT
    CASE WHEN GROUPING(departement) = 1 THEN 'TOUS' ELSE departement END AS dept,
    CASE WHEN GROUPING(YEAR(date_embauche)) = 1 THEN 'TOUTES' 
         ELSE CAST(YEAR(date_embauche) AS VARCHAR) END AS annee,
    SUM(salaire) AS total,
    COUNT(*) AS nb
FROM employes
GROUP BY CUBE(departement, YEAR(date_embauche))
ORDER BY dept, annee;
```
</details>

**Exercice 3** : Transformer un tableau de ventes mensuelles (colonnes jan, feb, mar...) en format lignes avec UNPIVOT.

<details>
<summary>Solution</summary>

```sql
SELECT produit, mois, montant
FROM ventes_rapport
UNPIVOT (montant FOR mois IN (jan, feb, mar, apr, mai, jun))
ORDER BY produit, mois;
```
</details>

---

## 6. Jointures avancées

### Définitions

| Type | Description |
|------|-------------|
| `CROSS JOIN` | Produit cartésien (chaque ligne × chaque ligne) |
| `SELF JOIN` | Table jointe avec elle-même |
| `LATERAL JOIN` | Sous-requête qui référence des colonnes de la table précédente |
| Anti-join | `LEFT JOIN ... WHERE t2.id IS NULL` — lignes sans correspondance |

### Exemples détaillés

**CROSS JOIN — Générer toutes les combinaisons**
```sql
-- Toutes les combinaisons produit × mois (pour rapport même sans ventes)
SELECT p.nom_produit, m.mois
FROM produits p
CROSS JOIN (
    SELECT DISTINCT DATE_TRUNC('MONTH', date_vente) AS mois
    FROM ventes
) m;
```

**SELF JOIN — Trouver les paires**
```sql
-- Employés du même département avec salaires proches (±5000)
SELECT
    e1.nom AS employe1,
    e2.nom AS employe2,
    e1.departement,
    ABS(e1.salaire - e2.salaire) AS diff_salaire
FROM employes e1
JOIN employes e2
    ON e1.departement = e2.departement
    AND e1.id < e2.id  -- éviter les doublons et auto-jointure
    AND ABS(e1.salaire - e2.salaire) <= 5000;
```

**LATERAL JOIN (Snowflake) — Top-N par groupe**
```sql
-- Top 2 des ventes par client
SELECT c.nom_client, v.date_vente, v.montant
FROM clients c,
LATERAL (
    SELECT date_vente, montant
    FROM ventes
    WHERE client_id = c.client_id
    ORDER BY montant DESC
    LIMIT 2
) v;
```

**Anti-join — Trouver les absences**
```sql
-- Clients sans commande ce mois
SELECT c.client_id, c.nom
FROM clients c
LEFT JOIN commandes co
    ON c.client_id = co.client_id
    AND co.date_commande >= DATE_TRUNC('MONTH', CURRENT_DATE)
WHERE co.commande_id IS NULL;
```

### Exercices

**Exercice 1** : Avec un SELF JOIN sur `employes_hierarchie`, afficher chaque employé avec le nom de son manager.

<details>
<summary>Solution</summary>

```sql
SELECT e.nom AS employe, m.nom AS manager
FROM employes_hierarchie e
LEFT JOIN employes_hierarchie m ON e.manager_id = m.id;
```
</details>

**Exercice 2** : Utiliser un LATERAL JOIN pour afficher les 3 dernières transactions de chaque compte.

<details>
<summary>Solution</summary>

```sql
SELECT a.numero_compte, a.titulaire, t.date_transaction, t.montant
FROM comptes a,
LATERAL (
    SELECT date_transaction, montant
    FROM transactions
    WHERE compte_id = a.compte_id
    ORDER BY date_transaction DESC
    LIMIT 3
) t;
```
</details>

**Exercice 3** : Trouver les produits qui n'ont jamais été vendus en utilisant un anti-join.

<details>
<summary>Solution</summary>

```sql
SELECT p.produit_id, p.nom_produit
FROM produits p
LEFT JOIN ventes v ON p.produit_id = v.produit_id
WHERE v.produit_id IS NULL;
```
</details>

---

## 7. Optimisation de requêtes

### Définitions

#### Plan d'exécution
```sql
-- Snowflake
EXPLAIN USING TEXT
SELECT ... ;

-- Ou via Query Profile dans l'interface Snowflake
```

#### Composants clés du plan
- **Table Scan** : Lecture complète de la table (coûteux)
- **Index Seek** : Utilisation d'un index (efficace)
- **Hash Join vs Nested Loop vs Merge Join** : Stratégies de jointure
- **Sort** : Tri (coûteux si gros volumes)
- **Partition Pruning** (Snowflake) : Élimination de micro-partitions

### Patterns à éviter et corrections

```sql
-- ❌ MAUVAIS : fonction dans WHERE empêche l'utilisation d'index
SELECT * FROM employes WHERE YEAR(date_embauche) = 2020;
-- ✅ BON : utiliser un range
SELECT * FROM employes
WHERE date_embauche >= '2020-01-01' AND date_embauche < '2021-01-01';

-- ❌ MAUVAIS : SELECT * (colonnes inutiles)
SELECT * FROM ventes WHERE client_id = 42;
-- ✅ BON : seulement les colonnes nécessaires
SELECT date_vente, montant FROM ventes WHERE client_id = 42;

-- ❌ MAUVAIS : DISTINCT comme pansement pour mauvaise jointure
SELECT DISTINCT e.nom FROM employes e JOIN departements d ON ...;
-- ✅ BON : corriger la jointure pour éviter les doublons

-- ❌ MAUVAIS : OR dans WHERE (peut empêcher l'utilisation d'index)
SELECT * FROM employes WHERE departement = 'IT' OR ville = 'Paris';
-- ✅ BON : UNION ALL
SELECT * FROM employes WHERE departement = 'IT'
UNION ALL
SELECT * FROM employes WHERE ville = 'Paris' AND departement != 'IT';

-- ❌ MAUVAIS : NOT IN avec sous-requête (problème avec NULL)
SELECT * FROM t1 WHERE id NOT IN (SELECT id FROM t2);
-- ✅ BON : NOT EXISTS
SELECT * FROM t1 WHERE NOT EXISTS (SELECT 1 FROM t2 WHERE t2.id = t1.id);

-- ❌ MAUVAIS : sous-requête corrélée répétée
SELECT nom, (SELECT COUNT(*) FROM commandes WHERE client_id = c.id) AS nb
FROM clients c;
-- ✅ BON : jointure
SELECT c.nom, COUNT(co.id) AS nb
FROM clients c
LEFT JOIN commandes co ON c.id = co.client_id
GROUP BY c.nom;
```

### Bonnes pratiques Snowflake
```sql
-- Utiliser les clustering keys pour les grandes tables
ALTER TABLE ventes CLUSTER BY (date_vente, region);

-- Vérifier le pruning
SELECT SYSTEM$CLUSTERING_INFORMATION('ventes');

-- Eviter ORDER BY sans LIMIT sur les grandes tables
-- Utiliser LIMIT pour les explorations
SELECT * FROM grande_table LIMIT 100;
```

### Exercices

**Exercice 1** : Réécrire cette requête pour de meilleures performances :
```sql
SELECT * FROM commandes WHERE UPPER(statut) = 'EXPÉDIÉ' AND MONTH(date_commande) = 3;
```

<details>
<summary>Solution</summary>

```sql
SELECT commande_id, client_id, montant, date_commande, statut
FROM commandes
WHERE statut = 'Expédié'  -- Stocker les données de manière cohérente
AND date_commande >= '2026-03-01' AND date_commande < '2026-04-01';
-- Si la casse est variable, créer une colonne calculée ou un index fonctionnel
```
</details>

**Exercice 2** : Cette requête est lente. Identifier le problème et la réécrire :
```sql
SELECT c.nom, o.total
FROM clients c, commandes o
WHERE c.id = o.client_id
AND o.total > (SELECT AVG(total) FROM commandes WHERE client_id = c.id);
```

<details>
<summary>Solution</summary>

```sql
-- Problème : sous-requête corrélée exécutée pour chaque ligne
WITH avg_client AS (
    SELECT client_id, AVG(total) AS avg_total
    FROM commandes
    GROUP BY client_id
)
SELECT c.nom, o.total
FROM clients c
JOIN commandes o ON c.id = o.client_id
JOIN avg_client a ON o.client_id = a.client_id
WHERE o.total > a.avg_total;
```
</details>

**Exercice 3** : Optimiser cette requête qui doit retourner les 10 dernières commandes par client :
```sql
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY date_commande DESC) rn
    FROM commandes
) WHERE rn <= 10;
```

<details>
<summary>Solution</summary>

```sql
-- La requête est déjà bien structurée avec ROW_NUMBER
-- Optimisations possibles :
-- 1. Sélectionner uniquement les colonnes nécessaires
-- 2. S'assurer qu'il y a un clustering key sur (client_id, date_commande)
-- 3. Utiliser QUALIFY dans Snowflake (plus concis) :
SELECT commande_id, client_id, date_commande, montant
FROM commandes
QUALIFY ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY date_commande DESC) <= 10;
```
</details>

---

## 8. Manipulation de dates et chaînes

### Fonctions de date

```sql
-- DATE_TRUNC : tronquer à une précision
SELECT DATE_TRUNC('MONTH', CURRENT_DATE);        -- 2026-04-01
SELECT DATE_TRUNC('QUARTER', CURRENT_DATE);      -- 2026-04-01
SELECT DATE_TRUNC('YEAR', CURRENT_DATE);         -- 2026-01-01

-- DATEADD : ajouter un intervalle
SELECT DATEADD(DAY, 7, CURRENT_DATE);            -- +7 jours
SELECT DATEADD(MONTH, -3, CURRENT_DATE);         -- -3 mois

-- DATEDIFF : différence entre deux dates
SELECT DATEDIFF(DAY, '2026-01-01', '2026-04-02');    -- 91
SELECT DATEDIFF(MONTH, '2026-01-15', '2026-04-02');  -- 3

-- EXTRACT : extraire une partie
SELECT EXTRACT(YEAR FROM CURRENT_DATE);    -- 2026
SELECT EXTRACT(MONTH FROM CURRENT_DATE);   -- 4
SELECT EXTRACT(DOW FROM CURRENT_DATE);     -- jour de la semaine (0=dim)

-- LAST_DAY : dernier jour du mois
SELECT LAST_DAY(CURRENT_DATE);             -- 2026-04-30

-- Conversions
SELECT TO_DATE('02/04/2026', 'DD/MM/YYYY');
SELECT TO_TIMESTAMP('2026-04-02 14:30:00', 'YYYY-MM-DD HH24:MI:SS');
SELECT TO_CHAR(CURRENT_DATE, 'DD Month YYYY');  -- '02 April 2026'
```

### Fonctions de chaînes

```sql
-- Concaténation
SELECT 'Hello' || ' ' || 'World';
SELECT CONCAT('Hello', ' ', 'World');

-- LISTAGG : agrégation de chaînes
SELECT departement, LISTAGG(nom, ', ') WITHIN GROUP (ORDER BY nom) AS employes
FROM employes
GROUP BY departement;
-- Finance → 'Alice, Bob, Charlie'

-- SPLIT : découper une chaîne
SELECT SPLIT('a,b,c', ',');               -- ['a','b','c'] (ARRAY dans Snowflake)
SELECT SPLIT_PART('a,b,c', ',', 2);      -- 'b'

-- REGEXP
SELECT REGEXP_LIKE('ABC-123', '[A-Z]+-[0-9]+');     -- TRUE
SELECT REGEXP_SUBSTR('Email: test@mail.com', '[\\w.]+@[\\w.]+');  -- test@mail.com
SELECT REGEXP_REPLACE('Tél: 01-23-45', '[^0-9]', '');  -- '012345'
SELECT REGEXP_COUNT('ababab', 'ab');      -- 3

-- CASE WHEN avancé
SELECT
    nom,
    salaire,
    CASE
        WHEN salaire >= 90000 THEN 'Senior'
        WHEN salaire >= 75000 THEN 'Confirmé'
        WHEN salaire >= 65000 THEN 'Intermédiaire'
        ELSE 'Junior'
    END AS niveau,
    -- CASE avec recherche (searched CASE)
    CASE departement
        WHEN 'Finance' THEN 'F'
        WHEN 'IT' THEN 'I'
        WHEN 'RH' THEN 'R'
    END AS code_dept
FROM employes;

-- Gestion des NULL
SELECT
    COALESCE(telephone, email, 'Aucun contact') AS contact,  -- premier non-NULL
    NULLIF(statut, 'N/A') AS statut_clean,                    -- NULL si = 'N/A'
    NVL(bonus, 0) AS bonus_safe,                               -- remplace NULL (Snowflake)
    NVL2(manager_id, 'A un manager', 'Pas de manager') AS statut_mgr  -- NVL2(expr, si_non_null, si_null)
FROM employes_detail;

-- IFF (Snowflake) : CASE simplifié
SELECT nom, IFF(salaire > 80000, 'Haut', 'Normal') AS categorie
FROM employes;
```

### Exercices

**Exercice 1** : Calculer l'ancienneté en années et mois de chaque employé.

<details>
<summary>Solution</summary>

```sql
SELECT
    nom,
    date_embauche,
    DATEDIFF(YEAR, date_embauche, CURRENT_DATE) AS annees,
    MOD(DATEDIFF(MONTH, date_embauche, CURRENT_DATE), 12) AS mois_restants,
    DATEDIFF(YEAR, date_embauche, CURRENT_DATE) || ' ans et ' ||
    MOD(DATEDIFF(MONTH, date_embauche, CURRENT_DATE), 12) || ' mois' AS anciennete
FROM employes;
```
</details>

**Exercice 2** : Extraire les adresses email d'un champ texte libre et les normaliser en minuscules.

<details>
<summary>Solution</summary>

```sql
SELECT
    id,
    commentaire,
    LOWER(REGEXP_SUBSTR(commentaire, '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z]{2,}')) AS email_extrait
FROM tickets;
```
</details>

**Exercice 3** : Pour chaque mois de 2025, afficher le nombre de jours ouvrables (lun-ven) en utilisant une CTE récursive et les fonctions de date.

<details>
<summary>Solution</summary>

```sql
WITH RECURSIVE dates AS (
    SELECT DATE '2025-01-01' AS dt
    UNION ALL
    SELECT DATEADD(DAY, 1, dt) FROM dates WHERE dt < DATE '2025-12-31'
)
SELECT
    DATE_TRUNC('MONTH', dt) AS mois,
    COUNT(*) AS jours_ouvrables
FROM dates
WHERE DAYOFWEEK(dt) NOT IN (0, 6)  -- 0=dimanche, 6=samedi (Snowflake)
GROUP BY DATE_TRUNC('MONTH', dt)
ORDER BY mois;
```
</details>

---

## 9. Exercices de synthèse type HackerRank

### Exercice de synthèse 1 : Analyse des ventes (Medium)

**Schéma :**
```sql
CREATE TABLE ventes (
    vente_id INT,
    vendeur_id INT,
    produit_id INT,
    montant DECIMAL(10,2),
    date_vente DATE,
    region VARCHAR(20)
);

CREATE TABLE vendeurs (
    vendeur_id INT,
    nom VARCHAR(50),
    equipe VARCHAR(30),
    date_embauche DATE
);
```

**Énoncé** : Écrire une requête qui retourne pour chaque vendeur :
- Son nom et son équipe
- Son total de ventes
- Son rang dans son équipe (par total de ventes, décroissant)
- Le pourcentage de ses ventes par rapport au total de son équipe
- La différence avec le vendeur classé juste au-dessus

Filtrer uniquement les ventes de 2025 et les vendeurs qui ont fait au moins 5 ventes.

<details>
<summary>Solution</summary>

```sql
WITH ventes_2025 AS (
    SELECT vendeur_id, SUM(montant) AS total_ventes, COUNT(*) AS nb_ventes
    FROM ventes
    WHERE date_vente >= '2025-01-01' AND date_vente < '2026-01-01'
    GROUP BY vendeur_id
    HAVING COUNT(*) >= 5
)
SELECT
    v.nom,
    v.equipe,
    vt.total_ventes,
    RANK() OVER (PARTITION BY v.equipe ORDER BY vt.total_ventes DESC) AS rang_equipe,
    ROUND(vt.total_ventes * 100.0 /
        SUM(vt.total_ventes) OVER (PARTITION BY v.equipe), 2) AS pct_equipe,
    vt.total_ventes - LAG(vt.total_ventes)
        OVER (PARTITION BY v.equipe ORDER BY vt.total_ventes DESC) AS diff_precedent
FROM vendeurs v
JOIN ventes_2025 vt ON v.vendeur_id = vt.vendeur_id
ORDER BY v.equipe, rang_equipe;
```
</details>

### Exercice de synthèse 2 : Détection de fraude (Medium-Hard)

**Schéma :**
```sql
CREATE TABLE transactions (
    txn_id INT,
    compte_id INT,
    montant DECIMAL(12,2),
    date_txn TIMESTAMP,
    type_txn VARCHAR(10),  -- 'DEBIT' ou 'CREDIT'
    lieu VARCHAR(50)
);
```

**Énoncé** : Identifier les transactions potentiellement frauduleuses selon ces critères :
1. Montant supérieur à 3 fois la moyenne du compte
2. Deux transactions du même compte dans des lieux différents espacées de moins de 30 minutes
3. Plus de 5 transactions le même jour pour le même compte

Retourner txn_id, compte_id, montant, date_txn, et la raison du flag.

<details>
<summary>Solution</summary>

```sql
WITH stats_compte AS (
    SELECT compte_id, AVG(montant) AS avg_montant
    FROM transactions
    GROUP BY compte_id
),
-- Critère 1 : montant élevé
flag_montant AS (
    SELECT t.txn_id, 'Montant > 3x moyenne' AS raison
    FROM transactions t
    JOIN stats_compte s ON t.compte_id = s.compte_id
    WHERE t.montant > 3 * s.avg_montant
),
-- Critère 2 : lieux différents < 30 min
flag_lieu AS (
    SELECT t1.txn_id, 'Lieux différents < 30min' AS raison
    FROM transactions t1
    JOIN transactions t2
        ON t1.compte_id = t2.compte_id
        AND t1.txn_id != t2.txn_id
        AND t1.lieu != t2.lieu
        AND ABS(DATEDIFF(MINUTE, t1.date_txn, t2.date_txn)) < 30
),
-- Critère 3 : > 5 transactions/jour
flag_volume AS (
    SELECT t.txn_id, 'Plus de 5 txn/jour' AS raison
    FROM transactions t
    JOIN (
        SELECT compte_id, DATE(date_txn) AS jour
        FROM transactions
        GROUP BY compte_id, DATE(date_txn)
        HAVING COUNT(*) > 5
    ) j ON t.compte_id = j.compte_id AND DATE(t.date_txn) = j.jour
)
SELECT DISTINCT
    t.txn_id,
    t.compte_id,
    t.montant,
    t.date_txn,
    f.raison
FROM transactions t
JOIN (
    SELECT * FROM flag_montant
    UNION
    SELECT * FROM flag_lieu
    UNION
    SELECT * FROM flag_volume
) f ON t.txn_id = f.txn_id
ORDER BY t.compte_id, t.date_txn;
```
</details>

### Exercice de synthèse 3 : Cohortes RH (Hard)

**Schéma :**
```sql
CREATE TABLE employes_rh (
    employe_id INT,
    nom VARCHAR(100),
    departement VARCHAR(50),
    poste VARCHAR(50),
    salaire DECIMAL(10,2),
    date_embauche DATE,
    date_depart DATE,        -- NULL si toujours actif
    manager_id INT
);
```

**Énoncé** : Créer un rapport de cohortes montrant :
- Pour chaque trimestre d'embauche, le nombre d'employés recrutés
- Le taux de rétention à 6 mois, 1 an, et 2 ans
- Le salaire moyen d'embauche de la cohorte vs le salaire moyen global de la même période
- Le département avec le plus de départs dans chaque cohorte

<details>
<summary>Solution</summary>

```sql
WITH cohortes AS (
    SELECT
        DATE_TRUNC('QUARTER', date_embauche) AS trimestre_embauche,
        employe_id,
        departement,
        salaire,
        date_embauche,
        date_depart
    FROM employes_rh
),
retention AS (
    SELECT
        trimestre_embauche,
        COUNT(*) AS nb_recrutes,
        AVG(salaire) AS salaire_moyen_embauche,
        -- Rétention 6 mois
        SUM(CASE WHEN date_depart IS NULL
                  OR DATEDIFF(MONTH, date_embauche, date_depart) >= 6
             THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS retention_6m,
        -- Rétention 1 an
        SUM(CASE WHEN date_depart IS NULL
                  OR DATEDIFF(MONTH, date_embauche, date_depart) >= 12
             THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS retention_1an,
        -- Rétention 2 ans
        SUM(CASE WHEN date_depart IS NULL
                  OR DATEDIFF(MONTH, date_embauche, date_depart) >= 24
             THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS retention_2ans
    FROM cohortes
    GROUP BY trimestre_embauche
),
departs_dept AS (
    SELECT
        DATE_TRUNC('QUARTER', date_embauche) AS trimestre_embauche,
        departement,
        COUNT(*) AS nb_departs,
        ROW_NUMBER() OVER (
            PARTITION BY DATE_TRUNC('QUARTER', date_embauche)
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM employes_rh
    WHERE date_depart IS NOT NULL
    GROUP BY DATE_TRUNC('QUARTER', date_embauche), departement
),
salaire_global AS (
    SELECT AVG(salaire) AS avg_global FROM employes_rh
)
SELECT
    r.trimestre_embauche,
    r.nb_recrutes,
    ROUND(r.salaire_moyen_embauche, 2) AS avg_salaire_cohorte,
    ROUND(sg.avg_global, 2) AS avg_salaire_global,
    ROUND(r.retention_6m, 1) AS retention_6m_pct,
    ROUND(r.retention_1an, 1) AS retention_1an_pct,
    ROUND(r.retention_2ans, 1) AS retention_2ans_pct,
    dd.departement AS dept_plus_departs
FROM retention r
CROSS JOIN salaire_global sg
LEFT JOIN departs_dept dd
    ON r.trimestre_embauche = dd.trimestre_embauche AND dd.rn = 1
ORDER BY r.trimestre_embauche;
```
</details>

### Exercice de synthèse 4 : Analyse de portefeuille financier (Hard)

**Schéma :**
```sql
CREATE TABLE positions (
    position_id INT,
    portefeuille_id INT,
    instrument VARCHAR(20),    -- 'ACTION', 'OBLIGATION', 'OPTION'
    ticker VARCHAR(10),
    quantite INT,
    prix_achat DECIMAL(12,4),
    date_achat DATE
);

CREATE TABLE prix_marche (
    ticker VARCHAR(10),
    date_prix DATE,
    prix_cloture DECIMAL(12,4),
    volume INT
);
```

**Énoncé** : Pour chaque portefeuille, calculer :
1. La valeur totale actuelle (prix du dernier jour disponible × quantité)
2. Le P&L (profit/perte) non réalisé total et par instrument
3. Le rendement en pourcentage
4. La concentration maximale (% de la valeur dans un seul ticker)
5. Classer les portefeuilles par rendement (DENSE_RANK)

<details>
<summary>Solution</summary>

```sql
WITH derniers_prix AS (
    SELECT ticker, prix_cloture
    FROM prix_marche
    QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY date_prix DESC) = 1
),
valorisation AS (
    SELECT
        p.portefeuille_id,
        p.instrument,
        p.ticker,
        p.quantite,
        p.prix_achat,
        dp.prix_cloture AS prix_actuel,
        p.quantite * p.prix_achat AS cout_total,
        p.quantite * dp.prix_cloture AS valeur_actuelle,
        p.quantite * (dp.prix_cloture - p.prix_achat) AS pnl
    FROM positions p
    JOIN derniers_prix dp ON p.ticker = dp.ticker
),
par_portefeuille AS (
    SELECT
        portefeuille_id,
        SUM(valeur_actuelle) AS valeur_totale,
        SUM(cout_total) AS cout_total,
        SUM(pnl) AS pnl_total,
        ROUND(SUM(pnl) * 100.0 / SUM(cout_total), 2) AS rendement_pct,
        MAX(valeur_actuelle * 100.0 / SUM(valeur_actuelle) OVER (PARTITION BY portefeuille_id))
            AS concentration_max_pct
    FROM valorisation
    GROUP BY portefeuille_id
)
SELECT
    portefeuille_id,
    ROUND(valeur_totale, 2) AS valeur_totale,
    ROUND(pnl_total, 2) AS pnl_total,
    rendement_pct,
    ROUND(concentration_max_pct, 2) AS concentration_max_pct,
    DENSE_RANK() OVER (ORDER BY rendement_pct DESC) AS rang_rendement
FROM par_portefeuille
ORDER BY rang_rendement;
```
</details>

### Exercice de synthèse 5 : Fenêtres glissantes et gaps (Hard)

**Schéma :**
```sql
CREATE TABLE connexions (
    user_id INT,
    date_connexion DATE
);
```

**Énoncé** :
1. Pour chaque utilisateur, trouver la plus longue série de jours consécutifs de connexion
2. Identifier les utilisateurs qui se sont connectés au moins 7 jours consécutifs
3. Pour chaque série, indiquer la date de début et de fin

<details>
<summary>Solution</summary>

```sql
WITH connexions_uniques AS (
    SELECT DISTINCT user_id, date_connexion
    FROM connexions
),
groupes AS (
    SELECT
        user_id,
        date_connexion,
        -- Astuce : date - ROW_NUMBER donne la même valeur pour les jours consécutifs
        DATEADD(DAY,
            -ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date_connexion),
            date_connexion
        ) AS groupe
    FROM connexions_uniques
),
series AS (
    SELECT
        user_id,
        groupe,
        MIN(date_connexion) AS debut_serie,
        MAX(date_connexion) AS fin_serie,
        COUNT(*) AS jours_consecutifs
    FROM groupes
    GROUP BY user_id, groupe
),
max_series AS (
    SELECT
        user_id,
        debut_serie,
        fin_serie,
        jours_consecutifs,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY jours_consecutifs DESC) AS rn
    FROM series
)
-- Résultat 1 : Plus longue série par utilisateur
SELECT user_id, debut_serie, fin_serie, jours_consecutifs
FROM max_series
WHERE rn = 1
ORDER BY jours_consecutifs DESC;

-- Résultat 2 : Utilisateurs avec au moins 7 jours consécutifs
-- SELECT user_id, debut_serie, fin_serie, jours_consecutifs
-- FROM series
-- WHERE jours_consecutifs >= 7
-- ORDER BY jours_consecutifs DESC;
```
</details>

---

## Aide-mémoire rapide

### Différences de syntaxe entre SGBD

| Fonctionnalité | Snowflake | PostgreSQL | SQL Server |
|---|---|---|---|
| Limiter les résultats | `LIMIT n` | `LIMIT n` | `TOP n` |
| Filtrer window func | `QUALIFY` | Sous-requête | Sous-requête |
| Concaténation | `\|\|` ou `CONCAT` | `\|\|` | `+` ou `CONCAT` |
| Date courante | `CURRENT_DATE` | `CURRENT_DATE` | `GETDATE()` |
| Ajouter jours | `DATEADD(DAY,n,d)` | `d + INTERVAL 'n days'` | `DATEADD(DAY,n,d)` |
| NVL | `NVL(a,b)` | `COALESCE(a,b)` | `ISNULL(a,b)` |
| Auto-increment | `AUTOINCREMENT` | `SERIAL` | `IDENTITY` |
| UPSERT | `MERGE` | `INSERT...ON CONFLICT` | `MERGE` |
| Regexp match | `REGEXP_LIKE` | `~` | `LIKE` (limité) |
| Aplatir JSON | `LATERAL FLATTEN` | `jsonb_array_elements` | `OPENJSON` |

---

> **Conseil pour le test** : Commencer par les exercices les plus simples pour sécuriser des points, puis attaquer les plus complexes. Utiliser `QUALIFY` dans Snowflake au lieu d'une sous-requête — c'est plus concis et souvent attendu.
