from i2_core.ids import new_feedback_id, new_meeting_id


def test_meeting_id_has_guild_prefix():
    mid = new_meeting_id(12345)
    assert mid.startswith("12345-")
    assert len(mid.split("-")[1]) == 12


def test_feedback_ids_unique():
    assert new_feedback_id() != new_feedback_id()
