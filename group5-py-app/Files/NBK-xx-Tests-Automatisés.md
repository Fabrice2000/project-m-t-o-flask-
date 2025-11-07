# Tester un programme en Python

Il existe plusieurs façons de tester votre code. Dans ce tutoriel, vous apprendrez les techniques à partir des étapes les plus élémentaires et travaillerez vers des méthodes avancées.

## Tests Automatisés vs. tests manuels

Vous avez probablement déjà créé un test sans vous en rendre compte.
Quand vous avez exécuté votre application et l'avez utilisée pour la première fois? Avez-vous vérifié les fonctionnalités et expérimenté en les utilisant? C’est ce qu’on appelle le **test exploratoire** et c’est une forme de test manuel. Le test exploratoire est une forme de test qui se fait sans plan. Dans un test exploratoire, vous explorez simplement l’application. Pour avoir un ensemble complet de tests manuels, tout ce que vous devez faire est de lister toutes les fonctionnalités de votre application, les différents types d'entrées qu'elle peut accepter et les résultats attendus. Maintenant, chaque fois que vous faites une modification de votre code, vous devez parcourir chaque élément de cette liste et le vérifier. C'est très fastidieux (et fragile, de surcroît).

C’est là qu’interviennent les tests automatisés. Le test automatisé est l'exécution de votre plan de test (les parties de votre application que vous souhaitez tester, l'ordre dans lequel vous voulez les tester et les réponses attendues) par un script au lieu d'un humain. Python est déjà livré avec un ensemble d'outils et de bibliothèques pour vous aider à créer des tests automatisés pour votre application.

## Tests unitaires vs. tests d'intégration

Le monde des tests ne manque pas de terminologie. Il existe une gande variété de tests différents :
- tests unitaires
- tests fonctionnels
- tests d'intégration
- tests end-to-end (de bout en bout, souvent notés E2E)
- tests d'acceptation
- tests de charge
- test utilisateurs

Cette liste n'est pas exhaustive. Il existe d'ailleurs une norme pour la dénomination de tous les tests, norme par ailleurs assez peu connue.

Globalement, les tests automatisés forment une hérarchie qui permet d'explorer le code du programme du niveau le plus local au niverau le plus global. Typiquement :
- Un **test unitaire** est un test qui vérifie qu'une fonction isolée fait exactement ce que vous voulez. C'est pourquoi, il est esssentiel de suivre les préceptes de la **programmation fonctionnelle** et d'écrire des **fonctions pures**, c'est-à-dire des fonctions dont le résultat ne dépend que des valeurs de paramètres d'entrée ou de variables locales. Une fonction pure exclut notamment les variables globales. Il n'est pas toujours si simple de tester les fonctions isolément.
- Un **test d'intégration**, comme son nom l'indique, permet de vérifier que les combinaisons de composants s'agrègent correctement. Dès le moment ou une fonction appelle une autre fonction (ou un service un autre service), on entre dans le domaine des tests d'intégration (ou quelquefois fonctionnels).C'est pour cela que les prioncipes SOLID en Programmation Orientée Objet sont très importants pour séparer les responsabilités de classes.
- Les **tests E2E**, sont chargés de simuler des scenarii complets, comme des cas d'utilisation, par exemple. DAns le cadre des applications web, ce tyupe de test permet de s'assurer que l'utilisateur peut atteindre l'objectif qu'il s'est fixé. Par exemple, acheter un produit sur un site de commerce en ligne, ce qui suppose sue séquence complexe d'actions tant du c^té du navigateur que de celui du serveur.

Python et son écoystème fournissent tous les outils pour concevoir les différents types de tests.

Il existe d'abord une méthode très simple, avec la fonction `assert` :
```python
assert sum([1, 2, 3]) == 6, "Should be 6"
```

Cela ne produit rien sur la REPL car les valeurs sont correctes. Si le résultat de `sum()` est incorrect, cela échouera avec un `AssertionError` et le message "Should be 6".
```python
assert sum([1, 1, 1]) == 6, "Should be 6"

# Traceback (most recent call last):
#  File "<stdin>", line 1, in <module>
# AssertionError: Should be 6
```
ou, plus communément :
```python
# test_sum.py
def test_sum(values):
    assert sum(values) == 6, "Should be 6"

if __name__ == "__main__":
    test_sum([1,2,3])
    print("Everything passed")
```
que vous éxécuterez en ligne de commande :
```bash
python test_sum.py
# Everything passed
```

