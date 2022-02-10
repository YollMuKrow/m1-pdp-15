from abc import ABC, abstractmethod

# builder pattern
from robocup.dynamic_object.state import AlliesVision, OpponentsVision, DefaultRelativeState
from robocup.utility.func_utility import invert_dict
from robocup.creation.factory import AdultSizeCreator, KidSizeCreator
from robocup.spec.specification import RoboCupSpecification
from robocup.dynamic_object.team import Team
from robocup.game import DelayScreen, Game
from robocup.dynamic_object.ball import *
from robocup.rules.field import *
from robocup.rules.referee import Referee

# Utiliser pour retrouver la couleur de l'agent entraîné (l'agent qui récupère la première action depuis step(action, *args)
#
#     Paramètres
#     ----------
#     team_left_color_num_action_dict : Dict[str, int]
#         Dictionnaire pour l'équipe de gauche {clé=couleur_agent, valeur=numéro de l'action dans step)
#         team_left_color_num_action_dict = {'yellow': 0, 'green': 1} par exemple
#     team_right_color_num_action_dict : Dict[str, int]
#          Dictionnaire pour l'équipe de droite {clé=couleur_agent, valeur=numéro de l'action dans step)
#     print_cols : bool, optional
#         A flag used to print the columns to the console (default is
#         False)
#
#     Sorties
#     -------
#     str
#         couleur de l'agent en chaîne de caractère par exemple 'yellow'

def find_color_agent_being_trained(team_left_color_num_action_dict: Dict[str, int],
                                   team_right_color_num_action_dict: Dict[str, int]) -> str:
    my_inverted_team_left_color_num_action_dict = invert_dict(team_left_color_num_action_dict)
    my_inverted_team_right_color_num_action_dict = invert_dict(team_right_color_num_action_dict)

    color_agent = ''

    if my_inverted_team_left_color_num_action_dict.__contains__(0):
        color_agent = my_inverted_team_left_color_num_action_dict[0]
    elif my_inverted_team_right_color_num_action_dict.__contains__(0):
        color_agent = my_inverted_team_right_color_num_action_dict[0]

    return color_agent

# Utiliser pour créer un objet RelativeState (pour un agent)
#
#     Paramètres
#     ----------
#     allies_vision_enable : bool
#         booléen pour indiquer si la vision des alliés est activée
#     opponents_vision_enable : bool
#         booléen pour indiquer si la vision des opposants est activée

#     Sorties
#     -------
#     RelativeState
#         un objet RelativeState


def create_relative_state(allies_vision_enable: bool = True, opponents_vision_enable: bool = True) -> RelativeState:
    relative_state = AlliesVision(OpponentsVision(DefaultRelativeState()))

    # utilisation du design pattern Decorator

    if not allies_vision_enable and not opponents_vision_enable:
        relative_state = DefaultRelativeState()

    elif not allies_vision_enable:

        relative_state = OpponentsVision(DefaultRelativeState())

    elif not opponents_vision_enable:

        relative_state = AlliesVision(DefaultRelativeState())

    return relative_state

# Défini les services communs pour les classes concrètes Builder
# Ne spécifie pas le produit retourné par un Builder, celui-ci peut être différent d'un Builder à un autre

