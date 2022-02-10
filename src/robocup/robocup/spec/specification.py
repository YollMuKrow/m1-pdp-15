# Par rapport aux habitudes de programmation et aux données du rapport
# width = length, height = width

class FieldSpecification:

    def __init__(self, field_width: float, field_height: float, line_density: float,
                 center_circle_diameter: float, center_circle_diameter_factor: float,
                 penalty_area_width: float, penalty_area_height: float, goal_area_width:
                 float, goal_area_height: float, goal_width: float, goal_height: float,
                 goal_density: float):

        # toutes les données sont en mètre

        self._field_width: float = field_width
        self._field_height: float = field_height

        self._border_strip_width: float = 1

        self._line_density: float = line_density

        self._center_circle_diameter: float = center_circle_diameter
        self._center_circle_diameter_density_factor: float = center_circle_diameter_factor

        self._penalty_area_width: float = penalty_area_width
        self._penalty_area_height: float = penalty_area_height

        self._goal_area_width: float = goal_area_width
        self._goal_area_height: float = goal_area_height

        self._goal_width: float = goal_width
        self._goal_height: float = goal_height
        self._goal_density: float = goal_density

    def show(self) -> None:
        print(self._field_width, self._field_height, self._border_strip_width,
              self._line_density, self._center_circle_diameter, self._center_circle_diameter_density_factor,
              self._penalty_area_width,
              self._penalty_area_height, self._goal_area_width, self._goal_area_height, self._goal_width,
              self._goal_height, self._goal_density)

    @property
    def field_width(self) -> float:
        return self._field_width

    @property
    def field_height(self) -> float:
        return self._field_height

    @property
    def border_strip_width(self) -> float:
        return self._border_strip_width

    @property
    def line_density(self) -> float:
        return self._line_density

    @property
    def center_circle_diameter(self) -> float:
        return self._center_circle_diameter

    @property
    def center_circle_diameter_density_factor(self) -> float:
        return self._center_circle_diameter_density_factor

    @property
    def penalty_area_width(self) -> float:
        return self._penalty_area_width

    @property
    def penalty_area_height(self) -> float:
        return self._penalty_area_height

    @property
    def goal_area_width(self) -> float:
        return self._goal_area_width

    @property
    def goal_area_height(self) -> float:
        return self._goal_area_height

    @property
    def goal_width(self) -> float:
        return self._goal_width

    @property
    def goal_height(self) -> float:
        return self._goal_height

    @property
    def goal_density(self) -> float:
        return self._goal_density


class FieldSpecificationAdultSize(FieldSpecification):

    def __init__(self):
        super().__init__(16, 11, 0.05, 3, 2.08, 3, 6, 1, 4, 0.6, 2.6, 0.12)


class FieldSpecificationKidSize(FieldSpecification):

    def __init__(self):
        super().__init__(11, 8, 0.05, 1.5, 2.15, 2, 5, 1, 3, 0.6, 2.6, 0.12)


class BallSpecification:

    def __init__(self, diameter: float, weight: float):
        self._diameter: float = diameter  # mètre
        self._weight: float = weight  # kilogramme

    @property
    def diameter(self) -> float:
        return self._diameter

    @property
    def weight(self) -> float:
        return self._weight


class BallSpecificationAdultSize(BallSpecification):

    def __init__(self):
        super().__init__(0.22, 0.435)


class BallSpecificationKidSize(BallSpecification):

    def __init__(self):
        super().__init__(0.13, 0.205)


class RobotSpecification:

    def __init__(self, max_speed: float, max_rotation_speed: float, weight: float, diameter: float):
        self._max_speed: float = max_speed
        self._max_rotation_speed: float = max_rotation_speed
        self._weight: float = weight
        self._diameter: float = diameter

    @property
    def max_speed(self) -> float:
        return self._max_speed

    @property
    def max_rotation_speed(self) -> float:
        return self._max_rotation_speed

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def diameter(self) -> float:
        return self._diameter


class RobotSpecificationAdultSize(RobotSpecification):

    def __init__(self):
        super().__init__(0, 0, 0, 0.6)


class RobotSpecificationKidSize(RobotSpecification):

    def __init__(self):
        super().__init__(0, 0, 0, 0.4)


class RoboCupSpecification:

    def __init__(self, field_specification: FieldSpecification, ball_specification: BallSpecification, robot_specification: RobotSpecification):
        self._field_specification: FieldSpecification = field_specification
        self._ball_specification: BallSpecification = ball_specification
        self._robot_specification: RobotSpecification = robot_specification

    @property
    def field_specification(self) -> FieldSpecification:
        return self._field_specification

    @property
    def ball_specification(self) -> BallSpecification:
        return self._ball_specification

    @property
    def robot_specification(self) -> RobotSpecification:
        return self._robot_specification
