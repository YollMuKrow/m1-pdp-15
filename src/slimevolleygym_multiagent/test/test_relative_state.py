import unittest
import numpy as np

from slimevolleygym import RelativeState


class TestRelativeState(unittest.TestCase):

    def setUp(self) -> None:
        self.relativeState = RelativeState()

        self.relativeState.set_agent_state((1.6, 2.6, 3.6, 4.6))

        self.relativeState.set_ball_state((5.6, 6.6, 7.6, 8.6))

        self.relativeState.set_allies_color_state_dict(('yellow', (9.6, 10.6, 11.6, 12.6)))

        self.relativeState.set_opponents_color_state_dict(('purple', (13.6, 14.6, 15.6, 16.6)))
        self.relativeState.set_opponents_color_state_dict(('green', (17.6, 18.6, 19.6, 20.6)))

    def test_get_observation(self):
        expected_result = np.array(
            [1.6, 2.6, 3.6, 4.6, 5.6, 6.6, 7.6, 8.6, 9.6, 10.6, 11.6, 12.6, 13.6, 14.6, 15.6, 16.6, 17.6, 18.6, 19.6,
             20.6]) / 10
        result = self.relativeState.getObservation()
        np.testing.assert_array_equal(expected_result, result)


if __name__ == '__main__':
    unittest.main()
