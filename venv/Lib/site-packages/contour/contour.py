import logging
import os
import UserDict

import yaml

CONTOUR_YAML_NAMES = ['contour.yaml', 'contour.yml']

# TODO: Handle other configuration formats.
# TODO: Handle persitent storage of configuration.


class MissingConfigurationError(Exception):
    """Missing configuration option."""


class BadModulePathError(Exception):
    """Invalid module path."""


class InvalidYamlFile(Exception):
    """The config.yaml file is invalid yaml."""


class EmptyYamlFile(Exception):
    """The config.yaml file is empty."""


class MissingYamlFile(Exception):
    """config.yaml cannot be found."""


class Contour(UserDict.IterableUserDict):

    def __init__(self, config_name=None, config_path=None,
                 local_config_name=None, local_config_path=None,
                 defaults=None):

        UserDict.IterableUserDict.__init__(self, dict=defaults)

        self._load_config(config_name, config_path)

        # Override with the local config if it exists.
        self._load_config(local_config_name, local_config_path)

    def _load_by_path(self, path):
        data = _load_yaml_config(path)
        options = _parse_yaml_config(data)
        self.data.update(options)

    def _load_config(self, config_name=None, config_path=None):
        if not config_path and not config_name:
            return

        # Load by path if it exists.
        if config_path:
            self._load_by_path(config_path)
            return

        # Load by name if it exists.
        path = find_contour_yaml(names=[config_name])
        self._load_by_path(path)

    def load(self, option_key, default=None):
        option = self.get(option_key, default)

        if not option:
            return

        return module_import(option)

    @classmethod
    def load_option(cls, option):
        # TODO: Load the option, could be a module, function or class.
        return

    def __setitem__(self, key, item):
        raise TypeError

    def __delitem__(self, key):
        raise TypeError

    def clear(self):
        raise TypeError

    def pop(self, key, *args):
        raise TypeError

    def popitem(self):
        raise TypeError


def module_import(module_path):
    """Imports the module indicated in name

    Args:
        module_path: string representing a module path such as
        'app.config' or 'app.extras.my_module'
    Returns:
        the module matching name of the last component, ie: for
        'app.extras.my_module' it returns a
        reference to my_module
    Raises:
        BadModulePathError if the module is not found
    """
    try:
        # Import whole module path.
        module = __import__(module_path)

        # Split into components: ['contour',
        # 'extras','appengine','ndb_persistence'].
        components = module_path.split('.')

        # Starting at the second component, set module to a
        # a reference to that component. at the end
        # module with be the last component. In this case:
        # ndb_persistence
        for component in components[1:]:
            module = getattr(module, component)

        return module

    except ImportError:
        raise BadModulePathError(
            'Unable to find module "%s".' % (module_path,))


def find_contour_yaml(config_file=__file__, names=None):
    """
    Traverse directory trees to find a contour.yaml file

    Begins with the location of this file then checks the
    working directory if not found

    Args:
        config_file: location of this file, override for
        testing
    Returns:
        the path of contour.yaml or None if not found
    """
    checked = set()
    contour_yaml = _find_countour_yaml(os.path.dirname(config_file), checked,
                                       names=names)

    if not contour_yaml:
        contour_yaml = _find_countour_yaml(os.getcwd(), checked, names=names)

    return contour_yaml


def _find_countour_yaml(start, checked, names=None):
    """Traverse the directory tree identified by start
    until a directory already in checked is encountered or the path
    of countour.yaml is found.

    Checked is present both to make the loop termination easy
    to reason about and so the same directories do not get
    rechecked

    Args:
        start: the path to start looking in and work upward from
        checked: the set of already checked directories

    Returns:
        the path of the countour.yaml file or None if it is not found
    """
    extensions = []

    if names:
        for name in names:
            if not os.path.splitext(name)[1]:
                extensions.append(name + ".yaml")
                extensions.append(name + ".yml")

    yaml_names = (names or []) + CONTOUR_YAML_NAMES + extensions
    directory = start

    while directory not in checked:
        checked.add(directory)

        for fs_yaml_name in yaml_names:
            yaml_path = os.path.join(directory, fs_yaml_name)

            if os.path.exists(yaml_path):
                return yaml_path

        directory = os.path.dirname(directory)

    return


def _load_yaml_config(path=None):
    """Open and return the yaml contents."""
    countour_yaml_path = path or find_contour_yaml()

    if countour_yaml_path is None:
        logging.debug("countour.yaml not found.")
        return None

    with open(countour_yaml_path) as yaml_file:
        return yaml_file.read()


def _parse_yaml_config(config_data=None):
    """
    Gets the configuration from the found countour.yaml
    file and parses the data.
    Returns:
        a dictionary parsed from the yaml file
    """
    data_map = {}

    # If we were given config data to use, use it.  Otherwise, see if there is
    # a countour.yaml to read the config from.
    config_data = config_data or _load_yaml_config()

    if config_data is None:
        logging.debug("No custom countour config, using default config.")
        return data_map

    config = yaml.safe_load(config_data)

    # If there was a valid custom config, it will be a dict.  Otherwise,
    # ignore it.
    if isinstance(config, dict):
        # Apply the custom config over the default config.  This allows us to
        # extend functionality without breaking old stuff.
        data_map.update(config)

    elif not None:
        raise InvalidYamlFile("The countour.yaml file "
                              "is invalid yaml")

    return data_map
