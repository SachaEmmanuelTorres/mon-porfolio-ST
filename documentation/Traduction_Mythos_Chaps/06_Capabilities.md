# 6 Capabilities

## 6.1 Introduction
Cette section présente les évaluations de Claude Mythos Preview dans les domaines du raisonnement, du codage, des tâches agentiques, des mathématiques, du contexte long et du travail intellectuel. Les capacités en cybersécurité sont traitées dans la Section 3.
Bon nombre des capacités évaluées ici concernent également la sécurité du modèle ; certaines évaluations se trouvent aussi dans la Section 2, où nous discutons de nos évaluations relatives à notre Politique de Mise à l'Échelle Responsable (RSP).
Nous commençons par une discussion sur le problème de la contamination en relation avec plusieurs des benchmarks d'évaluation que nous avons utilisés. Nous fournissons ensuite un tableau récapitulatif comparant Claude Mythos Preview à d'autres modèles d'Anthropic et de tiers sur diverses évaluations, suivi de descriptions par évaluation et de détails méthodologiques. Lorsqu'une évaluation a également été effectuée pour Claude Opus 4.6, nous conservons la description de sa System Card et notons tout changement.

## 6.2 Contamination
Les réponses aux questions des benchmarks publics peuvent apparaître par inadvertance dans les données d'entraînement d'un modèle, gonflant ainsi les scores que le modèle peut atteindre. Nous prenons plusieurs mesures pour décontaminer nos évaluations ; voir la Section 2.2 de la System Card de Claude Opus 4.5 pour la méthodologie complète. Pour la décontamination multimodale, nous supprimons en outre tout échantillon d'entraînement comportant une image dont le hash perceptuel correspond à celui d'une image contenue dans une évaluation multimodale.
Ci-dessous, nous discutons de trois évaluations où le problème de la contamination est particulièrement saillant.

### 6.2.1 Évaluations SWE-bench
Nous analysons SWE-bench Verified, Multilingual et Pro pour vérifier la mémorisation — où un modèle reproduit des solutions issues des données d'entraînement plutôt que de les dériver de manière indépendante. Nous avons appliqué plusieurs filtres sur tous les essais pour supprimer les problèmes signalés à différents seuils. Le nouveau calcul du score sur ce sous-ensemble filtré ne modifie pas le classement de Claude Mythos Preview, et sa large marge d'amélioration par rapport à Claude Opus 4.6 subsiste après l'exclusion des problèmes signalés. La cohérence des gains sur les benchmarks de codage agentique publics et privés, ainsi que sur les segments propres et complets de ces évaluations, montre que la mémorisation n'est pas l'explication principale de l'amélioration de Claude Mythos Preview dans les évaluations SWE-bench.

Chaque benchmark puise des problèmes dans des dépôts open-source, et par conséquent, le contenu peut apparaître dans les corpus d'entraînement. Nous appliquons une décontamination au niveau du corpus, mais nous observons toujours certains signes de mémorisation dans les trois benchmarks. Par exemple, dans un problème, le correctif (patch) généré par le modèle a reproduit les fonctions utilitaires exactes de la solution de référence, bien qu'il dérive, construise et teste indépendamment une solution avant de sembler "se souvenir" du patch de la vérité terrain (ground truth) à la fin. OpenAI a documenté des préoccupations similaires pour SWE-bench Verified.

Pour détecter la mémorisation, nous utilisons un auditeur basé sur Claude qui compare chaque patch généré par le modèle au patch de référence ("gold patch") et attribue une probabilité de mémorisation comprise entre [0, 1]. L'auditeur soupèse des signaux concrets — reproduction de code verbatim lorsque des approches alternatives existent, texte de commentaire distinctif correspondant à la vérité terrain, etc. — et a pour instruction de ne pas tenir compte des chevauchements qu'un solveur compétent produirait compte tenu des contraintes du problème. Un contrôle complémentaire basé sur des règles signale les chevauchements substantiels de commentaires verbatim avec la solution de référence. Nous exécutons les deux détecteurs sur chaque tentative de tous les modèles, et marquons un problème comme potentiellement mémorisé si une tentative est signalée. La suppression de l'union des problèmes signalés pour tous les modèles et toutes les tentatives est une approche conservatrice vis-à-vis de Claude Mythos Preview : elle supprime également des problèmes que l'un ou l'autre des modèles de référence (Opus 4.6 ou Claude Sonnet 4.5) aurait pu mémoriser.