En Python, `sum()` accepte tout itérable comme son premier argument. Vous avez testé avec une liste. Maintenant, testez la fonction en lui passant un tupl.

> **N.B.** Il est possible de documenter et de tester simultanément votre code, tout en vous assurant que votre code et sa documentation restent synchronisés, avec le module `doctest`.

## Choisir un lanceur de test

Écrire des tests de cette façon est correct pour un simple contrôle, mais que se passe-t-il si plus d'un échoue? C'est là qu'interviennent les « _test runners_ ». C'est une application spéciale conçue pour exécuter des tests, vérifier la sortie et vous donner des outils pour le déboguage et le diagnostic des tests et des applications.

Il existe de nombreux coureurs de test disponibles pour Python. Celui intégré dans la bibliothèque standard Python est appelé `unittest`. Les plus populaires sont:
- unittest
- nose ou nose2
- `pytest`
- robot
- cucumber

## Les tests unitaires en Python

### Exécuter des tests avec unittest

`unittest` a été intégré dans la bibliothèque standard Python depuis la version 2.1. Vous le verrez probablement dans les applications Python commerciales et les projets open source.

`unittest` est à la fois un cadre de test et un lanceur de test. Il a certaines exigences importantes pour la rédaction et l'exécution des tests.
- Vous devez définir vos tests dans comme méthodes de classes de tests
- Vous devez utiliser une série de **méthodes d'assertions** spéciales dans une classe dérivée de `unittest.TestCase`

