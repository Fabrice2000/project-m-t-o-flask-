# Typer les programmes Python

## Introduction
Tous les langages de programmation comprennent une sorte de système de typage qui formalise les catégories d'objets avec lesquels il peut fonctionner et comment ces catégories sont traitées. Par exemple, un système de type peut définir un type numérique, avec 42 comme un exemple d'un objet de ce type.

### Le typage dynamique
Python est un langage dynamiquement typé dynamiquement. Cela signifie :
- que l'interpréteur Python vérifie uniquement au fur et à mesure que le code s'exécute
- que le type d'une variable est autorisé à changer au cours de sa durée de vie.

Les exemples factices suivants démontrent que Python a un typage dynamique:
```python
>>> if False:
...     1 + "two"  # This line never runs, so no TypeError is raised
... else:
...     1 + 2
...
3

>>> 1 + "two"  # Now this is type checked, and a TypeError is raised
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

Dans le premier exemple, la branche 1 + "two" ne peut jamais fonctionner ; il n’est donc jamais vérifié. Le deuxième exemple montre que lorsque 1 + "two"est évalué qu'il soulève un `TypeError` puisque vous ne pouvez pas ajouter un entier et une chaîne en Python.

Ensuite, les variables peuvent changer de type:
```python
>>> thing = "Hello"
>>> type(thing)
<class 'str'>

>>> thing = 28.1
>>> type(thing)
<class 'float'>
```

`type()` retourne le type d'un objet. Ces exemples confirment que le type de `thing` est autorisé à changer, et Python en déduit correctement le type au fur et à mesure qu'il change.

### Typage statique

Le contraire du typage dynamique est le **typage statique**. Les vérifications sont alors effectuées sans exécuter le programme. Dans la plupart des langages statiquement typés, par exemple C et Java, cela se fait lorsque le programme est compilé.

> **N.B.** Certains langages comme **PHP** sont dans une situation intermédiaire, car ils sont compilés « _à la volée_ », c'est-à-dire juste au moment de l'exécution.

Avec le typage statique, les variables ne sont généralement pas autorisées à changer de type, bien que des mécanismes de transtypage (ou « _casting_ » en anglais) d'une variable à un type différent puissent exister.

Regardons un exemple rapide d'un langage statiquement typé. Considérez l'extrait Java suivant:
```java
String thing;
thing = "Hello";
```

Python restera toujours un langage de type dynamique. Cependant, **PEP 484** a introduit des indices de type, qui permettent également de faire une vérification statique de type de code Python.

Contrairement à la façon dont les types fonctionnent dans la plupart des autres langages statiquement typés, les indices de type en eux-mêmes ne font pas en sorte que Python applique les types. Comme son nom l'indique, les indices de type suggèrent simplement des types. Il existe d’autres outils, que vous verrez plus tard, qui effectuent la vérification statique de type en utilisant des indices de type.

### Duck Typing

Un autre terme qui est souvent utilisé lorsque l'on parle de Python est le « _duck typing_ ». Ce surnom vient de la phrase « _s’il marche comme un canard et qu’il cancane comme un canard, alors il doit être un canard_ » (ou l’une de ses variations).

Le « _duck typing_ » est un concept lié à au typage dynamique, où le type (ou la classe) d'un objet est moins important que les méthodes qu'il définit. En utilisant cette solution, vous ne vérifiez pas du tout les types. Au lieu de cela, vous vérifiez la présence d'une méthode ou d'un attribut donné.

À titre d'exemple, vous pouvez appeler len()sur n'importe quel objet Python qui définit un .__len__()méthode:
```python
>>> class TheHobbit:
...     def __len__(self):
...         return 95022
...
>>> the_hobbit = TheHobbit()
>>> len(the_hobbit)
95022
```

Notez que l'appel à `len()` donne la valeur de retour de la méthode .__len__(). En fait, la mise en œuvre de `len()` est essentiellement équivalent aux éléments suivants:
```python
def len(obj):
    return obj.__len__()
```

Pour appeler len(obj), la seule vraie contrainte sur objest qu'elle doit définir une méthode `__len__()`. Sinon, l'objet peut être de types aussi différents que str, list, dict, ou TheHobbit.

Le « _duck typing_ » est quelque peu prise en charge lors de la vérification statique de type de code Python, en utilisant le sous-typage structurel

## Types !

Commencçons par un exemple. La fonction suivante transforme une chaîne de texte en titre en ajoutant une capitalisation appropriée et une ligne décorative:
```python
def headline(text, align=True):
    if align:
        return f"{text.title()}\n{'-' * len(text)}"
    else:
        return f" {text.title()} ".center(50, "o")
```

Par défaut, la fonction renvoie le titre gauche aligné sur un soulignement.
En définissant le paramètre align à False, vous pouvez alternativement avoir le titre être centré avec une ligne environnante de o:
```python
>>> print(headline("python type checking"))
Python Type Checking
--------------------

>>> print(headline("python type checking", align=False))
oooooooooooooo Python Type Checking oooooooooooooo
```

Pour ajouter des informations sur les types à la fonction, il vous suffit d'annoter ses arguments et de retourner la valeur comme suit:
```python
def headline(text: str, align: bool = True) -> str:
    ...
```
L'indication `: str` dit que le textargument devrait être de type `str`. De même, l'arguembnt optionnel align devrait avoir pour type `bool` (avec la valeur par défaut `True`). Enfin, `-> str` spécifie que `headline()` retournera une chaîne de caractères.

En termes de style, PEP 8 recommande ce qui suit:
> - Utilisez des règles normales pour les virgules, c'est-à-dire pas d'espace avant et un espace après une virgule : `text: str`.
> - Utilisez des espaces autour du signe `=` lors de la combinaison d'une annotation d'argument avec une valeur par défaut : `align: bool = True`.
> - Utilisez des espaces autour de la flèche `-> : ` -> str`.

Attention, ajouter des indices de type n'a aucun effet lors de l'exécution Par exemple :
```python
>>> print(headline("python type checking", align="left"))
Python Type Checking
--------------------
```

Pour cela, il faut utiliser un vérificateur de types statique. Vous avez peut-être déjà un tel vérificateur de type intégré à votre éditeur. Par exemple PyCharm vous donne immédiatement un avertissement.

L'outil le plus courant pour faire cela est le paquet `mypy`.
Si vous n’avez pas déjà `mypy` sur votre système, vous pouvez l’installer en utilisant pip:
```bash
pip install mypy
```

Placez le code suivant dans un fichier appelé headlines.py:
```python
# headlines.py
def headline(text: str, align: bool = True) -> str:
    if align:
        return f"{text.title()}\n{'-' * len(text)}"
    else:
        return f" {text.title()} ".center(50, "o")

print(headline("python type checking"))

print(headline("use mypy", align="center"))
```
C'est essentiellement le même code que vous avez vu plus tôt: la définition de headline()et deux exemples qui l'utilisent.

Maintenant, exécutez `mypy` sur ce code:
```bash
mypy headlines.py
headlines.py:10: error: Argument "align" to "headline" has incompatible
                        type "str"; expected "bool"
```

Voilà !

Au passage, renommer le paramètre `align` en `centered` serait préférable, en termes de documentation du code.
```python
# headlines.py
def headline(text: str, centered: bool = False) -> str:
    if not centered:
        return f"{text.title()}\n{'-' * len(text)}"
    else:
        return f" {text.title()} ".center(50, "o")

print(headline("python type checking"))

print(headline("use mypy", centered=True))
```

## Pros and Cons

La section précédente vous a donné un petit avant-goût de la vérification de type en Python. Vous avez également vu un exemple de l'un des avantages de l'ajout de types à votre code: les conseils de type aident à détecter certaines erreurs. D'autres avantages comprennent:
- Les conseils de type aident à documenter votre code. Traditionnellement, vous utiliseriez des docstrings si vous vouliez documenter les types attendus d’arguments d’une fonction. Cela fonctionne, mais comme il n’y a pas de norme pour les docstrings malgré PEP 257, ils ne peuvent pas être facilement utilisés pour les vérifications automatiques.)
- Les indices de type améliorent les IDE et les linters. Ils rendent beaucoup plus facile de raisonner statiquement votre code. Cela permet aux IDE d'offrir une meilleure achèvement de code et des fonctionnalités similaires. Avec l'annotation de type, PyCharm sait que textest une chaîne, et peut donner des suggestions spécifiques basées sur ceci:
- Les indices de type vous aident à construire et à maintenir une architecture plus propre. L'acte d'écrire des indices vous oblige à penser aux types de votre programme. Alors que la nature dynamique de Python est l'un de ses grands atouts, être conscient de compter sur la frappe de canard, les méthodes surchargées ou plusieurs types de retour est une bonne chose.

Bien sûr, la vérification statique de type a aussi quelques inconvénients que vous devriez considérer:
- Les indices de type prennent du temps et des efforts de développement pour ajouter. Même si cela paie probablement en passant moins de temps à déboguer, vous passerez plus de temps à entrer du code.
- Les indices de type fonctionnent mieux dans les versions récentes de Pythons. Les annotations ont été introduites dans Python 3.0, et il est possible d'utiliser des commentaires de type dans Python 2.7. Néanmoins, des améliorations telles que des annotations de variables et une évaluation reportée des indices de type signifient que vous aurez une meilleure expérience de faire des vérifications de type en utilisant Python 3.6 ou même Python 3.7.
- Les indices de type introduisent une légère pénalité dans le temps de démarrage. Si vous avez besoin d'utiliser le typingmodule le temps d'importation peut être important, surtout dans les scripts courts.

