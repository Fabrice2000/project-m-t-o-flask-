# Documentation des projets Python

## Pourquoi documenter votre code est si important

> “Le code est plus souvent lu qu'écrit.”
>
> — Guido van Rossum

Lorsque vous écrivez du code, vous l’écrivez pour deux publics principaux : vos utilisateurs et vos développeurs (y compris vous-même). Les deux publics sont tout aussi importants. Si vous êtes comme moi, vous avez probablement ouvert de vieilles bases de code et vous vous êtes demandé : « _À quoi pensais-je ?_ ». Si vous rencontrez un problème pour lire votre propre code, imaginez ce que vivent vos utilisateurs ou autres développeurs lorsqu'ils essaient d'utiliser ou contribuer à votre code.

À l’inverse, je suis sûr que vous vous êtes retrouvé dans une situation où vous vouliez faire quelque chose en Python et avez trouvé ce qui ressemble à une excellente bibliothèque capable de faire le travail. Cependant, lorsque vous commencez à utiliser la bibliothèque, vous recherchez des exemples, des articles ou même de la documentation officielle sur la façon de faire quelque chose de spécifique et vous ne trouvez pas immédiatement la solution.

Après avoir cherché, vous vous rendez compte que la documentation fait défaut ou pire encore, qu'elle manque complètement. C’est un sentiment frustrant qui vous dissuade d’utiliser la bibliothèque, quelle que soit la qualité ou l’efficacité du code. Daniele Procida a le mieux résumé cette situation :

> “Peu importe la qualité de votre logiciel, car si la documentation n'est pas assez bonne, les gens ne l'utiliseront pas.“
>
> — Daniele Procida

### Code de commentaire ou de documentation

Avant de pouvoir expliquer comment documenter votre code Python, nous devons distinguer la documentation des commentaires.

En général, commenter consiste à décrire votre code aux/pour les développeurs. Le public principal visé est constitué des mainteneurs et des développeurs du code Python. Associés à un code bien écrit, les commentaires aident à guider le lecteur pour mieux comprendre votre code, son objectif et sa conception :
> “Le code vous dit comment ; les commentaires vous disent pourquoi.”
>
> — Jeff Atwood (alias Coding Horror)

Documenter le code consiste à décrire son utilisation et ses fonctionnalités à vos utilisateurs. Bien que cela puisse être utile dans le processus de développement, le principal public visé est constitué des utilisateurs.

