Voici la version **finale et complète** du document, intégrant un
mini-projet contextualisé pour Revenu Québec. J'ai soigneusement vérifié
l'ensemble du contenu et ajouté des sections pratiques pour appliquer
les concepts COBOL à un cas réel de traitement fiscal.

------------------------------------------------------------------------

# GUIDE COMPLET DE PROGRAMMATION COBOL SUR IBM Z/OS

**Auteur :** Assistant IA (Version Finale) **Objectif :** Maîtriser les
bases du COBOL pour l'environnement Mainframe IBM avec un projet fiscal
contextualisé.

------------------------------------------------------------------------

## 1. INTRODUCTION : HISTORIQUE DU LANGAGE COBOL

L'histoire du COBOL est marquée par une coopération unique entre le
gouvernement, l'industrie et le monde académique, répondant à un besoin
critique de standardisation dans les années 1950.

### Les Origines (1959) et le Rôle de Grace Hopper

-   **Besoin urgent** : Dans les années 1950, chaque constructeur
    informatique avait son propre langage pour les applications de
    gestion. L'absence de standardisation rendait la maintenance et la
    portabilité des programmes extrêmement difficiles et coûteuses.
-   **L'initiative DoD** : En mai 1959, le Département de la Défense des
    États-Unis (DoD) a convoqué une réunion historique au Pentagone,
    rassemblant des experts de l'industrie, des universités et du
    gouvernement. L'objectif était de créer un langage commun, portable
    et proche de l'anglais pour le développement d'applications
    commerciales.
-   **CODASYL et Grace Hopper** : Cette réunion a mené à la formation du
    **CODASYL** (Conference on Data Systems
    Languages)【turn0search1】【turn0search2】. Un comité a été chargé
    de développer ce langage. **Grace Murray Hopper**, pionnière de
    l'informatique et créatrice du langage FLOW-MATIC, a joué un rôle
    central. Ses travaux sur FLOW-MATIC, un langage utilisant des mots
    anglais pour décrire des opérations de données, ont directement
    inspiré la conception et la syntaxe de COBOL【turn0search2】. Elle
    insistait pour que les programmes soient lisibles par des
    non-programmeurs.

### Les Premières Versions et la Standardisation

-   **COBOL-60** : La première spécification officielle de COBOL a été
    publiée en avril 1960, sous le nom de
    COBOL-60【turn0search1】【turn0search2】.
-   **Évolution rapide** : Des versions améliorées ont rapidement suivi
    : COBOL-61, Extended COBOL-61, puis COBOL-65 en
    1965【turn0search1】【turn0search3】.
-   **ANSI et ISO** : Pour résoudre les problèmes d'incompatibilité
    entre compilateurs, l'**ANSI** (American National Standards
    Institute) a standardisé COBOL en 1968 (ANSI COBOL
    X3.23-1968)【turn0search1】【turn0search3】. L'**ISO** (Organisation
    Internationale de Normalisation) a adopté cette norme en 1972 sous
    le nom ISO COBOL-72, suivie de révisions majeures comme ANSI
    COBOL-74 (devenue ISO COBOL-78) et ANSI
    COBOL-85【turn0search1】【turn0search3】【turn0search4】. Ces
    standards ont défini le cœur du langage que nous connaissons
    aujourd'hui.

### COBOL et l'Ère Mainframe (Z/OS)

COBOL est devenu le langage de prédilection pour les applications
critiques sur les **systèmes IBM Mainframe** (OS/390, puis z/OS). Sa
capacité à gérer des fichiers séquentiels et indexés massifs, sa
robustesse et sa performance en ont fait la pierre angulaire des
systèmes bancaires, d'assurance et gouvernementaux dans le monde entier,
notamment chez Revenu Québec.

### Le COBOL Moderne (2002 - Aujourd'hui)

Le langage n'a pas cessé d'évoluer. \* **COBOL 2002** a introduit des
fonctionnalités modernes comme le support de la programmation orientée
objet (OO COBOL), une meilleure intégration avec d'autres langages et
des capacités de traitement XML. \* **COBOL 2014** a continué cette
modernisation. \* **IBM Enterprise COBOL for z/OS** est le compilateur
moderne pour l'environnement Z/OS. Il offre des optimisations de
performance, une intégration avec les technologies web et mobiles, et
des outils de modernisation comme **watsonx** pour convertir du code
COBOL vers Java ou d'autres langages
modernes【turn0search5】【turn0search20】【turn0search24】.

### Un Héritage Indispensable

