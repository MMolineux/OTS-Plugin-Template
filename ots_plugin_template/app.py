import colorlog
from flask import Flask, Blueprint, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from opentakserver.plugins.Plugin import Plugin
from opentakserver.extensions import *
import importlib.metadata


class PluginTemplate(Plugin):
    # Use a URL prefix of "/api/your_plugin_name" and change the Blueprint name to YourPluginBlueprint
    blueprint = Blueprint("PluginTemplateBlueprint", __name__, url_prefix="/api/plugins/plugin_template", template_folder="templates")

    def activate(self, app: Flask, logger: colorlog, db: SQLAlchemy):
        with app.app_context():
            self.app = app
            self.logger = logger
            self.logger.info(f"Loaded plugin template")
            self.db = db

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
