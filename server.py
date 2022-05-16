from flask import Flask, abort, request
from threading import Thread

import pymongo

import json

from .config import Config

# blueprint
from .html.blueprint import html_blueprint
from .api.sensor.blueprint import api_sensor

class AetherServer(Thread):
    def __init__(self, name = "AetherServer"):
        super().__init__()
        self.webApp = Flask(name)

        # load the blueprints
        self.webApp.register_blueprint(html_blueprint)
        self.webApp.register_blueprint(api_sensor)

        # load the config
        self.webApp.config.from_object(Config)

    def run(self):
        self.webApp.run(host="10.0.0.206", port="8080")