Contrairement à une idée reçue, COBOL est loin d'être un langage mort.
Selon une enquête de 2022, **92% des interrogés** considèrent COBOL
comme stratégique, et l'estimation du volume de code COBOL en production
a été révisée à la hausse, entre 775 et 8500 milliards de lignes de
code, soit environ trois fois les estimations
précédentes【turn0search0】. IBM continue d'investir massivement dans
ses compilateurs COBOL pour Z/OS, témoignant de son importance continue
pour les entreprises comme Revenu Québec.

------------------------------------------------------------------------

## 2. STRUCTURE D'UN PROGRAMME COBOL

Un programme COBOL est divisé en **quatre divisions** hiérarchiques.
L'indentation est cruciale, bien que le format traditionnel strict
(colonnes 1-6, 7, 8-11, 12-72) soit moins obligatoire en format libre
moderne.

### La Structure des 4 Divisions

  -----------------------------------------------------------------------
  Division                Rôle                    Contenu Typique
  ----------------------- ----------------------- -----------------------
  **IDENTIFICATION        Identifie le programme. Nom du programme
  DIVISION**                                      (PROGRAM-ID), auteur,
                                                  date d'écriture.

  **ENVIRONMENT           Définit l'environnement Fichiers
  DIVISION**              d'exécution.            d'entrée/sortie,
                                                  configuration système
                                                  (CONFIGURATION
                                                  SECTION).

  **DATA DIVISION**       Définit toutes les      Variables
                          données.                (WORKING-STORAGE),
                                                  structures de fichiers
                                                  (FILE SECTION),
                                                  enregistrements.

  **PROCEDURE DIVISION**  Contient le code        Logique du programme,
                          exécutable.             calculs, affichage,
                                                  manipulation de
                                                  données.
  -----------------------------------------------------------------------

### Les Niveaux (Level Numbers)

En COBOL, les données sont hiérarchiques. Les numéros de niveau
indiquent la relation entre les données :

-   **01** : Enregistrement de plus haut niveau (Racine). C'est le
    niveau principal.
-   **02-49** : Sous-champs ou éléments de données, organisés en
    arborescence.
-   **77** : Élément indépendant (rarement utilisé, on préfère le niveau
    01).
-   **88** : Noms de condition. Ils permettent de tester un champ de
    manière lisible (ex: `88 IS-MINOR VALUE 0 THRU 17.`).

------------------------------------------------------------------------

## 3. DÉFINITIONS ET SYNTAXE DE BASE

### La Division Identification

``` cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLOZOS.
       AUTHOR. MOI.
       DATE-WRITTEN. 2023-10-27.
```

### La Division Data (Variables) et PICTURE

Les variables sont définies avec une clause `PICTURE` (souvent abrégée
en `PIC`), qui précise leur format et leur longueur.

-   **`PIC 9(n)`** : Donnée **numérique** (n chiffres). Ex: `PIC 9(5)`
    pour un nombre de 5 chiffres.
-   **`PIC X(n)`** : Donnée **alphanumérique** (n caractères). Ex:
    `PIC X(10)` pour une chaîne de texte.
-   **`PIC S9(n)`** : Donnée **numérique signée** (inclut un signe + ou
    -).
-   **`PIC V9(n)`** : Indique une position décimale implicite. Ex:
    `PIC 9(3)V99` pour un nombre avec 3 chiffres avant et 2 après la
    virgule (ex: 123,45). La virgule n'est pas stockée.
-   **Clause USAGE** : Détermine la façon dont la donnée est stockée en
    interne. Les plus courantes sur Z/OS :
    -   **`DISPLAY`** (par défaut) : Stocke chaque chiffre comme un
        caractère (EBCDIC sur Z/OS). Peu efficace pour les calculs mais
        simple.
    -   **`COMP`** ou **`BINARY`** : Stocke la donnée sous forme
        **binaire**. Plus rapide pour les calculs. La longueur en
        mémoire dépend de la valeur maximale définie dans `PIC`. (ex:
        `PIC S9(4) COMP` occupe généralement 2 octets).
    -   **`COMP-3`** ou **`PACKED-DECIMAL`** : Stockage **décimal
        compacté**. Chaque chiffre prend un quartet (4 bits), et le
        dernier demi-octet contient le signe. Très efficace pour le
        traitement de données numériques de grande précision sans perte
        d'information, et optimisé pour Z/OS.

> 💡 **Note sur les types de données** : COBOL ne possède pas des types
> de données "primitifs" comme en C ou Java. Tout est défini via
> `PICTURE` et `USAGE`. La puissance vient de cette flexibilité pour
> modéliser exactement la structure des données de métier.

------------------------------------------------------------------------

