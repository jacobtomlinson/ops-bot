"""Helper functions to use within OpsDroid."""

import datetime
import os
import stat
import shutil
import logging
import filecmp
import json

import nbformat
from nbconvert import PythonExporter

_LOGGER = logging.getLogger(__name__)


# pylint: disable=inconsistent-return-statements
def get_opsdroid():
    """Return the running opsdroid instance.

    Returns:
        object: opsdroid instance.

    """
    from opsdroid.core import OpsDroid

    if len(OpsDroid.instances) == 1:
        return OpsDroid.instances[0]


def del_rw(action, name, exc):
    """Error handler for removing read only files.

    Args:
        action: the function that raised the exception
        name: path name passed to the function (path and file name)
        exc: exception information return by sys.exc_info()

    Raises:
        OsError : If the file to be removed is a directory.

    """
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


# This is meant to provide backwards compatibility for versions
# prior to  0.16.0 in the future this will be deleted


def convert_dictionary(modules):
    """Convert dictionary to new format.

    We iterate over all the modules in the list and change the dictionary
    to be in the format 'name_of_module: { config_params}'

    Args:
        modules (list): List of dictionaries that contain the module configuration

    Return:
        List: New modified list following the new format.

    """
    config = dict()

    try:
        if isinstance(modules, list):
            _LOGGER.warning(
                "Opsdroid has a new configuration format since version 0.17.0, we will change your configuration now. Please read on how to migrate in the documentation."
            )
            for module in modules:
                module_copy = module.copy()
                del module_copy["name"]

                config[module["name"]] = module_copy

            return config
        else:
            return modules
    except TypeError:
        return {}


def update_pre_0_17_config_format(config):
    """Update each configuration param that contains 'name'.

    We decided to ditch the name param and instead divide each module by it's name.
    This change was due to validation issues. Now instead of a list of dictionaries
    without any pointer to what they are, we are using the name of the module and then a
    dictionary containing the configuration params for said module.

    Args:
        config (dict): Dictionary containing config got from configuration.yaml

    Returns:
        dict: updated configuration.

    """
    updated_config = {}
    for config_type, modules in config.items():
        if config_type in ("parsers", "connectors", "skills", "databases"):
            updated_config[config_type] = convert_dictionary(modules)

    config.update(updated_config)

    return config


# This is meant to provide backwards compatibility for versions
# prior to  0.12.0 in the future this will probably be deleted


def move_config_to_appdir(src, dst):
    """Copy any .yaml extension in "src" to "dst" and remove from "src".

    Args:
        src (str): path file.
        dst (str): destination path.

    Logging:
        info (str): File 'my_file.yaml' copied from '/path/src/
                       to '/past/dst/' run opsdroid -e to edit
                       the  main config file.

    Examples:
        src : source path with .yaml file '/path/src/my_file.yaml.
        dst : destination folder to paste the .yaml files '/path/dst/.

    """
    yaml_files = [file for file in os.listdir(src) if ".yaml" in file[-5:]]

    if not os.path.isdir(dst):
        os.mkdir(dst)

    for file in yaml_files:
        original_file = os.path.join(src, file)
        copied_file = os.path.join(dst, file)
        shutil.copyfile(original_file, copied_file)
        _LOGGER.info(
            _(
                "File %s copied from %s to %s "
                "run opsdroid -e to edit the "
                "main config file"
            ),
            file,
            src,
            dst,
        )
        if filecmp.cmp(original_file, copied_file):
            os.remove(original_file)


def file_is_ipython_notebook(path):
    """Check whether a file is an iPython Notebook.

    Args:
        path (str): path to the file.

    Examples:
        path : source path with .ipynb file '/path/src/my_file.ipynb.

    """
    return path.lower().endswith(".ipynb")


