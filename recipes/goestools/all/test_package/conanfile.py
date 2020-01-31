from conans import ConanFile
import os


class TestPackage(ConanFile):

    def test(self):
        self.run("goesproc --version", run_environment=True)
        self.run("goesrecv --version", run_environment=True)
