# HN BlackBox Plugins

Place user-controlled extensions in a folder containing `plugin.py`.
The module may expose a `PLUGIN` metadata dictionary. Plugins are discovered
only from this local directory and are never fetched from the network.