Alors, devriez-vous utiliser la vérification de type statique dans votre propre code ? Ce n’est pas une question de tout ou rien. Heureusement, Python supporte le concept de typage progressif. Cela signifie que vous pouvez introduire progressivement des types dans votre code. Le code sans indices de type sera ignoré par le vérificateur de type statique. Par conséquent, vous pouvez commencer à ajouter des types à des composants critiques, et continuer tant qu'il vous ajoute de la valeur.

En regardant les listes ci-dessus de avantages et de inconvénients, vous remarquerez que l’ajout de types n’aura aucun effet sur votre programme en cours d’exécution ou les utilisateurs de votre programme. La vérification des types est destinée à rendre votre vie de développeur meilleure et plus pratique.

Quelques règles de base sur l'ajout de types à votre projet sont:
- Si vous commencez tout juste à apprendre Python, vous pouvez attendre en toute sécurité avec des indices de type jusqu'à ce que vous ayez plus d'expérience.
- Les indices de type ajoutent peu de valeur dans les courts scripts de jet.
- Dans les bibliothèques qui seront utilisées par d'autres, en particulier celles publiées sur PyPI, les indices de type ajoutent beaucoup de valeur. D'autres codes utilisant vos bibliothèques ont besoin de ces indices de type pour être correctement vérifiés. Pour des exemples de projets utilisant des indices de type, voir cursive_re, black, notre propre lecteur Python réel, et Mypy lui-même.
- Dans les projets plus importants, les conseils de type vous aident à comprendre comment les types circulent dans votre code, et sont fortement recommandés. Encore plus dans les projets où vous coopérez avec les autres.

Dans son excellent article « _The State of Type Hints_ », Python Bernát Gábor recommande que « les indices de type soient utilisés chaque fois que des tests unitaires valent la peine d’être écrits ». En effet, les indices de type jouent un rôle similaire à celui des tests dans votre code : ils vous aident en tant que développeur à écrire un meilleur code.

## Annotations

Les annotations ont été introduites dans Python 3.0, à l'origine sans but spécifique. Ils étaient simplement un moyen d'associer des expressions arbitraires pour fonctionner des arguments et retourner des valeurs.

Des années plus tard, **PEP 484** a défini comment ajouter des indices de type à votre code Python, basé sur le travail que **Jukka Lehtosalo** avait fait sur son projet de doctorat, `mypy`. La principale façon d'ajouter des indices de type est d'utiliser des annotations. Comme la vérification de type devient de plus en plus courante, cela signifie également que les annotations doivent principalement être réservées aux indices de type.

### Annotations de fonctions

Pour les fonctions, vous pouvez annoter les arguments et la valeur de retour. Ceci est fait comme suit:
```python
def func(arg: arg_type, optarg: arg_type = default) -> return_type:
    ...
```
Pour les arguments, la syntaxe est `argument: annotation`, alors que le type de retour est annoté en utilisant `-> annotation`.

> Notez que l'annotation doit être une expression Python valide.

L'exemple simple suivant ajoute des annotations à une fonction qui calcule la circonférence d'un cercle:
```python
import math

def circumference(radius: float) -> float:
    return 2 * math.pi * radius
```

Lors de l'exécution du code, vous pouvez également inspecter les annotations. Ils sont stockés dans un attribut spécial `.__annotations__` de la fonction:
```python
>>> circumference(1.23)
7.728317927830891

>>> circumference.__annotations__
{'radius': <class 'float'>, 'return': <class 'float'>}
```

Parfois, vous pourriez être trompé par la façon dont `mypy` interprète vos indices de type. Pour ces cas, il y a des expressions mypy spéciales, comme `reveal_type()`et `reveal_locals()`. Vous pouvez les ajouter à votre code avant d'exécuter mypy, et mypy signalera avec diligence les types qu'il a déduits. Par exemple, enregistrez le code suivant pour reveal.py:# reveal.py
```python
import math

reveal_type(math.pi)
radius = 1
circumference = 2 * math.pi * radius
reveal_locals()
```
Ensuite, exécutez ce code à travers mypy:
```bash
mypy reveal.py
reveal.py:4: error: Revealed type is 'builtins.float'

reveal.py:8: error: Revealed local types are:
reveal.py:8: error: circumference: builtins.float
reveal.py:8: error: radius: builtins.int
```
Même sans annotations, mypy a correctement déduit les types de la constante `math.pi`, ainsi que nos variables locales `radius` et `circumference`.

> Remarque: Les expressions de révélation sont uniquement conçues comme un outil vous aidant à ajouter des types et à déboguer vos indices de type. Si vous essayez de lancer le script le reveal.py, il va se bloquer avec un `NameError` car `reveal_type()` n'est pas une fonction connue de l'interpréteur Python.

### Annotations variables

Dans la définition de `circumference()` dans la section précédente, vous n'avez annoté que les arguments et la valeur de retour. Vous n'avez pas ajouté d'annotations à l'intérieur du corps de la fonction. Le plus souvent, cela suffit.

Cependant, parfois, le vérificateur de type a besoin d'aide pour déterminer les types de variables aussi bien. Les annotations variables ont été définies dans PEP 526 et introduites en Python 3.6. La syntaxe est la même que pour les annotations d'argument de fonction:
```python
pi: float = 3.142

def circumference(radius: float) -> float:
    return 2 * pi * radius
```
La variable `pi` a été annotée avec le type `float`.

> Remarque: Les vérificateurs de type statique sont plus que capables de comprendre cela 3.142 est un nombre à virgule flottante, donc dans cet exemple l'annotation de `pi` n'est pas nécessaire. Lorsque vous en apprendrez plus sur le système de type Python, vous verrez des exemples plus pertinents d’annotations de variables.

Les annotations de variables sont stockées dans le niveau d'un dictionnaire `__annotations__` dans le module :
```python
>>> circumference(1)
6.284

>>> __annotations__
{'pi': <class 'float'>}
```

Vous êtes autorisé à annoter une variable sans lui donner de valeur. Cela ajoute l'annotation à la __annotations__dictionnaire, alors que la variable reste indéfinie:
```python
>>> nothing: str
>>> nothing
NameError: name 'nothing' is not defined

>>> __annotations__
{'nothing': <class 'str'>}
```

Puisqu'aucune valeur n'a été attribuée à `nothing`, le nom lui-même n'est pas encore défini.

### Commentaires de typage

Comme mentionné, des annotations ont été introduites dans Python 3 et elles n’ont pas été rétroportées à Python 2. Cela signifie que si vous écrivez du code qui doit prendre en charge Python hérité, vous ne pouvez pas utiliser d’annotations.

Au lieu de cela, vous pouvez utiliser des commentaires de type. Ce sont des commentaires spécialement formatés qui peuvent être utilisés pour ajouter des indices de type compatibles avec le code plus ancien. Pour ajouter des commentaires de type à une fonction, vous faites quelque chose comme ceci:
```python
import math

def circumference(radius):
    # type: (float) -> float
    return 2 * math.pi * radius
```

Les commentaires de type ne sont que des commentaires, ils peuvent donc être utilisés dans n'importe quelle version de Python.

Les commentaires de type sont traités directement par le vérificateur de type, de sorte que ces types ne sont pas disponibles dans le __annotations__dictionnaire:
```python
>>> circumference.__annotations__
{}
```

Un commentaire de type doit commencer par le littéral `type:`, et être sur la même ou la ligne suivante comme la définition de la fonction. Si vous voulez annoter une fonction avec plusieurs arguments, vous écrivez chaque type séparé par comma:
```python
def headline(text, width=80, fill_char="-"):
    # type: (str, int, str) -> str
    return f" {text.title()} ".center(width, fill_char)

print(headline("type comments work", width=40))
```
Vous êtes également autorisé à écrire chaque argument sur une ligne séparée avec sa propre annotation:
```python
# headlines.py
def headline(
    text,           # type: str
    width=80,       # type: int
    fill_char="-",  # type: str
):                  # type: (...) -> str
    return f" {text.title()} ".center(width, fill_char)

print(headline("type comments work", width=40))
```

Exécutez l'exemple à travers Python et mypy:
```bash
python headlines.py
---------- Type Comments Work ----------

mypy headlines.py
Success: no issues found in 1 source file
```
Si vous avez des erreurs, par exemple si vous avez appelé headline()avec width="full"sur la ligne 10, mypy vous dira:
```bash
$ mypy headline.py
headline.py:10: error: Argument "width" to "headline" has incompatible
                       type "str"; expected "int"
```

De la même manière, on peut ajouter de commentaires de typage sur les varaibles =
```python
pi = 3.142  # type: float
```

## Playing With Python Types, Part 1

Jusqu’à présent, vous n’avez utilisé que des types de base comme str, float, et booldans votre type de conseils. Le système de type Python est assez puissant et prend en charge de nombreux types plus complexes. Ceci est nécessaire car il doit être capable de modéliser raisonnablement la nature de la typage dynamique de canard de Python.

### Example: A Deck of Cards