class GameBuilder(ABC):


    @abstractmethod
    def set_team_left_color_num_action_dict(self, team_left_color_num_action_dict: Dict[str, int]) -> None:
        pass

    @abstractmethod
    def set_team_right_color_num_action_dict(self, team_right_color_num_action_dict: Dict[str, int]) -> None:
        pass

    # Utiliser pour créer un objet FieldModel
    #
    #     Paramètres
    #     ----------
    #     Sorties
    #     -------

    @abstractmethod
    def create_field_model(self) -> None:
        pass

    # Utiliser pour créer un objet FieldModel pour l'équipe de gauche
    #
    #     Paramètres
    #     ----------
    #     allies_vision_enable: bool
    #           booléen pour indiquer si la vision des alliés est activée
    #     opponents_vision_enable : bool
    #           booléen pour indiquer si la vision des opposants est activée
    #     Sorties
    #     -------

    @abstractmethod
    def create_team_left(self, allies_vision_enable: bool = True,
                         opponents_vision_enable: bool = True) -> None:
        pass

    # identique à la méthode précédente mais pour l'équipe de droite

    @abstractmethod
    def create_team_right(self, allies_vision_enable: bool = True,
                          opponents_vision_enable: bool = True) -> None:
        pass

    # Créer la balle du jeu
    #
    #     Paramètres
    #     ----------
    #     Sorties
    #     -------

    @abstractmethod
    def create_ball(self) -> None:
        pass

    # Utiliser pour créer un objet Referee
    #
    #     Paramètres
    #     ----------
    #     penalty_collision_enable: bool
    #           booléen pour indiquer si la pénalité de la collision entre agents adverses est activée (non implémenter)
    #     collision_enable: bool
    #         booléen pour indiquer si la collision entre agents est activée
    #     Sorties
    #     -------


    @abstractmethod
    def create_referee(self, penalty_collision_enable: bool = False,
                       collision_enable: bool = True) -> None:
        pass

    # Utiliser pour créer un objet DelayScreen
    #
    #     Paramètres
    #     ----------
    #     Sorties
    #     -------

    @abstractmethod
    def create_delay_screen(self) -> None:
        pass

    # Utiliser pour récupérer la couleur de l'agent entraîné
    #
    #     Paramètres
    #     ----------
    #     Sorties
    #     -------

    @abstractmethod
    def set_color_agent_being_trained(self) -> None:
        pass

    # Classe utilisée pour représenter un Builder AdultSize
    #
    # Attributs
    # ----------
    # _field_model : FieldModel
    #     un objet FieldModel pour représenter le terrain
    # _team_left : Team
    #     un objet Team pour représenter l'équipe de gauche
    # _referee : Referee
    #     un objet Referee pour représenter l'arbitre du jeu
    # _delay_screen : DelayScreen
    #     un objet DelayScreen
    # _color_agent_being_trained : str
    #     une chaîne de caractère pour représenter la couleur de l'agent entraîné
    # _team_left_color_num_action_dict : Dict[str, int]
    #     dictionnaire pour l'équipe de gauche {clé=couleur_agent, valeur=numéro de l'action dans step)
    #     team_left_color_num_action_dict = {'yellow': 0, 'green': 1} par exemple
    # _team_right_color_num_action_dict : Dict[str, int]
    #     dictionnaire pour l'équipe de droite {clé=couleur_agent, valeur=numéro de l'action dans step)
    # _game: Game
    #     l'objet Game à construire
    # _robocup_specification: RoboCupSpecification
    #     les données de spécification pour construire le jeu