## Notions de base sur le code de commentaire
Les commentaires sont créés en Python en utilisant le signe dièse (#) et doivent être de brèves déclarations ne dépassant pas quelques phrases. Voici un exemple simple :
```python
def hello_world():
    # A simple comment preceding a simple print statement
    print("Hello World")
```
Selon **PEP 8**, les commentaires doivent avoir une longueur maximale de 72 caractères. Ceci est vrai même si votre projet modifie la longueur maximale de la ligne pour qu'elle soit supérieure aux 80 caractères recommandés. Si un commentaire doit être supérieur à la limite de caractères du commentaire, il est approprié d'utiliser plusieurs lignes pour le commentaire :
```python
def hello_long_world():
    # A very long statement that just goes on and on and on and on and
    # never ends until after it's reached the 80 char limit
    print("Hellooooooooooooooooooooooooooooooooooooooooooooooooooooooo World")
```
Commenter votre code sert objectifs multiples, notamment:

1. **Planification et révision** : Lorsque vous développez de nouvelles parties de votre code, il peut être approprié d’utiliser d’abord les commentaires comme moyen de planifier ou de décrire cette section de code. N'oubliez pas de supprimer ces commentaires une fois le codage réel implémenté et examiné/testé
2. **Description du code** : Les commentaires peuvent être utilisés pour expliquer l’intention de sections spécifiques du code :
3. **Description algorithmique** : Lorsque des algorithmes sont utilisés, en particulier des algorithmes complexes, il peut être utile d'expliquer comment fonctionne l'algorithme ou comment il est implémenté dans votre code. Il peut également être approprié de décrire pourquoi un algorithme spécifique a été sélectionné plutôt qu’un autre.
4. **Marquage**: L’utilisation du balisage peut être utilisée pour étiqueter des sections spécifiques de code où se trouvent des problèmes connus ou des domaines d’amélioration. Voici quelques exemples : BUG, FIXME, et TODO.

Les commentaires sur votre code doivent être brefs et ciblés. Évitez d’utiliser de longs commentaires lorsque cela est possible. De plus, vous devez utiliser les quatre règles essentielles suivantes comme suggéré par Jeff Atwood:
- Gardez les commentaires aussi proches que possible du code décrit. Les commentaires qui ne sont pas proches de leur code de description sont frustrants pour le lecteur et passent facilement inaperçus lorsque des mises à jour sont effectuées.
- N'utilisez pas de formatage complexe (tel que des tableaux ou des figures ASCII). Un formatage complexe conduit à un contenu distrayant et peut être difficile à maintenir au fil du temps.
- N'incluez pas d'informations redondantes. Supposons que le lecteur du code ait une compréhension de base des principes de programmation et de la syntaxe du langage.
- Concevez votre code pour qu'il se commente lui-même. La façon la plus simple de comprendre le code est de le lire. Lorsque vous concevez votre code à l’aide de concepts clairs et faciles à comprendre, le lecteur sera en mesure de conceptualiser rapidement votre intention.

N'oubliez pas que les commentaires sont conçus pour le lecteur, y compris vous-même, afin de l'aider à comprendre le but et la conception du logiciel.

### Commenter le code via Type Hinting (Python 3.5+)

L'indication de type a été ajoutée à Python 3.5 et constitue un option supplémentaire (fortement conseillée) pour aider les lecteurs de votre code. Il permet au développeur de concevoir et d'expliquer des parties de son code sans commenter. Voici un exemple rapide :
```python
def hello_name(name: str) -> str:
    return(f"Hello {name}")
```

En examinant l'indication de type, vous pouvez immédiatement dire que la fonction attend l'entrée name être une chaîne de caractères. Vous pouvez également dire que la sortie attendue de la fonction sera également une chaîne de caractères.

Le typage du code Python est une question en soi qui ne sera pas développée ici.

## Documenter votre base de code Python à l'aide de Docstrings

### Contexte des chaînes de documents

La documentation de votre code Python est entièrement centrée sur les `docstrings`. Ce sont des chaînes intégrées qui, lorsqu'elles sont configurées correctement, peuvent aider vos utilisateurs et vous-même avec la documentation de votre projet. En plus des docstrings, Python dispose également de la fonction intégrée help() qui imprime la `docstring` des objets sur la console. Voici un exemple rapide :
```python
>>> help(str)
Help on class str in module builtins:

class str(object)
 |  str(object='') -> str
 |  str(bytes_or_buffer[, encoding[, errors]]) -> str
 |
 |  Create a new string object from the given object. If encoding or
 |  errors are specified, then the object must expose a data buffer
 |  that will be decoded using the given encoding and error handler.
 |  Otherwise, returns the result of object.__str__() (if defined)
 |  or repr(object).
 |  encoding defaults to sys.getdefaultencoding().
 |  errors defaults to 'strict'.
 # Truncated for readability
 #
 ```

Comment cette sortie est-elle générée ? Puisque tout en Python est un objet, vous pouvez examiner le répertoire de l'objet à l'aide de la commande `dir()` :
```python
>>> dir(str)
['__add__', ..., '__doc__', ..., 'zfill'] # Truncated for readability
```

Dans cette sortie, il y a une propriété intéressante, `__doc__`. Si vous examinez cette propriété, vous découvrirez ceci :
```python
>>> print(str.__doc__)
str(object='') -> str
str(bytes_or_buffer[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors are specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.
```

Voilà ! Vous avez trouvé où les `docstrings` sont stockés dans l'objet. Cela signifie que vous pouvez manipuler directement cette propriété. Cependant, il existe des restrictions pour les fonctions intégrées :
```python
>>> str.__doc__ = "I'm a little string doc! Short and stout; here is my input and print me for my out"
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: can't set attributes of built-in/extension type 'str'
```

Cette propriété peut naturellement être manipulée :
```python
def say_hello(name):
    print(f"Hello {name}, is it me you're looking for?")

say_hello.__doc__ = "A simple function that says hello... Richie style"

>>> help(say_hello)
Help on function say_hello in module __main__:

say_hello(name)
    A simple function that says hello... Richie style
```
Python dispose d'une fonctionnalité supplémentaire qui simplifie la création de `docstring`. Au lieu de manipuler directement la propriété __doc__, le placement de la chaîne littérale directement sous l'objet définira automatiquement le `__doc__` valeur. Voici ce qui se passe avec le même exemple que ci-dessus :
```python
def say_hello(name):
    """A simple function that says hello... Richie style"""
    print(f"Hello {name}, is it me you're looking for?")
>>> help(say_hello)
Help on function say_hello in module __main__:

say_hello(name)
    A simple function that says hello... Richie style
```
Voilà ! Vous comprenez maintenant le contexte des `docstrings`.

### Types de chaînes de documents

Les conventions `docstring` sont décrites dans **PEP 257**. Leur objectif est de fournir à vos utilisateurs un bref aperçu de l’objet. Ils doivent être suffisamment concis pour être faciles à maintenir tout en restant suffisamment élaborés pour que les nouveaux utilisateurs puissent comprendre leur objectif et comment utiliser l'objet documenté.

Dans tous les cas, les docstrings doivent utiliser les guillemets triples-doubles (""") comme format de chaîne, que la docstring soit multiligne ou non. Au strict minimum, une docstring doit être un résumé rapide de ce que vous décrivez et doit être contenue dans une seule ligne :
```python
"""This is a quick summary line used as a description of the object."""
```
Des docstrings multilignes sont utilisées pour développer davantage l'objet au-delà du résumé. Toutes les docstrings multilignes comportent les parties suivantes :
- Une ligne récapitulative d'une seule ligne
- Une ligne vide précédant le résumé
- Toute élaboration supplémentaire pour la docstring
- Une autre ligne vide
```python
"""This is the summary line

This is the further elaboration of the docstring. Within this section,
you can elaborate further on details as appropriate for the situation.
Notice that the summary and the elaboration is separated by a blank new
line.
"""

# Notice the blank line above. Code should continue on this line.
```
Toutes les docstrings doivent avoir la même longueur maximale de caractères que les commentaires (72 caractères). Les Docstrings peuvent être subdivisées en trois grandes catégories :
- Classes et méthodes de classe
- Paquets, modules et fonctions
- Scripts et fonctions

#### Classe Docstrings
Les docstrings de classe sont créés pour la classe elle-même, ainsi que pour toutes les méthodes de classe. Les docstrings sont placés immédiatement après la classe ou la méthode de classe indentée d'un niveau :
```python
class SimpleClass:
    """Class docstrings go here."""

    def say_hello(self, name: str):
        """Class method docstrings go here."""

        print(f'Hello {name}')
```
Les docstrings de classe doivent contenir les informations suivantes :
- Un bref résumé de son objectif et de son comportement
- Toutes méthodes publiques, accompagnées d'une brève description
- Toutes les propriétés de classe (attributs)
- Tout ce qui concerne le interface pour les sous-classeurs, si la classe est destinée à être sous-classée

Les docstrings de méthode de classe doivent contenir les éléments suivants :
- Une brève description de ce qu'est la méthode et à quoi elle sert
- Tous les arguments (obligatoires et facultatifs) transmis, y compris les arguments de mots-clés
- Étiquetez tous les arguments considérés comme facultatifs ou ayant une valeur par défaut
- Tous les effets secondaires qui surviennent lors de l’exécution de la méthode
- Toutes exceptions qui sont soulevées
- Toute restriction quant au moment où la méthode peut être appelée

Prenons un exemple simple d’une classe de données qui représente un animal. Cette classe contiendra quelques propriétés de classe, des propriétés d'instance, a __init__, et un seul méthode d'instance:
```python
class Animal:
    """
    A class used to represent an Animal

    ...

    Attributes
    ----------
    says_str : str
        a formatted string to print out what the animal says
    name : str
        the name of the animal
    sound : str
        the sound that the animal makes
    num_legs : int
        the number of legs the animal has (default 4)

    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """

    says_str = "A {name} says {sound}"

    def __init__(self, name, sound, num_legs=4):
        """
        Parameters
        ----------
        name : str
            The name of the animal
        sound : str
            The sound the animal makes
        num_legs : int, optional
            The number of legs the animal (default is 4)
        """

        self.name = name
        self.sound = sound
        self.num_legs = num_legs

    def says(self, sound=None):
        """Prints what the animals name is and what sound it makes.

        If the argument `sound` isn't passed in, the default Animal
        sound is used.

        Parameters
        ----------
        sound : str, optional
            The sound the animal makes (default is None)

        Raises
        ------
        NotImplementedError
            If no sound is set for the animal or passed in as a
            parameter.
        """

        if self.sound is None and sound is None:
            raise NotImplementedError("Silent Animals are not supported!")

        out_sound = self.sound if sound is None else sound
        print(self.says_str.format(name=self.name, sound=out_sound))
```

#### Docstrings de paquet et de module

Les docstrings du paquet doivent être placés en haut du fichier `__init__.py`. Cette docstring doit répertorier les modules et sous-paquets exportés par le package.

Les docstrings de module sont similaires aux docstrings de classe. Au lieu de documenter les classes et les méthodes, il s'agit désormais du module et de toutes les fonctions qu'il contient. Les docstrings du module sont placés en haut du fichier avant même toute importation. Les docstrings du module doivent inclure les éléments suivants :
- Une brève description du module et de son objectif
- Une liste de toutes les classes, exceptions, fonctions et tout autre objet exporté par le module

La docstring d'une fonction de module doit inclure les mêmes éléments qu'une méthode de classe :
- Une brève description de ce qu'est la fonction et à quoi elle sert
- Tous les arguments (obligatoires et facultatifs) transmis, y compris les arguments de mots-clés
- Étiquetez tous les arguments considérés comme facultatifs
- Tous les effets secondaires qui surviennent lors de l'exécution de la fonction
- Toutes exceptions qui sont soulevées
- Toute restriction quant au moment où la fonction peut être appelée

#### Docstrings de scripts

Les scripts sont considérés comme des exécutables à fichier unique exécutés à partir de la console. Les docstrings pour les scripts sont placés en haut du fichier et doivent être suffisamment bien documentés pour que les utilisateurs puissent avoir une compréhension suffisante de la façon d'utiliser le script. Il doit être utilisable pour son message “d'utilisation”, lorsque l'utilisateur transmet incorrectement un paramètre ou utilise le -h option.

Si vous utilisez `argparse`, vous pouvez alors omettre la documentation spécifique aux paramètres, en supposant qu'elle ait été correctement documentée dans le paramètre `help` dde la fonction `add_argument`.

Enfin, toutes les importations personnalisées ou tierces doivent être répertoriées dans les docstrings pour permettre aux utilisateurs de savoir quels packages peuvent être nécessaires à l'exécution du script. Voici un exemple de script utilisé pour imprimer simplement les en-têtes de colonnes d'une feuille de calcul :
```python
"""Spreadsheet Column Printer

This script allows the user to print to the console all columns in the
spreadsheet. It is assumed that the first row of the spreadsheet is the
location of the columns.

This tool accepts comma separated value files (.csv) as well as excel
(.xls, .xlsx) files.

This script requires that `pandas` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * get_spreadsheet_cols - returns the column headers of the file
    * main - the main function of the script
"""

import argparse

import pandas as pd


def get_spreadsheet_cols(file_loc, print_cols=False):
    """Gets and prints the spreadsheet's header columns

    Parameters
    ----------
    file_loc : str
        The file location of the spreadsheet
    print_cols : bool, optional
        A flag used to print the columns to the console (default is
        False)

    Returns
    -------
    list
        a list of strings used that are the header columns
    """

    file_data = pd.read_excel(file_loc)
    col_headers = list(file_data.columns.values)

    if print_cols:
        print("\n".join(col_headers))

    return col_headers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'input_file',
        type=str,
        help="The spreadsheet file to pring the columns of"
    )
    args = parser.parse_args()
    get_spreadsheet_cols(args.input_file, print_cols=True)


if __name__ == "__main__":
    main()
```

### Formats Docstring

Vous avez peut-être remarqué que, tout au long des exemples donnés dans ce tutoriel, il y a eu un formatage spécifique avec des éléments communs : Arguments, Returns, et Attributes. Il existe des formats de docstrings spécifiques qui peuvent être utilisés pour aider les analyseurs de docstrings et les utilisateurs à disposer d'un format familier et connu. Le formatage utilisé dans les exemples de ce didacticiel sont des docstrings de style NumPy/SciPy. Certains des formats les plus courants sont les suivants :
| Type de formatage |	Description |	Reconnu par Sphiynx |Spécification formelle |
|---|---|---|---|
| Chaînes de documents | Google	Forme de documentation recommandée par Google |	Oui |	Non |
| reStructuredText |	Norme officielle de documentation Python ; pas adaptée aux débutants mais riche en fonctionnalités |	Oui	| Oui |
| Chaînes de documents NumPy/SciPy |	Combinaison de reStructuredText et de Google Docstrings par NumPy |	Oui |	Oui |
| Epytext	| Une adaptation Python d'Epydoc | Idéal pour les développeurs Java	| Pas officiellement | Oui |

Le choix du format docstring dépend de vous, mais vous devez vous en tenir au même format tout au long de votre document/projet. Voici des exemples de chaque type pour vous donner une idée de l’apparence de chaque format de documentation.

#### Exemple de Google Docstrings
```python
"""Gets and prints the spreadsheet's header columns

Args:
    file_loc (str): The file location of the spreadsheet
    print_cols (bool): A flag used to print the columns to the console
        (default is False)

Returns:
    list: a list of strings representing the header columns
"""
```

#### Exemple de texte restructuré
```python
"""Gets and prints the spreadsheet's header columns

:param file_loc: The file location of the spreadsheet
:type file_loc: str
:param print_cols: A flag used to print the columns to the console
    (default is False)
:type print_cols: bool
:returns: a list of strings representing the header columns
:rtype: list
"""
```

#### Exemple de docstrings NumPy/SciPy
```python
"""Gets and prints the spreadsheet's header columns

Parameters
----------
file_loc : str
    The file location of the spreadsheet
print_cols : bool, optional
    A flag used to print the columns to the console (default is False)

Returns
-------
list
    a list of strings representing the header columns
"""
```

#### Exemple d'Epytext
```python
"""Gets and prints the spreadsheet's header columns

@type file_loc: str
@param file_loc: The file location of the spreadsheet
@type print_cols: bool
@param print_cols: A flag used to print the columns to the console
    (default is False)
@rtype: list
@returns: a list of strings representing the header columns
"""
```

## Documenter vos projets Python

Les projets Python se présentent sous toutes sortes de formes, de tailles et d’objectifs. La façon dont vous documentez votre projet doit être adaptée à votre situation spécifique. Gardez à l’esprit qui seront les utilisateurs de votre projet et adaptez-vous à leurs besoins. Selon le type de projet, certains aspects de la documentation sont recommandés. Le général mise en page du projet et sa documentation doivent être les suivantes :
```
project_root/
│
├── project/  # Project source code
├── docs/
├── README
├── HOW_TO_CONTRIBUTE
├── CODE_OF_CONDUCT
├── examples.py
```

Les projets peuvent être généralement subdivisés en trois grands types : privés, partagés et publics/open source.

### Projets privés

Les projets privés sont des projets destinés à un usage personnel uniquement et ne sont généralement pas partagés avec d'autres utilisateurs ou développeurs. La documentation peut être assez légère sur ce type de projets. Il y a quelques pièces recommandées à ajouter si nécessaire :
- Lisez-moi (README): Un bref résumé du projet et de son objectif. Inclure toutes les exigences particulières pour l’installation ou l’exploitation du projet.
- examples.py: Un fichier de script Python qui donne des exemples simples de la façon d'utiliser le projet.

N'oubliez pas que même si les projets privés vous sont destinés personnellement, vous êtes également considéré comme un utilisateur. Pensez à tout ce qui pourrait vous prêter à confusion par la suite et assurez-vous de les capturer dans les commentaires, les docstrings ou le readme.

### Projets partagés

Les projets partagés sont des projets dans lesquels vous collaborez avec quelques autres personnes dans le développement et/ou l'utilisation du projet. Le “client” ou l'utilisateur du projet continue d'être vous-même et les personnes qui utilisent également le projet.

La documentation doit être un peu plus rigoureuse que nécessaire pour un projet privé, principalement pour aider à intégrer de nouveaux membres au projet ou alerter les contributeurs/utilisateurs des nouveaux changements apportés au projet. Certaines des parties recommandées à ajouter au projet sont les suivantes :
- Lisez-moi: Un bref résumé du projet et de son objectif. Inclure toutes les exigences particulières pour l’installation ou l’exploitation du projet. De plus, ajoutez toutes les modifications majeures depuis la version précédente.
- examples.py: Un fichier de script Python qui donne des exemples simples de la façon d'utiliser les projets.
- Comment contribuer : Cela devrait inclure la manière dont les nouveaux contributeurs au projet peuvent commencer à contribuer.

### Projets publics et open source

Les projets publics et Open Source sont des projets destinés à être partagés avec un large groupe d'utilisateurs et peuvent impliquer de grandes équipes de développement. Ces projets devraient accorder une priorité aussi élevée à la documentation du projet qu’au développement proprement dit du projet lui-même. Certaines des parties recommandées à ajouter au projet sont les suivantes :
- Lisez-moi: Un bref résumé du projet et de son objectif. Inclure toutes les exigences particulières pour l’installation ou l’exploitation des projets. De plus, ajoutez toutes les modifications majeures depuis la version précédente. Enfin, ajoutez des liens vers d’autres documentations, des rapports de bogues et toute autre information importante pour le projet. Dan Bader a mis ensemble un super tutoriel sur ce que tout doit être inclus dans votre readme.
- Comment contribuer : Cela devrait inclure la manière dont les nouveaux contributeurs au projet peuvent aider. Cela inclut le développement de nouvelles fonctionnalités, la résolution de problèmes connus, l’ajout de documentation, l’ajout de nouveaux tests ou le signalement de problèmes.
- Code de conduite : Définit comment les autres contributeurs doivent se traiter mutuellement lors du développement ou de l'utilisation de votre logiciel. Cela indique également ce qui se passera si ce code est cassé. Si vous utilisez Github, un code de conduite modèle peut être généré avec la formulation recommandée. Pour les projets Open Source en particulier, pensez à ajouter ceci.
- Licence: Un fichier en texte clair qui décrit la licence utilisée par votre projet. Pour les projets Open Source en particulier, pensez à ajouter ceci.
- docs: Un dossier qui contient une documentation supplémentaire. La section suivante décrit plus en détail ce qui doit être inclus et comment organiser le contenu de ce dossier.

### Les quatre principales sections du dossier de documentation

Daniele Procida mentionne que tous les projets devraient comporter les quatre sections principales suivantes pour vous aider à concentrer votre travail :
- Tutoriels: Des leçons qui emmènent le lecteur par la main à travers une série d’étapes pour réaliser un projet (ou un exercice significatif). Orienté vers l'apprentissage de l'utilisateur.
- Guides pratiques: Des guides qui guident le lecteur à travers les étapes nécessaires pour résoudre un problème courant (recettes axées sur les problèmes).
- Références: Explications qui clarifient et éclairent un sujet particulier. Orienté vers la compréhension.
- Explications: Descriptions techniques des machines et de leur fonctionnement (classes clés, fonctions, API, etc.). Pensez à l’article de l’Encyclopédie.

## Outils et ressources de documentation

Documenter votre code, en particulier les grands projets, peut être intimidant. Heureusement, il existe quelques outils et références pour vous aider à démarrer :

| Outil |	Description |
|---|---|
| Sphinx |	Une collection d'outils pour générer automatiquement de la documentation dans plusieurs formats |
| Epydoc |	Un outil pour générer de la documentation API pour les modules Python en fonction de leurs docstrings |
| ReadTheDocs |	Création, gestion des versions et hébergement automatiques de vos documents pour vous |
| Doxygène |	Un outil pour générer de la documentation prenant en charge Python ainsi que plusieurs autres langages |
| MkDocs |	Un générateur de site statique pour aider à créer la documentation du projet à l'aide du langage Markdown |
| pycco	| Un générateur de documentation “rapide et sale” qui affiche le code et la documentation côte à côte |
| doctest |	Un module de bibliothèque standard pour exécuter des exemples d'utilisation sous forme de tests automatisés |

## Ressources

Quelques tutoriels, vidéos et articles supplémentaires :

- Carol Willing : [Sphinx pratique, PyCon 2018](https://www.youtube.com/watch?v=0ROZRNZkPS8)
- Daniele Procida : [Développement axé sur la documentation, Leçons du projet Django, PyCon 2016](https://www.youtube.com/watch?v=bQSR1UpUdFQ)
- Eric Holscher : [Documenter votre projet avec Sphinx & Read the Docs, PyCon 2016](https://www.youtube.com/watch?v=hM4I58TA72g)
- Titus Brown, Luiz Irber : [Créer, construire, tester et documenter un projet Python : un HOWTO pratique, PyCon 2016](https://youtu.be/SUt3wT43AeM?t=6299)
- [Documentation officielle](http://docutils.sourceforge.net/rst.html) de reStructuredText
- [Introduction au texte restructuré](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) de Sphinx
- [Documenter des projets Python avec Sphinx et ReadTheDocs](https://realpython.com/courses/python-sphinx/)
- [Documentez votre code Python et vos projets avec ChatGPT](https://realpython.com/document-python-code-with-chatgpt/)

Quelques projet sbien documentés :
- [Django](https://docs.djangoproject.com/en/2.0/)
- [requests](https://requests.readthedocs.io/en/master/)
- [click](http://click.pocoo.org/dev/)
- [pandas](http://pandas.pydata.org/pandas-docs/stable/)
