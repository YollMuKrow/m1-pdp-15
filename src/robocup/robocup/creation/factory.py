from abc import abstractmethod
from robocup.spec.specification import *

# Abstract Factory pattern

# Fabrique abstraite RoboCupSpecification
# Défini les services de création pour les données de spécification
# Données réelles du terrain, données de la balle, données du robot

class RoboCupSpecificationAbstractFactory:

    @abstractmethod
    def create_field_specification(self) -> FieldSpecification:
        pass

    @abstractmethod
    def create_ball_specification(self) -> BallSpecification:
        pass

    @abstractmethod
    def create_robot_specification(self) -> RobotSpecification:
        pass

# Fabrique concrète AdultSizeFactory

class AdultSizeFactory(RoboCupSpecificationAbstractFactory):

    def create_field_specification(self) -> FieldSpecification:
        return FieldSpecificationAdultSize()

    def create_ball_specification(self) -> BallSpecification:
        return BallSpecificationAdultSize()

    def create_robot_specification(self) -> RobotSpecification:
        return RobotSpecificationAdultSize()

# Fabrique concrète KidSizeFactory

class KidSizeFactory(RoboCupSpecificationAbstractFactory):

    def create_field_specification(self) -> FieldSpecification:
        return FieldSpecificationKidSize()

    def create_ball_specification(self) -> BallSpecification:
        return BallSpecificationKidSize()

    def create_robot_specification(self) -> RobotSpecification:
        return RobotSpecificationKidSize()


# Factory method pattern

class RoboCupSpecificationCreator:

    @abstractmethod
    def create_specification(self) -> RoboCupSpecification:
        pass

# Utilise la fabrique appropriée pour créer l'objet RoboCupSpecification

class AdultSizeCreator(RoboCupSpecificationCreator):

    def create_specification(self) -> RoboCupSpecification:
        field_specification: FieldSpecification = AdultSizeFactory().create_field_specification()
        ball_specification: BallSpecification = AdultSizeFactory().create_ball_specification()
        robot_specification: RobotSpecification = AdultSizeFactory().create_robot_specification()

        return RoboCupSpecification(field_specification=field_specification, ball_specification=ball_specification,
                                    robot_specification=robot_specification)


class KidSizeCreator(RoboCupSpecificationCreator):

    def create_specification(self) -> RoboCupSpecification:
        field_specification: FieldSpecification = KidSizeFactory().create_field_specification()
        ball_specification: BallSpecification = KidSizeFactory().create_ball_specification()
        robot_specification: RobotSpecification = KidSizeFactory().create_robot_specification()

        return RoboCupSpecification(field_specification=field_specification, ball_specification=ball_specification,
                                    robot_specification=robot_specification)
