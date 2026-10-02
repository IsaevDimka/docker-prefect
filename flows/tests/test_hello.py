from pipelines.hello.flow import build_greeting, hello


def test_build_greeting():
    assert build_greeting.fn("Prefect") == "Hello, Prefect!"


def test_hello_flow():
    assert hello(name="CI") == "Hello, CI!"
