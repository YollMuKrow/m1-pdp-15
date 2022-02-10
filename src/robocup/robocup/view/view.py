#   Classe vue du terrain, elle affiche les données du terrain à sa manière
from typing import Tuple, Union

from gym.envs.classic_control.rendering import FilledPolygon, PolyLine

from robocup.dynamic_object.ball import Ball
from robocup.dynamic_object.team import Team
from robocup.rules.field import FieldModel
from robocup.view.geom import Rectangle, Circle, create_canvas
from robocup.dynamic_object.player import Agent
from robocup.spec.settings import BACKGROUND_COLOR, GOAL_NET_COLOR

from colour import Color


def rgb_converter(color: str) -> Tuple[int, int, int]:
    color = Color(color)
    color_0_1_scale = color.rgb
    to_255_scale = (255, 255, 255)

    res = (int(color_0_1_scale[0] * to_255_scale[0]),
           int(color_0_1_scale[1] * to_255_scale[1]), int(color_0_1_scale[2] * to_255_scale[2]))

    return res


class Window:

    def __init__(self, window_width: int, window_height: int, field_model: FieldModel):

        #   facteur d'agrandissement de la fenêtre

        self._window_width = window_width
        self._window_height = window_height

        self._field_model: FieldModel = field_model
        self._factor_windows: float = window_width / field_model.field_width

    # Conversion d'une coordonnée en absisse dans le repaire cartésien du terrain en une coordonnée x de la fenêtre
    # réelle

    def _to_x(self, x) -> float:
        return (x + self._field_model.field_width / 2) * self._factor_windows

    # Conversion d'une coordonnée en ordonnée dans le repaire cartésien du terrain en une coordonnée y de la fenêtre
    # réelle
    def _to_y(self, y) -> float:
        return y * self._factor_windows

    #   Conversion d'un périmètre dans le repaire cartésien du terrain en un périmètre de la fenêtre réelle
    def _to_p(self, perimeter) -> float:
        return perimeter * self._factor_windows

    #   À appeler, lorsqu'on l'on souhaite créer et afficher un canvas
    #   Les coordonnées du repaire cartésien du terrain et les coordonnées de la fenêtre sont différentes

    def convert_to_windows_scale(self, x: float, y: float, perimeter_x: float = None, perimeter_y: float = None) \
            -> Union[Tuple[float, float], Tuple[float, float, float], Tuple[float, float, float, float]]:

        if perimeter_x is not None and perimeter_y is not None:
            return self._to_x(x), self._to_y(y), self._to_p(perimeter_x), self._to_p(perimeter_y)
        elif perimeter_x is not None:
            return self._to_x(x), self._to_y(y), self._to_p(perimeter_x)
        else:
            return self._to_x(x), self._to_y(y)

    @property
    def window_width(self) -> int:
        return self._window_width

    @property
    def window_height(self) -> int:
        return self._window_height


