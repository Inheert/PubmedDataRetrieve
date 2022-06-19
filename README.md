# PubmedDataRetrieve

## Introduction

Ce script permet la récupération d'articles Pubmed via l'utilisation de Seletium un module fournissant une **API** pratique pour accéder aux pilotes web tel que Firefox, 
Chrome (utilisé dans le script) ou bien Edge. 

Initialisation (main.py): 

```python
from PubmedGroup import PubmedGroup

# Création de l'objet
my_object = PubmedGroup(pathologies = ["goitre"])

# Lancement de la récupération des données
my_object.StartRetrieve()

# assemblage des dataframes et créations des fichiers csv
my_object.JoinAndCleanDataframe()
```

## Attributs

PubmedGroup():
- **pathologies** *(default: None)*: définis les pathologies à scraper, il est possible d'utiliser celles par défaut (*hyperthyroidie, hypothyroidie, goitre, 
thyroidites, thyroid neoplasm, euthyroid sick syndromes, hyperthyroxinemia, thyroid nodule, thyroid disease*) ou de rentrer une recherche personnalisée
via Pubmed : https://pubmed.ncbi.nlm.nih.gov/advanced/ et de récupérer le résultat dans "query box" :
![image](https://user-images.githubusercontent.com/90567698/174417518-efad561e-001d-4bb8-b56e-a5112f42261f.png)
- **filters** *(default: None)*: permet l'utilisation des différents filtres Pubmed, les noms sont les mêmes que ceux présents sur l'outil de recherche, il est préférable de les écrires en minuscule.
- **ThreadingObject** *(default: 3)*: définis le nombre d'instance qui travailleront simultanèment (une instance = une pathologie/requête).
- **delay** *(default: 1)*: délai en seconde entre chaque action effectué par Selenium.

Pour accéder aux informations de notre objet Pubmed tel que les pathologies par défaut ou les filtres disponibles, il suffit d'utiliser `my_objet.GetInfos()`.

## Ajouter de nouvelles pathologies par défaut

Il est possible d'ajouter de nouvelles pathologies par défaut via `Pubmed.default_pathologies` :
````python
from Pubmed import Pubmed

Pubmed.default_pathologies["NOM_DE_LA_PATHO"] = "REQUÊTE_DE_LA_PATHO"
````

## Exemples

#### exemple 1:
````python
from PubmedGroup import PubmedGroup

# Création de l'objet + précision de 3 pathologies pré-enregistrées
my_object = PubmedGroup(pathologies = ["goitre", "hyperthyroidie", "thyroid neoplasm"])

# Lancement de la récupération des données
my_object.StartRetrieve()

# assemblage des dataframes et créations des fichiers csv
my_object.JoinAndCleanDataframe()
````

#### exemple 2:
````python
from PubmedGroup import PubmedGroup

# 3 pathologies + utilisations du filtre 'humans'
my_object = PubmedGroup(pathologies = ["goitre", "hyperthyroidie", "thyroid neoplasm"], filters=["humans"])

# Lancement de la récupération des données
my_object.StartRetrieve()

# assemblage des dataframes et créations des fichiers csv
my_object.JoinAndCleanDataframe()
````

#### exemple 3 : 
````python
from PubmedGroup import PubmedGroup

# utilisation des pathologies prédéfinis ainsi que d'une requête Pubmed + ajouts d'un nouveau filtre
my_object = PubmedGroup(pathologies = ["goitre", "hyperthyroidie", "thyroid neoplasm", "((thyroid neoplasms) OR (thyroid cancer)) OR (thyroid carcinoma)"], 
                        filters=["humans", "books and documents"])

# Lancement de la récupération des données
my_object.StartRetrieve()

# assemblage des dataframes et créations des fichiers csv
my_object.JoinAndCleanDataframe()
````

#### exemple 4 : 
````python
from PubmedGroup import PubmedGroup

# utilisation de 5 pathologies prédéfinis + définition de l'argument 'threadingObject' à 5 pour faire travailler les 5 pathos simultanèments.
my_object = PubmedGroup(pathologies = ["goitre", "hyperthyroidie", "thyroid neoplasm", "euthyroid sick syndromes", "thyroid disease"], 
                        filters=["humans", "books and documents"],
                        threadingObject=5)

# Lancement de la récupération des données
my_object.StartRetrieve()

# assemblage des dataframes et créations des fichiers csv
my_object.JoinAndCleanDataframe()
````

#### exemple 5:
````python
from Pubmed import Pubmed
from PubmedGroup import PubmedGroup

# Ajout d'une nouvelle pathologie à la class Pubmed
Pubmed.default_pathologies["parathyroid diseases"] = "((hyperparathyroidism, primary) OR (primary hyperparathyroidism)) OR (hyperparathyroidism, secondary)"

# Création de l'objet + précision de 3 pathologies pré-enregistrées + utilisation de la patho précèdement ajoutée
my_object = PubmedGroup(pathologies = ["goitre", "hyperthyroidie", "parathyroid diseases"])

# Lancement de la récupération des données
my_object.StartRetrieve()

# assemblage des dataframes et créations des fichiers csv
my_object.JoinAndCleanDataframe()
````