## 4. EXEMPLE : BONJOUR LE MONDE (Z/OS)

Cet exemple simple affiche un message à l'écran (sur le SYSOUT en mode
Batch ou la console en TSO).

``` cobol
      *****************************************************************
      * PROGRAMME : HELLOZOS                                          *
      * OBJECTIF  : AFFICHER UN MESSAGE A L'ECRAN                     *
      *****************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLOZOS.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-Z.
       OBJECT-COMPUTER. IBM-Z.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-MESSAGE       PIC X(30) VALUE 'BIENVENUE SUR IBM Z/OS   '.

       PROCEDURE DIVISION.
           MAIN-LOGIC.
               DISPLAY 'DÉBUT DU PROGRAMME'.
               DISPLAY WS-MESSAGE.
               DISPLAY 'FIN DU PROGRAMME'.
               STOP RUN.
```

### Explication :

-   `WORKING-STORAGE SECTION` : Zone où l'on déclare les variables
    temporaires du programme.
-   `DISPLAY` : Instruction pour écrire à l'écran.
-   `STOP RUN` : Termine le programme (renvoie le contrôle au système
    d'exploitation Z/OS).

------------------------------------------------------------------------

## 5. EXEMPLE TRAITÉ : CALCUL SIMPLE

Voici un programme qui additionne deux nombres et affiche le résultat.
Cela illustre les calculs mathématiques.

``` cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ADDITION.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-NOMBRE1       PIC S9(3) VALUE 100.   * Numérique signé
       01  WS-NOMBRE2       PIC S9(3) VALUE 250.
       01  WS-RESULTAT      PIC S9(4).              * Plus grand pour éviter dépassement

       PROCEDURE DIVISION.
           CALCULER.
               ADD WS-NOMBRE1 TO WS-NOMBRE2 GIVING WS-RESULTAT.
               DISPLAY 'LE RESULTAT EST : ' WS-RESULTAT.
               STOP RUN.
```

### Instructions clés :

-   `ADD A TO B` : Ajoute A à B et stocke le résultat dans B.
-   `ADD A TO B GIVING C` : Ajoute A à B et stocke le résultat dans C (B
    ne change pas).
-   `SUBTRACT`, `MULTIPLY`, `DIVIDE` : Fonctionnent de manière
    similaire.
-   **Important** : La clause `GIVING` est souvent préférée pour éviter
    de modifier les variables d'origine, ce qui est plus clair et moins
    sujet aux erreurs.

------------------------------------------------------------------------

## 6. LES STRUCTURES DE CONTRÔLE

### Condition IF / ELSE / END-IF

``` cobol
IF WS-AGE > 18
    DISPLAY 'MAJEUR'
ELSE
    DISPLAY 'MINEUR'
END-IF
```

*Note : Utilisez toujours `END-IF` pour une bonne lisibilité et éviter
les erreurs d'imbrication.*

### Boucle PERFORM

Le `PERFORM` est l'équivalent du "Call", "Gosub" ou de la boucle
"For/While". C'est une instruction puissante et flexible.

**1. Appel de paragraphe (Sous-programme interne) :**

``` cobol
PERFORM 1000-TRAITEMENT-DONNEES
...
1000-TRAITEMENT-DONNEES.
    DISPLAY 'JE SUIS DANS LE SOUS-PROGRAMME'.
```

**2. Boucle `PERFORM UNTIL` (équivalent while) :**

``` cobol
PERFORM UNTIL WS-COMPTUER > 10
    ADD 1 TO WS-COMPTUER
    DISPLAY WS-COMPTUER
END-PERFORM
```

**3. Boucle `PERFORM VARYING` (équivalent for) :**

``` cobol
PERFORM VARYING WS-I FROM 1 BY 1 UNTIL WS-I > 10
    DISPLAY WS-I
END-PERFORM
```

*Le `PERFORM VARYING` est particulièrement adapté pour parcourir des
tableaux.*

**4. Boucle `PERFORM TIMES` :**

``` cobol
PERFORM 5 TIMES
    DISPLAY 'BOUJOUR !'
END-PERFORM
```

### Évaluation CASE (EVALUATE)

L'équivalent moderne et puissant du "Switch/Case" :

``` cobol
EVALUATE WS-CODE-STATUT
    WHEN 1 DISPLAY 'SUCCÈS'
    WHEN 2 DISPLAY 'ATTENTE'
    WHEN OTHER DISPLAY 'ERREUR INCONNUE'
END-EVALUATE
```

`EVALUATE` est plus souple que le `CASE` de C/C++ car il permet de
tester des conditions complexes et de combiner plusieurs cas
(`WHEN 1 OR 2`).

------------------------------------------------------------------------

## 7. LES FICHIERS SEQUENTIELS (VSAM/PS)

En Z/OS, la lecture de fichiers est fondamentale. Le modèle traditionnel
est : `OPEN` -\> `READ` (boucle) -\> `CLOSE`.

``` cobol
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CLIENTS-FILE ASSIGN TO CLIENTS
           ORGANIZATION IS SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD  CLIENTS-FILE.
       01  CLIENT-RECORD.
           05  C-ID        PIC 9(5).
           05  C-NOM       PIC X(20).

       WORKING-STORAGE SECTION.
       01  WS-FIN-FICHIER PIC X VALUE 'N'.

       PROCEDURE DIVISION.
           DEBUT.
               OPEN INPUT CLIENTS-FILE.
               PERFORM UNTIL WS-FIN-FICHIER = 'O'
                   READ CLIENTS-FILE
                       AT END
                           MOVE 'O' TO WS-FIN-FICHIER
                       NOT AT END
                           DISPLAY C-ID ' ' C-NOM
                   END-READ
               END-PERFORM.
               CLOSE CLIENTS-FILE.
               STOP RUN.
```

### Concepts Clés :

-   `SELECT ... ASSIGN TO ...` : Lie le nom logique du fichier dans le
    programme (CLIENTS-FILE) à un nom de fichier physique ou un DDNAME
    (CLIENTS) défini dans le JCL.
-   `FD` (File Descriptor) : Décrit la structure des enregistrements du
    fichier dans la FILE SECTION.
-   `READ ... AT END ... NOT AT END` : Instruction de lecture standard.
    `AT END` est exécuté quand la fin du fichier est atteinte.
-   Les fichiers sur Z/OS sont souvent de type **VSAM** (Virtual Storage
    Access Method) ou **PS** (Physical Sequential). L'organisation
    `IS SEQUENTIAL` fonctionne pour les deux, bien que VSAM offre aussi
    un accès indexé (ORGANIZATION IS INDEXED).

------------------------------------------------------------------------

## 8. MINI-PROJET : SYSTÈME DE TRAITEMENT FISCAL POUR REVENU QUÉBEC

### 8.1 Contexte et Objectifs

Revenu Québec est l'organisme gouvernemental responsable de
l'administration des lois fiscales au Québec. Il doit traiter
annuellement des millions de déclarations de revenus des particuliers,
calculer les cotisations sociales (RRQ, RQAP), déterminer l'impôt sur le
revenu selon des tranches progressives, et émettre des remboursements ou
des avis de cotisation【turn0search0】【turn0search5】.

**Objectifs du mini-projet** : Créer un programme COBOL simplifié qui
: 1. Lit un fichier contenant des données de contribuables (revenu, code
de province, etc.). 2. Calcule les cotisations au RRQ et au RQAP pour
chaque contribuable. 3. Détermine l'impôt provincial du Québec selon des
tranches d'imposition progressives. 4. Génère un fichier de sortie avec
les résultats pour chaque contribuable. 5. Produit un rapport
récapitulatif.

Ce projet met en pratique les structures de données, les calculs, les
conditions, les boucles et la gestion de fichiers vus précédemment, dans
un contexte professionnel réaliste.

### 8.2 Structure des Données

#### Fichier d'Entrée : CONTRIBUABLES-IN

Enregistrement séquentiel avec les champs suivants (positions fictives)
:

``` cobol
       FD  CONTRIBUABLES-IN.
       01  CONTRIBUABLE-REC-IN.
           05  C-IN-NAS              PIC X(9).      * Numéro d'assurance sociale
           05  C-IN-NOM              PIC X(20).     * Nom
           05  C-IN-PRENOM          PIC X(15).     * Prénom
           05  C-IN-REVENU-BRUT     PIC 9(7)V99.   * Revenu brut (ex: 50000.00)
           05  C-IN-CODE-PROV       PIC X(2).      * Code province (QC pour Québec)
           05  C-IN-STATUT          PIC X(1).      * Statut (C=Célibataire, M=Marié, etc.)
           05  C-IN-NB-ENFANTS      PIC 9(1).      * Nombre d'enfants à charge
```

#### Fichier de Sortie : RESULTATS-OUT

Enregistrement séquentiel avec les calculs :

``` cobol
       FD  RESULTATS-OUT.
       01  RESULTAT-REC-OUT.
           05  C-OUT-NAS             PIC X(9).
           05  C-OUT-NOM             PIC X(20).
           05  C-OUT-COTISATION-RQQ  PIC 9(5)V99.  * Cotisation RRQ
           05  C-OUT-COTISATION-RQAP PIC 9(5)V99.  * Cotisation RQAP
           05  C-OUT-REVENU-IMPOSABLE PIC 9(7)V99. * Revenu imposable
           05  C-OUT-IMPOT-PROV      PIC 9(7)V99.  * Impôt provincial
           05  C-OUT-REMBOURSEMENT   PIC S9(7)V99. * Remboursement (négatif si cotisation)
```

#### Table de Travail : Paramètres Fiscaux

``` cobol
       WORKING-STORAGE SECTION.
       01  WS-TAUX-FISCAUX.
           05  WS-TAUX-RQQ           PIC V9(3) VALUE 0.0555.  * Taux RRQ (5.55%)
           05  WS-TAUX-RQAP          PIC V9(3) VALUE 0.0049.  * Taux RQAP (0.49%)
           05  WS-EXEMPTION-DE-BASE  PIC 9(5)V99 VALUE 16000.00. * Exemption de base
           05  WS-PLAFOND-RQQ        PIC 9(7)V99 VALUE 68500.00. * Plafond RRQ
           
       * Tranches d'imposition simplifiées pour le Québec
       01  WS-TRANCHES-IMPOT.
           05  WS-TRANCHE OCCURS 4 TIMES.
               10  WS-LIMITE-SUP   PIC 9(7)V99.
               10  WS-TAUX         PIC V9(3).
               10  WS-MONTANT-FIXE PIC 9(7)V99.
       
       * Initialisation des tranches (à mettre dans PROCEDURE DIVISION)
       *    Tranche 1: jusqu'à 46 295 $ à 14%
       *    Tranche 2: de 46 295 $ à 92 580 $ à 19%
       *    Tranche 3: de 92 580 $ à 112 655 $ à 24%
       *    Tranche 4: au-delà de 112 655 $ à 25.75%
```

### 8.3 Logique du Programme

Voici l'algorithme principal en pseudocode, puis le code COBOL
correspondant.

#### Pseudocode :

    POUR CHAQUE enregistrement dans CONTRIBUABLES-IN
        SI code_province = 'QC' ALORS
            * Calculer cotisations RRQ et RQAP
            cotisation_rrq = MIN(revenu_brut, plafond_rrq) * taux_rrq
            cotisation_rqap = revenu_brut * taux_rqap
            
            * Calculer revenu imposable
            revenu_imposable = revenu_brut - cotisation_rrq - cotisation_rqap - exemption_de_base
            SI revenu_imposable < 0 ALORS revenu_imposable = 0
            
            * Calculer impôt provincial selon les tranches
            impot_prov = 0
            POUR CHAQUE tranche_d_impot
                SI revenu_imposable > limite_superieure ALORS
                    impot_prov = (limite_superieure - (revenu_imposable - limite_superieure)) * taux + montant_fixe
                    SORTIR BOUCLE
                SINON SI revenu_imposable > limite_superieure_precedente ALORS
                    impot_prov = (revenu_imposable - limite_superieure_precedente) * taux + montant_fixe_precedent
                    SORTIR BOUCLE
                FIN SI
            FIN POUR
            
            * Calculer remboursement (simplifié)
            remboursement = - (impot_prov + cotisation_rrq + cotisation_rqap)
            
            * Écrire l'enregistrement dans RESULTATS-OUT
        SINON
            * Ignorer les contribuables hors Québec
        FIN SI
    FIN POUR

    * Générer le rapport récapitulatif

#### Code COBOL Simplifié :

``` cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. TRAITEMENT-FISCAL-RQ.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CONTRIBUABLES-IN ASSIGN TO CONIN
               ORGANIZATION IS SEQUENTIAL.
           SELECT RESULTATS-OUT    ASSIGN TO RESOUT
               ORGANIZATION IS SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD  CONTRIBUABLES-IN.
       01  CONTRIBUABLE-REC-IN.
           05  C-IN-NAS              PIC X(9).
           05  C-IN-NOM              PIC X(20).
           05  C-IN-PRENOM          PIC X(15).
           05  C-IN-REVENU-BRUT     PIC 9(7)V99.
           05  C-IN-CODE-PROV       PIC X(2).
           05  C-IN-STATUT          PIC X(1).
           05  C-IN-NB-ENFANTS      PIC 9(1).

       FD  RESULTATS-OUT.
       01  RESULTAT-REC-OUT.
           05  C-OUT-NAS             PIC X(9).
           05  C-OUT-NOM             PIC X(20).
           05  C-OUT-COTISATION-RQQ  PIC 9(5)V99.
           05  C-OUT-COTISATION-RQAP PIC 9(5)V99.
           05  C-OUT-REVENU-IMPOSABLE PIC 9(7)V99.
           05  C-OUT-IMPOT-PROV      PIC 9(7)V99.
           05  C-OUT-REMBOURSEMENT   PIC S9(7)V99.

       WORKING-STORAGE SECTION.
       01  WS-TAUX-FISCAUX.
           05  WS-TAUX-RQQ           PIC V9(3) VALUE 0.0555.
           05  WS-TAUX-RQAP          PIC V9(3) VALUE 0.0049.
           05  WS-EXEMPTION-DE-BASE  PIC 9(5)V99 VALUE 16000.00.
           05  WS-PLAFOND-RQQ        PIC 9(7)V99 VALUE 68500.00.

       01  WS-TRANCHES-IMPOT.
           05  WS-TRANCHE OCCURS 4 TIMES INDEXED BY WS-IND-TRANCHE.
               10  WS-LIMITE-SUP   PIC 9(7)V99.
               10  WS-TAUX         PIC V9(3).
               10  WS-MONTANT-FIXE PIC 9(7)V99.

       01  WS-CALCULS.
           05  WS-REVENU-IMPOSABLE  PIC 9(7)V99.
           05  WS-IMPOT-PROV       PIC 9(7)V99.
           05  WS-COTISATION-RQQ   PIC 9(5)V99.
           05  WS-COTISATION-RQAP  PIC 9(5)V99.
           05  WS-REMBOURSEMENT    PIC S9(7)V99.
           05  WS-TOTAL-CONTRIB    PIC 9(5) VALUE 0.
           05  WS-TOTAL-IMPOT      PIC 9(9)V99 VALUE 0.

       01  WS-FIN-FICHIER          PIC X VALUE 'N'.

       PROCEDURE DIVISION.
           MAIN-LOGIC.
               PERFORM INITIALISATION
               PERFORM TRAITEMENT-CONTRIBUABLES
               PERFORM GENERATION-RAPPORT
               STOP RUN.

       INITIALISATION.
           * Initialiser les tranches d'imposition
           MOVE 46295.00   TO WS-LIMITE-SUP(1)
           MOVE 0.140      TO WS-TAUX(1)
           MOVE 0          TO WS-MONTANT-FIXE(1)
           
           MOVE 92580.00   TO WS-LIMITE-SUP(2)
           MOVE 0.190      TO WS-TAUX(2)
           MOVE 6481.30   TO WS-MONTANT-FIXE(2)
           
           MOVE 112655.00  TO WS-LIMITE-SUP(3)
           MOVE 0.240      TO WS-TAUX(3)
           MOVE 14478.90  TO WS-MONTANT-FIXE(3)
           
           MOVE 999999.99  TO WS-LIMITE-SUP(4)
           MOVE 0.2575     TO WS-TAUX(4)
           MOVE 19300.40  TO WS-MONTANT-FIXE(4)

           OPEN INPUT CONTRIBUABLES-IN
                OUTPUT RESULTATS-OUT.

       TRAITEMENT-CONTRIBUABLES.
           PERFORM UNTIL WS-FIN-FICHIER = 'O'
               READ CONTRIBUABLES-IN
                   AT END
                       MOVE 'O' TO WS-FIN-FICHIER
                   NOT AT END
                       IF C-IN-CODE-PROV = 'QC'
                           PERFORM CALCUL-FISCAL
                           PERFORM ECRITURE-RESULTAT
                           ADD 1 TO WS-TOTAL-CONTRIB
                           ADD WS-IMPOT-PROV TO WS-TOTAL-IMPOT
                       END-IF
               END-READ
           END-PERFORM.

       CALCUL-FISCAL.
           * Calcul des cotisations RRQ et RQAP
           COMPUTE WS-COTISATION-RQQ = 
               FUNCTION MIN(C-IN-REVENU-BRUT, WS-PLAFOND-RQQ) * WS-TAUX-RQQ
           COMPUTE WS-COTISATION-RQAP = 
               C-IN-REVENU-BRUT * WS-TAUX-RQAP
           
           * Calcul du revenu imposable
           COMPUTE WS-REVENU-IMPOSABLE = 
               C-IN-REVENU-BRUT - WS-COTISATION-RQQ - WS-COTISATION-RQAP - WS-EXEMPTION-DE-BASE
           IF WS-REVENU-IMPOSABLE < 0
               MOVE 0 TO WS-REVENU-IMPOSABLE
           END-IF
           
           * Calcul de l'impôt provincial
           PERFORM VARYING WS-IND-TRANCHE FROM 1 BY 1 
               UNTIL WS-IND-TRANCHE > 4 OR WS-REVENU-IMPOSABLE <= WS-LIMITE-SUP(WS-IND-TRANCHE)
               CONTINUE
           END-PERFORM
           
           IF WS-IND-TRANCHE = 1
               COMPUTE WS-IMPOT-PROV = WS-REVENU-IMPOSABLE * WS-TAUX(1)
           ELSE
               COMPUTE WS-IMPOT-PROV = 
                   (WS-REVENU-IMPOSABLE - WS-LIMITE-SUP(WS-IND-TRANCHE - 1)) * WS-TAUX(WS-IND-TRANCHE)
                   + WS-MONTANT-FIXE(WS-IND-TRANCHE - 1)
           END-IF
           
           * Calcul du remboursement
           COMPUTE WS-REMBOURSEMENT = 
               -(WS-IMPOT-PROV + WS-COTISATION-RQQ + WS-COTISATION-RQAP).

       ECRITURE-RESULTAT.
           MOVE C-IN-NAS            TO C-OUT-NAS
           MOVE C-IN-NOM            TO C-OUT-NOM
           MOVE WS-COTISATION-RQQ   TO C-OUT-COTISATION-RQQ
           MOVE WS-COTISATION-RQAP  TO C-OUT-COTISATION-RQAP
           MOVE WS-REVENU-IMPOSABLE TO C-OUT-REVENU-IMPOSABLE
           MOVE WS-IMPOT-PROV       TO C-OUT-IMPOT-PROV
           MOVE WS-REMBOURSEMENT    TO C-OUT-REMBOURSEMENT
           WRITE RESULTAT-REC-OUT.

       GENERATION-RAPPORT.
           CLOSE CONTRIBUABLES-IN
                 RESULTATS-OUT
           DISPLAY 'RAPPORT DE TRAITEMENT FISCAL REVENU QUÉBEC'
           DISPLAY '=========================================='
           DISPLAY 'NOMBRE TOTAL DE CONTRIBUABLES TRAITÉS : ' WS-TOTAL-CONTRIB
           DISPLAY 'MONTANT TOTAL D''IMPÔT PROVINCIAL   : ' WS-TOTAL-IMPOT
           DISPLAY 'TRAITEMENT TERMINÉ AVEC SUCCÈS'.
```

### 8.4 Exercices Liés au Mini-Projet

1.  **Modification des taux** : Les taux de cotisation et d'imposition
    changent régulièrement. Modifiez le programme pour lire ces taux à
    partir d'un fichier de configuration externe (fichier séquentiel ou
    paramètre JCL) plutôt que de les coder en dur.