class FieldView:

    def __init__(self, field_model: FieldModel, window: Window):
        self.field_model: FieldModel = field_model

        self._window: Window = window

        self._create_sideline()
        self._create_middle_line()
        self._create_penalty_area()
        self._create_goal_area()
        self._create_goal()

    # Créer un canvas rectangle pour les touches, un deuxième canvas avec les couleurs du terrain à l'intérieur pour
    # dessiner les touches sans avoir à construire 4 canvas

    def _create_sideline(self) -> None:
        side_line_data = self.field_model.side_line_data

        x, y, width, height = self._window.convert_to_windows_scale(side_line_data['side_line_x'],
                                                                    side_line_data['side_line_y'],
                                                                    side_line_data['side_line_width'],
                                                                    side_line_data['side_line_height'])

        self.side_line: Rectangle = Rectangle(x, y, width, height, rgb_converter('white'))

        x, y, width, height = self._window.convert_to_windows_scale(side_line_data['x_background'],
                                                                    side_line_data['y_background'],
                                                                    side_line_data['width_background'],
                                                                    side_line_data['height_background'])

        self.side_line_background: Rectangle = Rectangle(x, y, width, height, BACKGROUND_COLOR)

    # Dessine le milieu de terrain, la ligne horizontale et le cercle au milieu, même principe que pour
    # _create_sideline

    def _create_middle_line(self) -> None:
        middle_line_data = self.field_model.middle_line_data

        x, y, width, height = self._window.convert_to_windows_scale(middle_line_data['middle_line_x'],
                                                                    middle_line_data['middle_line_y'],
                                                                    middle_line_data['middle_line_width'],
                                                                    middle_line_data['middle_line_height'])

        self.middle_line: Rectangle = Rectangle(x, y, width, height, rgb_converter('white'))

        x, y, r = self._window.convert_to_windows_scale(middle_line_data['circle_x'], middle_line_data['circle_y'],
                                                        middle_line_data['circle_r'])

        self.middle_line_circle: Circle = Circle(x, y, r, rgb_converter('white'))

        x, y, r = self._window.convert_to_windows_scale(middle_line_data['circle_x'], middle_line_data['circle_y'],
                                                        middle_line_data['circle_background_r'])

        self.middle_line_circle_background: Circle = Circle(x, y, r, BACKGROUND_COLOR)

    #   Dessine les deux zones de penalty, à droite et à gauche

    def _create_penalty_area(self) -> None:
        penalty_area_data = self.field_model.penalty_area_data

        x, y, width, height = self._window.convert_to_windows_scale(penalty_area_data['penalty_area_left_x'],
                                                                    penalty_area_data['penalty_area_y'],
                                                                    penalty_area_data['penalty_area_width'],
                                                                    penalty_area_data['penalty_area_height'])

        self.penalty_area_left: Rectangle = Rectangle(x, y, width, height, rgb_converter('white'))

        x, y, width, height = self._window. \
            convert_to_windows_scale(penalty_area_data['penalty_area_left_x_background'],
                                     penalty_area_data['penalty_area_y_background'],
                                     penalty_area_data['penalty_area_width_background'],
                                     penalty_area_data['penalty_area_height_background'])

        self.penalty_area_left_background: Rectangle = Rectangle(x, y, width, height, BACKGROUND_COLOR)

        x, y, width, height = self._window.convert_to_windows_scale(penalty_area_data['penalty_area_right_x'],
                                                                    penalty_area_data['penalty_area_y'],
                                                                    penalty_area_data['penalty_area_width'],
                                                                    penalty_area_data['penalty_area_height'])

        self.penalty_area_right: Rectangle = Rectangle(x, y, width, height, rgb_converter('white'))

        x, y, width, height = self._window. \
            convert_to_windows_scale(penalty_area_data['penalty_area_right_x_background'],
                                     penalty_area_data['penalty_area_y_background'],
                                     penalty_area_data['penalty_area_width_background'],
                                     penalty_area_data['penalty_area_height_background'])

        self.penalty_area_right_background: Rectangle = Rectangle(x, y, width, height, BACKGROUND_COLOR)

    #   Dessine les deux zones de but, à droite et à gauche

    def _create_goal_area(self) -> None:
        goal_area_data = self.field_model.goal_area_data

        x, y, width, height = self._window.convert_to_windows_scale(goal_area_data['goal_area_left_x'],
                                                                    goal_area_data['goal_area_y'],
                                                                    goal_area_data['goal_area_width'],
                                                                    goal_area_data['goal_area_height'])

        self.goal_area_left: Rectangle = Rectangle(x, y, width, height, rgb_converter('white'))

        x, y, width, height = self._window.convert_to_windows_scale(goal_area_data['goal_area_left_x_background'],
                                                                    goal_area_data['goal_area_y_background'],
                                                                    goal_area_data['goal_area_width_background'],
                                                                    goal_area_data['goal_area_height_background'])

        self.goal_area_left_background: Rectangle = Rectangle(x, y, width, height, BACKGROUND_COLOR)

        x, y, width, height = self._window.convert_to_windows_scale(goal_area_data['goal_area_right_x'],
                                                                    goal_area_data['goal_area_y'],
                                                                    goal_area_data['goal_area_width'],
                                                                    goal_area_data['goal_area_height'])

        self.goal_area_right: Rectangle = Rectangle(x, y, width, height, rgb_converter('white'))

        x, y, width, height = self._window.convert_to_windows_scale(goal_area_data['goal_area_right_x_background'],
                                                                    goal_area_data['goal_area_y_background'],
                                                                    goal_area_data['goal_area_width_background'],
                                                                    goal_area_data['goal_area_height_background'])

        self.goal_area_right_background: Rectangle = Rectangle(x, y, width, height, BACKGROUND_COLOR)

    #   Dessine les deux cages de but, à droite et à gauche

    def _create_goal(self) -> None:
        goal_data = self.field_model.goal_data

        x, y, width, height = self._window.convert_to_windows_scale(goal_data['goal_left_x'],
                                                                    goal_data['goal_y'],
                                                                    goal_data['goal_width'],
                                                                    goal_data['goal_height'])

        self.goal_left: Rectangle = Rectangle(x, y, width, height, rgb_converter('white'))

        x, y, width, height = self._window.convert_to_windows_scale(goal_data['goal_left_x_background'],
                                                                    goal_data['goal_y_background'],
                                                                    goal_data['goal_width_background'],
                                                                    goal_data['goal_height_background'])

        self.goal_left_background: Rectangle = Rectangle(x, y, width, height, GOAL_NET_COLOR)

        x, y, width, height = self._window.convert_to_windows_scale(goal_data['goal_right_x'],
                                                                    goal_data['goal_y'],
                                                                    goal_data['goal_width'],
                                                                    goal_data['goal_height'])

        self.goal_right: Rectangle = Rectangle(x, y, width, height, rgb_converter('white'))

        x, y, width, height = self._window.convert_to_windows_scale(goal_data['goal_right_x_background'],
                                                                    goal_data['goal_y_background'],
                                                                    goal_data['goal_width_background'],
                                                                    goal_data['goal_height_background'])

        self.goal_right_background: Rectangle = Rectangle(x, y, width, height, GOAL_NET_COLOR)

    #   Affiche tous les canvas

    def display(self, canvas) -> Union[FilledPolygon, PolyLine]:
        canvas = self.side_line.display(canvas)
        canvas = self.side_line_background.display(canvas)

        canvas = self.middle_line_circle.display(canvas)
        canvas = self.middle_line_circle_background.display(canvas)
        canvas = self.middle_line.display(canvas)

        canvas = self.penalty_area_left.display(canvas)
        canvas = self.penalty_area_left_background.display(canvas)
        canvas = self.penalty_area_right.display(canvas)
        canvas = self.penalty_area_right_background.display(canvas)

        canvas = self.goal_area_left.display(canvas)
        canvas = self.goal_area_left_background.display(canvas)
        canvas = self.goal_area_right.display(canvas)
        canvas = self.goal_area_right_background.display(canvas)

        canvas = self.goal_left.display(canvas)
        canvas = self.goal_left_background.display(canvas)
        canvas = self.goal_right.display(canvas)
        canvas = self.goal_right_background.display(canvas)

        return canvas


