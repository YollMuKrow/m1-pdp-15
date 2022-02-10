# Utiliser pour vérifier si une liste contient un élément dupliqué
#
#     Paramètres
#     ----------
#     list_e: List
#           liste d'éléments quelconques
#     Sorties
#     -------
#     bool
#           renvoie vrai si la liste contient au moins un élément dupliqué, sinon faux
#

def check_if_duplicate(list_e):
    for elem in list_e:
        if list_e.count(elem) > 1:
            return True
    return False


# Inverse les clés et les valeurs d'un dictionnaire
#
#     Paramètres
#     ----------
#     dict_e: Dict
#           dictionnaire d'éléments quelconques
#     Sorties
#     -------
#     Dict
#           le dictionnaire en paramètre avec les clés et les valeurs inversés

def invert_dict(dict_e):
    return dict(map(reversed, dict_e.items()))
