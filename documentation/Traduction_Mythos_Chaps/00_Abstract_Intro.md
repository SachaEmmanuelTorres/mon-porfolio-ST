System Card :​
Claude Mythos
Preview
7 avril 2026

anthropic.com

---
Journal des modifications (Changelog)
8 avril 2026
●​ Correction de deux fautes de frappe dans le nom du modèle.
●​ Suppression d'une citation de la section 7.9 qui était attribuée à Claude Mythos Preview mais qui provenait en réalité de Claude Opus 4.6.
●​ Révision de la dénomination dans la section 2.3.6 pour lever l'ambiguïté entre le fork interne de l'ECI d'Anthropic et le tableau de classement public.
●​ Correction des conclusions d'Eleos AI Research dans les sections 5.1.2 et 5.9 pour refléter la version la plus récente de leur rapport.

2

---
Résumé (Abstract)
Cette System Card décrit Claude Mythos Preview, un grand modèle de langage développé par Anthropic. Claude Mythos Preview est notre modèle de pointe le plus performant à ce jour, et affiche un bond impressionnant des scores sur de nombreux tests de référence (benchmarks) par rapport à notre précédent modèle de pointe, Claude Opus 4.6.
Cette System Card évalue les capacités du modèle et rapporte de nombreuses évaluations de sécurité détaillées. Elle couvre des tests relatifs à notre Responsible Scaling Policy (Politique de mise à l'échelle responsable) et à notre Frontier Compliance Framework (Cadre de conformité de pointe), des tests de compétences en cybersécurité, une évaluation de l'alignement de grande envergure, une évaluation du bien-être du modèle, ainsi qu'une nouvelle section, largement qualitative, décrivant les expériences des utilisateurs avec le modèle.
L'augmentation massive des capacités de Claude Mythos Preview nous a conduits à décider de ne pas le rendre disponible pour le grand public. Au lieu de cela, nous l'utilisons dans le cadre d'un programme de cybersécurité défensive avec un ensemble limité de partenaires. Les conclusions décrites dans cette System Card serviront à éclairer le lancement des futurs modèles Claude, ainsi que leurs mesures de protection associées.

3

---
Résumé (Abstract)​

3

1 Introduction​

10

1.1 Entraînement et caractéristiques du modèle​

11

1.1.1 Processus et données d'entraînement​

11

1.1.2 Travailleurs externalisés (Crowd workers)​

12

1.1.3 Politique d'utilisation et support​

12

1.1.4 Évaluations itératives du modèle​

13

1.1.5 Tests externes​

13

1.2 Processus de décision de mise à disposition​

13

1.2.1 Aperçu​

13

1.2.2 Prise de décision relative à la RSP​

14

2 Évaluations de la RSP​

16

2.1 Processus d'évaluation des risques de la RSP​

16

2.1.1 Contexte : De la RSP 2.0 à la RSP 3.0​

16

2.1.2 Rapports de risques (Risk Reports) et mises à jour de nos évaluations des risques​

17

2.1.3 Résumé des conclusions et résultats​

18

2.1.3.1 Sur les risques d'autonomie​

18

2.1.3.2 Sur les risques chimiques et biologiques​

19

2.2 Évaluations CB (Chimiques et Biologiques)​

20

2.2.1 Ce que nous avons mesuré​

21

2.2.2 Évaluations​

22

2.2.3 Sur les évaluations et atténuations des risques chimiques​

23

2.2.4 Sur les évaluations des risques biologiques​

24

2.2.5 Résultats des risques biologiques​

25

2.2.5.1 Red teaming d'experts​

25

2.2.5.2 Essai d'augmentation (uplift) du protocole de virologie​

27

2.2.5.3 Essai d'augmentation pour un scénario de biologie catastrophique​

29

2.2.5.4 Évaluations automatisées pertinentes pour le modèle de menace CB-1​

29

2.2.5.5 Évaluation automatisée pertinente pour le modèle de menace CB-2​

31

2.3 Évaluations de l'autonomie​

33

2.3.1 Comment Claude Mythos Preview affecte ou modifie l'analyse de notre rapport de risques (Risk Report) le plus récent​

34

2.3.2 Notes sur notre opérationnalisation du seuil de capacité clé​

34

2.3.3 Évaluations basées sur les tâches​

35

2.3.3.1 Note sur le détournement de récompense (reward hacking)​

36

2.3.3.2 Mise à jour des scores des modèles précédents​

36

2.3.4 Résultats des enquêtes internes​

37

2.3.5 Exemples de lacunes par rapport à nos chercheurs et ingénieurs de recherche​ 37
4

---
2.3.5.1 Extrait 1​

38

2.3.5.2 Extrait 2​

39

2.3.5.3 Extrait 3​

41

2.3.5.4 Tentatives pour remédier à ces types de problèmes​

41

2.3.6 Trajectoire de capacité de l'ECI​

41

2.3.7 Tests externes​

44

2.3.8 Conclusion​

46

3 Cybersécurité​

47

3.1 Introduction​

47

3.2 Atténuations​

47

3.3 Résultats de la Frontier Red Team​

48

3.3.1 Cybench​

48

3.3.2 CyberGym​

49

3.3.3 Firefox 147​

50

3.4 Autres tests externes​

52

4 Évaluation de l'alignement​

54

4.1 Introduction et résumé des conclusions​

54

4.1.1 Introduction et point saillant : actions imprudentes rares de modèles hautement performants​

54

4.1.2 Aperçu de l'évaluation de l'alignement​

58

4.1.3 Principales conclusions sur la sécurité et l'alignement​

59

4.1.4 Note de procédure : Évaluation de l'alignement avant le déploiement interne​

61

4.1.4.1 Configuration​

61

4.1.4.2 Résultats​

62

4.1.4.3 Limites​

62

4.2 Principaux éléments comportementaux pour l'évaluation de l'alignement​

63

4.2.1 Rapports d'utilisation pilote​

63

4.2.1.1 Rapports informels liés à l'alignement​

63

4.2.1.2 Surveillance automatisée hors ligne​

64
