import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from player import Player
from Room12_owen import Room, column, circle


class TestColumns(unittest.TestCase):

    def test_column_cycles_through_letters(self):
        wheel = column(
            "test column",
            "A test wheel.",
            False,
            "initial",
            True,
            ["Y", "M", "S"]
        )

        self.assertEqual(wheel.letter, "Y")

        with redirect_stdout(io.StringIO()):
            wheel.use()
        self.assertEqual(wheel.letter, "M")

        with redirect_stdout(io.StringIO()):
            wheel.use()
        self.assertEqual(wheel.letter, "S")

        with redirect_stdout(io.StringIO()):
            wheel.use()
        self.assertEqual(wheel.letter, "Y")


class TestPressurePlate(unittest.TestCase):

    def setUp(self):
        self.left = column(
            "left column", "", False, "", True, ["Y", "M", "S"]
        )
        self.middle = column(
            "middle column", "", False, "", True, ["C", "A", "T"]
        )
        self.right = column(
            "right column", "", False, "", True, ["M", "X", "N"]
        )

        self.plate = circle(
            "pressure plate",
            "A pressure plate.",
            False,
            "unsolved?",
            True,
            [self.left, self.middle, self.right]
        )

        self.player = Player("Tester", 80, "healthy", 12)

    def test_wrong_letters_do_not_solve(self):
        output = io.StringIO()

        with redirect_stdout(output):
            self.plate.use(self.player)

        self.assertIn("What walks on four legs", output.getvalue())
        self.assertEqual(self.plate.state, "unsolved?")
        self.assertEqual(self.player.health, 80)
        self.assertEqual(self.player.score, 0)

    def test_one_correct_letter_is_identified(self):
        self.left.letter = "M"
        output = io.StringIO()

        with redirect_stdout(output):
            self.plate.use(self.player)

        self.assertIn("column to your left", output.getvalue())
        self.assertEqual(self.plate.state, "unsolved?")

    def test_two_correct_letters_are_identified(self):
        self.left.letter = "M"
        self.middle.letter = "A"
        output = io.StringIO()

        with redirect_stdout(output):
            self.plate.use(self.player)

        self.assertIn("both", output.getvalue())
        self.assertIn("column to your left", output.getvalue())
        self.assertIn("column to your front", output.getvalue())
        self.assertEqual(self.plate.state, "unsolved?")

    def test_correct_answer_solves_plate(self):
        self.left.letter = "M"
        self.middle.letter = "A"
        self.right.letter = "N"

        with redirect_stdout(io.StringIO()):
            self.plate.use(self.player)

        self.assertEqual(self.plate.state, "solved")
        self.assertEqual(self.player.score, 50)
        self.assertEqual(self.player.health, 110)

    def test_health_reward_is_capped_at_110(self):
        self.player.health = 100
        self.left.letter = "M"
        self.middle.letter = "A"
        self.right.letter = "N"

        with redirect_stdout(io.StringIO()):
            self.plate.use(self.player)

        self.assertEqual(self.player.health, 110)
        self.assertEqual(self.player.score, 50)

    def test_solved_plate_does_not_reward_player_again(self):
        self.left.letter = "M"
        self.middle.letter = "A"
        self.right.letter = "N"

        with redirect_stdout(io.StringIO()):
            self.plate.use(self.player)
            self.plate.use(self.player)

        self.assertEqual(self.plate.state, "solved")
        self.assertEqual(self.player.score, 50)
        self.assertEqual(self.player.health, 110)


class TestRoom12(unittest.TestCase):

    def setUp(self):
        self.room = Room()
        self.player = Player("Tester", 100, "healthy", 0)

    def test_room_starts_with_closed_east_exit(self):
        output = io.StringIO()

        with redirect_stdout(output):
            self.room.describe_room()

        self.assertIn(
            "door to the east, currently closed",
            output.getvalue()
        )

    def test_cannot_leave_before_solving(self):
        output = io.StringIO()

        with redirect_stdout(output):
            destination = self.room.move("east", self.player)

        self.assertIsNone(destination)
        self.assertIn("solid stone door", output.getvalue())

    def test_room_objects_cannot_be_picked_up(self):
        object_names = [
            "pressure plate",
            "left column",
            "middle column",
            "right column"
        ]

        for item_name in object_names:
            with self.subTest(item=item_name):
                output = io.StringIO()

                with redirect_stdout(output):
                    self.room.get(item_name, self.player)

                self.assertIn("cannot be taken", output.getvalue())
                self.assertFalse(self.player.has_item(item_name))

    def test_moving_to_pressure_plate_uses_it(self):
        self.room.objects[1].letter = "M"
        self.room.objects[2].letter = "A"
        self.room.objects[3].letter = "N"

        with redirect_stdout(io.StringIO()):
            destination = self.room.move("pressure plate", self.player)

        self.assertIsNone(destination)
        self.assertEqual(self.room.objects[0].state, "solved")
        self.assertEqual(self.player.score, 50)

    def test_using_pressure_plate_with_wrong_letters_does_not_unlock_door(self):
        output = io.StringIO()

        with redirect_stdout(output):
            self.room.use("pressure plate", self.player)

        self.assertNotEqual(self.room.objects[0].state, "solved")
        self.assertEqual(self.player.score, 0)

        with redirect_stdout(io.StringIO()):
            destination = self.room.move("east", self.player)

        self.assertIsNone(destination)

    def test_mock_gameplay_solve_leave_and_return(self):
        # Starting letters are Y, C, M.
        # These commands turn the wheels to M, A, N.
        commands = [
            "use left column",
            "use middle column",
            "use right column",
            "use right column",
            "move pressure plate",
            "move east"
        ]

        with patch("builtins.input", side_effect=commands):
            with redirect_stdout(io.StringIO()):
                destination = self.room.enter(self.player)

        self.assertEqual(destination, "east")
        self.assertEqual(self.room.objects[0].state, "solved")
        self.assertEqual(self.player.score, 50)
        self.assertEqual(self.player.health, 110)

        # Re-enter the same room instance after leaving.
        with patch("builtins.input", side_effect=["move east"]):
            output = io.StringIO()

            with redirect_stdout(output):
                destination = self.room.enter(self.player)

        self.assertEqual(destination, "east")
        self.assertIn("open door to the east", output.getvalue())
        self.assertEqual(self.room.objects[0].state, "solved")
        self.assertEqual(self.player.score, 50)
        self.assertEqual(self.player.health, 110)


if __name__ == "__main__":
    unittest.main(verbosity=2)