class AgentView:
    def __init__(self, agent: Agent, window: Window, color_team: str):
        self.agent: Agent = agent
        self._window: Window = window
        self._color_team: str = color_team

    def display(self, canvas) -> Union[FilledPolygon, PolyLine]:
        x = self.agent.x
        y = self.agent.y
        radius = self.agent.r
        direction = self.agent.dir
        color_agent = self.agent.color_agent

        # circle hitbox (pour tester la collision)

        circle_hitbox_x, circle_hitbox_y, circle_hitbox_radius = self._window.convert_to_windows_scale(
            self.agent.point_circle_hitbox.x,
            self.agent.point_circle_hitbox.y,
            self.agent.circle_hitbox_radius)

        circle = Circle(circle_hitbox_x, circle_hitbox_y, circle_hitbox_radius, GOAL_NET_COLOR)

        canvas = circle.display(canvas)

        # body

        x_body, y_body, radius_body = self._window.convert_to_windows_scale(x, y, radius)

        circle = Circle(x_body, y_body, radius_body, rgb_converter(color_agent))

        canvas = circle.display(canvas)

        # color team

        color_team = self._color_team

        x_team, y_team, radius_team = self._window.convert_to_windows_scale(x, y, radius * 0.8)

        circle = Circle(x_team, y_team, radius_team, rgb_converter(color_team))

        canvas = circle.display(canvas)

        # eye left

        eye_left_x, eye_left_y, eye_left_radius = self._window.convert_to_windows_scale(self.agent.point_eye_left.x,
                                                                                        self.agent.point_eye_left.y,
                                                                                        self.agent.r / 4)

        circle = Circle(eye_left_x, eye_left_y, eye_left_radius, rgb_converter('white'))

        canvas = circle.display(canvas)

        # iris left

        iris_left_x, iris_left_y, iris_left_radius = self._window.convert_to_windows_scale(self.agent.point_eye_left.x,
                                                                                           self.agent.point_eye_left.y,
                                                                                           self.agent.r / 16)

        circle = Circle(iris_left_x, iris_left_y, iris_left_radius, rgb_converter('black'))

        canvas = circle.display(canvas)

        # eye right

        eye_right_x, eye_right_y, eye_right_radius = self._window.convert_to_windows_scale(self.agent.point_eye_right.x,
                                                                                           self.agent.point_eye_right.y,
                                                                                           self.agent.r / 4)

        circle = Circle(eye_right_x, eye_right_y, eye_right_radius, rgb_converter('white'))

        canvas = circle.display(canvas)

        # iris right

        iris_right_x, iris_right_y, iris_right_radius = self._window.convert_to_windows_scale(
            self.agent.point_eye_right.x,
            self.agent.point_eye_right.y,
            self.agent.r / 16)

        circle = Circle(iris_right_x, iris_right_y, iris_right_radius, rgb_converter('black'))

        canvas = circle.display(canvas)



        return canvas