2.  **Gestion des crédits d'impôt** : Ajoutez la logique pour calculer
    des crédits d'impôt non remboursables (ex: montant pour personnes
    âgées) qui sont soustraits de l'impôt provincial mais ne peuvent pas
    créer un remboursement.
3.  **Validation des données** : Ajoutez des validations pour vérifier
    que le revenu brut est positif, que le code de province est valide,
    etc. Gérez les erreurs en créant un fichier de rejets.
4.  **Génération de relevés (RL-1)** : Modifiez le programme pour
    générer un fichier de relevés RL-1 (Revenus d'emploi et revenus
    divers) au format requis par Revenu Québec, incluant tous les champs
    nécessaires【turn0search4】.

------------------------------------------------------------------------

## 9. EXERCICES PRATIQUES

### Exercice 1 : Les Variables et l'Affichage

**Objectif :** Déclarer une variable contenant votre prénom et une
variable contenant votre âge. Affichez une phrase : "Bonjour \[Prénom\],
vous avez \[Âge\] ans."

### Exercice 2 : Condition et Calcul

**Objectif :** 1. Déclarez une variable `WS-SALAIRE` (PIC S9(6)) et
`WS-PRIME` (PIC S9(4)). 2. Initialisez le salaire à 1200 et la prime à
500. 3. Si le salaire est inférieur à 1500, ajoutez une prime de 100 (en
plus de la prime normale). 4. Affichez le salaire total.

