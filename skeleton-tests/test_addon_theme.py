# -*- coding: utf-8 -*-

from base import dummy_contextmanager
from base import file_exists
from base import generate_answers_ini

import os.path
import subprocess


def test_addon_theme(tmpdir, capsys, config):
    template = """[variables]
package.description = Dummy package

author.name = The Plone Collective
author.email = collective@plone.org
author.github.user = collective
subtemplate_warning=False
package.git.init = True

plone.version = {version}
""".format(
        version=config.version,
    )
    generate_answers_ini(tmpdir.strpath, template)

    # generate template addon:
    config.template = 'addon'
    config.package_name = 'plonetheme.blacksea'
    result = subprocess.call(
        [
            'mrbob',
            '-O', config.package_name,
            'bobtemplates.plone:' + config.template,
            '--config', 'answers.ini',
            '--non-interactive',
        ],
        cwd=tmpdir.strpath,
    )
    assert result == 0

    wd = os.path.abspath(
        os.path.join(tmpdir.strpath, config.package_name),
    )

    # generate subtemplate content_type:
    template = """[variables]
theme.name = Plone theme Blacksea
subtemplate_warning=False
"""
    generate_answers_ini(wd, template)

    config.template = 'theme'
    result = subprocess.call(
        [
            'mrbob',
            'bobtemplates.plone:' + config.template,
            '--config', 'answers.ini',
            '--non-interactive',
        ],
        cwd=wd,
    )
    assert result == 0

    assert file_exists(wd, '/src/plonetheme/blacksea/theme/manifest.cfg')

    with capsys.disabled() if config.verbose else dummy_contextmanager():
        try:
            test_result = subprocess.check_output(
                ['tox'],
                cwd=wd,
            )
            print(test_result)
        except subprocess.CalledProcessError as execinfo:
            print(execinfo.output)
            assert 'failed' in execinfo
