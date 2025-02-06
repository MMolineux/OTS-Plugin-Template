import os

import yaml
from flask import Blueprint, render_template, jsonify, Flask
from opentakserver.plugins.Plugin import Plugin
from opentakserver.extensions import *
from .default_config import DefaultConfig
import importlib.metadata


class PluginTemplate(Plugin):
    # Use a URL prefix of "/api/your_plugin_name" and change the Blueprint name to YourPluginBlueprint
    blueprint = Blueprint("PluginTemplateBlueprint", __name__, url_prefix="/api/plugins/plugin_template", template_folder="templates")

    def __init__(self):
        self._app: Flask | None = None
        self._config = {}

    def activate(self, app: Flask):
        logger.info("Loaded Plugin Template")
        self._app = app
        self._app.config.update({"OTS_PLUGIN_TEMPLATE_TEST": "Hello World"})
        self._load_config()

    # Loads default config and user config from ~/ots/config.yml
    # In most cases you don't need to change this
    def _load_config(self):
        # Gets default config key/value pairs from default_config.py
        for key in dir(DefaultConfig):
            if key.isupper():
                self._config[key] = getattr(DefaultConfig, key)

        # Get user overrides from config.yml
        with open(os.path.join(self._app.config.get("OTS_DATA_FOLDER"), "config.yml")) as yaml_file:
            yaml_config = yaml.safe_load(yaml_file)
            for key in self._config.keys():
                value = yaml_config.get(key)
                if value:
                    self._config[key] = value

    # Make route methods static to avoid "no-self-use" errors
    @staticmethod
    @blueprint.route("/")
    def plugin_info():  # Do not put "self" as a method parameter here
        # This method will return JSON with info about the plugin derived from pyproject.toml, please do not change it
        try:
            distribution = None
            distributions = importlib.metadata.packages_distributions()
            for distro in distributions:
                if str(__name__).startswith(distro):
                    distribution = distributions[distro][0]
                    break

            if distribution:
                info = importlib.metadata.metadata(distribution)
                return jsonify(info.json)
            else:
                return jsonify({'success': False, 'error': 'Plugin not found'}), 404
        except BaseException as e:
            logger.error(e)
            return jsonify({'success': False, 'error': e}), 500

    # OpenTAKServer's web UI will call your plugin's /ui endpoint and display the results
    @staticmethod
    @blueprint.route("/ui")
    def ui():
        return render_template("index.html")