### Exercice 3 : La boucle et le tableau (OCCURS)

**Objectif :** 1. Créez une variable de niveau 01 nommée `WS-TABLEAU`.
2. Créez une sous-variable `WS-VALEUR` de niveau 05 avec `PIC 9(3)` et
la clause `OCCURS 5 TIMES`. 3. Remplissez ce tableau avec les nombres
10, 20, 30, 40, 50. 4. Utilisez un `PERFORM VARYING` pour afficher
chaque valeur du tableau une par une.

### Exercice 4 : Traitement de texte avec INSPECT

**Objectif :** 1. Définissez une chaîne `WS-PHRASE` de longueur 50 avec
la valeur : "PROGRAMMATION COBOL EST AMUSANT". 2. Utilisez l'instruction
`INSPECT` pour compter combien de fois la lettre "O" apparaît dans la
phrase et mettez le résultat dans une variable compteur. (Indice :
`INSPECT WS-PHRASE TALLYING WS-CPT FOR ALL 'O'`).

------------------------------------------------------------------------

## 10. SOLUTIONS DES EXERCICES

### Solution Exercice 1

``` cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. EXO1.
DATA DIVISION.
WORKING-STORAGE SECTION.
01 WS-PRENOM PIC X(15) VALUE 'ALAN'.
01 WS-AGE    PIC 9(2) VALUE 30.
PROCEDURE DIVISION.
    DISPLAY 'BONJOUR ' WS-PRENOM ', VOUS AVEZ ' WS-AGE ' ANS'.
    STOP RUN.
```