L'exemple suivant montre la mise en oeuvre d'un jeu de cartes ordinaire (français):
```python
# game.py
import random

SUITS = "♠ ♡ ♢ ♣".split()
RANKS = "2 3 4 5 6 7 8 9 10 J Q K A".split()

def create_deck(shuffle=False):
    """Create a new deck of 52 cards"""
    deck = [(s, r) for r in RANKS for s in SUITS]
    if shuffle:
        random.shuffle(deck)
    return deck

def deal_hands(deck):
    """Deal the cards in the deck into four hands"""
    return (deck[0::4], deck[1::4], deck[2::4], deck[3::4])

def play():
    """Play a 4-player card game"""
    deck = create_deck(shuffle=True)
    names = "P1 P2 P3 P4".split()
    hands = {n: h for n, h in zip(names, deal_hands(deck))}
    for name, cards in hands.items():
        card_str = " ".join(f"{s}{r}" for (s, r) in cards)
        print(f"{name}: {card_str}")

if __name__ == "__main__":
    play()
```

Ce qui suit est une sortie typique:
```bash
$ python game.py
P4: ♣9 ♢9 ♡2 ♢7 ♡7 ♣A ♠6 ♡K ♡5 ♢6 ♢3 ♣3 ♣Q
P1: ♡A ♠2 ♠10 ♢J ♣10 ♣4 ♠5 ♡Q ♢5 ♣6 ♠A ♣5 ♢4
P2: ♢2 ♠7 ♡8 ♢K ♠3 ♡3 ♣K ♠J ♢A ♣7 ♡6 ♡10 ♠K
P3: ♣2 ♣8 ♠8 ♣J ♢Q ♡9 ♡J ♠4 ♢8 ♢10 ♠9 ♡4 ♠Q
```

### Séquences et mappings

Ajoutons des indices de type à notre jeu de cartes. En d’autres termes, annotons les fonctions `create_deck()`, `deal_hands()`, et `play()`. Le premier défi est que vous devez annoter les types composites comme la liste utilisée pour représenter le jeu de cartes et les tuples utilisés pour représenter les cartes elles-mêmes.

Avec des types simples comme str, float, et bool, l'ajout d'indices de type est aussi facile que d'utiliser le type lui-même:
```python
>>> name: str = "Guido"
>>> pi: float = 3.142
>>> centered: bool = False
```
Avec les types composites, vous êtes autorisé à faire la même chose:
```python
>>> names: list = ["Guido", "Jukka", "Ivan"]
>>> version: tuple = (3, 7, 1)
>>> options: dict = {"centered": False, "capitalize": True}
```

Cependant, cela ne raconte pas vraiment l'histoire complète. Quels seront les types de names[2], version[0], et options["centered"]? Dans ce cas concret, vous pouvez voir qu'ils sont str, int, et bool, respectivement. Cependant, le type leur suggère de ne donner aucune information à ce sujet.

Au lieu de cela, vous devez utiliser les types spéciaux définis dans le module `typing`. Ces types ajoutent de la syntaxe pour spécifier les types d'éléments de types composites. C'est ce que l'on appelle souvent des « _génériques_ ». Vous pouvez ainsi écrire :
```python
>>> from typing import Dict, List, Tuple

>>> names: List[str] = ["Guido", "Jukka", "Ivan"]
>>> version: Tuple[int, int, int] = (3, 7, 1)
>>> options: Dict[str, bool] = {"centered": False, "capitalize": True}
```

Notez que chacun de ces types commence par une majuscule et qu'ils utilisent tous des crochets pour définir les types d'articles:
- names est une liste de chaînes
- versionest un triplet composé de trois entiers
- options est un dictionnaire mappant des chaînes à des valeurs booléennes

Le module `typing` contient de nombreux autres types composites, y compris Counter, Deque, FrozenSet, NamedTuple, et Set. En outre, le module comprend d’autres types de types que vous verrez dans les sections ultérieures.

Revenons au jeu de cartes. Une carte est représentée par un tuple de deux cordes. Vous pouvez écrire ceci comme Tuple[str, str], donc le type de jeu de cartes devient `List[Tuple[str, str]]`. Vous pouvez donc annoter `create_deck()` comme suit:
```python
def create_deck(shuffle: bool = False) -> List[Tuple[str, str]]:
    """Create a new deck of 52 cards"""
    deck = [(s, r) for r in RANKS for s in SUITS]
    if shuffle:
        random.shuffle(deck)
    return deck
```

En plus de la valeur de retour, vous avez également ajouté le type bool à l'argument optionnel shuffle.

> Remarque: Les tuples et les listes sont annotés différemment.
>
> Un tuple est une séquence immuable, et se compose généralement d'un nombre fixe d'éléments éventuellement différents. Par exemple, nous représentons une carte comme un tuple de costume et de rang. En général, vous écrivez Tuple[t_1, t_2, ..., t_n]pour un n-tuple.
>
> Une liste est une séquence mutable et se compose généralement d'un nombre inconnu d'éléments du même type, par exemple une liste de cartes. Peu importe le nombre d'éléments dans la liste, il n'y a qu'un seul type dans l'annotation: List[t].

Dans de nombreux cas, vos fonctions s'attendront à une sorte de séquence, et ne vous souciez pas vraiment de savoir s'il s'agit d'une liste ou d'un tuple. Dans ces cas, vous devez utiliser `typing.Sequence` lors de la déclaration de l'argument de la fonction:
```python
from typing import List, Sequence

def square(elems: Sequence[float]) -> List[float]:
    return [x**2 for x in elems]
```

Voici un exemple d'utilisation du « _ducj tyuping_ ». Une Sequence est tout ce qui supporte `len()` et `__getitem__()`, indépendante de son type réel.

### Alias de type

es indices de type peuvent devenir assez obliques lorsque vous travaillez avec des types imbriqués comme le jeu de cartes. Vous devrez peut-être regarder List[Tuple[str, str]] deux fois avant de déterminer qu'il correspond à notre représentation d'un jeu de cartes.

Maintenant, réfléchissez à la façon dont vous annoteriez deal_hands():
```python
def deal_hands(
    deck: List[Tuple[str, str]]
) -> Tuple[
    List[Tuple[str, str]],
    List[Tuple[str, str]],
    List[Tuple[str, str]],
    List[Tuple[str, str]],
]:
    """Deal the cards in the deck into four hands"""

    return (deck[0::4], deck[1::4], deck[2::4], deck[3::4])
```

Oups !

Rappelez-vous que les annotations de type sont des expressions Python régulières. Cela signifie que vous pouvez définir vos propres alias de type en les attribuant à de nouvelles variables. Vous pouvez par exemple créer Card et DeckType d'alias:
```python
from typing import List, Tuple

Card = Tuple[str, str]
Deck = List[Card]
```

Card peut maintenant être utilisé dans des indices de type ou dans la définition de nouveaux alias de type, comme Deck dans l'exemple ci-dessus.
```python
def deal_hands(deck: Deck) -> Tuple[Deck, Deck, Deck, Deck]:
    """Deal the cards in the deck into four hands"""
    return (deck[0::4], deck[1::4], deck[2::4], deck[3::4])
```

Les alias de type sont parfaits pour rendre votre code et son intention plus claires. Dans le même temps, ces alias peuvent être inspectés pour voir ce qu'ils représentent:
```python
>>> from typing import List, Tuple
>>> Card = Tuple[str, str]
>>> Deck = List[Card]

>>> Deck
typing.List[typing.Tuple[str, str]]
```
Notez que lors de l'impression Deck, cela montre qu’il s’agit d’un alias pour une liste de 2-tuples de chaînes.

### Fonctions sans valeur de retour

Vous pouvez savoir que les fonctions sans retour explicite reviennent encore None:
```python
>>> def play(player_name):
...     print(f"{player_name} plays")
...

>>> ret_val = play("Jacob")
Jacob plays

>>> print(ret_val)
None
```

Bien que de telles fonctions renvoient techniquement quelque chose, cette valeur de retour n'est pas utile. Vous devriez ajouter des indices de type en disant autant en utilisant Noneaussi comme le type de retour:
```python
# play.py
def play(player_name: str) -> None:
    print(f"{player_name} plays")

ret_val = play("Filip")
```

Les annotations aident à repérer certains bogues subtils où vous essayez d'utiliser une valeur de retour vide de sens. Mypy vous donnera un avertissement utile:
```bash
mypy play.py
play.py:6: error: "play" does not return a value
```

Notez qu'être explicite sur une fonction ne retournant rien est différent de ne pas ajouter un indice de type sur la valeur de retour:
```python
# play.py

def play(player_name: str):
    print(f"{player_name} plays")

ret_val = play("Henrik")
```

Dans ce dernier cas, mypy n'a aucune information sur la valeur de retour donc il ne générera aucun avertissement:
```bash
mypy play.py
Success: no issues found in 1 source file
```

Comme cas plus exotique, notez que vous pouvez également annoter des fonctions qui ne sont jamais censées revenir normalement. Ceci est fait en utilisant NoReturn:
```python
from typing import NoReturn

def black_hole() -> NoReturn:
    raise Exception("There is no going back ...")
```

`black_hole()`  lève toujours une exception, elle ne peut jamais terminer correctement.

### Exemple: Jouer aux cartes

