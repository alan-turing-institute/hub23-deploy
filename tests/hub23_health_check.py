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

MG_API_KEY = os.getenv("MG_API_KEY", None)
if MG_API_KEY is None:
    print("Set the MG_API_KEY environment variable")
    sys.exit(1)


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


class Email:
    def __init__(self, to, at_most_every=600):
        self.to = to
        self.at_most_every = timedelta(at_most_every)
        self._last_time = datetime.datetime.utcnow() - self.at_most_every

        self.client = AsyncHTTPClient()

    async def report(self, url, message):
        now = datetime.datetime.utcnow()
        if (now - self._last_time) >= self.at_most_every:
            self._last_time = now

            data = {
                "from": "Is Hub23 Up? <ishub23up@sandbox13ae26f28a834e0f99963b8466fc6b84.mailgun.org>",
                "sender": "Is Hub23 Up? <ishub23up@sandbox13ae26f28a834e0f99963b8466fc6b84.mailgun.org>",
                "to": self.to,
                "subject": "%s is down" % url,
                "text": "%s\n\n%s"
                % (now.strftime("%Y-%m-%d %H:%M:%S"), message),
            }

            await self.client.fetch(
                "https://api.mailgun.net/v3/sandbox13ae26f28a834e0f99963b8466fc6b84.mailgun.org/messages",
                method="POST",
                auth_username="api",
                auth_password=MG_API_KEY,
                body=urllib.parse.urlencode(data),
            )


class LogIt:
    def __init__(self):
        self.url = None

    async def report(self, url, message):
        self.at = datetime.datetime.utcnow()
        self.url = url
        self.message = message


async def main(once=False):
    if once:
        global IsUp
        IsUp = partial(IsUp, every=None)

    checks = [
        IsUp(
            "https://binder.hub23.turing.ac.uk",
            [Email("hub23registry@turing.ac.uk")],
        ),
        IsUp(
            "https://hub.hub23.turing.ac.uk/hub/api",
            [Email("hub23registry@turing.ac.uk")],
        ),
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
