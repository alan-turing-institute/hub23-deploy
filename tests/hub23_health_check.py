import argparse
import asyncio
import datetime
import json
import logging
import os
import sys
import urllib

from functools import partial

from tornado.locks import Event
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError


def timedelta(delta):
    return datetime.timedelta(seconds=delta)


class IsUp:
    def __init__(self, url, reporters, every=60):
        self.reporters = reporters
        self.url = url
        self.every = every

        self.done = Event()

        self.client = AsyncHTTPClient()

    async def check(self):
        logging.info(f"Is {self.url} up?")

        r = await self.client.fetch(
            self.url, raise_error=False, request_timeout=5
        )

        if r.code >= 400:
            logging.warning(f"{self.url} returned a {r.code}.")

            reports = [
                reporter.report(self.url, f"{self.url} returned a {r.code}.")
                for reporter in self.reporters
            ]

            await asyncio.gather(*reports)

        # wait till we are done to schedule the next call
        if self.every is not None:
            IOLoop.current().call_later(self.every, self.check)
        else:
            self.done.set()


class LogIt:
    def __init__(self):
        self.url = None

    async def report(self, url, message):
        self.at = datetime.datetime.utcnow()
        self.url = url
        self.message = message


async def main(once=False):
    if once:
        global IsUp, BinderBuilds
        IsUp = partial(IsUp, every=None)

    checks = [
        IsUp("https://binder.hub23.turing.ac.uk", [None]),
        IsUp("https://hub.hub23.turing.ac.uk/hub/api", [None]),
    ]

    signals = []
    for check in checks:
        IOLoop.current().add_callback(check.check)
        signals.append(check.done.wait())

    await asyncio.gather(*signals)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s %(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(description="Is the hub up?")
    parser.add_argument(
        "--once", action="store_true", help="Check once and exit"
    )
    args = parser.parse_args()

    IOLoop.current().run_sync(lambda: main(once=args.once))
