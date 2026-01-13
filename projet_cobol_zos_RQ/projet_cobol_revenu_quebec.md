
# Plan complet : Installation du terminal 3270 et remise à niveau en COBOL pour les impôts au Québec sur Z/OS

## Étape 1 : Installation et configuration du terminal 3270 sur Ubuntu 24.04
**Objectif** : Pouvoir se connecter au mainframe Z/OS via un émulateur 3270.

1. **Installer x3270/c3270** :
   - Ouvrir un terminal et exécuter :
     ```bash
     sudo apt update
     sudo apt install x3270
     ```
   - Pour une version en ligne de commande (c3270) :
     ```bash
     sudo apt install c3270
     ```

2. **Lancer le terminal** :
   - Pour x3270 (interface graphique) :
     ```bash
     x3270 <adresse_du_mainframe>:<port>
     ```
   - Pour c3270 (terminal) :
     ```bash
     c3270 <adresse_du_mainframe>:<port>
     ```
   - Remplacer `<adresse_du_mainframe>` et `<port>` par les informations fournies par l'administrateur IBM.

3. **Configurer le VPN** :
   - Installer et configurer le client VPN fourni par IBM (ex : OpenConnect, AnyConnect).
   - Se connecter au VPN avant de lancer le terminal 3270.

---

## Étape 2 : Connexion au mainframe Z/OS et prise en main de l’environnement
**Objectif** : Se familiariser avec TSO/ISPF, JCL, et les outils de base.

1. **Se connecter via TSO** :
   - Une fois le terminal 3270 lancé, entrer son identifiant et mot de passe.
   - Taper `ISPF` pour accéder à l’interface ISPF/PDF.

2. **Découvrir ISPF/PDF** :
   - ISPF est l’éditeur et l’interface principale pour coder, compiler et soumettre des jobs.
   - Options utiles :
     - `3.2` : Éditer un fichier (pour coder en COBOL).
     - `6` : Soumettre un job (JCL).
     - `SD` : Liste des datasets (fichiers).

3. **Créer et soumettre un job JCL** :
   - Exemple de JCL pour compiler et exécuter un programme COBOL :
     ```jcl
     //MONJOB  JOB 1,'COBOL TEST',CLASS=A,MSGCLASS=X
     //STEP1   EXEC PGM=IGYCRCTL
     //SYSLIB   DD DSN=TON.BIBLIOTHEQUE.COBOL,DISP=SHR
     //SYSIN    DD *
           IDENTIFICATION DIVISION.
           PROGRAM-ID. HELLO.
           PROCEDURE DIVISION.
               DISPLAY 'HELLO, WORLD'.
               STOP RUN.
     /*
     //SYSOUT   DD SYSOUT=*
     ```
   - Soumettre ce job via l’option `6` d’ISPF.

---

## Étape 3 : Rappel des bases du COBOL (adapté aux connaissances anciennes)
**Objectif** : Rafraîchir la mémoire sur la syntaxe et les concepts clés du COBOL, avec un focus sur les évolutions des 20 dernières années.

### a. Structure d’un programme COBOL
Un programme COBOL est divisé en 4 sections principales :
```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. NOM-DU-PROGRAMME.
       AUTHOR. TON-NOM.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-Z.
       OBJECT-COMPUTER. IBM-Z.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  VARIABLE1 PIC 9(5).
       01  VARIABLE2 PIC X(10).

       PROCEDURE DIVISION.
           DISPLAY 'BONJOUR'.
           STOP RUN.
```

### b. Types de données et déclarations
- `PIC 9(n)` : Nombre (ex : `PIC 9(5)` pour un nombre de 5 chiffres).
- `PIC X(n)` : Chaîne de caractères (ex : `PIC X(10)`).
- `PIC 9(n)V99` : Nombre décimal (ex : `PIC 9(3)V99` pour 123.45).
- `OCCURS` : Tableaux (ex : `01 TABLEAU OCCURS 10 TIMES PIC 9(3)`).

### c. Instructions de base
- **Affectation** : `MOVE`, `COMPUTE`.
  ```cobol
  MOVE 100 TO VARIABLE1.
  COMPUTE VARIABLE2 = VARIABLE1 * 0.20.
  ```
- **Conditions** : `IF`, `ELSE`, `EVALUATE`.
  ```cobol
  IF VARIABLE1 > 100
      DISPLAY 'GRAND'
  ELSE
      DISPLAY 'PETIT'.
  ```
- **Boucles** : `PERFORM`.
  ```cobol
  PERFORM 10 TIMES
      DISPLAY 'BOUCLE'
  END-PERFORM.
  ```