class AdultSizeGameBuilder(GameBuilder):

    def __init__(self):
        self._field_model: FieldModel = None
        self._team_left: Team = None
        self._team_right: Team = None
        self._ball: Ball = None
        self._referee: Referee = None
        self._delay_screen: DelayScreen = None
        self._color_agent_being_trained: str = ''
        self._team_left_color_num_action_dict: Dict[str, int] = {}
        self._team_right_color_num_action_dict: Dict[str, int] = {}
        self._game: Game = None
        self._robocup_specification: RoboCupSpecification = AdultSizeCreator().create_specification()

    def set_team_left_color_num_action_dict(self, team_left_color_num_action_dict: Dict[str, int]) -> None:
        self._team_left_color_num_action_dict = team_left_color_num_action_dict

    def set_team_right_color_num_action_dict(self, team_right_color_num_action_dict: Dict[str, int]) -> None:
        self._team_right_color_num_action_dict = team_right_color_num_action_dict

    def create_field_model(self) -> None:
        self._field_model = FieldModel(self._robocup_specification.field_specification)

    def _create_color_agent_dict(self, team_left: bool, direction: int, origin_angle: float,
                                 allies_vision_enable: bool = True, opponents_vision_enable: bool = True) -> \
            Dict[str, Agent]:

        color_agent_dict = {}

        y_add = 0

        if team_left:
            color_num_action_dict = self._team_left_color_num_action_dict
        else:
            color_num_action_dict = self._team_right_color_num_action_dict

        radius = self._robocup_specification.robot_specification.diameter / 2

        for color_agent in color_num_action_dict.keys():
            relative_state = create_relative_state(allies_vision_enable=allies_vision_enable,
                                                   opponents_vision_enable=opponents_vision_enable)

            color_agent_dict[color_agent] = \
                Agent(direction=direction, x=direction * self._field_model.scale_meter,
                      y=((self._field_model.field_play_area_y - self._field_model.field_play_area_height / 2)
                         - self._field_model.scale_meter / 2)
                        + y_add * self._field_model.scale_meter,
                      radius=radius * self._field_model.scale_meter,
                      color_agent=color_agent, origin_angle=origin_angle,
                      relative_state=relative_state)
            y_add = y_add + 1

        return color_agent_dict

    # l'angle de rotation et la direction sont différents d'une équipe à une autre

    def create_team_left(self, allies_vision_enable: bool = True,
                         opponents_vision_enable: bool = True) -> None:
        team_left_color_agent_dict = \
            self._create_color_agent_dict(team_left=True,
                                          direction=-1, origin_angle=0, allies_vision_enable=allies_vision_enable,
                                          opponents_vision_enable=opponents_vision_enable)

        self._team_left = Team('red', color_num_action_dict=self._team_left_color_num_action_dict,
                               color_agent_dict=team_left_color_agent_dict)

    def create_team_right(self, allies_vision_enable: bool = True,
                          opponents_vision_enable: bool = True) -> None:
        team_right_color_agent_dict = self._create_color_agent_dict(
            team_left=False,
            direction=1, origin_angle=180, allies_vision_enable=allies_vision_enable,
            opponents_vision_enable=opponents_vision_enable)

        self._team_right = Team('blue', color_num_action_dict=self._team_right_color_num_action_dict,
                                color_agent_dict=team_right_color_agent_dict)

    def create_ball(self) -> None:
        radius = (self._robocup_specification.ball_specification.diameter / 2)
        self._ball = Ball(0, self._field_model.field_play_area_y - self._field_model.field_play_area_height / 2,
                          radius * self._field_model.scale_meter, color='yellow')

    def create_referee(self, penalty_collision_enable: bool = False, collision_enable: bool = True) -> None:
        self._referee = Referee(self._team_left, self._team_right, self._field_model, self._ball)
        self._referee.penalty_collision_enable = penalty_collision_enable
        self._referee.collision_enable = collision_enable

    def create_delay_screen(self) -> None:
        self._delay_screen = DelayScreen()

    def set_color_agent_being_trained(self) -> None:
        self._color_agent_being_trained = \
            find_color_agent_being_trained(team_left_color_num_action_dict=self._team_left_color_num_action_dict,
                                           team_right_color_num_action_dict=self._team_right_color_num_action_dict)

    # retourne l'objet Game (le produit doit être récupéré après la construction)

    @property
    def game(self) -> Game:
        self._game = Game(field_model=self._field_model, team_left=self._team_left, team_right=self._team_right,
                          ball=self._ball, referee=self._referee, delay_screen=self._delay_screen,
                          color_agent_being_trained=self._color_agent_being_trained)
        return self._game


    # Classe utilisée pour représenter un Builder KidSize
    #
    # Attributs
    # ----------
    # _field_model : FieldModel
    #     un objet FieldModel pour représenter le terrain
    # _team_left : Team
    #     un objet Team pour représenter l'équipe de gauche
    # _referee : Referee
    #     un objet Referee pour représenter l'arbitre du jeu
    # _delay_screen : DelayScreen
    #     un objet DelayScreen
    # _color_agent_being_trained : str
    #     une chaîne de caractère pour représenter la couleur de l'agent entraîné
    # _team_left_color_num_action_dict : Dict[str, int]
    #     dictionnaire pour l'équipe de gauche {clé=couleur_agent, valeur=numéro de l'action dans step)
    #     team_left_color_num_action_dict = {'yellow': 0, 'green': 1} par exemple
    # _team_right_color_num_action_dict : Dict[str, int]
    #     dictionnaire pour l'équipe de droite {clé=couleur_agent, valeur=numéro de l'action dans step)
    # _game: Game
    #     l'objet Game à construire
    # _robocup_specification: RoboCupSpecification
    #     les données de spécification pour construire le jeu

