from i2_integrations.discord_rest import _chunks


def test_short_message_single_chunk():
    assert _chunks("hello") == ["hello"]


def test_long_message_split_under_limit():
    content = "\n".join("あ" * 100 for _ in range(50))  # > 2000 chars
    parts = _chunks(content)
    assert len(parts) > 1
    assert all(len(p) <= 2000 for p in parts)
    assert "".join(parts) == content
