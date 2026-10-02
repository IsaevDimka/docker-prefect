from prefect import flow, get_run_logger, task


@task
def build_greeting(name: str) -> str:
    return f"Hello, {name}!"


@flow(name="hello", retries=1, retry_delay_seconds=10)
def hello(name: str = "world") -> str:
    greeting = build_greeting(name)
    get_run_logger().info(greeting)
    return greeting


if __name__ == "__main__":
    hello()