class KidSizeGameBuilder(GameBuilder):

    def __init__(self):
        self._field_model: FieldModel = None
        self._team_left: Team = None
        self._team_right: Team = None
        self._ball: Ball = None
        self._referee: Referee = None
        self._delay_screen: DelayScreen = None
        self._color_agent_being_trained: str = ''
        self._team_left_color_num_action_dict: Dict[str, int] = {}
        self._team_right_color_num_action_dict: Dict[str, int] = {}
        self._game: Game = None
        self._robocup_specification: RoboCupSpecification = KidSizeCreator().create_specification()

    def set_team_left_color_num_action_dict(self, team_left_color_num_action_dict: Dict[str, int]) -> None:
        self._team_left_color_num_action_dict = team_left_color_num_action_dict

    def set_team_right_color_num_action_dict(self, team_right_color_num_action_dict: Dict[str, int]) -> None:
        self._team_right_color_num_action_dict = team_right_color_num_action_dict

    def create_field_model(self) -> None:
        self._field_model = FieldModel(self._robocup_specification.field_specification)

    def _create_color_agent_dict(self, team_left: bool, direction: int, origin_angle: float,
                                 allies_vision_enable: bool = True, opponents_vision_enable: bool = True) -> \
            Dict[str, Agent]:

        color_agent_dict = {}

        y_add = 0

        if team_left:
            color_num_action_dict = self._team_left_color_num_action_dict
        else:
            color_num_action_dict = self._team_right_color_num_action_dict

        radius = self._robocup_specification.robot_specification.diameter / 2

        for color_agent in color_num_action_dict.keys():
            relative_state = create_relative_state(allies_vision_enable=allies_vision_enable,
                                                   opponents_vision_enable=opponents_vision_enable)

            color_agent_dict[color_agent] = \
                Agent(direction=direction, x=direction * self._field_model.scale_meter,
                      y=((self._field_model.field_play_area_y - self._field_model.field_play_area_height / 2)
                         - self._field_model.scale_meter / 2)
                        + y_add * self._field_model.scale_meter,
                      radius=radius * self._field_model.scale_meter,
                      color_agent=color_agent, origin_angle=origin_angle,
                      relative_state=relative_state)
            y_add = y_add + 1

        return color_agent_dict

    # l'angle de rotation et la direction sont différents d'une équipe à une autre

    def create_team_left(self, allies_vision_enable: bool = True,
                         opponents_vision_enable: bool = True) -> None:
        team_left_color_agent_dict = \
            self._create_color_agent_dict(team_left=True,
                                          direction=-1, origin_angle=0, allies_vision_enable=allies_vision_enable,
                                          opponents_vision_enable=opponents_vision_enable)

        self._team_left = Team('red', color_num_action_dict=self._team_left_color_num_action_dict,
                               color_agent_dict=team_left_color_agent_dict)

    def create_team_right(self, allies_vision_enable: bool = True,
                          opponents_vision_enable: bool = True) -> None:
        team_right_color_agent_dict = self._create_color_agent_dict(
            team_left=False,
            direction=1, origin_angle=180, allies_vision_enable=allies_vision_enable,
            opponents_vision_enable=opponents_vision_enable)

        self._team_right = Team('blue', color_num_action_dict=self._team_right_color_num_action_dict,
                                color_agent_dict=team_right_color_agent_dict)

    def create_ball(self) -> None:
        radius = (self._robocup_specification.ball_specification.diameter / 2)
        self._ball = Ball(0, self._field_model.field_play_area_y - self._field_model.field_play_area_height / 2,
                          radius * self._field_model.scale_meter, color='yellow')

    def create_referee(self, penalty_collision_enable: bool = False, collision_enable: bool = True) -> None:
        self._referee = Referee(self._team_left, self._team_right, self._field_model, self._ball)
        self._referee.penalty_collision_enable = penalty_collision_enable
        self._referee.collision_enable = collision_enable

    def create_delay_screen(self) -> None:
        self._delay_screen = DelayScreen()

    def set_color_agent_being_trained(self) -> None:
        self._color_agent_being_trained = \
            find_color_agent_being_trained(team_left_color_num_action_dict=self._team_left_color_num_action_dict,
                                           team_right_color_num_action_dict=self._team_right_color_num_action_dict)

    # retourne l'objet Game (le produit doit être récupéré après la construction)

    @property
    def game(self) -> Game:
        self._game = Game(field_model=self._field_model, team_left=self._team_left, team_right=self._team_right,
                          ball=self._ball, referee=self._referee, delay_screen=self._delay_screen,
                          color_agent_being_trained=self._color_agent_being_trained)
        return self._game


    # Classe utilisée pour diriger les étapes d'éxecution d'un Builder spécifique
    #
    # Attributs
    # ----------
    # _team_left_color_num_action_dict : Dict[str, int]
    #     dictionnaire pour l'équipe de gauche {clé=couleur_agent, valeur=numéro de l'action dans step)
    #     team_left_color_num_action_dict = {'yellow': 0, 'green': 1} par exemple
    # _team_right_color_num_action_dict : Dict[str, int]
    #     dictionnaire pour l'équipe de droite {clé=couleur_agent, valeur=numéro de l'action dans step)
    # _builder: GameBuilder
    #     le builder à utiliser pour construire le jeu

