import logging
__author__ = "jmichalo"

import pytest
from test.testutils import MockLoggingHandler
from ConfigParser import NoOptionError, NoSectionError
from pnc_cli.tools.config_ini_utils import ConfigReader as IniReader


def test_ini_parser_warning_on_singular_property():
    logger = logging.getLogger()
    log_catcher = MockLoggingHandler()
    logger.addHandler(log_catcher)
    IniReader('test/resources/cfg_singularproperty.ini')
    warning = log_catcher.messages.get("warning").pop()
    assert warning == 'Property: singular has no value.'


def test_ini_parser_wrong_section_name():
    with pytest.raises(NameError):
        IniReader('test/resources/cfg_badsectionname.ini')


def test_ini_parser_no_scmurl():
    with pytest.raises(NoOptionError):
        IniReader('test/resources/cfg_missingurl.ini')


def test_ini_parser_required_build_missing():
    with pytest.raises(NoSectionError):
        IniReader('test/resources/cfg_requiresnotincfg.ini')


def test_ini_parser_has_correct_output():
    cfg = IniReader('test/resources/cfg_correct.ini')
    arts, deps = cfg.get_dependency_structure()
    assert len(arts) is 5

    art = cfg.get_config('org.example.test-a')
    assert {'scmURL', 'artifact', 'options'}.issubset(art.keys())
    assert art.get('scmURL') == 'git://github.com:totallylegit/url.git?a#351da864abc'

    options = art.get('options')
    assert {'profiles', 'jvm_options', 'properties', 'goals', 'packages', 'envs'}.issubset(options.keys())
    assert options.get('patches') == ''
    assert {'name', 'name2'}.issubset(options.get('properties').keys())
    assert {'"value"', '"value with spaces"'}.issubset(options.get('properties').values())
    assert {'profile1', 'profile2', 'profile3'}.issubset(options.get('profiles'))

    dependencies = cfg.get_packages_and_dependencies()
    assert {'org.example.test-a','org.example.test-b','org.example.test-c','org.example.test-d','org.example.test-e'}\
        .issubset(dependencies.keys())

    e_deps = dependencies.get('org.example.test-e')
    assert {'org.example.test-a', 'org.example.test-d'}.issubset(e_deps)