class BallView:

    def __init__(self, ball: Ball, window: Window):
        self._ball: Ball = ball
        self._window: Window = window

    def display(self, canvas) -> Union[FilledPolygon, PolyLine]:
        x = self._ball.x
        y = self._ball.y
        radius = self._ball.r
        color = self._ball.color

        x, y, r = self._window.convert_to_windows_scale(x, y, radius)

        circle = Circle(x, y, r, rgb_converter(color))
        canvas = circle.display(canvas)
        return canvas


class TeamView:

    def __init__(self, team: Team, window: Window):
        self._team: Team = team
        self._window: Window = window

    def display(self, canvas) -> Union[FilledPolygon, PolyLine]:
        color_agent_dict = self._team.color_agent_dict

        for agent in color_agent_dict.values():
            agent_view = AgentView(agent=agent, window=self._window,
                                   color_team=self._team.color_team)

            canvas = agent_view.display(canvas)

        return canvas


class View:

    def __init__(self, window_width: int, window_height: int, field_model: FieldModel, team_left: Team,
                 team_right: Team, ball: Ball):
        self._window: Window = Window(window_width, window_height, field_model)
        self._field_view: FieldView = FieldView(field_model=field_model, window=self._window)
        self._team_left_view: TeamView = TeamView(team=team_left, window=self._window)
        self._team_right_view: TeamView = TeamView(team=team_right, window=self._window)
        self._ball_view: BallView = BallView(ball=ball, window=self._window)

    def update_view(self, field_model: FieldModel, team_left: Team, team_right: Team, ball: Ball) -> None:
        self._field_view = FieldView(field_model=field_model, window=self._window)
        self._team_left_view = TeamView(team=team_left, window=self._window)
        self._team_right_view = TeamView(team=team_right, window=self._window)
        self._ball_view = BallView(ball=ball, window=self._window)

    def display(self, canvas) -> Union[FilledPolygon, PolyLine]:
        canvas = create_canvas(canvas, window_width=self._window.window_width,
                               window_height=self._window.window_height, c=BACKGROUND_COLOR)
        canvas = self._field_view.display(canvas)
        canvas = self._team_left_view.display(canvas)
        canvas = self._team_right_view.display(canvas)
        canvas = self._ball_view.display(canvas)

        return canvas

    @property
    def window(self) -> Window:
        return self._window