Revenons à notre exemple de jeu de cartes. Dans cette deuxième version du jeu, nous proposons une main de cartes à chaque joueur comme avant. Ensuite, un joueur de départ est choisi et les joueurs jouent à tour de rôle leurs cartes. Il n'y a pas vraiment de règles dans le jeu cependant, donc les joueurs vont juste jouer des cartes aléatoires:
```python
# game.py
import random
from typing import List, Tuple

SUITS = "♠ ♡ ♢ ♣".split()
RANKS = "2 3 4 5 6 7 8 9 10 J Q K A".split()

Card = Tuple[str, str]
Deck = List[Card]

def create_deck(shuffle: bool = False) -> Deck:
    """Create a new deck of 52 cards"""
    deck = [(s, r) for r in RANKS for s in SUITS]
    if shuffle:
        random.shuffle(deck)
    return deck

def deal_hands(deck: Deck) -> Tuple[Deck, Deck, Deck, Deck]:
    """Deal the cards in the deck into four hands"""
    return (deck[0::4], deck[1::4], deck[2::4], deck[3::4])

def choose(items):
    """Choose and return a random item"""
    return random.choice(items)

def player_order(names, start=None):
    """Rotate player order so that start goes first"""
    if start is None:
        start = choose(names)
    start_idx = names.index(start)
    return names[start_idx:] + names[:start_idx]

def play() -> None:
    """Play a 4-player card game"""
    deck = create_deck(shuffle=True)
    names = "P1 P2 P3 P4".split()
    hands = {n: h for n, h in zip(names, deal_hands(deck))}
    start_player = choose(names)
    turn_order = player_order(names, start=start_player)

    # Randomly play cards from each player's hand until empty
    while hands[start_player]:
        for name in turn_order:
            card = choose(hands[name])
            hands[name].remove(card)
            print(f"{name}: {card[0] + card[1]:<3}  ", end="")
        print()

if __name__ == "__main__":
    play()
```

Notez qu’en plus de changer play(), nous avons ajouté deux nouvelles fonctions qui nécessitent des indices de type: choose()et player_order(). Avant de discuter de la façon dont nous allons ajouter y des indices de type, voici un exemple de sortie de l'exécution du jeu:

$ python game.py
P3: ♢10  P4: ♣4   P1: ♡8   P2: ♡Q
P3: ♣8   P4: ♠6   P1: ♠5   P2: ♡K
P3: ♢9   P4: ♡J   P1: ♣A   P2: ♡A
P3: ♠Q   P4: ♠3   P1: ♠7   P2: ♠A
P3: ♡4   P4: ♡6   P1: ♣2   P2: ♠K
P3: ♣K   P4: ♣7   P1: ♡7   P2: ♠2
P3: ♣10  P4: ♠4   P1: ♢5   P2: ♡3
P3: ♣Q   P4: ♢K   P1: ♣J   P2: ♡9
P3: ♢2   P4: ♢4   P1: ♠9   P2: ♠10
P3: ♢A   P4: ♡5   P1: ♠J   P2: ♢Q
P3: ♠8   P4: ♢7   P1: ♢3   P2: ♢J
P3: ♣3   P4: ♡10  P1: ♣9   P2: ♡2
P3: ♢6   P4: ♣6   P1: ♣5   P2: ♢8


### Le type AnyType