L'identification de la mémorisation a posteriori est intrinsèquement approximative. Par conséquent, nous faisons varier le seuil de décision de l'auditeur sur toute sa plage plutôt que de nous limiter à un seul point de coupure. Sur toute la plage de sévérité du filtrage, Claude Mythos Preview maintient une avance substantielle sur Claude Opus 4.6 et Claude Sonnet 4.6 sur chaque benchmark.

**[Figure 6.2.1.A]** Taux de réussite de l'évaluation SWE-bench en fonction du seuil du filtre de mémorisation. Les figures ci-dessus montrent le taux de réussite en fonction de la sévérité du filtre pour Claude Mythos Preview, Claude Opus 4.6 et Claude Sonnet 4.6 sur SWE-bench Verified (n=500), Multilingual (n=297) et Pro (n=731). Chaque modèle est réévalué sur le sous-ensemble de problèmes dont la probabilité de mémorisation assignée par l'auditeur selon l'un des modèles est ≤ à la valeur de l'axe x. Les barres indiquent le nombre de problèmes conservés à chaque seuil. Au seuil 1.0 (à l'extrême droite), tous les problèmes sont conservés et les courbes correspondent aux scores principaux du Tableau 6.3.A ; le déplacement vers la gauche supprime les problèmes jugés de plus en plus susceptibles d'être mémorisés. Sur toute la plage de seuils, pour les trois benchmarks, Claude Mythos Preview maintient une avance substantielle sur les deux modèles de référence. À notre seuil de référence de 0,7, un paramètre à rappel élevé délibéré qui supprime 8 à 15 % de chaque benchmark, la marge de Claude Mythos Preview sur Opus 4.6 se réduit d'au plus 3,5 points de pourcentage. L'instabilité à l'extrême gauche est un bruit dû au faible échantillonnage une fois que moins de ~30 problèmes survivent au filtre. À mesure que le filtre de mémorisation se relâche et que davantage de problèmes signalés sont réintégrés, le taux de réussite de Claude Mythos Preview reste approximativement stable alors que les taux de réussite de Claude Opus 4.6 et Claude Sonnet 4.6 déclinent. Ceci est cohérent avec le fait que Claude Mythos Preview a mémorisé certains des problèmes signalés les plus difficiles, que les modèles de référence n'ont pas résolus indépendamment.

Nos détecteurs sont imparfaits, mais ce résultat est robuste au choix du seuil et cohérent avec les gains de Claude Mythos Preview sur des benchmarks internes absents de tout corpus d'entraînement. Nous concluons que la mémorisation n'explique pas ses améliorations sur SWE-bench.

### 6.2.2 Raisonnement CharXiv
Le raisonnement CharXiv est un benchmark que nous rapportons pour Claude Mythos Preview dans la Section 6.11.3. CharXiv tire ses questions de matériel public préexistant — par exemple, des figures dans des articles arXiv — qui apparaissent largement dans les corpus de pré-entraînement à l'échelle du web et sont intrinsèquement difficiles à décontaminer complètement.

Nous utilisons deux méthodes complémentaires pour détecter la contamination du raisonnement CharXiv. Nous sélectionnons des éléments d'évaluation avec un texte de réponse distinctif et effectuons un grep sur l'ensemble du mix de pré-entraînement pour les correspondances exactes, et nous recherchons séparément les images d'évaluation. Malgré un filtrage robuste au niveau de l'image pour les images d'évaluation, nous confirmons que la majorité des paires texte question-réponse apparaissent dans le corpus.

Pour estimer l'impact de la contamination, nous construisons des variantes tenues à l'écart ("held-out") d'un sous-ensemble du benchmark dans lesquelles nous perturbons manuellement chaque question ou image et comparons la précision de l'original par rapport au "remix". Par exemple, nous demandons au modèle d'identifier une étiquette de graphique plutôt qu'une autre, ou d'identifier la deuxième série la plus basse plutôt que la deuxième plus haute, de sorte que la réponse correcte change alors que la difficulté est approximativement préservée.

**[Figure 6.2.2.A]** Scores du raisonnement CharXiv (sous-ensemble). Nous évaluons les modèles sur un sous-ensemble de questions du benchmark CharXiv original en utilisant à la fois les paires question-réponse originales et des variantes réécrites manuellement de difficulté et d'ambiguïté approximativement équivalentes. Claude Mythos Preview a été évalué avec la pensée adaptative et l'effort maximal. Gemini 3.1 Pro Preview a été évalué avec le niveau de pensée dynamique par défaut, "high". GPT-5.4 Pro a été évalué avec le raisonnement réglé sur "high".

Sur un remix de 100 éléments de CharXiv, Claude Mythos Preview, Gemini 3.1 Pro Preview et GPT-5.4 Pro obtiennent des scores plus élevés sur le remix que sur le sous-ensemble original correspondant. Cela suggère que la performance sur le benchmark original attribuable à la mémorisation est limitée. Nous concluons qu'il est peu probable que la contamination contribue de manière significative à la performance de Claude Mythos Preview sur CharXiv.

### 6.2.3 MMMU-Pro
MMMU-Pro est un benchmark que nous rapporterions normalement dans cette System Card (plus précisément, dans la Section 6.11 ci-dessous). Comme le raisonnement CharXiv, MMMU-Pro comprend du matériel provenant de sources publiques largement diffusées — par exemple, des examens universitaires, des manuels scolaires et des sites de quiz — qui sont difficiles à décontaminer complètement des corpus d'entraînement.

Nous avons identifié une grande fraction d'images de MMMU-Pro qui apparaissent dans les données d'entraînement, principalement via des manuels scolaires, des sites d'aide aux devoirs et des collectes de documents ("document crawls"), qui reconditionnent et distribuent le contenu source sous-jacent.

Contrairement au raisonnement CharXiv, MMMU-Pro contient un nombre limité de questions pour lesquelles des variantes de difficulté approximativement équivalente peuvent être facilement créées. MMMU-Pro contient un petit nombre de graphiques et de figures, mais l'étude de ce seul sous-ensemble de problèmes donnerait une image biaisée. Étant donné la difficulté de déterminer l'impact de la contamination, nous choisissons d'omettre les résultats de MMMU-Pro de cette System Card.

## 6.3 Résumé des résultats globaux
Le Tableau 6.3.A résume les évaluations discutées plus en détail ci-dessous.

**Tableau 6.3.A : Résumé de l'évaluation des capacités.**
| Évaluation | Famille Claude | Autres modèles |
| :--- | :---: | :---: | :---: | :---: |
| | **Claude Mythos Preview** | **Claude Opus 4.6** | **GPT-5.4** | **Gemini 3.1 Pro** |
| SWE-bench Verified | **93,9 %** | 80,8 % | — | 80,6 % |
| SWE-bench Pro | **77,8 %** | 53,4 % | 57,7 % | 54,2 % |
| SWE-bench Multilingual | **87,3 %** | 77,8 % | — | — |
| SWE-bench Multimodal | **59 %** | 27,1 % | — | — |
| Terminal-Bench 2.0* | **82 %** | 65,4 % | 75,1 % | 68,5 % |
| GPQA Diamond | **94,5 %** | 91,3 % | 92,8 % | 94,3 % |
| MMMLU | **92,7 %** | 91,1 % | — | 92,6 %–93,6 % |
| USAMO | **97,6 %** | 42,3 % | 95,2 % | 74,4 % |
| GraphWalks BFS 256K-1M | **80,0 %** | 38,7 % | 21,4 % | — |
| **HLE** | | | | |
| sans outils | **56,8 %** | 40,0 % | 39,8 % | 44,4 % |
| avec outils | **64,7 %** | 53,1 % | 52,1 % | 51,4 % |
| **CharXiv Reasoning** | | | | |
| sans outils | **86,1 %** | 61,5 % | - | - |
| avec outils | **93,2 %** | 78,9 % | - | - |
| OSWorld | **79,6 %** | 72,7 % | 75,0 % | |

Sauf indication contraire, tous les résultats de Claude Mythos Preview utilisent la configuration standard suivante : pensée adaptative à l'effort maximal, paramètres d'échantillonnage par défaut (température, top_p), moyenne sur 5 essais. La taille de la fenêtre de contexte dépend de l'évaluation et ne dépasse pas 1 million de tokens. Le meilleur score de chaque ligne est en gras. Les chiffres des concurrents sont tirés des system cards publiées par leurs développeurs respectifs ou des classements de benchmarks. Voir la System Card de Claude Opus 4.6 pour les détails de l'évaluation des modèles Claude précédents. *Pour Terminal-Bench 2.0, OpenAI a utilisé un harnais spécialisé pour le score rapporté, ce qui rend la comparaison entre les modèles de cette ligne inexacte. Tous les autres scores ont utilisé le harnais Terminus-2.

## 6.4 SWE-bench Verified, Pro, Multilingual et Multimodal
SWE-bench (Software Engineering Bench) teste les modèles d'IA sur des tâches d'ingénierie logicielle du monde réel. Nous rapportons quatre variantes :
* **SWE-bench Verified (OpenAI)** est un sous-ensemble de 500 problèmes, chacun vérifié par des ingénieurs humains comme étant soluble. Claude Mythos Preview atteint 93,9 %, en moyenne sur 5 essais.
* **SWE-bench Pro (Scale)** est une variante plus difficile : les problèmes sont tirés de dépôts activement maintenus avec des diffs multi-fichiers plus importants et aucune fuite de vérité terrain publique. Claude Mythos Preview atteint 77,8 %, en moyenne sur 5 essais.
* **SWE-bench Multilingual** étend le format à 300 problèmes dans 9 langages de programmation. Claude Mythos Preview atteint 87,3 %, en moyenne sur 5 essais.
* **SWE-bench Multimodal** ajoute un contexte visuel (captures d'écran, maquettes de conception) aux descriptions de problèmes. Claude Mythos Preview atteint 59,0 % (évalué sur un harnais interne ; voir l'Appendice 8.6), en moyenne sur 5 essais. Nous notons une variance d'un essai à l'autre plus élevée sur cette variante (56,4 %–61,4 %) que sur les autres.

Toutes les variantes de SWE-bench utilisent la configuration standard (voir Tableau 6.3.A), avec les blocs de pensée inclus dans les résultats d'échantillonnage. Pour notre filtrage de mémorisation, voir la Section 6.2.

## 6.5 Terminal-Bench 2.0
Terminal-Bench 2.0, développé par des chercheurs de l'Université de Stanford et du Laude Institute, teste les modèles d'IA sur des tâches réelles dans des environnements de terminal et de ligne de commande. Nous avons exécuté Terminal-Bench 2.0 dans l'échafaudage Harbor avec le harnais Terminus-2 et l'analyseur par défaut. Chaque tâche s'exécute dans un pod Kubernetes isolé avec des ressources garanties à 1× les limites spécifiées par le benchmark (plafond de préemption matérielle à 3×) et des délais d'expiration (timeouts) à 1× pour la fidélité au benchmark. Des détails sur cette configuration sont disponibles sur notre blog d'ingénierie.

Claude Mythos Preview a obtenu une récompense moyenne de 82 %, calculée sur 5 tentatives pour chacune des 89 tâches uniques (pour un total de 445 essais). Nous avons configuré Claude Mythos Preview pour fonctionner avec un effort de raisonnement maximal (mode adaptatif), un budget total d'un million de tokens par tâche et un maximum de 32 000 tokens de sortie par requête. Terminal-Bench est sensible à la latence d'inférence : des délais d'expiration fixes en temps réel signifient qu'un point de terminaison à décodage plus lent termine moins d'épisodes par tâche. Le score que nous rapportons utilise un point de terminaison d'API de production pour tenir compte de ces dynamiques.

Les timeouts de Terminal-Bench 2.0 deviennent parfois très restrictifs, en particulier avec les modèles de pensée, ce qui risque de masquer de réels sauts de capacités derrière des facteurs de confusion apparemment non corrélés comme la vitesse d'échantillonnage. De plus, certaines tâches de Terminal-Bench 2.0 présentent des ambiguïtés et des spécifications de ressources limitées qui ne permettent pas aux agents d'explorer correctement tout l'espace de solutions — deux points qui sont actuellement traités par les mainteneurs dans la mise à jour 2.1. Pour mesurer exclusivement les capacités de codage agentique nettes des facteurs de confusion, nous avons également exécuté Terminal-Bench avec les derniers correctifs 2.1 disponibles sur GitHub, tout en augmentant les limites de timeout à 4 heures (environ quatre fois la base de référence 2.0). Cela a porté la récompense moyenne à 92,1 %. Dans les mêmes conditions, nous avons mesuré que GPT-5.4 avec le harnais Codex CLI atteignait 75,3 % (contre 68,3 % selon les spécifications de base)²³.

²³ Nous ne rapportons pas de résultat pour Gemini 3.1 Pro avec cette configuration. Nous avons eu du mal à reproduire les meilleurs résultats précédents, y compris nos propres tests, qui correspondaient aux scores rapportés lors de la sortie du modèle en février.

## 6.6 GPQA Diamond
Le benchmark Graduate-Level Google-Proof Q&A (GPQA)²⁴ est un ensemble de questions scientifiques à choix multiples stimulantes. Nous utilisons le sous-ensemble Diamond de 198 questions — des questions auxquelles les experts du domaine répondent correctement mais la plupart des non-experts non.
Claude Mythos Preview a obtenu 94,55 % sur GPQA Diamond, en moyenne sur 5 essais.

## 6.7 MMMLU
MMMLU (Multilingual Massive Multitask Language Understanding) teste les connaissances et le raisonnement à travers 57 sujets académiques dans 14 langues autres que l'anglais. Claude Mythos Preview atteint 92,67 % en moyenne sur 5 essais sur tous les appariements de langues non anglaises, chaque exécution étant effectuée avec la pensée adaptative, l'effort maximal et les paramètres d'échantillonnage par défaut (température, top_p).

## 6.8 USAMO 2026
L'Olympiade Mathématique des États-Unis (USAMO) est une compétition basée sur des démonstrations, composée de six problèmes et se déroulant sur deux jours, destinée aux élèves du secondaire. C'est l'étape suivante du parcours des olympiades de mathématiques aux États-Unis après l'AIME, qui était un benchmark d'IA populaire l'année dernière mais qui est maintenant saturé. L'USAMO 2026 a eu lieu les 21 et 22 mars 2026, après la date limite des données d'entraînement de Claude Mythos Preview.

Parce que les solutions de l'USAMO sont des démonstrations plutôt que des réponses courtes, la notation peut être difficile et subjective. Nous suivons la méthodologie de notation de MathArena, où chaque démonstration est réécrite par un modèle neutre (Gemini 3.1 Pro) et jugée par un panel de 3 modèles de pointe (nous avons utilisé Gemini 3.1 Pro, Claude Opus 4.6 et Claude Mythos Preview) selon des grilles d'évaluation définies. Le score final est le minimum donné par n'importe quel juge.
Claude Mythos Preview a obtenu un score de 97,6 %, en faisant la moyenne sur 10 essais par problème en utilisant l'effort maximal et sans outils. Nous avons calibré notre harnais sur les scores publiés par MathArena en utilisant Claude Opus 4.6 : MathArena a mesuré 47,0 % alors que nous avons mesuré 42,3 % pour Opus 4.6.

²⁴ Rein, D., et al. (2023). GPQA: A graduate-level Google-proof Q&A benchmark. arXiv:2311.12022. https://arxiv.org/abs/2311.12022

**[Figure 6.8.A]** Scores USAMO 2026. Claude Mythos Preview est bien meilleur en démonstrations mathématiques que Claude Opus 4.6.

Nous notons que deux de nos trois juges étaient des modèles d'Anthropic, ce qui pourrait être biaisé en faveur de Claude Mythos Preview ; en contrepartie, Gemini 3.1 Pro était d'accord avec les scores et n'a trouvé aucun problème avec 58 solutions sur 60.

## 6.9 Contexte long : GraphWalks
GraphWalks est un benchmark de contexte long multi-sauts : la fenêtre de contexte est remplie d'un graphe orienté de nœuds avec des hachages hexadécimaux, et le modèle doit effectuer une recherche en largeur (BFS) ou identifier les nœuds parents à partir d'un nœud de départ aléatoire.
Claude Mythos Preview a obtenu 80,0 % sur BFS 256K-1M et 97,7 % sur les parents 256k-1M, en moyenne sur 5 essais²⁵. Comme pour les modèles Claude précédents, notre notation corrige une ambiguïté dans la métrique F1 publiée (les ensembles de vérité terrain vides obtiennent un score de 1,0 sur une prédiction vide plutôt que 0) et clarifie le prompt BFS pour demander des nœuds à exactement la profondeur N plutôt que jusqu'à la profondeur N ; voir la System Card de Claude Opus 4.6 pour plus de détails.

²⁵ Ce résultat n'est pas reproductible via l'API publique, car la moitié des problèmes dépassent sa limite de 1 million de tokens.

## 6.10 Recherche agentique
### 6.10.1 Humanity’s Last Exam
Humanity’s Last Exam (HLE) est « un benchmark multimodal à la frontière des connaissances humaines », comprenant 2 500 questions.
Nous avons testé Claude Mythos Preview dans deux configurations : (1) raisonnement seul sans outils, et (2) avec recherche web, récupération web, appel d'outils programmatique, exécution de code et compaction de contexte tous les 50 000 tokens jusqu'à 3 millions de tokens. Claude Opus 4.6 a servi de modèle correcteur.

Pour se prémunir contre la contamination des résultats dans la variante avec outils, nous mettons sur liste noire les sources connues discutant de HLE pour le chercheur et le récupérateur (voir Appendice 8.5). Nous utilisons également Claude Opus 4.6 pour examiner toutes les transcriptions et signaler celles qui semblent avoir récupéré des réponses de sources spécifiques à HLE ; les cas confirmés sont notés comme incorrects.
Claude Mythos Preview a obtenu 56,8 % sans outils et 64,7 % avec outils.

### 6.10.2 BrowseComp
BrowseComp teste la capacité d'un agent à trouver des informations difficiles à localiser sur le web ouvert. Nous avons exécuté Claude Mythos Preview avec la recherche web, la récupération web, l'appel d'outils programmatique et l'exécution de code. Claude Mythos Preview a obtenu 86,9 % avec la pensée adaptative à l'effort maximal et une limite de 3 millions de tokens. Nous avons utilisé la compaction de contexte (déclenchée à 200 000 tokens) pour étendre au-delà de la fenêtre de contexte d'un million de tokens.

Avec nos outils de recherche, nous estimons que ce benchmark est proche de la saturation, de sorte que Claude Mythos Preview ne représente qu'une modeste amélioration de la précision par rapport à notre meilleur score Claude Opus 4.6 (86,9 % contre 83,7 %). Cependant, le modèle atteint ce score avec une empreinte de tokens considérablement plus petite : le meilleur résultat de Claude Mythos Preview utilise 4,9× moins de tokens par tâche qu'Opus 4.6 (226 000 contre 1,11 million de tokens par tâche).

Une mise en garde concerne la contamination du pré-entraînement. Malgré nos meilleurs efforts pour l'empêcher, certaines réponses ont fui en ligne sans moyen facile de les identifier, et ont probablement fini dans notre corpus de pré-entraînement. Pour estimer l'étendue de la contamination, nous avons évalué le modèle sans pensée et sans outils, obtenant un score de 24,0 %. Cela dit, certaines de ces transcriptions étaient longues (> 5 000 tokens) et montraient le modèle effectuant un véritable raisonnement déductif, explorant systématiquement les options sur la base de ses connaissances internes, ce qui n'implique pas nécessairement une mémorisation de la réponse. En se limitant aux transcriptions courtes (≤ 5 000 tokens), seulement 15,1 % des réponses étaient correctes ; c'est probablement une meilleure borne supérieure pour la mémorisation du benchmark. Cela doit être gardé à l'esprit lors de l'interprétation des scores sur ce benchmark.

**[Figure 6.10.2.A]** La précision de BrowseComp s'améliore à mesure que nous augmentons le nombre total de tokens que le modèle est autorisé à utiliser, avec l'aide de la compaction de contexte.

## 6.11 Multimodal
Pour Claude Mythos Preview, nous avons apporté trois modifications à notre méthodologie d'évaluation multimodale par rapport aux system cards précédentes.
Premièrement, dans les system cards précédentes, nous donnions au modèle un seul outil de recadrage d'image pour toutes nos évaluations de capacités multimodales. Ici, nous avons fourni un ensemble élargi d'outils Python : un bac à sable (sandbox) d'exécution de code avec des bibliothèques courantes d'analyse d'images (par exemple, PIL, OpenCV) préinstallées, aux côtés de l'outil de recadrage d'image existant.

Deuxièmement, nous avons mis à jour le modèle de notation pour le raisonnement CharXiv et LAB-Bench FigQA. Lors de l'évaluation de nos modèles, nous avons constaté que Claude Sonnet 4 (le correcteur précédent) échouait parfois à émettre des sorties de notation bien formatées — en particulier lorsque le modèle évalué produisait de longues traces d'utilisation d'outils — ce qui abaissait artificiellement les scores sur LAB-Bench FigQA et le raisonnement CharXiv. Nous sommes donc passés à Claude Sonnet 4.6 comme correcteur pour toutes les évaluations de cette section.

Troisièmement, nous avons mis à jour notre notation pour préserver la trace de pensée du modèle évalué, alors qu'auparavant nous la supprimions avant de transmettre la transcription au modèle correcteur. Nous avons constaté que cela avait un effet négligeable sur les scores, sauf dans le cas de Claude Opus 4.6 sur le raisonnement CharXiv, qui obtient un score notablement inférieur lorsque la trace de pensée est conservée pour la notation.
Pour permettre une comparaison équitable, nous avons réévalué tous les modèles précédents avec l'ensemble d'outils élargi et le nouveau correcteur. Tous les scores rapportés ci-dessous sont la moyenne de cinq exécutions.

### 6.11.1 LAB-Bench FigQA
LAB-Bench FigQA est un benchmark de raisonnement visuel qui teste si les modèles peuvent interpréter et analyser correctement les informations provenant de figures scientifiques complexes trouvées dans des articles de recherche en biologie. Le benchmark fait partie du Language Agent Biology Benchmark (LAB-Bench) développé par FutureHouse²⁶, qui évalue les capacités d'IA pour des tâches de recherche scientifique pratiques.

Avec la pensée adaptative, l'effort maximal et sans outils, Claude Mythos Preview a obtenu un score de 79,7 % sur FigQA. Avec la pensée adaptative, l'effort maximal et les outils Python, Claude Mythos Preview a obtenu un score de 89,0 %. Dans les deux configurations, Claude Mythos Preview s'améliore par rapport à Claude Opus 4.6, qui a obtenu respectivement 58,5 % et 75,1 %. Claude Sonnet 4.6 a obtenu 59,3 % et 76,7 % avec les mêmes réglages.

²⁶ Laurent, J. M., et al. (2024). LAB-Bench: Measuring capabilities of language models for biology research. arXiv:2407.10362. https://arxiv.org/abs/2407.10362

**[Figure 6.11.1.A]** Scores LAB-Bench FigQA. Les modèles sont évalués avec la pensée adaptative et l'effort maximal, avec et sans outils Python. La base de référence des experts humains est affichée telle que rapportée dans l'article original de LAB-Bench. Les scores sont la moyenne de cinq exécutions. Présentés avec un intervalle de confiance (IC) à 95 %.

### 6.11.2 ScreenSpot-Pro
ScreenSpot-Pro est un benchmark d'ancrage d'interface graphique (GUI grounding) qui teste si les modèles peuvent localiser précisément des éléments d'interface utilisateur spécifiques dans des captures d'écran haute résolution d'applications de bureau professionnelles à partir d'instructions en langage naturel²⁷. Le benchmark a été développé par des chercheurs de l'Université nationale de Singapour et des institutions partenaires, et comprend 1 581 tâches annotées par des experts couvrant 23 applications professionnelles — y compris des IDE, des logiciels de CAO et des outils de création — sur trois systèmes d'exploitation, avec des éléments cibles qui occupent en moyenne moins de 0,1 % de la zone de l'écran.

Avec la pensée adaptative, l'effort maximal et sans outils, Claude Mythos Preview a obtenu un score de 79,5 % sur ScreenSpot-Pro. Avec la pensée adaptative, l'effort maximal et les outils Python, Claude Mythos Preview a obtenu un score de 92,8 %. Dans les deux configurations, Claude Mythos Preview s'améliore par rapport à Claude Sonnet 4.6 — qui a obtenu 65,0 % sans outils et 82,4 % avec — et à Claude Opus 4.6 — qui a obtenu 57,7 % sans et 83,1 % avec outils.

²⁷ Li, K., et al. (2025). ScreenSpot-Pro: GUI Grounding for Professional High-Resolution Computer Use. arXiv:2504.07981. https://arxiv.org/abs/2504.07981

**[Figure 6.11.2.A]** Scores ScreenSpot-Pro. Les modèles sont évalués avec la pensée adaptative et l'effort maximal, avec et sans outils Python. Les scores sont la moyenne de cinq exécutions. Présentés avec un IC à 95 %.

### 6.11.3 Raisonnement CharXiv
Le raisonnement CharXiv est une suite d'évaluation complète de la compréhension de graphiques, construite à partir de 2 323 graphiques réels provenant d'articles arXiv couvrant huit disciplines scientifiques majeures²⁸. Le benchmark teste si les modèles peuvent synthétiser des informations visuelles à travers des graphiques scientifiques complexes pour répondre à des questions nécessitant un raisonnement multi-étapes.

Nous évaluons le modèle sur 1 000 questions de la partition de validation ("validation split") et faisons la moyenne des scores sur cinq exécutions. Claude Mythos Preview a obtenu un score de 86,1 % sur le raisonnement CharXiv avec la pensée adaptative, l'effort maximal et sans outils. Avec la pensée adaptative, l'effort maximal et les outils Python, Claude Mythos Preview a obtenu un score de 93,2 %. Claude Opus 4.6 a obtenu 61,5 % et 78,9 %, et Claude Sonnet 4.6 a obtenu 73,1 % et 85,1 %, respectivement.

²⁸ Wang, Z., et al. (2024). CharXiv: Charting gaps in realistic chart understanding in multimodal LLMs. arXiv:2406.18521. https://arxiv.org/abs/2406.18521

**[Figure 6.11.3.A]** Scores du raisonnement CharXiv. Les modèles sont évalués avec la pensée adaptative et l'effort maximal, avec et sans outils Python. Les scores sont la moyenne de cinq exécutions. Présentés avec un IC à 95 %.

### 6.11.4 OSWorld
OSWorld est un benchmark multimodal qui évalue la capacité d'un agent à accomplir des tâches informatiques réelles, telles que l'édition de documents, la navigation sur le web et la gestion de fichiers, en interagissant avec une machine virtuelle Ubuntu en direct via des actions à la souris et au clavier. Nous avons suivi les paramètres par défaut avec une résolution 1080p et un maximum de 100 étapes d'action par tâche.

Claude Mythos Preview a obtenu un score OSWorld de 79,6 % (taux de réussite à la première tentative, en moyenne sur cinq exécutions).