- **Gestion de fichiers** : `OPEN`, `READ`, `WRITE`, `CLOSE`.
  ```cobol
  OPEN INPUT FICHIER-ENTREE.
  READ FICHIER-ENTREE.
  CLOSE FICHIER-ENTREE.
  ```

### d. Évolutions récentes (depuis 20 ans)
- **Support XML/JSON** : Intégration native pour échanger des données avec des systèmes modernes.
- **Appels REST** : Possibilité d’appeler des APIs web directement depuis le COBOL.
- **Intégration avec Java** : Utilisation de COBOL/Java pour étendre les applications mainframe.
- **Gestion Unicode** : Support des caractères nationaux (UTF-8).

---

## Étape 4 : COBOL pour les impôts au Québec – Concepts clés
**Objectif** : Comprendre comment le COBOL est utilisé pour gérer les calculs de taxes, les validations, et les interfaces avec les systèmes de déclaration.

### a. Gestion des calculs de taxes
- Utilisation de **tables de taux** (ex : taux d’imposition progressif).
- Exemple de structure pour une table de taux :
  ```cobol
  01  TABLE-TAUX.
      05  TAUX OCCURS 5 TIMES.
          10  SEUIL PIC 9(7).
          10  POURCENTAGE PIC 9(2)V99.
  ```
- **Logique de calcul** :
  ```cobol
  IF REVENU > SEUIL(1)
      COMPUTE TAXE = (REVENU - SEUIL(1)) * POURCENTAGE(1)
  ELSE
      COMPUTE TAXE = 0.
  ```

### b. Validation des données
- Vérification des numéros d’assurance sociale, montants déclarés, etc.
- Utilisation de `FILE STATUS` pour gérer les erreurs de fichiers :
  ```cobol
  OPEN INPUT FICHIER-DECLARATIONS.
  IF RETURN-CODE NOT = 0
      DISPLAY 'ERREUR OUVERTURE FICHIER'.
  ```

### c. Interfaces avec DB2 et CICS
- **DB2** : Pour stocker/retriever les données fiscales.
  - Exemple d’appel SQL embarqué :
    ```cobol
    EXEC SQL
        SELECT MONTANT FROM DECLARATIONS WHERE ID = :ID-DECLARANT
    END-EXEC.
    ```
- **CICS** : Pour les transactions en temps réel (ex : saisie de déclarations).
  - Exemple d’appel CICS :
    ```cobol
    EXEC CICS
        SEND MAP('DECLARATION-MAP')
    END-EXEC.
    ```

---

## Étape 5 : Ressources pour approfondir
1. **Documentation IBM** :
   - [Enterprise COBOL for z/OS Documentation](https://www.ibm.com/support/pages/enterprise-cobol-zos-documentation-library) (guides, exemples, bonnes pratiques).
   - [COBOL on z/OS](https://www.ibm.com/docs/en/zos-basic-skills?topic=zos-cobol) (tutoriels et références).

2. **Formations en ligne** :
   - [Formation COBOL – Doussou Formation (Québec)](https://www.doussou-formation.com/formation/formation-cobol/) (cours adaptés au mainframe et au contexte québécois).
   - [Cours de fiscalité – UQTR](https://oraprdnt.uqtr.uquebec.ca/portail/gscw031?owa_no_site=1730&owa_no_fiche=134) (pour comprendre les règles fiscales québécoises).

3. **Communautés** :
   - [Développez.net – Forum COBOL](https://www.developpez.net/forums/d1358313/autres-langages/autres-langages/cobol/) (pour poser des questions techniques).

---

## Étape 6 : Projet pratique – Simuler un calcul d’impôt
**Objectif** : Appliquer les connaissances en créant un programme COBOL qui calcule l’impôt québécois à partir d’un revenu déclaré.

1. Créer un fichier d’entrée (ex : `DECLARANT.DATA`) avec des revenus tests.
2. Écrire un programme COBOL qui :
   - Lit le fichier d’entrée.
   - Applique les taux d’imposition progressifs du Québec.
   - Affiche ou écrit le montant de l’impôt dans un fichier de sortie.
3. Compiler et exécuter le programme via JCL.

---

## Étape 7 : Aller plus loin
- **Intégration avec DB2** : Stocker les déclarations dans une base de données.
- **Automatisation** : Utiliser des scripts JCL pour enchaîner plusieurs programmes (ex : validation → calcul → archivage).
- **Modernisation** : Explorer l’appel d’APIs REST depuis le COBOL pour interagir avec des systèmes modernes.
