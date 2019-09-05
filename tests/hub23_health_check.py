import os
import sys
import json
import urllib
import asyncio
import logging
import argparse
import datetime

from functools import partial

from tornado.locks import Event
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPClientError

API_KEY = os.getenv("API_KEY", None)
if API_KEY is None:
    print("Set the API_KEY environment variable.")
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

class BinderBuilds:
    def __init__(
        self, repo_spec, reporters, every=600,
        host="http://binder.hub23.turing.ac.uk"
    ):
        self.every = every
        self.reporters = reporters
        self.url = host + "/build/" + repo_spec

        self.done = Event()

        self.client = AsyncHTTPClient()
        self._reset()

    def _reset(self):
        self._body = b""
        self._phase = ""
        self._log_lines = ""

    def _buffer(self, chunk):
        self._body += chunk

        idx = self._body.find(b"\n\n")
        while idx > -1:
            message = self._body[:idx].decode("utf8", "replace")
            after_newlines = idx + 2
            self._body = self._body[after_newlines:]

            if message.startswith("data:"):
                data = json.loads(message.split(":", 1)[1])
                self._phase = data["phase"]
                self._log_lines += "%s %s" % (
                    data["phase"].upper(),
                    data["message"],
                )

            idx = self._body.find(b"\n\n")

    async def check(self):
        logging.info("Does %s launch?" % self.url)
        try:
            r = await self.client.fetch(
                self.url,
                raise_error=False,
                streaming_callback=self._buffer,
                request_timeout=60 * 5,
            )

        except HTTPClientError as e:
            logging.warning(f"Launching {self.url} failed with a {e}.")

        else:
            if r.code >= 400 or self._phase != "ready":
                logging.warning(
                    f"Launching {self.url} failed with a {r.code} exception."
                )

                reports = [
                    reporter.report(self.url, self._log_lines)
                    for reporter in self.reporters
                ]

                await asyncio.gather(*reports)

            else:
                logging.info(f"Launching {self.url} took {r.request_time}s.")

        self._reset()
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
        if now - self._last_time >= self.at_most_every:
            self._last_time = now

            data = {
                "from": "Is Hub23 Up <>",
                "sender": "Is Hub23 Up <>",
                "to": self.to,
                "subject": "%s is down" % url,
                "text": "%s\n\n%s"
                % (now.strftime("%d %B %Y at %X UTC"), message),
            }

            await self.client.fetch(
                "",
                method="POST",
                auth_username="api",
                auth_password=API_KEY,
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
        global IsUp, BinderBuilds
        IsUp = partial(IsUp, every=None)
        BinderBuilds = partial(BinderBuilds, every=None)

    checks = [
        IsUp(
            "http://binder.hub23.turing.ac.uk",
            [
                Email("sgibson@turing.ac.uk")
            ]
        ),
        IsUp(
            "https://hub.hub23.turing.ac.uk/hub/api",
            [
                Email("sgibson@turing.ac.uk")
            ]
        ),
        BinderBuilds(
            "gh/binder-examples/requirements/master",
            [
                Email("sgibson@turing.ac.uk")
            ]
        )
    ]

    signals = []
    for check in checks:
        IOLoop.current().add_callback(check.check)
        signals.append(check.done.wait())

    await asyncio.gather(*signals)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%X %Z",
        format="%(asctime)s %(levelname)-8s %(message)s",
    )

    parser = argparse.ArgumentParser(description="Is the hub up?")
    parser.add_argument(
        "--once", action="store_true", help="Check once and exit"
    )
    args = parser.parse_args()

    IOLoop.current().run_sync(lambda: main(once=args.once))
