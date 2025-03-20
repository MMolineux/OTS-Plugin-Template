import os
import pathlib
import traceback

import yaml
from flask import Blueprint, render_template, jsonify, Flask, current_app as app, send_from_directory
from opentakserver.plugins.Plugin import Plugin
from opentakserver.extensions import *

from .default_config import DefaultConfig
import importlib.metadata


class PluginTemplate(Plugin):
    # Do not change url_prefix
    url_prefix = f"/api/plugins/{pathlib.Path(__file__).resolve().parent.name}"
    blueprint = Blueprint("PluginTemplate", __name__, url_prefix=url_prefix)
                                       #^
                                       #|
                            # Change this to your plugin's name

    # This is your plugin's entry point. It will be called from OpenTAKServer to start the plugin
    def activate(self, app: Flask):
        self._app = app
        self._load_config()
        self._load_metadata()

        try:
            # Do stuff here
            logger.info(f"Successfully Loaded {self._name}")
        except BaseException as e:
            logger.error(f"Failed to load {self._name}: {e}")
            logger.error(traceback.format_exc())

    # Loads default config and user config from ~/ots/config.yml
    # In most cases you don't need to change this
    def _load_config(self):
        # Gets default config key/value pairs from the plugin's default_config.py
        for key in dir(DefaultConfig):
            if key.isupper():
                self._config[key] = getattr(DefaultConfig, key)
                self._app.config.update({key: getattr(DefaultConfig, key)})

        # Get user overrides from config.yml
        with open(os.path.join(self._app.config.get("OTS_DATA_FOLDER"), "config.yml")) as yaml_file:
            yaml_config = yaml.safe_load(yaml_file)
            for key in self._config.keys():
                value = yaml_config.get(key)
                if value:
                    self._config[key] = value
                    self._app.config.update({key: value})

    def _load_metadata(self):
        try:
            distributions = importlib.metadata.packages_distributions()
            for distro in distributions:
                if str(__name__).startswith(distro):
                    self._name = distributions[distro][0]
                    self._distro = distro
                    info = importlib.metadata.metadata(self._distro)
                    self._metadata = info.json
                    break

        except BaseException as e:
            logger.error(e)

    def get_info(self):
        self._load_metadata()
        self.get_plugin_routes(self.url_prefix)
        return {'name': self._name, 'distro': self._distro, 'routes': self._routes}

    def stop(self):
        # Shut down your plugin gracefully here
        pass

    # Make route methods static to avoid "no-self-use" errors
    @staticmethod
    @blueprint.route("/")
    def plugin_info():  # Do not put "self" as a method parameter here
        # This method will return JSON with info about the plugin derived from pyproject.toml, please do not change it
        # Make sure that your plugin has a README.md to show in the UI's about page
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

    # OpenTAKServer's web UI will display your plugin's UI in an iframe
    @staticmethod
    @blueprint.route("/ui")
    def ui():
        # Uncomment the following line if your plugin does not require a UI
        # return send_from_directory(f"../{pathlib.Path(__file__).resolve().parent.name}/dist", "index.html", as_attachment=False)

        # Otherwise use this line if your plugin requires a UI
        return send_from_directory(f"../{pathlib.Path(__file__).resolve().parent.name}/dist", "index.html", as_attachment=False)

    # Add more routes here. Make sure to use try/except blocks around all of your code. Otherwise, an exception in a plugin
    # could cause the whole server to crash
