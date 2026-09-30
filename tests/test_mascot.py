from orbit.cli.widgets.mascot import Mascot, MascotState


def test_mascot_defines_all_agent_states() -> None:
    assert set(Mascot.FRAMES) == set(MascotState)


def test_working_mascot_has_animated_frames() -> None:
    assert len(Mascot.FRAMES[MascotState.WORKING]) > 1