def convert_ipynb_to_script(notebook_path, output_path):
    """Convert an iPython Notebook to a python script.

    Args:
        notebook_path (str): path to the notebook file.
        output_path (str): path to the script file destination.

    Examples:
        notebook_path : source path with .ipynb file '/path/src/my_file.ipynb.
        output_path : destination path with .py file '/path/src/my_file.py.

    """
    with open(notebook_path, "r") as notebook_path_handle:
        raw_notebook = notebook_path_handle.read()
        notebook = nbformat.reads(raw_notebook, as_version=4)
        script, _ = PythonExporter().from_notebook_node(notebook)
        with open(output_path, "w") as output_path_handle:
            output_path_handle.write(script)


def extract_gist_id(gist_string):
    """Extract the gist ID from a url.

    Will also work if simply passed an ID.

    Args:
        gist_string (str): Gist URL.

    Returns:
        string: The gist ID.

    Examples:
        gist_string : Gist url 'https://gist.github.com/{user}/{id}'.

    """
    return gist_string.split("/")[-1]


def add_skill_attributes(func):
    """Add the attributes which makes a function a skill.

    Args:
        func (func): Skill function.

    Returns:
        func: The skill function with the new attributes.

    """
    if not hasattr(func, "skill"):
        func.skill = True
    if not hasattr(func, "matchers"):
        func.matchers = []
    if not hasattr(func, "constraints"):
        func.constraints = []
    return func


class JSONEncoder(json.JSONEncoder):
    """A extended JSONEncoder class.

    This class is customised JSONEncoder class which helps to convert
    dict to JSON. The datetime objects are converted to dict with fields
    as keys.

    """

    # pylint: disable=method-hidden
    # See https://github.com/PyCQA/pylint/issues/414 for reference

    serializers = {}

    def default(self, o):
        """Convert the given datetime object to dict.

        Args:
            o (object): The datetime object to be marshalled.

        Returns:
            dict (object): A dict with datatime object data.

        Example:
            A dict which is returned after marshalling::

                {
                    "__class__": "datetime",
                    "year": 2018,
                    "month": 10,
                    "day": 2,
                    "hour": 0,
                    "minute": 41,
                    "second": 17,
                    "microsecond": 74644
                }

        """
        marshaller = self.serializers.get(type(o), super(JSONEncoder, self).default)
        return marshaller(o)


class JSONDecoder:
    """A JSONDecoder class.

    This class will convert dict containing datetime values
    to datetime objects.

    """

    decoders = {}

    def __call__(self, dct):
        """Convert given dict to datetime objects.

        Args:
            dct (object): A dict containing datetime values and class type.

        Returns:
            object or dct: The datetime object for given dct, or dct if
                             respective class decoder is not found.

        Example:
            A datetime object returned after decoding::

                datetime.datetime(2018, 10, 2, 0, 41, 17, 74644)

        """
        if dct.get("__class__") in self.decoders:
            return self.decoders[dct["__class__"]](dct)
        return dct


def register_json_type(type_cls, fields, decode_fn):
    """Register JSON types.

    This method will register the serializers and decoders for the
    JSONEncoder and JSONDecoder classes respectively.

    Args:
        type_cls (object): A datetime object.
        fields (list): List of fields used to store data in dict.
        decode_fn (object): A lambda function object for decoding.

    """
    type_name = type_cls.__name__
    JSONEncoder.serializers[type_cls] = lambda obj: dict(
        __class__=type_name, **{field: getattr(obj, field) for field in fields}
    )
    JSONDecoder.decoders[type_name] = decode_fn


register_json_type(
    datetime.datetime,
    ["year", "month", "day", "hour", "minute", "second", "microsecond"],
    lambda dct: datetime.datetime(
        dct["year"],
        dct["month"],
        dct["day"],
        dct["hour"],
        dct["minute"],
        dct["second"],
        dct["microsecond"],
    ),
)

register_json_type(
    datetime.date,
    ["year", "month", "day"],
    lambda dct: datetime.date(dct["year"], dct["month"], dct["day"]),
)

register_json_type(
    datetime.time,
    ["hour", "minute", "second", "microsecond"],
    lambda dct: datetime.time(
        dct["hour"], dct["minute"], dct["second"], dct["microsecond"]
    ),
)