choose()fonctionne pour les listes de noms et de listes de cartes (et toute autre séquence d'ailleurs). Une façon d'ajouter des indices de type pour cela serait le suivant:
```python
import random
from typing import Any, Sequence

def choose(items: Sequence[Any]) -> Any:
    return random.choice(items)
```

Cela signifie plus ou moins ce qu'il dit: itemsest une séquence qui peut contenir des éléments de tout type et choose()retournera un tel article de tout type. Malheureusement, ce n'est pas si utile. Examinez l'exemple suivant:
```python
# choose.py
import random
from typing import Any, Sequence

def choose(items: Sequence[Any]) -> Any:
    return random.choice(items)

names = ["Guido", "Jukka", "Ivan"]
reveal_type(names)
name = choose(names)
reveal_type(name)
```

Alors que mypy en déduit correctement que names est une liste de chaînes, cette information est perdue après l'appel à choose(), en raison de l'utilisation de `AnyType`:
```bash
mypy choose.py
choose.py:10: error: Revealed type is 'builtins.list[builtins.str*]'
choose.py:13: error: Revealed type is 'Any'
```

Vous verrez bientôt une meilleure façon.

## une brève théorie des types

Cette partie est principalement un guide pratique et nous allons seulement effleurer la surface de la théorie qui sous-tend les conseils de type Python. Pour plus de détails, le **PEP 483** est un bon point de départ.

### Sous-types

Un concept important est celui des sous-types. Formellement, nous disons qu'un type T est un sous-type de U si les deux conditions suivantes sont réunies:
- Chaque valeur de T est également dans l'ensemble des valeurs de U .
- Toutes les fonctions de U sont également dans l'ensemble des fonctions de T.

Ces deux conditions garantissent que même si T est différent de U, toute variable de type T peut toujours prétendre apartenir à U.

Pour un exemple concret, considérer T = bool et U = int. Le type bool ne prend que deux valeurs. Généralement, ceux-ci sont notés True et False, mais ces noms ne sont que des alias pour les valeurs entières 1et 0, respectivement:
```python
>>> int(False)
0
>>> int(True)
1
>>> True + True
2
>>> issubclass(bool, int)
True
```

Comme 0 et 1 sont les deux entiers, la première condition tient. Vous pouvez voir ci-dessus que les booléens peuvent être ajoutés ensemble, mais ils peuvent également faire tout ce que les entiers peuvent faire. C'est la deuxième condition ci-dessus. Autrement dit, boolest un sous-type de int.

L'importance des sous-types est qu'un sous-type peut toujours prétendre être son supertype. Par exemple, le type de code suivant est correct:
```python
def double(number: int) -> int:
    return number * 2

print(double(True))  # Passing in bool instead of int
```

Les sous-types sont quelque peu liés aux sous-classes. En effet toutes les sous-classes correspondent à des sous-types, et bool est un sous-type de int parce que bool est une sous-classe de int. Cependant, il existe également des sous-types qui ne correspondent pas à des sous-classes. Par exemple int est un sous-type de float, mais int n'est pas une sous-classe de float.

### Covariant, Contravariant, and Invariant

Que se passe-t-il lorsque vous utilisez des sous-types à l'intérieur de types composites? Par exemple, Tuple[bool] est-il un sous-type de Tuple[int]? La réponse dépend du type composite, et si ce type est covariant, contravariant ou invariant. Cela devient technique rapidement, alors donnons juste quelques exemples:
-Tuple est covariant : Cela signifie qu'il conserve la hiérarchie de type de ses types d'éléments: Tuple[bool] est un sous-type de Tuple[int] parce que bool est un sous-type de int.
- List est invariant. Les types invariants ne donnent aucune garantie sur les sous-types. Alors que toutes les valeurs de List[bool] sont des valeurs de List[int], vous pouvez ajouter un int à List[int] et non pour List[bool]. En d'autres termes, la deuxième condition pour les sous-types ne tient pas, et List[bool] n'est pas un sous-type de List[int].
- Callable est contravariant dans ses arguments. Cela signifie qu'il inverse la hiérarchie de type. Vous verrez comment Callable travaille plus tard, mais pour l'instant pensez à Callable[[T], ...]en fonction avec son seul argument étant de type T. Être contravariant signifie que si une fonction fonctionne sur un bool est attendu, puis une fonction fonctionnant sur un int, cela serait accepté.

En général, vous n’avez pas besoin de garder ces expressions droites. Cependant, vous devez être conscient que les sous-types et les types composites peuvent ne pas être simples et intuitifs.

### Typage graduel et consistant

Plus tôt, nous avons mentionné que Python prend en charge la saisie progressive, où vous pouvez ajouter progressivement des indices de type à votre code Python. Le typage progressif est essentiellement rendu possible par `AnyType`.

 `Any` se trouve, d'une certaine façon, à la fois en haut et en bas de la hiérarchie de types. Tout type se comporte comme s'il s'agissait d'un sous-type de `Any`, et `Any` se comporte comme s'il s'agissait d'un sous-type de tout autre type. En regardant la définition des sous-types ci-dessus, ce n'est pas vraiment possible. Au lieu de cela, nous parlons de types cohérents.

Le type T est compatible avec le type U si :
- soit T est un sous-type de U
- soit T ou U est Any.

Le vérificateur de type ne se plaint que de types incohérents. Vous ne verrez donc jamais d'erreurs de type découlant de la Anytype.

Cela signifie que vous pouvez utiliser Any pour retomber explicitement sur un typage dynamique, décrire des types trop complexes à décrire dans le système de type Python, ou décrire des éléments dans des types composites. Par exemple, un dictionnaire avec des clefs de de type `str` peut prendre n'importe quel type car ses valeurs peuvent être annotées Dict[str, Any].

N'oubliez pas, cependant, si vous utilisez Anyle vérificateur de type statique ne fera en effet aucune vérification de type.

## Jouer Avec Les Types Python, Partie 2

Let’s return to our practical examples. Recall that you were trying to annotate the general choose() function:

import random
from typing import Any, Sequence

def choose(items: Sequence[Any]) -> Any:
    return random.choice(items)

The problem with using Any is that you are needlessly losing type information. You know that if you pass a list of strings to choose(), it will return a string. Below you’ll see how to express this using type variables, as well as how to work with:

    Duck types and protocols
    Arguments with None as default value
    Class methods
    The type of your own classes
    Variable number of arguments

### Variables de type

Une variable de type est une variable spéciale qui peut prendre n'importe quel type, selon la situation.
Créons une variable de type qui encapsulera efficacement le comportement de choose():
```python
# choose.py
import random
from typing import Sequence, TypeVar

Choosable = TypeVar("Choosable")

def choose(items: Sequence[Choosable]) -> Choosable:
    return random.choice(items)

names = ["Guido", "Jukka", "Ivan"]
reveal_type(names)
name = choose(names)
reveal_type(name)
```

Une variable de type doit être définie en utilisant TypeVar du modue typing. Lorsqu'il est utilisé, une variable de type se compare à tous les types possibles et prend le type le plus spécifique possible. Dans l'exemple, nameest maintenant un str :
```bash
mypy choose.py
choose.py:12: error: Revealed type is 'builtins.list[builtins.str*]'
choose.py:15: error: Revealed type is 'builtins.str*'
```
Ou encore :
```python
# choose_examples.py
from choose import choose
reveal_type(choose(["Guido", "Jukka", "Ivan"]))
reveal_type(choose([1, 2, 3]))
reveal_type(choose([True, 42, 3.14]))
reveal_type(choose(["Python", 3, 7]))
```

Les deux premiers exemples devraient avoir le type str et int Mais qu'en est-il des deux derniers ? Les éléments de liste individuels ont différents types, et dans ce cas, le type variable` Choosable` fait de son mieux pour accueillir:
```bash
mypy choose_examples.py
choose_examples.py:5: error: Revealed type is 'builtins.str*'
choose_examples.py:6: error: Revealed type is 'builtins.int*'
choose_examples.py:7: error: Revealed type is 'builtins.float*'
choose_examples.py:8: error: Revealed type is 'builtins.object*'
```

Comme vous l’avez déjà vu bool est un sous-type de int, qui encore une fois est un sous-type de float. Donc, dans le troisième exemple, la valeur de retour de choose() est garantie d'être quelque chose que l'on peut considérer comme un float. Dans le dernier exemple, il n'y a pas de relation de sous-type entre str et int, donc le meilleur de ce qui peut être dit sur la valeur de retour est qu'il s'agit d'un objet.

Notez qu'aucun de ces exemples n'a soulevé une erreur de type. Y a-t-il un moyen de dire au vérificateur de type que choose()devrait accepter à la fois les chaînes et les chiffres, mais pas les deux en même temps ? Vous pouvez limiter les variables de type en énumérant les types acceptables:
```python
# choose.py
import random
from typing import Sequence, TypeVar

Choosable = TypeVar("Choosable", str, float)

def choose(items: Sequence[Choosable]) -> Choosable:
    return random.choice(items)

reveal_type(choose(["Guido", "Jukka", "Ivan"]))
reveal_type(choose([1, 2, 3]))
reveal_type(choose([True, 42, 3.14]))
reveal_type(choose(["Python", 3, 7]))
```
Maintenant Choosable ne peut être que soit str, soit float, et mypy notera que le dernier exemple est une erreur:
```bash
$ mypy choose.py
choose.py:11: error: Revealed type is 'builtins.str*'
choose.py:12: error: Revealed type is 'builtins.float*'
choose.py:13: error: Revealed type is 'builtins.float*'
choose.py:14: error: Revealed type is 'builtins.object*'
choose.py:14: error: Value of type variable "Choosable" of "choose"
                     cannot be "object"
```

Dans notre jeu de cartes, nous voulons restreindre choose() à utiliser pour str et Card:
```python
Choosable = TypeVar("Choosable", str, Card)

def choose(items: Sequence[Choosable]) -> Choosable:
    ...
```

Comme nous l'avons brièvement mentionné Sequencere représente à la fois les listes et les tuples.

### Duck typing et protocoles

Soit :
```python
def len(obj):
    return obj.__len__()
```

len() peut renvoyer la longueur de tout objet ayant implémenté la méthode .__len__(). Comment ajouter des indices de type à len(), et en particulier l'argument obj ?

La réponse se cache derrière l'expression de **sous-typage structurel**. Une façon de catégoriser les systèmes de type est de savoir s'ils sont nominaux ou structurels:
- Dans un système nominal, les comparaisons entre les types sont basées sur les noms et les déclarations. Le système de type Python est principalement nominal, où un int peut être utilisé à la place d'un float à cause de leur relation de sous-type.
- Dans un système structurel, les comparaisons entre types sont basées sur la structure. Vous pouvez définir un type de structure Sized qui inclut toutes les instances qui définissent .__len__(), quel que soit leur type nominal.

Il y a un travail en cours pour apporter un système de type structurel à part entière à Python via **PEP 544** qui vise à ajouter un concept appelé **protocoles**. La majeure partie de la PEP 544 est déjà implémentée dans mypy.

Un protocole spécifie une ou plusieurs méthodes qui doivent être mises en œuvre. Par exemple, toutes les classes définissant .__len__() accomplir le protocole `typing.Sized`. Nous pouvons donc annoter len() comme suit:
```python
from typing import Sized

def len(obj: Sized) -> int:
    return obj.__len__()
```

D'autres exemples de protocoles définis dans le module `typing` incluent Container, Iterable, Awaitable, et ContextManager.

Vous pouvez également définir vos propres protocoles. Ceci est fait en héritant de Protocolet définissant les signatures de fonction (avec des corps de fonction vides) que le protocole attend. L'exemple suivant montre comment len()et Sizedaurait pu être mise en œuvre:
```python
from typing_extensions import Protocol

class Sized(Protocol):
    def __len__(self) -> int: ...

def len(obj: Sized) -> int:
    return obj.__len__()
```

### The Optional Type

Un comportement courant en Python consiste à utiliser `None` comme une valeur par défaut pour un argument. Cela est généralement fait soit pour éviter les problèmes avec les valeurs par défaut mutables ou pour avoir une valeur sentinelle signalant un comportement spécial.

Dans l'exemple de la carte, la fonction player_order() utilise None comme une valeur sentinelle pour dire que si aucun joueur de départ n'est donné, il devrait être choisi au hasard:
```python
def player_order(names, start=None):
    """Rotate player order so that start goes first"""
    if start is None:
        start = choose(names)
    start_idx = names.index(start)

    return names[start_idx:] + names[:start_idx]
```

Le défi que cela crée pour l'indication de type est que, en général, ce devrait être une chaîne. Cependant, il peut également prendre la valeur spéciale `None`. Dans ce cas, il est possible d'utiloiser un type spécial :
```python
from typing import Sequence, Optional

def player_order(
    names: Sequence[str], start: Optional[str] = None
) -> Sequence[str]:
    ...
```

`Optionalt-Type` dit simplement qu'une variable a le type spécifié ou None. Une manière équivalente de spécifier la même chose serait d'utiliser `UnionType`: Union[None, str]

Notez que lors de l'utilisation de l'un ou l'autre Optionalou Unionvous devez veiller à ce que la variable ait le bon type lorsque vous y opérez. Ceci est fait dans l'exemple en testant si start is None. Ne pas le faire causerait à la fois des erreurs de type statique ainsi que d'éventuelles erreurs d'exécution:
```python
# player_order.py
from typing import Sequence, Optional
def player_order(
    names: Sequence[str], start: Optional[str] = None
) -> Sequence[str]:
    start_idx = names.index(start)

    return names[start_idx:] + names[:start_idx]
```

`mypy` vous dit que vous n'avez pas pris soin du cas où start est None:
```bash
mypy player_order.py
player_order.py:8: error: Argument 1 to "index" of "list" has incompatible
                          type "Optional[str]"; expected "str"
```

> Remarque : L'utilisation de Nonepour les arguments optionnels est si commun que mypy le gère automatiquement. Mypy suppose qu'un argument par défaut de Noneindique un argument optionnel même si l'indice de type ne le dit pas explicitement. Vous auriez pu utiliser ce qui suit:
```python
def player_order(names: Sequence[str], start: str = None) -> Sequence[str]:
    ...
```

Si vous ne voulez pas que mypy fasse cette hypothèse, vous pouvez l'inhiber avec l'option de ligne de commande ` --no-implicit-optional`.

## Exemple

Réécrivons le jeu de cartes pour être plus orienté vers les objets. Cela nous permettra de discuter de la manière d’annoter correctement les classes et les méthodes. Une traduction plus ou moins directe de notre jeu de cartes en code qui utilise des classes pour Card, Deck, Player, et GameOn dirait quelque chose comme ce qui suit:
```python
# game.py
import random
import sys

class Card:
    SUITS = "♠ ♡ ♢ ♣".split()
    RANKS = "2 3 4 5 6 7 8 9 10 J Q K A".split()

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.suit}{self.rank}"

class Deck:
    def __init__(self, cards):
        self.cards = cards

    @classmethod
    def create(cls, shuffle=False):
        """Create a new deck of 52 cards"""
        cards = [Card(s, r) for r in Card.RANKS for s in Card.SUITS]
        if shuffle:
            random.shuffle(cards)
        return cls(cards)

    def deal(self, num_hands):
        """Deal the cards in the deck into a number of hands"""
        cls = self.__class__

        return tuple(cls(self.cards[i::num_hands]) for i in range(num_hands))

class Player:
    def __init__(self, name, hand):
        self.name = name
        self.hand = hand

    def play_card(self):
        """Play a card from the player's hand"""
        card = random.choice(self.hand.cards)
        self.hand.cards.remove(card)
        print(f"{self.name}: {card!r:<3}  ", end="")

        return card

class Game:
    def __init__(self, *names):
        """Set up the deck and deal cards to 4 players"""
        deck = Deck.create(shuffle=True)
        self.names = (list(names) + "P1 P2 P3 P4".split())[:4]
        self.hands = {
            n: Player(n, h) for n, h in zip(self.names, deck.deal(4))
        }

    def play(self):
        """Play a card game"""
        start_player = random.choice(self.names)
        turn_order = self.player_order(start=start_player)
        # Play cards from each player's hand until empty
        while self.hands[start_player].hand.cards:
            for name in turn_order:
                self.hands[name].play_card()
            print()

    def player_order(self, start=None):
        """Rotate player order so that start goes first"""
        if start is None:
            start = random.choice(self.names)
        start_idx = self.names.index(start)
        return self.names[start_idx:] + self.names[:start_idx]

if __name__ == "__main__":
    # Read player names from command line
    player_names = sys.argv[1:]
    game = Game(*player_names)
    game.play()
```

### Indices de types pour les méthodes

First of all type hints for methods work much the same as type hints for functions. The only difference is that the self argument need not be annotated, as it always will be a class instance. The types of the Card class are easy to add:
```python
class Card:
    SUITS = "♠ ♡ ♢ ♣".split()
    RANKS = "2 3 4 5 6 7 8 9 10 J Q K A".split()

    def __init__(self, suit: str, rank: str) -> None:
        self.suit = suit
        self.rank = rank

    def __repr__(self) -> str:
        return f"{self.suit}{self.rank}"
```

Notez que la méthode .__init__() devrait toujours avoir None comme type de retour.

### Classes comme types

Il existe une correspondance entre les classes et les types. Par exemple, l'ensemble de toutes les instances de la classe Card forme le type Card. Pour utiliser des classes comme types, vous utilisez simplement le nom de la classe.

Ainsi, un Deck est simplement un ensemble de Card :
```python
class Deck:

    def __init__(self, cards: List[Card]) -> None:
        self.cards = cards
```

`mypy` est capable de connecter le type Card à la définition de la classe qui porte le même nom.

Mais cela ne fonctionne pas aussi bien quand vous devez vous référer à la classe actuellement en cours de définition. Par exemple, la méthode de classe Deck.create() renvoie un objet avec type Deck. Cependant, vous ne pouvez pas simplement ajouter `-> Deck`, car la classe n'est pas encore entièrement définie.

Au lieu de cela, vous êtes autorisé à utiliser des littéraux de chaîne dans les annotations. Ces chaînes ne seront évaluées que par le vérificateur de type plus tard, et peuvent donc contenir des références d'auto et d'avance. La méthode `create()` devrait utiliser de tels littéraux de chaîne pour ses types:
```python
class Deck:
    @classmethod
    def create(cls, shuffle: bool = False) -> "Deck":
        """Create a new deck of 52 cards"""
        cards = [Card(s, r) for r in Card.RANKS for s in Card.SUITS]
        if shuffle:
            random.shuffle(cards)

        return cls(cards)
```

Notez que la classe Player fait aussi référenceà la classe Deck. Ce n'est cependant pas un problème, puisque Deck est défini avant Player:
```python
class Player:
    def __init__(self, name: str, hand: Deck) -> None:
        self.name = name
        self.hand = hand
```

Habituellement, les annotations ne sont pas utilisées au moment de l'exécution. Cela a incité à l'idée de reporter l'évaluation des annotations. Au lieu d'évaluer les annotations en tant qu'expressions Python et de stocker leur valeur, la proposition est de stocker la représentation de chaîne de l'annotation et de ne l'évaluer qu'en cas de besoin.

Une telle fonctionnalité est prévue pour devenir standard dans une version Python 4.0 encore mythique. Cependant, en Python 3.7 et versions ultérieures, les références à l'avance sont disponibles via `__future__`:
```python
from __future__ import annotations

class Deck:
    @classmethod
    def create(cls, shuffle: bool = False) -> Deck:
        ...
```

Ainsi, vous pouvez faire référence à Deck avant même qu'elle soit définie.

### self ou cls ?

Comme indiqué, vous ne devez généralement pas annoter les arguments avec self ou cls. En partie, cela n'est pas nécessaire comme self pointe vers une instance de la classe, donc il aura le type de la classe. Dans l'exemple de Card, self a le type implicite Card. En outre, l'ajout de ce type serait explicitement encombrant puisque la classe n'est pas encore définie. Vous devriez utiliser la syntaxe littérale de chaîne, self: "Card".

Il y a un cas où vous voudrez peut-être annoter self ou cls, cependant. Considérez ce qui se passe si vous avez une super-classe dont les autres classes héritent, et qui a des méthodes qui reviennent self ou cls:
```python
# dogs.py
from datetime import date

class Animal:
    def __init__(self, name: str, birthday: date) -> None:
        self.name = name
        self.birthday = birthday

    @classmethod
    def newborn(cls, name: str) -> "Animal":
        return cls(name, date.today())

    def twin(self, name: str) -> "Animal":
        cls = self.__class__

        return cls(name, self.birthday)

class Dog(Animal):
    def bark(self) -> None:
        print(f"{self.name} says woof!")

fido = Dog.newborn("Fido")
pluto = fido.twin("Pluto")
fido.bark()
pluto.bark()
```

Alors que le code s'exécute sans problème, mypy signalera un problème:

$ mypy dogs.py
dogs.py:24: error: "Animal" has no attribute "bark"
dogs.py:25: error: "Animal" has no attribute "bark"

Les méthodes vont retourner un Dog, car l'annotation dit qu'ils retournent un Animal !

Dans de tels cas, vous voulez être plus prudent pour vous assurer que l'annotation est correcte. Le type de retour doit correspondre au type de self ou le type d'instance de cls. Cela peut être fait en utilisant des variables de type qui gardent une trace de ce qui est réellement passé selfet cls:
```python
# dogs.py
from datetime import date
from typing import Type, TypeVar

TAnimal = TypeVar("TAnimal", bound="Animal")

class Animal:
    def __init__(self, name: str, birthday: date) -> None:
        self.name = name
        self.birthday = birthday

    @classmethod
    def newborn(cls: Type[TAnimal], name: str) -> TAnimal:
        return cls(name, date.today())

    def twin(self: TAnimal, name: str) -> TAnimal:
        cls = self.__class__
        return cls(name, self.birthday)

class Dog(Animal):
    def bark(self) -> None:
        print(f"{self.name} says woof!")

fido = Dog.newborn("Fido")
pluto = fido.twin("Pluto")
fido.bark()
pluto.bark()
```

Il y a quelques points à noter dans cet exemple:
- La variable de type TAnimalest utilisé pour indiquer que les valeurs de retour peuvent être des instances de sous-classes de Animal.
- Nous précisons que Animalest une borne supérieure pour TAnimal. Spécifier boundsignifie que TAnimalne sera que Animalou l'une de ses sous-classes. Cela est nécessaire pour restreindre correctement les types autorisés.
- La construction typing.Type[] est l'équivalent de type(). Vous devez noter que la méthode de classe attend une classe et retourne une instance de cette classe.

### Annoter *args and **kwargs

Dans la version orientée objet du jeu, nous avons ajouté l'option de nommer les joueurs sur la ligne de commande. Ceci est fait en énumérant les noms des joueurs après le nom du programme:
```bash
python game.py GeirArne Dan Joanna
Dan: ♢A   Joanna: ♡9   P1: ♣A   GeirArne: ♣2
Dan: ♡A   Joanna: ♡6   P1: ♠4   GeirArne: ♢8
Dan: ♢K   Joanna: ♢Q   P1: ♣K   GeirArne: ♠5
Dan: ♡2   Joanna: ♡J   P1: ♠7   GeirArne: ♡K
Dan: ♢10  Joanna: ♣3   P1: ♢4   GeirArne: ♠8
Dan: ♣6   Joanna: ♡Q   P1: ♣Q   GeirArne: ♢J
Dan: ♢2   Joanna: ♡4   P1: ♣8   GeirArne: ♡7
Dan: ♡10  Joanna: ♢3   P1: ♡3   GeirArne: ♠2
Dan: ♠K   Joanna: ♣5   P1: ♣7   GeirArne: ♠J
Dan: ♠6   Joanna: ♢9   P1: ♣J   GeirArne: ♣10
Dan: ♠3   Joanna: ♡5   P1: ♣9   GeirArne: ♠Q
Dan: ♠A   Joanna: ♠9   P1: ♠10  GeirArne: ♡8
Dan: ♢6   Joanna: ♢5   P1: ♢7   GeirArne: ♣4
```

Ceci est mis en œuvre par déballage et passage du tgableau `sys.argv` à Game() quand il est instancié. `__init__ ` utilise la syntaxe  *names pour emballer les noms donnés dans un tuple.

Concernant les annotations de type: même si names est un tuple de chaînes, vous ne devez annoter que le type de chaque nom. En d'autres termes, vous devriez utiliser str et non Tuple[str]:
```python
class Game:

    def __init__(self, *names: str) -> None:
        """Set up the deck and deal cards to 4 players"""
        deck = Deck.create(shuffle=True)
        self.names = (list(names) + "P1 P2 P3 P4".split())[:4]
        self.hands = {
            n: Player(n, h) for n, h in zip(self.names, deck.deal(4))
        }
```

De même, si vous avez une fonction ou une méthode d'acceptation `**kwargs`, alors vous ne devez annoter que le type de chaque argument de mot clé possible.

### Callables

Les fonctions sont des objets de première classe en Python. Cela signifie que vous pouvez utiliser des fonctions comme arguments d'autres fonctions. Cela signifie également que vous devez être en mesure d'ajouter des indices de type représentant des fonctions.

Les fonctions, ainsi que les lambdas, les méthodes et les classes, sont représentées par `typing.Callable`. Les types d'arguments et la valeur de retour sont généralement également représentés. Par exemple, `Callable[[A1, A2, A3], Rt]` représente une fonction avec trois arguments avec des types A1, A2, et A3, respectivement. Le type de retour de la fonction est Rt.

Dans l'exemple suivant, la fonction do_twice()appelle deux fois une fonction donnée et imprime les valeurs de retour:
```python
# do_twice.py
from typing import Callable

def do_twice(func: Callable[[str], str], argument: str) -> None:
    print(func(argument))
    print(func(argument))

def create_greeting(name: str) -> str:
    return f"Hello {name}"

do_twice(create_greeting, "Jekyll")
```

Notez l'annotation de l'argument func à do_twice(). Il dit que func devrait être un « _callbale_ » avec un argument de type chaîne, qui retourne également une chaîne. Un exemple d'un tel « _callbale_ » est create_greeting(), défini à la ligne 9.

La plupart des types « _callbale_ » peuvent être annotés de la même manière. Cependant, si vous avez besoin de plus de flexibilité, consultez les protocoles de callback et les types « _callbale_ » étendus.

## Finale : Cœurs

Terminons par un exemple complet du jeu de Hearts. Vous connaissez peut-être déjà ce jeu à partir d'autres simulations informatiques. Voici un résumé rapide des règles:
- Quatre joueurs jouent avec une main de 13 cartes chacune.
- Le joueur tenant le ♣2 commence le premier tour, et doit jouer ♣2.
- Les joueurs jouent à tour de rôle à jouer, en suivant la figure principale, si possible.
- Le joueur jouant la carte la plus haute dans la combinaison principale gagne le tour, et devient joueur de départ dans le tour suivant.
- Un joueur ne peut pas diriger avec un ♡ jusqu'à ce qu'un ♡ ait déjà été joué dans un tour plus tôt.
- Une fois que toutes les cartes sont jouées, les joueurs obtiennent des points s'ils prennent certaines cartes:
    - 13 points pour le ♠Q
    - 1 point pour chacun ♡
- Une partie dure plusieurs tours, jusqu'à ce qu'un joueur ait 100 points ou plus. Le joueur avec le moins de points gagne.

Il n'y a pas de nouveaux concepts de typage dans cet exemple que vous n'ayez pas déjà vu. Nous ne passerons donc pas en revue ce code en détail, mais le laisserons comme un exemple de code annoté.

Voici quelques points à noter dans le code:
- Pour les relations de type qui sont difficiles à exprimer en utilisant Unionou tapez des variables, vous pouvez utiliser le @overloaddécorateur. Voir Deck.__getitem__()par exemple et la documentation pour plus d'informations.
- Les sous-classes correspondent à des sous-types, de sorte qu'une HumanPlayerpeut être utilisé partout où un Playerest attendu.
- Lorsqu'une sous-classe réimplémente une méthode d'une superclasse, les annotations de type doivent correspondre. Voir HumanPlayer.play_card()par un exemple.

Lorsque vous démarrez la partie, vous contrôlez le premier joueur. Entrez les chiffres pour choisir les cartes à jouer. Ce qui suit est un exemple de jeu, avec les lignes surlignées montrant où le joueur a fait un choix:
```python
$ python hearts.py GeirArne Aldren Joanna Brad

Starting new round:
Brad -> ♣2
  0: ♣5  1: ♣Q  2: ♣K  (Rest: ♢6 ♡10 ♡6 ♠J ♡3 ♡9 ♢10 ♠7 ♠K ♠4)
  GeirArne, choose card: 2
GeirArne => ♣K
Aldren -> ♣10
Joanna -> ♣9
GeirArne wins the trick

  0: ♠4  1: ♣5  2: ♢6  3: ♠7  4: ♢10  5: ♠J  6: ♣Q  7: ♠K  (Rest: ♡10 ♡6 ♡3 ♡9)
  GeirArne, choose card: 0
GeirArne => ♠4
Aldren -> ♠5
Joanna -> ♠3
Brad -> ♠2
Aldren wins the trick

...

Joanna -> ♡J
Brad -> ♡2
  0: ♡6  1: ♡9  (Rest: )
  GeirArne, choose card: 1
GeirArne => ♡9
Aldren -> ♡A
Aldren wins the trick

Aldren -> ♣A
Joanna -> ♡Q
Brad -> ♣J
  0: ♡6  (Rest: )
  GeirArne, choose card: 0
GeirArne => ♡6
Aldren wins the trick

Scores:
Brad             14  14
Aldren           10  10
GeirArne          1   1
Joanna            1   1
```

## Vérification de type statique

Jusqu'à présent, vous avez vu comment ajouter des indices de type à votre code. Dans cette section, vous en apprendrez plus sur la façon d'effectuer réellement la vérification statique de type de code Python.

### Le projet Mypy

Mypy a été lancé par Jukka Lehtosalo lors de ses études de doctorat à Cambridge vers 2012. Mypy a été initialement envisagé comme une variante Python avec une frappe dynamique et statique transparente.

La plupart de ces idées originales jouent encore un rôle important dans le projet mypy. En fait, le slogan « dactylographie dynamique et statique sans soudure_» est toujours visible sur la page d'accueil de mypy et décrit la motivation pour utiliser des indices de type en Python bien.

Le plus grand changement depuis 2012 est que mypy n'est plus une variante de Python. Dans ses premières versions, mypy était un langage autonome compatible avec Python, à l'exception de ses déclarations de type. Suite à une suggestion de Guido van Rossum, Mypy a été réécrit pour utiliser des annotations à la place. Aujourd'hui, mypy est un vérificateur de type statique pour le code Python régulier.

### Éxécuter Mypy

Avant d'exécuter mypy pour la première fois, vous devez installer le programme. Ceci est le plus facile à faire en utilisant pip:
```bash
pip install mypy
```
Puyis :
```bash
mypy my_program.py
```

Il existe de nombreuses options disponibles lors de la vérification de votre code. Comme `mypy` est toujours en cours de développement très actif, les options de ligne de commande sont susceptibles de changer entre les versions. Vous devriez vous référer à l'aide de Mypy pour voir quels paramètres sont par défaut sur votre version:
```bash
mypy --help
usage: mypy [-h] [-v] [-V] [more options; see below]
            [-m MODULE] [-p PACKAGE] [-c PROGRAM_TEXT] [files ...]

Mypy is a program that will type check your Python code.

[... The rest of the help hidden for brevity ...]
```

De plus, la documentation en ligne de la ligne de commande mypy contient de nombreuses informations.

Voyons quelques-unes des options les plus courantes. Tout d’abord, si vous utilisez des paquets tiers sans indices de type, vous voudrez peut-être réduire au silence les avertissements de Mypy à ce sujet. Cela peut être fait avec l'option `--ignore-missing-importsoption`.

L'exemple suivant utilise Numpy pour calculer et imprimer le cosinus de plusieurs nombres:
```python
# cosine.py
import numpy as np

def print_cosine(x: np.ndarray) -> None:
    with np.printoptions(precision=3, suppress=True):
        print(np.cos(x))

x = np.linspace(0, 2 * np.pi, 9)
print_cosine(x)
```

Puis :
```bash
python cosine.py
[ 1.     0.707  0.    -0.707 -1.    -0.707 -0.     0.707  1.   ]
```

Le produit réel de cet exemple n'est pas important. Cependant, vous devez noter que l'argument x est annoté avec `np.ndarray`, car nous voulons imprimer le cosinus d'une liste complète de chiffres.

Vous pouvez exécuter mypy sur ce fichier comme d'habitude:
```bash
$ mypy cosine.py
cosine.py:3: error: No library stub file for module 'numpy'
cosine.py:3: note: (Stub files are from https://github.com/python/typeshed)
```

Dans la plupart des cas, les indices de type manquants dans les paquets tiers ne sont pas quelque chose avec lequel vous voulez être dérangé afin que vous puissiez réduire au silence ces messages:
```bash
mypy --ignore-missing-imports cosine.py
Success: no issues found in 1 source file
```

Si vous utilisez `--ignore-missing-import`, Mypy n'essaiera pas de suivre ou d'avertir de toute importation manquante. Cela pourrait cependant être un peu lourd, car il ignore également les erreurs réelles, comme l'appellation erronée du nom d'un paquet. Deux façons moins intrusives de gérer les paquets tiers utilisent des commentaires de type ou des fichiers de configuration.

Dans un exemple simple comme celui ci-dessus, vous pouvez faire taire l'avertissement en ajoutant un commentaire de type à la ligne contenant l'importation:
```python
import numpy as np  # type: ignore
```

Le littéral `# type: ignore` dit à mypy d'ignorer l'importation de Numpy.

Si vous avez plusieurs fichiers, il peut être plus facile de garder une trace des importations à ignorer dans un fichier de configuration. mypy lit un fichier appelé `mypy.ini` dans le répertoire courant s'il est présent. Ce fichier de configuration doit contenir une section appelée [mypy] et peut contenir des sections spécifiques au module de la forme [mypy-module]. Le fichier de configuration suivant ignorera que Numpy manque des indices de type:
```ini
# mypy.ini

[mypy]

[mypy-numpy]
ignore_missing_imports = True
```

Il existe de nombreuses options qui peuvent être spécifiées dans le fichier de configuration. Il est également possible de spécifier un fichier de configuration global. Voir la documentation pour plus d'informations.

### Ajouter des stubs

Des indices de type sont disponibles pour tous les paquets de la bibliothèque standard Python. Cependant, si vous utilisez des paquets tiers, vous avez déjà vu que la situation peut être différente.

L'exemple suivant utilise le paquet Parse pour effectuer un parsage de texte simple. Pour suivre, vous devez d'abord installer Parse:
```bash
$ pip install parse
```

Parse peut être utilisé pour reconnaître des motifs simples. Voici un petit programme qui fait de son mieux pour trouver votre nom:
```python
# parse_name.py
import parse

def parse_name(text: str) -> str:
    patterns = (
        "my name is {name}",
        "i'm {name}",
        "i am {name}",
        "call me {name}",
        "{name}",
    )
    for pattern in patterns:
        result = parse.parse(pattern, text)
        if result:
            return result["name"]

    return ""

answer = input("What is your name? ")
name = parse_name(answer)
print(f"Hi {name}, nice to meet you!")
```

Le flux principal est défini dans les trois dernières lignes:
- demandez votre nom ;
- analysez la réponse ;
- imprimez un salut.

Parse est appelé afin d'essayer de trouver un nom basé sur l'un des modèles énumérés. Le programme peut être utilisé comme suit:
```bash
$ python parse_name.py
What is your name? I am Geir Arne
Hi Geir Arne, nice to meet you!
```

Notez que même si je réponds I am Geir Arne, le programme détermine que I amne fait pas partie de mon nom.

Ajoutons un petit bug au programme et voyons si Mypy est capable de nous aider à le détecter. Changeons `return result["name"]` en `return result`. Cela rendra un objet `parse.Result` au lieu de la chaîne contenant le nom. Ensuite, exécutez Mypy sur le programme:
```bash
mypy parse_name.py
parse_name.py:3: error: Cannot find module named 'parse'
parse_name.py:3: note: (Perhaps setting MYPYPATH or using the
                       "--ignore-missing-imports" flag would help)
```

Mypy imprime une erreur similaire à celle que vous avez vue dans la section précédente: Il ne connaît pas le parsepaquet. Vous pouvez essayer d'ignorer l'importation:
```bash
mypy parse_name.py --ignore-missing-imports
Success: no issues found in 1 source file
```

Malheureusement, ignorer l'importation signifie que Mypy n'a aucun moyen de découvrir le bug dans notre programme. Une meilleure solution serait d'ajouter des indices de type au paquet Parse lui-même. Comme Parse est open source, vous pouvez réellement ajouter des types au code source et envoyer une demande de tirage.

Vous pouvez également ajouter les types dans un **fichier de souches** (« _stubs_ » en anglais). Un fichier stub est un fichier texte qui contient les signatures de méthodes et de fonctions, mais pas leurs implémentations. Leur fonction principale est d’ajouter des indices de type au code que vous ne pouvez pas modifier pour une raison quelconque. Pour montrer comment cela fonctionne, nous allons ajouter quelques souches pour le paquet Parse.

Tout d'abord, vous devriez mettre tous vos fichiers de souches dans un répertoire commun, et définir la variable d'environnement MYPYPATH vers ce répertoire. Sur Mac et Linux, vous pouvez définir MYPYPATH comme suit:
```bash
export MYPYPATH=/home/gahjelle/python/stubs
```

Vous pouvez définir rendre la variable persitante en ajoutant la ligne à votre fichier `.bashrc`. Sous Windows, vous pouvez cliquer sur le menu Démarrer et rechercher les variables d'environnement à définir MYPYPATH.

Ensuite, créez un fichier dans votre répertoire de stubs que vous appelez `parse.pyi`. Il doit être nommé pour le paquet pour lequel vous ajoutez des indices de type, avec un suffixe .pyi. Laissez ce fichier vide pour l'instant. Puis exécutez Mypy à nouveau:
```bash
mypy parse_name.py
parse_name.py:14: error: Module has no attribute "parse"
```

Si vous avez tout configuré correctement, vous devriez voir ce nouveau message d'erreur. Mypy utilise le nouveau fichier parse.pyi pour déterminer quelles fonctions sont disponibles dans le paquet parse. Puisque le fichier de souches est vide, mypy suppose que parse.parse() n'existe pas, puis donne l'erreur que vous voyez ci-dessus.

L'exemple suivant montre les indices de type que vous devez ajouter pour que mypy puisse taper vérifier votre utilisation de parse.parse():
```python
# parse.pyi

from typing import Any, Mapping, Optional, Sequence, Tuple, Union

class Result:
    def __init__(
        self,
        fixed: Sequence[str],
        named: Mapping[str, str],
        spans: Mapping[int, Tuple[int, int]],
    ) -> None: ...
    def __getitem__(self, item: Union[int, str]) -> str: ...
    def __repr__(self) -> str: ...

def parse(
    format: str,
    string: str,
    evaluate_result: bool = ...,
    case_sensitive: bool = ...,
) -> Optional[Result]: ...
```

Les ellipses `...` font partie de la syntaxe et doivent être écrits exactement comme ci-dessus. Le fichier stub ne doit contenir que des indices de type pour les variables, les attributs, les fonctions et les méthodes, de sorte que les implémentations doivent être laissées de côté et remplacées par ellipses.

Enfin, mypy est capable de repérer le bug que nous avons introduit:
```bash
mypy parse_name.py
parse_name.py:16: error: Incompatible return value type (got
                         "Result", expected "str")
```

### Typedé

Vous avez vu comment utiliser des talons pour ajouter des indices de type sans changer le code source lui-même. Dans la section précédente, nous avons ajouté quelques indices de type au paquet parse tiers. Maintenant, il ne serait pas très efficace si tout le monde devait créer ses propres fichiers de talons pour tous les paquets tiers qu’il utilise.

Typeshed est un dépôt Github qui contient des indices de type pour la bibliothèque standard Python, ainsi que de nombreux paquets tiers. Typeshed est livré avec mypy donc si vous utilisez un paquet qui a déjà des indices de type définis dans Typeshed, la vérification de type fonctionnera simplement.

Vous pouvez également contribuer à des indices de type à Typeshed. Assurez-vous d’obtenir d’abord la permission du propriétaire du paquet, surtout parce qu’il pourrait travailler sur l’ajout d’indices de type dans le code source lui-même – ce qui est l’approche préférée.

### Autres vérificateurs de type statique

Dans ce tutoriel, nous nous sommes principalement concentrés sur la vérification de type en utilisant mypy. Cependant, il existe d'autres vérificateurs de type statique dans l'écosystème Python.

L'éditeur PyCharm est livré avec son propre type de vérificateur inclus. Si vous utilisez PyCharm pour écrire votre code Python, il sera automatiquement vérifié.

Facebook a développé Pyre. L'un de ses objectifs est d'être rapide et performant. Bien qu'il existe certaines différences, les fonctions Pyre sont principalement similaires à la mypie. Consultez la documentation si vous êtes intéressé à essayer Pyre.

De plus, Google a créé le type de pytype. Ce vérificateur de type fonctionne également principalement de la même manière que mypy. En plus de vérifier le code annoté, Pytype a une certaine prise en charge pour exécuter des vérifications de type sur le code non annoté et même ajouter des annotations au code automatiquement. Voir le document quickstart pour plus d'informations.
Utilisation de types à Runtime

En dernier lieu, il est possible d’utiliser des indices de type également à l’exécution lors de l’exécution de votre programme Python. La vérification de type Runtime ne sera probablement jamais prise en charge nativement en Python.

Cependant, les indices de type sont disponibles à l'exécution dans le __annotations__dictionnaire, et vous pouvez les utiliser pour faire des vérifications de type si vous le souhaitez. Avant de vous enfuir et d'écrire votre propre paquet pour faire respecter les types, vous devez savoir qu'il existe déjà plusieurs paquets qui le font pour vous. Jetez un coup d'œil à Enforce, Pydantic, ou Pytypes pour quelques exemples.

Une autre utilisation des indices de type est de traduire votre code Python en C et de le compiler pour l'optimisation. Le populaire projet Cython utilise un langage hybride C/Python pour écrire du code Python de type statique. Cependant, depuis la version 0.27 Cython a également pris en charge des annotations de type. Récemment, le projet Mypyc est devenu disponible. Bien qu'il ne soit pas encore prêt pour une utilisation générale, il peut compiler des extensions Python annotées de type à C.
Conclusion

Le type de type en Python est une fonctionnalité très utile que vous pouvez vivre heureux sans. Les indices de type ne vous rendent pas capable d’écrire n’importe quel code que vous ne pouvez pas écrire sans utiliser des indices de type. Au lieu de cela, l'utilisation d'indices de type vous permet de raisonner plus facilement le code, de trouver des bugs subtils et de maintenir une architecture propre.

Dans ce tutoriel, vous avez appris comment l'indice de type fonctionne en Python, et comment la frappe progressive rend les vérifications de type en Python plus flexibles que dans de nombreuses autres langues. Vous avez vu certains des avantages et des inconvénients de l’utilisation des indices de type, et comment ils peuvent être ajoutés au code en utilisant des annotations ou des commentaires de type. Enfin, vous avez vu beaucoup des différents types que Python prend en charge, ainsi que la façon d'effectuer la vérification de type statique.

Il existe de nombreuses ressources pour en savoir plus sur la vérification statique de type en Python. **PEP 483** et **PEP 484** donnent beaucoup d'arrière-plan sur la façon dont la vérification de type est implémentée en Python. La documentation mypy a une excellente section de référence détaillant tous les différents types disponibles.
