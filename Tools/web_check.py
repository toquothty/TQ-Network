from os import system
from pathlib import Path

urls = Path().absolute() / "urls.txt"


def url_ping():
    with urls.open(mode="r", encoding="utf-8") as file:

        for url in file.readlines():
            result = system(f"ping {url}")

        try:
            print(result)
            # do something
        except Exception as e:
            print(e)
            # do something else


if __name__ == "__main__":
    url_ping()
