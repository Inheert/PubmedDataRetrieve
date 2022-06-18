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
- **filters** *(default: None)*: permet l'utilisation des différents filtres Pubmed, les noms sont les mêmes que ceux présents sur l'outil de recherche, il est préférable de les écrires 
en minuscule et de remplacer les espaces par un "_".
- **ThreadingObject** *(default: 3)*: définis le nombre d'instance qui travailleront simultanèment (une instance = une pathologie).
- **delay** *(default: 1)*: délai en seconde entre chaque action effectué par Selenium.

## Exemples

#### exemple 1:
````python
from PubmedGroup import PubmedGroup

# Création de l'objet
my_object = PubmedGroup(pathologies = ["goitre", "hyperthyroidie", "thyroid neoplasm"], filters=["humans"])

# Lancement de la récupération des données
my_object.StartRetrieve()

# assemblage des dataframes et créations des fichiers csv
my_object.JoinAndCleanDataframe()
````

#### exemple 2:
````python
from PubmedGroup import PubmedGroup

# Création de l'objet
my_object = PubmedGroup(pathologies = ["goitre", "hyperthyroidie", "thyroid neoplasm"], filters=["humans"])

# Lancement de la récupération des données
my_object.StartRetrieve()

# assemblage des dataframes et créations des fichiers csv
my_object.JoinAndCleanDataframe()
````