Par exemple :
```python
import unittest

class TestSum(unittest.TestCase):

    def test_sum_true(self):
        """
       Test de la fonction Python sum()
       On utilise ici la méthode d'assertion assertEquals de unittest,
        qui teste l'égalité de deux valeurs.
        """
        values = [1,2,3]
        self.assertEqual(sum(values), 6, "Should be 6")

    def test_sum_false(self):
        """
       Test de la fonction Python sum()
       On utilise ici la méthode d'assertion assertEquals de unittest,
        qui teste l'égalité de deux valeurs.
        """
        values = [1,1,1]
        self.assertEqual(sum(values), 6, "Should be 6")

if __name__ == "__main_":
    # La méthode main() lance les tests
    unittest.main()
```
Si vous exécutez cela sur la ligne de commande, vous verrez un succès (indiqué avec .) et un échec (indiqué avec F::
```bash
python test_sum_unittest.py
# .F
# ======================================================================
# FAIL: test_sum_tuple (__main__.TestSum)
# ----------------------------------------------------------------------
# Traceback (most recent call last):
#   File "test_sum_unittest.py", line 9, in test_sum_tuple
#     self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")
# AssertionError: Should be 6
#
# ----------------------------------------------------------------------
# Ran 2 tests in 0.001s
#
# FAILED (failures=1)
```

> **N.B.** Faites attention si vous écrivez des cas de test qui doivent être exécutés à la fois en Python 2 et 3. En Python 2.7 et en dessous, unittest est appelé `unittest2`. Si vous importez simplement de unittest, vous obtiendrez différentes versions avec différentes fonctionnalités entre Python 2 et 3.
>
> [Documentation du module unittest](https://docs.python.org/3/library/unittest.html)

### Exécuter des tests avec nose

Au fil du temps, lorsque vous écrirez des centaines, voire des milliers de tests pour votre application, vous constaterez qu'il de plus en plus difficile de comprendre et d’utiliser la sortie `unittest`.

`nose` est compatible avec tous les tests écrits en utilisant le cadre de tests `unittest` et peut être utilisé comme une alternative en tant que lanceur de tests. Pour commencer installez `nose` avec `pip` et exécutez-le en ligne de commande. `nose` essaiera de découvrir tous les scripts de test nommés `test*.py` et les cas de test héritant de `unittest.TestCase` dans le répertoire actuel:
```bash
pip install nose2
python -m nose2
# .F
# ======================================================================
# FAIL: test_sum_tuple (__main__.TestSum)
#----------------------------------------------------------------------
# Traceback (most recent call last):
#  File "test_sum_unittest.py", line 9, in test_sum_tuple
#    self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")
# AssertionError: Should be 6
#
# ----------------------------------------------------------------------
# Ran 2 tests in 0.001s
#
# FAILED (failures=1)
```
`nose`peut être vu comme une extension de `unittetst`, qui offre de nombreuses options pour filtrer les tests à exécuter.

> **N.B.** Si `nose` est compatible avec Python 3.x, certains pligins peuvent ne pas l'être.
>
> [Documentation de nose](https://nose.readthedocs.io/en/latest/)

### Exécuter des tests avec `pytest`

`pytest` supporte l'exécution de de cas de tests `unittest`. Le véritable avantage de `pytest` vient de l'écriture de cas de tests spécificuaes à `pytest`. Ceux-ci sont écrits sous forme de fonctions dans des fichiers Python commençant par le préfixe `test_`.

`pytest`a d'autres grandes caractéristiques:
- support l'instruction `assert` au lieu des méthodes d'assertion
- prise en charge du filtrage des cas de test
- possibilité de réexécuter à partir du dernier test défaillant
- un écosystème de centaines de plugins pour étendre les fonctionnalités
- la découverte automatique des cas de tests
- affichage d'information détaillées en cas d'échec d'un test
- prise en charge de « _fixtures_ » (des données factices) pour diversifier des cas de tests traités

De fait, `pytest` s'est imposée comme la principale bibliothèque pour les test unitaires en Python. Écrire l'exemple `TestSum` pour `pytest` ressemble à cela:
```python
# test_sum.py
#
def test_sum():
    assert sum([1, 2, 3]) == 6, "Should be 6"

def test_sum_tuple():
    assert sum((1, 2, 2)) == 6, "Should be 6"
```

Vous n'avez plus besoin de `TestCase` et l'exécution des tests se fait avec la commande `pytest`.

> [Documentaion de pytest](https://docs.pytest.org/en/latest/)

### Écrire un premier test unitaire

Créez un nouveau dossier de projet et, à l'intérieur de cela, créez un nouveau dossier appelé my_sum. À l'intérieur my_sum, créer un fichier vide appelé __init__.py. Créer le __init__.pyfichier signifie que le my_sumLe dossier peut être importé en tant que module à partir du répertoire parent.
```
project/
│
└── my_sum/
    └── __init__.py
```

Ouvrez `my_sum/__init__.py` et créez une nouvelle fonction appelée `sum()`, qui prend une itérable (une liste, un tuple ou un ensemble) et ajoute les valeurs ensemble:
```python
def sum(arg):
    total = 0
    for val in arg:
        total += val
    return total
```

Cet exemple de code crée une variable appelée `total`, itère sur toutes les valeurs en arg, et les ajoute à total. Il retourne ensuite le résultat une fois que l'itérable a été épuisé.

Pour commencer à écrire des tests, vous pouvez simplement créer un fichier appelé `test_my_sum.py`, qui contiendra votre premier cas de test. Parce que le fichier devra être en mesure d'importer votre application pour pouvoir la tester, vous devrez le placer au-dessus du dossier du module, de sorte que votre arbre de répertoire ressemblera à ceci:
```
project/
│
├── my_sum/
│   └── __init__.py
|
└── test_my_sum.py
```

Vous constaterez que, à mesure que vous ajoutez de plus en plus de tests, e fichier unique deviendra difficile à maintenir, de sorte que l'on crée généralement un dossier appelé `tests/` et que l'on divise les tests en un certain nombre de catégories différentes.

#### Comment structurer un test Python

> Sans entrer dans les détails, rappelons qu'une bonne pratique de développement est de suivre la méthode **TDD** (pour Test Driven Design), qui consiste à considérer les tests comme une partie de la spécification de l'application, et donc de les écrire _prioritairement_, avant ou en même temps que le code lui-même.
>
> cf. [TDD](https://fr.wikipedia.org/wiki/Test_driven_development)

Avant de vous lancer dans l'écriture des tests, vous voudrez d’abord prendre quelques décisions:
- Que voulez-vous tester ?
- Vous écrivez un test unitaire ou un test d’intégration ?

Ensuite, la structure d'un test devrait suivre vaguement ce flux de travail:
- Créez vos entrées
- Exécuter le code en cours de test, en capturant la sortie
- Comparez la sortie avec un résultat attendu

Pour cette application, vous testez `sum()`. Il y a beaucoup de comportements dans sum()vous pouvez vérifier, tels que:
- Peut-il résumer une liste de nombres entiers (entiers)?
- Peut-il résumer un tuple ou un ensemble?
- Peut-il résumer des nombres à virgule flattante ?
- Que se passe-t-il lorsque vous lui fournissez une mauvaise valeur, comme un seul entier ou une chaîne de caractères?
- Que se passe-t-il quand l'une des valeurs est négative ?

Un fichier `test_sum.py` pour `pytest` resemblerait à cela :
```python
# test_sum.py
#
import pytest
from my_sum import sum

def test_array():
    assert sum([1, 2, 3]) == 6, "Should be 6"

def test_sum_tuple():
    assert sum((1, 2, 3)) == 6, "Should be 6"

def test_sum_set():
    assert sum({1, 2, 3}) == 6, "Should be 6"

def test_sum_float():
    assert sum((1, 2.0, 3)) == 6, "Should be 6"

def test_sum_unique():
    # assert sum(3) == 3, "Should be 6"

def test_sum_string():
    # assert sum([1, 'Oups', 3]) == ..., "Should be 6"

def test_sum_negative():
    assert sum([1,-5, 2]) == -2, "Should be -2"
```

Les cas de tests seront découverts automatiquement par `pytest`. Vous remarquerez certainement que certains cas de tests sopnt problématiques, car ce sont des cas d'erreurs de la fonction `sum`. Celle-ci échouera avant même que l'assertion de test puisse être évaluée.

#### Tester les exceptions

Pour capturer les cas d'erreurs `pytest` utilise des contextes Python. La fonction `sum()` n'admet pas un nombre unique comme argument. Pour pouvoir vérifier cela, il faut encapsuler son exécution dans un contexte spécial, qui donnera ceci :
```python
# ...
def test_sum_unique():
    with pytest.raises(TypeError) as e:
        sum(3)
    assert e.value ==  "'init' is not iterable", "sum ne devrait pas accepter un argument non itérable"
#...
```

## Tests pour des cadriciels web

Si vous écrivez des tests pour une application Web en utilisant l’un des frameworks populaires comme Django, Flask ou FastAPI, il existe des différences importantes dans la façon dont vous écrivez et exécutez les tests.

Pensez à tout le code que vous devez tester dans une application web :
- les routes,
- les vues
- les modèles,
- la logique métier
- le « _middleware_ »
- etc.

### Créer des tests unitaires pour FastAPI

#### Arborescence conseillée du projet

On admettra que l'arbirescence miniale d'un application avec FastAPI répond  au schéma ci-dessous :
```bash
app/
├── main.py           # Application FastAPI
├── routers/
│   └── items.py      # Exemple d’endpoint
├── services/
│   └── service.py      # Exemple d’endpoint
└── tests/
    └── test_main.py  # Tests unitaires
```

Le tests sont donc rassemblés dans un dossier spécifique. Éventuellement, comme nous l'avons dit plus haut, il peut exister des sous-dossiers pour des catégories de tests différentes.

#### Premier test unitaire avec pytest

Créez un fichier `app/tests/test_service.py` :
```python
from services.service import f

def test_service():
    result = f(1)
    assert result == true
```

On définit ici une fonction (fictive) `f`, qui répond à un besoin métier. Le test est très simple, puisqu'il s'agit ici d'exécuter cette fonction et de vérifier le résultat.

Une fois le test écrit, il ne reste qu'à lancer la revue des tests depuis la libne de commande :
Lancez les tests :
```bash
pytest -v
```

#### Premier test fonctionnel avec FastAPI

L'objectif des tests fonctionnels est de vérifier qu'une deamnde utilisateur est bien remplie.
Dans le cadre  d'une application web, cela nous oblige à prendre en compte une requête et à vérifier que la réponse est bien conforme à ce qui et demandé.

Dans un premier cas très simple, on veut tester, qu'un message de bienvenue est renvoyé à l'utilisateur, ou q'une valeur est bien incrémentée. Nous avons donc la base de code suivante :
Dans `app/main.py` :
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    item_id += 1
    return {"item_id": item_id}
```

Le test envisagé pourrait donc être écrit dans un fichier `app/tests/test_welcome.py` :
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur FastAPI!"}

def test_read_item():
    item_id = 42
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"item_id": 43}
```

#### Tester les dépendances avec `Depends`
FastAPI permet d’injecter des dépendances via la fonction `Depends`. On peut les tester en simulant des appels HTTP avec des valeurs précises.

Ajoutez dans `main.py` :
```python
from fastapi import Depends

def get_query(q: str = None):
    return q

@app.get("/search/")
def search(query: str = Depends(get_query)):
    return {"query": query}
```

Puis dans `test_main.py` :
```python
def test_search():
    query = "pytest"
    response = client.get(f"/search/?q={query}")
    assert response.status_code == 200
    assert response.json() == {"query": query}
```

### Réduire la répétition avec les fixtures

Lorsque vous avez besoin de réutiliser une configuration (exemple : un client FastAPI ou une base de données en mémoire), utilisez une « _fixture_ » (donnée factice) fournie par `pytest`.
Une donnée factice est définie par une fonction décorée par `@pytest.fixture`, comme on le voit ci-dessous :
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_client():
    return TestClient(app)

def test_root_fixture(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
```

On voit que la fonction génératrice est passée en argument de la fonction de test.

Les fixtures permettent de factoriser le code commun aux tests et de gérer facilement la configuration.
Mais elles permettent surtout de préparer des données consommées par les fonctions à tester

> [Documentation des fixtures de pytest](https://docs.pytest.org/en/6.2.x/fixture.html)

### Paramétrer plusieurs cas de test

Pour tester plusieurs entrées avec la même logique, utilisez `@pytest.mark.parametrize` :

```python
import pytest

@pytest.mark.parametrize("item_id", [1, 2, 3])
def test_multiple_items(test_client, item_id):
    response = test_client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json() == {"item_id": item_id}
```

### Aller plus loin : couverture de test

Pour mesurer la couverture, installez `pytest-cov` :
```bash
pip install pytest-cov
pytest --cov=app
```
Cela affiche le pourcentage de lignes de code couvertes par vos tests.

### Bonnes pratiques
1. **Fichier de configuration** : utilisez un `pytest.ini` pour définir les chemins de test et les options :
   ```ini
   [pytest]
   testpaths = tests
   addopts = -v --cov=app
   ```
2. **Convention de nommage** : nommez les fichiers et fonctions `test_*.py` pour être automatiquement détectés.
3. **Principe AAA** : Arrange, Act, Assert – préparez les données, exécutez la fonction, vérifiez le résultat.
4. **Isolation** : les tests doivent être indépendants les uns des autres.
5. **TDD (Test Driven Development)** : écrivez le test avant le code afin de guider l’implémentation.

## Tester dans différents contextes

Jusqu’à présent, vous avez testé une seule version de Python en utilisant un environnement virtuel avec un ensemble spécifique de dépendances. Vous voudrez peut-être vérifier que votre application fonctionne sur plusieurs versions de Python, ou plusieurs versions d'un paquet. Tox est une application qui automatise les tests dans plusieurs environnements.

### Installation de Tox

Tox est disponible sur PyPI sous forme de package pour installer via pip:
```bash
pip install tox
```
### Configuration de la tox pour vos dépendances

Tox est configuré via un fichier de configuration dans votre répertoire de projet. Le fichier de configuration Tox contient les éléments suivants:
- La commande à exécuter pour exécuter des tests
- Tous les paquets supplémentaires requis avant l'exécution
- Les versions Python cibles à tester

Au lieu d'avoir à apprendre la syntaxe de configuration Tox, vous pouvez prendre une longueur d'avance en exécutant l'application quickstart:
```bash
tox-quickstart
```
L'outil de configuration Tox vous posera ces questions et créera un fichier similaire à ce qui suit `tox.ini`:
```txt
[tox]
envlist = py27, py36

[testenv]
deps =

commands =
    python -m unittest discover
```

Avant de pouvoir exécuter Tox, cela nécessite que vous ayez un fichier `setup.py` dans votre dossier d'application contenant les étapes pour installer votre paquet. Alternativement, si votre projet n'est pas destiné à être distribué sur PyPI, vous pouvez ignorer cette exigence en ajoutant la ligne suivante dans le fichier `tox.ini` dans la section [tox]:
```txt
[tox]
envlist = py27, py36
skipsdist=True
```

Si vous ne créez pas un `setup.py`, et votre application a quelques dépendances de PyPI, vous devrez les spécifier sur un certain nombre de lignes dans la section [testenv]. Par exemple, FastAPI nécessiterait ce qui suit:

[testenv]
deps = fast-api

Une fois que vous avez terminé cette étape, vous êtes prêt à exécuter les tests.

Vous pouvez maintenant exécuter Tox, et il créera deux environnements virtuels: un pour Python 2.7 et un pour Python 3.6. Le répertoire Tox est appelé .tox/. Dans le répertoire .tox/, Tox va exécuter la commande `python -m unittest discover` dans chaque environnement virtuel. Vous pouvez exécuter ce processus en appelant Tox à la ligne de commande:
```bash
tox
```

Tox produira les résultats de vos tests par rapport à chaque environnement. La première fois qu'il fonctionne, Tox prend un peu de temps pour créer les environnements virtuels, mais une fois qu'il l'a fait, la deuxième exécution sera beaucoup plus rapide. La sortie de Tox est assez simple. Il crée un environnement pour chaque version, installe vos dépendances, puis exécute les commandes de test.

Il existe d'autres options de ligne de commande, par exemple :
```bash
# Exécutez un seul environnement, tel que Python 3.6:
tox -e py36

# Recréer les environnements virtuels, au cas où vos dépendances ont changé ou site-packages/ est corrompu:
tox -r

# Exécutez Tox avec une sortie moins verbeuse:
tox -q

# Exécuter Tox avec plus de sortie verbeuse:
tox -v
```

> [Documentation de Tox](https://tox.wiki/en/4.31.0/)
>
> [Introduction à Tox](https://blog.stephane-robert.info/docs/developper/programmation/python/tests/tox/)

## Intégration continue

Jusqu'à présent, vous avez exécuté les tests manuellement en exécutant une commande. Il existe certains outils pour exécuter des tests automatiquement lorsque vous effectuez des modifications et les engagez dans un référentiel de contrôle de source comme Git. Les outils de test automatisés sont souvent connus sous le nom d’outils CI/CD, ce qui signifie «Intégration continue/Déploiement continu». Ils peuvent exécuter vos tests, compiler et publier toutes les applications, et même les déployer en production.

La voie normale pour l'intégration continue dans Gitub passe par Github Actions, qui a remplacé Travis CI depuis quelques années.
Pour cela vous devrez créer un « _workflow_ » dans Github, via l'onglet **Actions**.
Le fichier de configuration `.github/workflows/test-fastapi.yml` pourrait ressembler à ceci :

```yaml
name: Test FastAPI app

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.6, 3.13]  # Liste des versions à tester
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests with pytest
        run: |
          pytest
```

### Points importants

- **Matrix Python Version** : La stratégie "matrix" exécute les mêmes étapes pour chacune des versions spécifiées (`3.6`, `3.13`), ce qui permet de vérifier la compatibilité FastAPI + pytest avec les deux interpréteurs.[4]
- **Pytest** : Pytest est utilisé pour le lancement des tests, adapté aux projets FastAPI même avec des tests asynchrones via des fixtures spécialisées.[1]
- **Installation des dépendances** : Installe toutes les dépendances à partir du fichier `requirements.txt` (vous pouvez adapter si vous utilisez Poetry ou un autre outil).[1]
- **Branches ciblées** : Les actions sont déclenchées sur `main` (modifiez si besoin).

> [Documentation des tests pour Python dans Github Actions](https://docs.github.com/fr/actions/tutorials/build-and-test-code/python)

## Introduire des linters dans votre application

Un « _linter_ » regarde votre code et le commente. Il peut vous donner des conseils sur les erreurs que vous avez commises, corriger les espaces et même prédire les bugs que vous avez peut-être introduits.

### flake8

Un linter populaire qui commente le style de votre code par rapport à la spécification PEP 8 est `flake8`.
```bash
pip install flake8
```

Vous pouvez alors exécuter `flake8` sur un seul fichier, un dossier ou un motif. Par exemple ;
```bash
flake8 test.py
# test.py:6:1: E302 expected 2 blank lines, found 1
# test.py:23:1: E305 expected 2 blank lines after class or function definition, found 1
# test.py:24:20: W292 no newline at end of file
```
Vous verrez une liste d'erreurs et d'avertissements pour votre code qui `flake8` a trouvés.

`flake8` est configurable sur la ligne de commande ou à l'intérieur d'un fichier de configuration dans votre projet. Si vous vouliez ignorer certaines règles, comme `E305` indiqué ci-dessus, vous pouvez les définir dans la configuration. flake8 inspectera un fichier `.flake8` dans le dossier du projet ou un fichier `setup.cfg`. Si vous avez décidé d'utiliser Tox, vous pouvez mettre une section `flake8` à l'intérieur `tox.ini`.
```txt
[flake8]
ignore = E305
exclude = .git,__pycache__
max-line-length = 90
```

Vous pouvez également fournir ces options sur la ligne de commande:
```bash
flake8 --ignore E305 --exclude .git,__pycache__ --max-line-length=90
```
> [Documentation de flake8](https://flake8.pycqa.org/en/latest/user/options.html)

### black

flake8 est un linter passif : il recommande des changements, mais vous devez aller changer le code. Une approche plus agressive est un **formateur de code**. Les formateurs de code modifieront automatiquement votre code pour répondre à une collection de pratiques de style et de mise en page.

`black` est un formateur impitoyable. Il n'a pas d'options de configuration, et il a un style très spécifique.
```bash
pip install black
```
Pour l'exécuter :
```bash
black test.py
```

> [Documentation de black](https://github.com/psf/black)

## Autres outils

### Tests de performance

Il existe plusieurs façons de comparer le code en Python. La bibliothèque standard fournit le module `timeit`, qui peut fonctionner plusieurs fois et vous donner la distribution. Cet exemple va s'exécuter test()100 fois et print()la sortie:

def test():
    # ... your code

if __name__ == "__main_":
    import timeit
    print(timeit.timeit("test()", setup="from __main__ import test", number=100))

Une autre option, si vous avez décidé d'utiliser `pytest`comme un lanceur de tests, est le plugin  `pytest-benchmark`. Ceci fournit un décorateur appelé `benchmark`. Vous pouvez ainsi décorer toute fonction pour obtenir les indcations de performance du code.
```bash
install pytest-benchmark
```
Puis :
```python
def test_my_function(benchmark):
    result = benchmark(test)
```

> [Documentation de pytest-benchmark](https://pytest-benchmark.readthedocs.io/en/latest/)

## Tests de sécurité de votre application

Un autre test que vous voudrez sans doute exécuter sur votre application est la traque les erreurs de sécurité et des vulnérabilités courantes. Vous pouvez installer `bandit` de PyPI en utilisant pip:
```bash
pip install bandit
```
Vous pouvez ensuite passer le nom de votre module d'application avec le drapeau `-r`, et il vous donnera un résumé:
```bash
bandit -r my_sum

# [main]  INFO    profile include tests: None
# [main]  INFO    profile exclude tests: None
# [main]  INFO    cli include tests: None
# [main]  INFO    cli exclude tests: None
# [main]  INFO    running on Python 3.5.2
# Run started:2018-10-08 00:35:02.669550
#
# Test results:
#         No issues identified.
#
# Code scanned:
#         Total lines of code: 5
#         Total lines skipped (#nosec): 0
#
# Run metrics:
#         Total issues (by severity):
#                 Undefined: 0.0
#                 Low: 0.0
#                 Medium: 0.0
#                 High: 0.0
#         Total issues (by confidence):
#                 Undefined: 0.0
#                 Low: 0.0
#                 Medium: 0.0
#                 High: 0.0
# Files skipped (0):
```
Comme pour flake8, les règles de `bandit` sont facilement configurables, et s'il y en a qui vous souhaitez ignorer, vous pouvez ajouter la section suivante à votre fichier `setup.cfg` avec les options:

```txt
[bandit]
exclude: /test
tests: B101,B102,B301
```

> [Documentation de bandit](https://github.com/PyCQA/bandit)