class GameDirector:

    def __init__(self, team_left_color_num_action_dict: Dict[str, int],
                 team_right_color_num_action_dict: Dict[str, int]) -> None:
        self._team_left_color_num_action_dict = team_left_color_num_action_dict
        self._team_right_color_num_action_dict = team_right_color_num_action_dict
        self._builder = None

    @property
    def builder(self) -> GameBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: GameBuilder) -> None:
        self._builder = builder

    #     Démarre la construction d'un jeu
    #
    #     Paramètres
    #     ----------
    #     build_configuration: List[str]
    #         configuration du build, par exemple configuration=['collision_disable', allies_vision_disable']
    #     Sorties
    #     -------
    def start_build(self, build_configuration: List[str]) -> None:

        collision_enable = True
        penalty_collision_enable = False

        allies_vision_enable = True
        opponents_vision_enable = True

        if build_configuration.__contains__('collision_disable') and build_configuration.__contains__(
                'penalty_collision_enable'):
            collision_enable = False
            penalty_collision_enable = False

        if build_configuration.__contains__('collision_disable'):
            collision_enable = False

        if build_configuration.__contains__('penalty_collision_enable'):
            penalty_collision_enable = True

        if build_configuration.__contains__('allies_vision_disable'):
            allies_vision_enable = False

        if build_configuration.__contains__('opponents_vision_disable'):
            opponents_vision_enable = False

        self._build_default_game(collision_enable=collision_enable, penalty_collision_enable=penalty_collision_enable,
                                 allies_vision_enable=allies_vision_enable,
                                 opponents_vision_enable=opponents_vision_enable)

    #     Construit le jeu
    #
    #     Paramètres
    #     ----------
    #     collision_enable: bool
    #         booléen pour indiquer si la collision entre agents est activée
    #     penalty_collision_enable: bool
    #           booléen pour indiquer si la pénalité de la collision entre agents adverses est activée (non implémenter)
    #     allies_vision_enable : bool
    #         booléen pour indiquer si la vision des alliés est activée
    #     opponents_vision_enable : bool
    #         booléen pour indiquer si la vision des opposants est activ
    #     Sorties
    #     -------


    def _build_default_game(self, collision_enable: bool = True, penalty_collision_enable: bool = False,
                            allies_vision_enable: bool = True, opponents_vision_enable: bool = True) -> None:

        self.builder.set_team_left_color_num_action_dict(self._team_left_color_num_action_dict)
        self.builder.set_team_right_color_num_action_dict(self._team_right_color_num_action_dict)

        self.builder.create_field_model()
        self.builder.create_team_left(
                                      allies_vision_enable=allies_vision_enable,
                                      opponents_vision_enable=opponents_vision_enable)
        self.builder.create_team_right(
                                       allies_vision_enable=allies_vision_enable,
                                       opponents_vision_enable=opponents_vision_enable)
        self.builder.create_ball()
        self.builder.create_referee(penalty_collision_enable=penalty_collision_enable,
                                    collision_enable=collision_enable)
        self.builder.create_delay_screen()
        self.builder. \
            set_color_agent_being_trained()
