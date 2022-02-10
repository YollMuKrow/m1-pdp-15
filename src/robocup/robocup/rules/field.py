from typing import Dict

from robocup.spec.specification import FieldSpecification


#   Classe modèle du terrain, elle réprèsente les données du terrain
#   Elle s'adapte en fonction de la taille de la fenêtre
#   On peut réduire l'espace d'observations en augmentant le facteur de rétrécissement de la fenêtre

class FieldModel:

    def __init__(self, field_specification: FieldSpecification):
        self._field_specification: FieldSpecification = field_specification

        #   L'espace de coordonnées cartésiennes dans lequel les agents
        #   évoluent est plus petit que les dimensions réelles de la fenêtre

        factor_cartesian = 4

        self._field_width: float = self._field_specification.field_width * factor_cartesian
        self._field_height: float = self._field_specification.field_height * factor_cartesian

        #    Échelle d'un mètre dans le repaire cartésien
        #    Par exemple avec field_width=64, real_field_width_meter_adult_size=16, résultat = 4
        #    -> intervalle de longueur 4 coordonnées en abscisse est équivalent à un mètre

        self._scale_meter: float = self._field_width / self._field_specification.field_width

        #   Coordonnées en haut à gauche du terrain

        self._field_x: float = (-self._field_width / 2)
        self._field_y: float = self._field_height

        self.border_strip_width: float = self._field_specification.border_strip_width * self.scale_meter

        #   Dimensions du terrain moins les touches

        self._field_play_area_width: float = self._field_width - (2 * self.border_strip_width)
        self._field_play_area_height: float = self._field_height - (2 * self.border_strip_width)

        #   Coordonnées en haut à gauche de la zone de jeu (à partir du corner haut gauche)

        self._field_play_area_x: float = self._field_x + self.border_strip_width
        self._field_play_area_y: float = self._field_y - self.border_strip_width

        self.side_line_data: Dict[str, float] = {}

        #   Densité des traits blancs

        self._field_line_density: float = self._field_specification.line_density * self.scale_meter

        self._init_side_line()

        self.middle_line_data: Dict[str, float] = {}

        self._init_middle_line(self._field_specification.center_circle_diameter,
                               self._field_specification.center_circle_diameter_density_factor)

        self.penalty_area_data: Dict[str, float] = {}

        real_field_play_area_width = self._field_specification.field_width - 2
        real_field_play_area_height = self._field_specification.field_height - 2

        real_distance_between_penalty_area_and_side_line = (real_field_play_area_height -
                                                            self._field_specification.penalty_area_height) / 2

        self._init_penalty_area(self._field_specification.penalty_area_width, self._field_specification.penalty_area_height,
                                real_distance_between_penalty_area_and_side_line)

        self.goal_area_data: Dict[str, float] = {}

        real_distance_between_goal_area_and_side_line = (real_field_play_area_height -
                                                         self._field_specification.goal_area_height) / 2

        self._init_goal_area(self._field_specification.goal_area_width, self._field_specification.goal_area_height,
                             real_distance_between_goal_area_and_side_line)

        self.goal_data: Dict[str, float] = {}

        real_distance_between_goal_and_side_line = (real_field_play_area_height - self._field_specification.goal_height) / 2

        self._init_goal(self._field_specification.goal_width, self._field_specification.goal_height,
                        self._field_specification.goal_density, real_distance_between_goal_and_side_line)

    #   Initialise les données nécessaires pour représenter les zones de touche

    def _init_side_line(self) -> None:
        self.side_line_data['side_line_x'] = self._field_play_area_x
        self.side_line_data['side_line_y'] = self._field_play_area_y

        self.side_line_data['side_line_width'] = self._field_play_area_width
        self.side_line_data['side_line_height'] = self._field_play_area_height

        self.side_line_data['x_background'] = self._field_play_area_x + self._field_line_density
        self.side_line_data['y_background'] = self._field_play_area_y - self._field_line_density

        self.side_line_data['width_background'] = self._field_play_area_width - (
                self._field_line_density * 2)
        self.side_line_data['height_background'] = self._field_play_area_height - (
                self._field_line_density * 2)

    #   Initialise les données nécessaires pour représenter le milieu de terrain

    def _init_middle_line(self, real_center_circle_diameter: float,
                          real_center_circle_diameter_density_factor: float) -> None:
        center_circle_diameter = real_center_circle_diameter * self.scale_meter

        self.middle_line_data['middle_line_x'] = (-self._field_line_density) / 2
        self.middle_line_data['middle_line_y'] = self._field_play_area_y

        self.middle_line_data['middle_line_width'] = self._field_line_density
        self.middle_line_data['middle_line_height'] = self._field_play_area_height

        self.middle_line_data['circle_x'] = 0
        self.middle_line_data['circle_y'] = self._field_y / 2
        self.middle_line_data['circle_r'] = center_circle_diameter / 2

        self.middle_line_data[
            'circle_background_r'] = center_circle_diameter / real_center_circle_diameter_density_factor

    #   Initialise les données nécessaires pour représenter les zones de penalty

    def _init_penalty_area(self, real_penalty_area_width: float, real_penalty_area_height: float,
                           real_distance_between_penalty_area_and_side_line: float) -> None:
        penalty_area_width = real_penalty_area_width * self.scale_meter
        penalty_area_height = real_penalty_area_height * self.scale_meter

        distance_between_penalty_area_and_side_line = \
            real_distance_between_penalty_area_and_side_line * self.scale_meter

        penalty_area_left_y = self._field_play_area_y - distance_between_penalty_area_and_side_line

        self.penalty_area_data['penalty_area_left_x'] = self._field_play_area_x
        self.penalty_area_data['penalty_area_y'] = penalty_area_left_y

        self.penalty_area_data['penalty_area_width'] = penalty_area_width
        self.penalty_area_data['penalty_area_height'] = penalty_area_height

        self.penalty_area_data['penalty_area_left_x_background'] = self._field_play_area_x + self._field_line_density
        self.penalty_area_data['penalty_area_y_background'] = penalty_area_left_y - self._field_line_density

        self.penalty_area_data['penalty_area_width_background'] = penalty_area_width - (self._field_line_density * 2)
        self.penalty_area_data['penalty_area_height_background'] = penalty_area_height - (self._field_line_density * 2)

        self.penalty_area_data['penalty_area_right_x'] = (self._field_play_area_x
                                                          + self._field_play_area_width) - penalty_area_width

        self.penalty_area_data['penalty_area_right_x_background'] = \
            ((self._field_play_area_x + self._field_play_area_width) - penalty_area_width) + self._field_line_density

    #   Initialise les données nécessaires pour représenter les zones de but

    def _init_goal_area(self, real_goal_area_width: float, real_goal_area_height: float,
                        real_distance_between_goal_area_and_side_line: float) -> None:
        goal_area_width = real_goal_area_width * self.scale_meter
        goal_area_height = real_goal_area_height * self.scale_meter

        distance_between_goal_area_and_side_line = real_distance_between_goal_area_and_side_line * self.scale_meter

        goal_area_left_y = self._field_play_area_y - distance_between_goal_area_and_side_line

        self.goal_area_data['goal_area_left_x'] = self._field_play_area_x
        self.goal_area_data['goal_area_y'] = goal_area_left_y

        self.goal_area_data['goal_area_width'] = goal_area_width
        self.goal_area_data['goal_area_height'] = goal_area_height

        self.goal_area_data['goal_area_left_x_background'] = self._field_play_area_x + self._field_line_density
        self.goal_area_data['goal_area_y_background'] = goal_area_left_y - self._field_line_density

        self.goal_area_data['goal_area_width_background'] = goal_area_width - (self._field_line_density * 2)
        self.goal_area_data['goal_area_height_background'] = goal_area_height - (self._field_line_density * 2)

        self.goal_area_data['goal_area_right_x'] = \
            (self._field_play_area_x + self._field_play_area_width) - goal_area_width

        self.goal_area_data['goal_area_right_x_background'] = ((self._field_play_area_x + self._field_play_area_width) -
                                                               goal_area_width) + self._field_line_density

    #   Initialise les données nécessaires pour représenter les cages de but

    def _init_goal(self, real_goal_width: float, real_goal_height: float, real_goal_density: float,
                   real_distance_between_goal_and_side_line: float) -> None:
        goal_width = real_goal_width * self.scale_meter
        goal_height = real_goal_height * self.scale_meter
        goal_density = real_goal_density * self.scale_meter

        distance_between_goal_and_side_line = real_distance_between_goal_and_side_line * self.scale_meter

        goal_left_y = self._field_play_area_y - distance_between_goal_and_side_line

        self.goal_data['goal_left_x'] = self._field_play_area_x - goal_width
        self.goal_data['goal_y'] = goal_left_y

        self.goal_data['goal_width'] = goal_width
        self.goal_data['goal_height'] = goal_height

        self.goal_data['goal_left_x_background'] = (self._field_play_area_x - goal_width) + goal_density
        self.goal_data['goal_y_background'] = goal_left_y - goal_density

        self.goal_data['goal_width_background'] = goal_width - goal_density
        self.goal_data['goal_height_background'] = goal_height - (goal_density * 2)

        self.goal_data['goal_right_x'] = (self._field_play_area_x + self._field_play_area_width)

        self.goal_data['goal_right_x_background'] = (self._field_play_area_x + self._field_play_area_width)

        self.goal_data['goal_density'] = goal_density

    #   Getter, à appeler, très utile pour créer et placer un objet dans le terrain avec les bonnes proportions
    #   Mais également pour identifier dans quelles zones du terrain sont situés les agents

    @property
    def scale_meter(self) -> float:
        return self._scale_meter

    @property
    def field_play_area_x(self) -> float:
        return self._field_play_area_x

    @property
    def field_play_area_y(self) -> float:
        return self._field_play_area_y

    @property
    def field_play_area_width(self) -> float:
        return self._field_play_area_width

    @property
    def field_play_area_height(self) -> float:
        return self._field_play_area_height

    @property
    def field_x(self) -> float:
        return self._field_x

    @property
    def field_y(self) -> float:
        return self._field_y

    @property
    def field_width(self) -> float:
        return self._field_width

    @property
    def field_height(self) -> float:
        return self._field_height

    @property
    def field_line_density(self) -> float:
        return self._field_line_density