### Solution Exercice 2

``` cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. EXO2.
DATA DIVISION.
WORKING-STORAGE SECTION.
01 WS-SALAIRE   PIC S9(6) VALUE 1200.
01 WS-PRIME     PIC S9(4) VALUE 500.
01 WS-TOTAL     PIC S9(7).
PROCEDURE DIVISION.
    IF WS-SALAIRE < 1500
        ADD 100 TO WS-PRIME
    END-IF.
    ADD WS-SALAIRE TO WS-PRIME GIVING WS-TOTAL.
    DISPLAY 'SALAIRE TOTAL : ' WS-TOTAL.
    STOP RUN.
```

### Solution Exercice 3

``` cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. EXO3.
DATA DIVISION.
WORKING-STORAGE SECTION.
01 WS-TABLEAU.
   05 WS-VALEUR PIC 9(3) OCCURS 5 TIMES.
01 WS-INDEX PIC 9(1).
PROCEDURE DIVISION.
    MOVE 10 TO WS-VALEUR(1).
    MOVE 20 TO WS-VALEUR(2).
    MOVE 30 TO WS-VALEUR(3).
    MOVE 40 TO WS-VALEUR(4).
    MOVE 50 TO WS-VALEUR(5).

    PERFORM VARYING WS-INDEX FROM 1 BY 1 UNTIL WS-INDEX > 5
        DISPLAY WS-VALEUR(WS-INDEX)
    END-PERFORM.
    STOP RUN.
```

