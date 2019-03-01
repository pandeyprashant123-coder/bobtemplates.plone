# -*- coding: utf-8 -*-

from base import dummy_contextmanager
from base import file_exists
from base import generate_answers_ini

import os.path
import subprocess


def test_vocabulary(tmpdir, capsys, config):
    template = """[variables]
package.description = Dummy package
package.example = True

author.name = The Plone Collective
author.email = collective@plone.org
author.github.user = collective
package.git.init = True

plone.version = {version}
""".format(
        version=config.version,
    )
    generate_answers_ini(tmpdir.strpath, template)

    # generate template addon:
    config.template = 'addon'
    config.package_name = 'collective.task'
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
vocabulary_name = AvailableTasks
subtemplate_warning = Yes
"""
    generate_answers_ini(wd, template)

    config.template = 'vocabulary'
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

    assert file_exists(wd, '/src/collective/task/vocabularies/configure.zcml')
    assert file_exists(
        wd,
        '/src/collective/task/tests/test_vocab_available_tasks.py',
    )
    assert file_exists(
        wd,
        '/src/collective/task/vocabularies/available_tasks.py',
    )

    with capsys.disabled() if config.verbose else dummy_contextmanager():
        try:
            test_result = subprocess.check_output(
                ['tox', '-vv'],
                cwd=wd,
            )
            print(test_result)
        except subprocess.CalledProcessError as execinfo:
            print(execinfo.output)
            assert 'failed' in execinfo
