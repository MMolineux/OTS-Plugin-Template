from dataclasses import dataclass


@dataclass
class DefaultConfig:
    # Config options go here in all caps with the name of your plugin first
    # This file will be loaded first, followed by user overrides from config.yml
    # Make sure not to duplicate any setting name in OpenTAKServers' defaultconfig.py
    OTS_PLUGIN_TEMPLATE_SOME_SETTING = "my_setting_value"
