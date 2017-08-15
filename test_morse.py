import morse


def test_text_to_morse():
    assert morse.text_to_morse("SOS") == "... --- ..."
    assert morse.text_to_morse("SOS sos") == "... --- ... / ... --- ..."