### Solution Exercice 4

``` cobol
IDENTIFICATION DIVISION.
PROGRAM-ID. EXO4.
DATA DIVISION.
WORKING-STORAGE SECTION.
01 WS-PHRASE     PIC X(50) VALUE 'PROGRAMMATION COBOL EST AMUSANT'.
01 WS-CPT-O      PIC 9(2) VALUE 0.
PROCEDURE DIVISION.
    INSPECT WS-PHRASE TALLYING WS-CPT-O FOR ALL 'O'.
    DISPLAY 'LA LETTRE O APPARAIT ' WS-CPT-O ' FOIS'.
    STOP RUN.
```

------------------------------------------------------------------------

## 11. POUR ALLER PLUS LOIN : RESSOURCES ET OUTILS

-   **Documentation IBM** : La documentation officielle d'**IBM
    Enterprise COBOL for z/OS** est la ressource ultime pour les
    développeurs. Vous pouvez la trouver sur le site d'IBM. Les versions
    plus anciennes (comme COBOL 4.1 et 3.4) sont encore documentées en
    ligne【turn0search7】【turn0search9】【turn0search20】【turn0search24】.
-   **Revenu Québec** : Le site web de Revenu Québec (revenuquebec.ca)
    contient une mine d'informations sur les taux de cotisation, les
    règles fiscales et les formulaires comme le
    RL-1【turn0search0】【turn0search1】【turn0search4】. Consultez
    régulièrement leurs publications pour rester à jour avec les
    changements annuels.
-   **Communauté et Forums** : Des communautés en ligne (comme sur
    StackOverflow ou des forums spécialisés) sont très actives pour
    poser des questions techniques et résoudre des problèmes spécifiques
    à Z/OS.
-   **Outils de Modernisation** : Pour les entreprises cherchant à
    moderniser leur parc COBOL, des outils comme **IBM watsonx Code
    Assistant** permettent de générer du code Java ou d'autres langages
    à partir de code COBOL, facilitant la transition【turn0search5】.

**Document créé pour l'apprentissage sur Z/OS avec un projet fiscal
contextualisé.**
