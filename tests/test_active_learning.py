versions pytest-8.4.0, python-3.11.10.final.0
invocation_dir=/home/tom/git/agent
cwd=/home/tom/git/agent
args=('--debug', 'tests/test_active_learning.py')

  pytest_cmdline_main [hook]
      config: <_pytest.config.Config object at 0x7f613db31910>
    pytest_plugin_registered [hook]
        plugin: <Session  exitstatus='<UNSET>' testsfailed=0 testscollected=0>
        plugin_name: session
        manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
    finish pytest_plugin_registered --> [] [hook]
    pytest_configure [hook]
        config: <_pytest.config.Config object at 0x7f613db31910>
      pytest_plugin_registered [hook]
          plugin: <_pytest.cacheprovider.LFPlugin object at 0x7f613d452450>
          plugin_name: lfplugin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.cacheprovider.NFPlugin object at 0x7f613d452710>
          plugin_name: nfplugin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
    early skip of rewriting module: faulthandler [assertion]
      pytest_plugin_registered [hook]
          plugin: <class '_pytest.legacypath.LegacyTmpdirPlugin'>
          plugin_name: legacypath-tmpdir
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
    early skip of rewriting module: pdb [assertion]
    early skip of rewriting module: cmd [assertion]
    early skip of rewriting module: code [assertion]
    early skip of rewriting module: codeop [assertion]
      pytest_plugin_registered [hook]
          plugin: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
          plugin_name: 140055637051600
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.config.Config object at 0x7f613db31910>
          plugin_name: pytestconfig
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.mark' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/mark/__init__.py'>
          plugin_name: mark
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.main' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/main.py'>
          plugin_name: main
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.runner' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/runner.py'>
          plugin_name: runner
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.fixtures' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/fixtures.py'>
          plugin_name: fixtures
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.helpconfig' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/helpconfig.py'>
          plugin_name: helpconfig
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.python' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/python.py'>
          plugin_name: python
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.terminal' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/terminal.py'>
          plugin_name: terminal
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.debugging' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/debugging.py'>
          plugin_name: debugging
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.unittest' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/unittest.py'>
          plugin_name: unittest
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.capture' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/capture.py'>
          plugin_name: capture
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.skipping' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/skipping.py'>
          plugin_name: skipping
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.legacypath' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/legacypath.py'>
          plugin_name: legacypath
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.tmpdir' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/tmpdir.py'>
          plugin_name: tmpdir
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.monkeypatch' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/monkeypatch.py'>
          plugin_name: monkeypatch
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.recwarn' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/recwarn.py'>
          plugin_name: recwarn
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.pastebin' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/pastebin.py'>
          plugin_name: pastebin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.assertion' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/assertion/__init__.py'>
          plugin_name: assertion
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.junitxml' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/junitxml.py'>
          plugin_name: junitxml
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.doctest' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/doctest.py'>
          plugin_name: doctest
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.cacheprovider' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/cacheprovider.py'>
          plugin_name: cacheprovider
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.freeze_support' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/freeze_support.py'>
          plugin_name: freeze_support
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.setuponly' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/setuponly.py'>
          plugin_name: setuponly
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.setupplan' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/setupplan.py'>
          plugin_name: setupplan
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.stepwise' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/stepwise.py'>
          plugin_name: stepwise
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.unraisableexception' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/unraisableexception.py'>
          plugin_name: unraisableexception
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.threadexception' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/threadexception.py'>
          plugin_name: threadexception
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.warnings' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/warnings.py'>
          plugin_name: warnings
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.logging' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/logging.py'>
          plugin_name: logging
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.reports' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/reports.py'>
          plugin_name: reports
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.faulthandler' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/faulthandler.py'>
          plugin_name: faulthandler
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module 'anyio.pytest_plugin' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/anyio/pytest_plugin.py'>
          plugin_name: anyio
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <CaptureManager _method='fd' _global_capturing=<MultiCapture out=<FDCapture 1 oldfd=5 _state='suspended' tmpfile=<_io.TextIOWrapper name="<_io.FileIO name=6 mode='rb+' closefd=True>" mode='r+' encoding='utf-8'>> err=<FDCapture 2 oldfd=7 _state='suspended' tmpfile=<_io.TextIOWrapper name="<_io.FileIO name=8 mode='rb+' closefd=True>" mode='r+' encoding='utf-8'>> in_=<FDCapture 0 oldfd=3 _state='started' tmpfile=<_io.TextIOWrapper name='/dev/null' mode='r' encoding='utf-8'>> _state='suspended' _in_suspended=False> _capture_fixture=None>
          plugin_name: capturemanager
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=0 testscollected=0>
          plugin_name: session
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.cacheprovider.LFPlugin object at 0x7f613d452450>
          plugin_name: lfplugin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.cacheprovider.NFPlugin object at 0x7f613d452710>
          plugin_name: nfplugin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <class '_pytest.legacypath.LegacyTmpdirPlugin'>
          plugin_name: legacypath-tmpdir
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.terminal.TerminalReporter object at 0x7f613d4530d0>
          plugin_name: terminalreporter
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.logging.LoggingPlugin object at 0x7f613dbf7e50>
          plugin_name: logging-plugin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
    finish pytest_configure --> [] [hook]
    pytest_sessionstart [hook]
        session: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=0 testscollected=0>
      pytest_plugin_registered [hook]
          plugin: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
          plugin_name: 140055637051600
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.config.Config object at 0x7f613db31910>
          plugin_name: pytestconfig
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.mark' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/mark/__init__.py'>
          plugin_name: mark
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.main' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/main.py'>
          plugin_name: main
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.runner' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/runner.py'>
          plugin_name: runner
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.fixtures' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/fixtures.py'>
          plugin_name: fixtures
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.helpconfig' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/helpconfig.py'>
          plugin_name: helpconfig
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.python' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/python.py'>
          plugin_name: python
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.terminal' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/terminal.py'>
          plugin_name: terminal
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.debugging' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/debugging.py'>
          plugin_name: debugging
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.unittest' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/unittest.py'>
          plugin_name: unittest
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.capture' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/capture.py'>
          plugin_name: capture
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.skipping' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/skipping.py'>
          plugin_name: skipping
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.legacypath' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/legacypath.py'>
          plugin_name: legacypath
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.tmpdir' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/tmpdir.py'>
          plugin_name: tmpdir
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.monkeypatch' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/monkeypatch.py'>
          plugin_name: monkeypatch
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.recwarn' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/recwarn.py'>
          plugin_name: recwarn
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.pastebin' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/pastebin.py'>
          plugin_name: pastebin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.assertion' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/assertion/__init__.py'>
          plugin_name: assertion
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.junitxml' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/junitxml.py'>
          plugin_name: junitxml
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.doctest' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/doctest.py'>
          plugin_name: doctest
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.cacheprovider' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/cacheprovider.py'>
          plugin_name: cacheprovider
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.freeze_support' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/freeze_support.py'>
          plugin_name: freeze_support
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.setuponly' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/setuponly.py'>
          plugin_name: setuponly
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.setupplan' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/setupplan.py'>
          plugin_name: setupplan
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.stepwise' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/stepwise.py'>
          plugin_name: stepwise
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.unraisableexception' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/unraisableexception.py'>
          plugin_name: unraisableexception
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.threadexception' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/threadexception.py'>
          plugin_name: threadexception
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.warnings' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/warnings.py'>
          plugin_name: warnings
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.logging' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/logging.py'>
          plugin_name: logging
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.reports' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/reports.py'>
          plugin_name: reports
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module '_pytest.faulthandler' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/faulthandler.py'>
          plugin_name: faulthandler
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <module 'anyio.pytest_plugin' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/anyio/pytest_plugin.py'>
          plugin_name: anyio
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <CaptureManager _method='fd' _global_capturing=<MultiCapture out=<FDCapture 1 oldfd=5 _state='suspended' tmpfile=<_io.TextIOWrapper name="<_io.FileIO name=6 mode='rb+' closefd=True>" mode='r+' encoding='utf-8'>> err=<FDCapture 2 oldfd=7 _state='suspended' tmpfile=<_io.TextIOWrapper name="<_io.FileIO name=8 mode='rb+' closefd=True>" mode='r+' encoding='utf-8'>> in_=<FDCapture 0 oldfd=3 _state='started' tmpfile=<_io.TextIOWrapper name='/dev/null' mode='r' encoding='utf-8'>> _state='suspended' _in_suspended=False> _capture_fixture=None>
          plugin_name: capturemanager
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=0 testscollected=0>
          plugin_name: session
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.cacheprovider.LFPlugin object at 0x7f613d452450>
          plugin_name: lfplugin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.cacheprovider.NFPlugin object at 0x7f613d452710>
          plugin_name: nfplugin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <class '_pytest.legacypath.LegacyTmpdirPlugin'>
          plugin_name: legacypath-tmpdir
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.terminal.TerminalReporter object at 0x7f613d4530d0>
          plugin_name: terminalreporter
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.logging.LoggingPlugin object at 0x7f613dbf7e50>
          plugin_name: logging-plugin
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_plugin_registered [hook]
          plugin: <_pytest.fixtures.FixtureManager object at 0x7f613d47f1d0>
          plugin_name: funcmanage
          manager: <_pytest.config.PytestPluginManager object at 0x7f613e7ec8d0>
      finish pytest_plugin_registered --> [] [hook]
      pytest_report_header [hook]
          config: <_pytest.config.Config object at 0x7f613db31910>
          start_path: /home/tom/git/agent
          startdir: /home/tom/git/agent
      early skip of rewriting module: email.parser [assertion]
      early skip of rewriting module: email.feedparser [assertion]
      finish pytest_report_header --> [['rootdir: /home/tom/git/agent', 'plugins: anyio-4.9.0'], ['using: pytest-8.4.0', 'registered third-party plugins:', '  anyio-4.9.0 at /home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/anyio/pytest_plugin.py']] [hook]
    finish pytest_sessionstart --> [] [hook]
    pytest_collection [hook]
        session: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=0 testscollected=0>
    perform_collect <Session  exitstatus=<ExitCode.OK: 0> testsfailed=0 testscollected=0> ['/home/tom/git/agent'] [collection]
        pytest_collectstart [hook]
            collector: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=0 testscollected=0>
        finish pytest_collectstart --> [] [hook]
        pytest_make_collect_report [hook]
            collector: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=0 testscollected=0>
        processing argument CollectionArgument(path=PosixPath('/home/tom/git/agent'), parts=[], module_name=None) [collection]
            pytest_collect_directory [hook]
                path: /home/tom/git/agent
                parent: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=0 testscollected=0>
            finish pytest_collect_directory --> <Dir agent> [hook]
        finish pytest_make_collect_report --> <CollectReport '' lenresult=1 outcome='passed'> [hook]
        pytest_collectreport [hook]
            report: <CollectReport '' lenresult=1 outcome='passed'>
        finish pytest_collectreport --> [] [hook]
    genitems <Dir agent> [collection]
      pytest_collectstart [hook]
          collector: <Dir agent>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir agent>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.aider.chat.history.md
            path: /home/tom/git/agent/.aider.chat.history.md
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/.aider.chat.history.md
            path: /home/tom/git/agent/.aider.chat.history.md
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.aider.input.history
            path: /home/tom/git/agent/.aider.input.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/.aider.input.history
            path: /home/tom/git/agent/.aider.input.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.aider.tags.cache.v4
            path: /home/tom/git/agent/.aider.tags.cache.v4
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.codeiumignore
            path: /home/tom/git/agent/.codeiumignore
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/.codeiumignore
            path: /home/tom/git/agent/.codeiumignore
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.env
            path: /home/tom/git/agent/.env
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/.env
            path: /home/tom/git/agent/.env
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.git
            path: /home/tom/git/agent/.git
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.gitignore
            path: /home/tom/git/agent/.gitignore
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/.gitignore
            path: /home/tom/git/agent/.gitignore
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.pytest_cache
            path: /home/tom/git/agent/.pytest_cache
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.simpledspy
            path: /home/tom/git/agent/.simpledspy
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/.venv
            path: /home/tom/git/agent/.venv
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/README.md
            path: /home/tom/git/agent/README.md
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/README.md
            path: /home/tom/git/agent/README.md
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/__pycache__
            path: /home/tom/git/agent/__pycache__
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/agent_repl
            path: /home/tom/git/agent/agent_repl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/agent_repl
            parent: <Dir agent>
        finish pytest_collect_directory --> <Package agent_repl> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/agent_simpledspy.py
            path: /home/tom/git/agent/agent_simpledspy.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/agent_simpledspy.py
            path: /home/tom/git/agent/agent_simpledspy.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/analytics.log
            path: /home/tom/git/agent/analytics.log
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/analytics.log
            path: /home/tom/git/agent/analytics.log
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/coding_agent_repl.log
            path: /home/tom/git/agent/coding_agent_repl.log
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/coding_agent_repl.log
            path: /home/tom/git/agent/coding_agent_repl.log
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/coding_agent_repl.py
            path: /home/tom/git/agent/coding_agent_repl.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/coding_agent_repl.py
            path: /home/tom/git/agent/coding_agent_repl.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/context.txt
            path: /home/tom/git/agent/context.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/context.txt
            path: /home/tom/git/agent/context.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/deepseek_simba_optimizer.py
            path: /home/tom/git/agent/deepseek_simba_optimizer.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/deepseek_simba_optimizer.py
            path: /home/tom/git/agent/deepseek_simba_optimizer.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_logs.jsonl
            path: /home/tom/git/agent/dspy_logs.jsonl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/dspy_logs.jsonl
            path: /home/tom/git/agent/dspy_logs.jsonl
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_modules
            path: /home/tom/git/agent/dspy_modules
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/dspy_modules
            parent: <Dir agent>
        finish pytest_collect_directory --> <Dir dspy_modules> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs
            path: /home/tom/git/agent/dspy_programs
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/dspy_programs
            parent: <Dir agent>
        finish pytest_collect_directory --> <Dir dspy_programs> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/info.md
            path: /home/tom/git/agent/info.md
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/info.md
            path: /home/tom/git/agent/info.md
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/interactive_chat.py
            path: /home/tom/git/agent/interactive_chat.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/interactive_chat.py
            path: /home/tom/git/agent/interactive_chat.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/iterative_improvement_elo.py
            path: /home/tom/git/agent/iterative_improvement_elo.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/iterative_improvement_elo.py
            path: /home/tom/git/agent/iterative_improvement_elo.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns
            path: /home/tom/git/agent/mlruns
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns
            parent: <Dir agent>
        finish pytest_collect_directory --> <Dir mlruns> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/model_map.py
            path: /home/tom/git/agent/model_map.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/model_map.py
            path: /home/tom/git/agent/model_map.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/notes.md
            path: /home/tom/git/agent/notes.md
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/notes.md
            path: /home/tom/git/agent/notes.md
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/online_optimization_system.py
            path: /home/tom/git/agent/online_optimization_system.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/online_optimization_system.py
            path: /home/tom/git/agent/online_optimization_system.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimization_dataset.json
            path: /home/tom/git/agent/optimization_dataset.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimization_dataset.json
            path: /home/tom/git/agent/optimization_dataset.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1748992159.json
            path: /home/tom/git/agent/optimized_model_v1748992159.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1748992159.json
            path: /home/tom/git/agent/optimized_model_v1748992159.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1748992473.json
            path: /home/tom/git/agent/optimized_model_v1748992473.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1748992473.json
            path: /home/tom/git/agent/optimized_model_v1748992473.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1748992695.json
            path: /home/tom/git/agent/optimized_model_v1748992695.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1748992695.json
            path: /home/tom/git/agent/optimized_model_v1748992695.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1748993566.json
            path: /home/tom/git/agent/optimized_model_v1748993566.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1748993566.json
            path: /home/tom/git/agent/optimized_model_v1748993566.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1748997112.json
            path: /home/tom/git/agent/optimized_model_v1748997112.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1748997112.json
            path: /home/tom/git/agent/optimized_model_v1748997112.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1748997168.json
            path: /home/tom/git/agent/optimized_model_v1748997168.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1748997168.json
            path: /home/tom/git/agent/optimized_model_v1748997168.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1748997205.json
            path: /home/tom/git/agent/optimized_model_v1748997205.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1748997205.json
            path: /home/tom/git/agent/optimized_model_v1748997205.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1748997223.json
            path: /home/tom/git/agent/optimized_model_v1748997223.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1748997223.json
            path: /home/tom/git/agent/optimized_model_v1748997223.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1749000077.json
            path: /home/tom/git/agent/optimized_model_v1749000077.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1749000077.json
            path: /home/tom/git/agent/optimized_model_v1749000077.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/optimized_model_v1749000137.json
            path: /home/tom/git/agent/optimized_model_v1749000137.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/optimized_model_v1749000137.json
            path: /home/tom/git/agent/optimized_model_v1749000137.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/requirements.txt
            path: /home/tom/git/agent/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/requirements.txt
            path: /home/tom/git/agent/requirements.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/self_review_agent.py
            path: /home/tom/git/agent/self_review_agent.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/self_review_agent.py
            path: /home/tom/git/agent/self_review_agent.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/shell_wrapper.py
            path: /home/tom/git/agent/shell_wrapper.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/shell_wrapper.py
            path: /home/tom/git/agent/shell_wrapper.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/simpledspy_demo.py
            path: /home/tom/git/agent/simpledspy_demo.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/simpledspy_demo.py
            path: /home/tom/git/agent/simpledspy_demo.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/simpledspy_main.py
            path: /home/tom/git/agent/simpledspy_main.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/simpledspy_main.py
            path: /home/tom/git/agent/simpledspy_main.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tasks.json
            path: /home/tom/git/agent/tasks.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/tasks.json
            path: /home/tom/git/agent/tasks.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/taskwarrior_dspy_agent.py
            path: /home/tom/git/agent/taskwarrior_dspy_agent.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/taskwarrior_dspy_agent.py
            path: /home/tom/git/agent/taskwarrior_dspy_agent.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/taskwarrior_dspy_definitions.py
            path: /home/tom/git/agent/taskwarrior_dspy_definitions.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/taskwarrior_dspy_definitions.py
            path: /home/tom/git/agent/taskwarrior_dspy_definitions.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/test_shell_wrapper.py
            path: /home/tom/git/agent/test_shell_wrapper.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/test_shell_wrapper.py
            path: /home/tom/git/agent/test_shell_wrapper.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir agent>
              module_path: /home/tom/git/agent/test_shell_wrapper.py
              path: /home/tom/git/agent/test_shell_wrapper.py
          finish pytest_pycollect_makemodule --> <Module test_shell_wrapper.py> [hook]
        finish pytest_collect_file --> [<Module test_shell_wrapper.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/test_textual_task_manager.py
            path: /home/tom/git/agent/test_textual_task_manager.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/test_textual_task_manager.py
            path: /home/tom/git/agent/test_textual_task_manager.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir agent>
              module_path: /home/tom/git/agent/test_textual_task_manager.py
              path: /home/tom/git/agent/test_textual_task_manager.py
          finish pytest_pycollect_makemodule --> <Module test_textual_task_manager.py> [hook]
        finish pytest_collect_file --> [<Module test_textual_task_manager.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests
            path: /home/tom/git/agent/tests
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/tests
            parent: <Dir agent>
        finish pytest_collect_directory --> <Dir tests> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/textual_task_manager.py
            path: /home/tom/git/agent/textual_task_manager.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir agent>
            file_path: /home/tom/git/agent/textual_task_manager.py
            path: /home/tom/git/agent/textual_task_manager.py
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport '.' lenresult=7 outcome='passed'> [hook]
    genitems <Package agent_repl> [collection]
      pytest_collectstart [hook]
          collector: <Package agent_repl>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Package agent_repl>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/agent_repl/__init__.py
            path: /home/tom/git/agent/agent_repl/__init__.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Package agent_repl>
            file_path: /home/tom/git/agent/agent_repl/__init__.py
            path: /home/tom/git/agent/agent_repl/__init__.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/agent_repl/__pycache__
            path: /home/tom/git/agent/agent_repl/__pycache__
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/agent_repl/agent.py
            path: /home/tom/git/agent/agent_repl/agent.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Package agent_repl>
            file_path: /home/tom/git/agent/agent_repl/agent.py
            path: /home/tom/git/agent/agent_repl/agent.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/agent_repl/commands.py
            path: /home/tom/git/agent/agent_repl/commands.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Package agent_repl>
            file_path: /home/tom/git/agent/agent_repl/commands.py
            path: /home/tom/git/agent/agent_repl/commands.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/agent_repl/config.py
            path: /home/tom/git/agent/agent_repl/config.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Package agent_repl>
            file_path: /home/tom/git/agent/agent_repl/config.py
            path: /home/tom/git/agent/agent_repl/config.py
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'agent_repl' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'agent_repl' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir dspy_modules> [collection]
      pytest_collectstart [hook]
          collector: <Dir dspy_modules>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir dspy_modules>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_modules/__pycache__
            path: /home/tom/git/agent/dspy_modules/__pycache__
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_modules/coding_agent.py
            path: /home/tom/git/agent/dspy_modules/coding_agent.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_modules>
            file_path: /home/tom/git/agent/dspy_modules/coding_agent.py
            path: /home/tom/git/agent/dspy_modules/coding_agent.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_modules/generator_module.py
            path: /home/tom/git/agent/dspy_modules/generator_module.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_modules>
            file_path: /home/tom/git/agent/dspy_modules/generator_module.py
            path: /home/tom/git/agent/dspy_modules/generator_module.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_modules/memory_gan.py
            path: /home/tom/git/agent/dspy_modules/memory_gan.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_modules>
            file_path: /home/tom/git/agent/dspy_modules/memory_gan.py
            path: /home/tom/git/agent/dspy_modules/memory_gan.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_modules/value_network.py
            path: /home/tom/git/agent/dspy_modules/value_network.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_modules>
            file_path: /home/tom/git/agent/dspy_modules/value_network.py
            path: /home/tom/git/agent/dspy_modules/value_network.py
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'dspy_modules' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'dspy_modules' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir dspy_programs> [collection]
      pytest_collectstart [hook]
          collector: <Dir dspy_programs>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir dspy_programs>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/__pycache__
            path: /home/tom/git/agent/dspy_programs/__pycache__
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/active_learning.py
            path: /home/tom/git/agent/dspy_programs/active_learning.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/active_learning.py
            path: /home/tom/git/agent/dspy_programs/active_learning.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/coding_agent_repl.py
            path: /home/tom/git/agent/dspy_programs/coding_agent_repl.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/coding_agent_repl.py
            path: /home/tom/git/agent/dspy_programs/coding_agent_repl.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/dataset_manager.py
            path: /home/tom/git/agent/dspy_programs/dataset_manager.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/dataset_manager.py
            path: /home/tom/git/agent/dspy_programs/dataset_manager.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/deepseek_simba_optimizer.py
            path: /home/tom/git/agent/dspy_programs/deepseek_simba_optimizer.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/deepseek_simba_optimizer.py
            path: /home/tom/git/agent/dspy_programs/deepseek_simba_optimizer.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/generator_module.py
            path: /home/tom/git/agent/dspy_programs/generator_module.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/generator_module.py
            path: /home/tom/git/agent/dspy_programs/generator_module.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/memory_gan.py
            path: /home/tom/git/agent/dspy_programs/memory_gan.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/memory_gan.py
            path: /home/tom/git/agent/dspy_programs/memory_gan.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/online_optimization.py
            path: /home/tom/git/agent/dspy_programs/online_optimization.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/online_optimization.py
            path: /home/tom/git/agent/dspy_programs/online_optimization.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/taskwarrior_agent.py
            path: /home/tom/git/agent/dspy_programs/taskwarrior_agent.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/taskwarrior_agent.py
            path: /home/tom/git/agent/dspy_programs/taskwarrior_agent.py
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/dspy_programs/value_network.py
            path: /home/tom/git/agent/dspy_programs/value_network.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir dspy_programs>
            file_path: /home/tom/git/agent/dspy_programs/value_network.py
            path: /home/tom/git/agent/dspy_programs/value_network.py
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'dspy_programs' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'dspy_programs' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir mlruns> [collection]
      pytest_collectstart [hook]
          collector: <Dir mlruns>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir mlruns>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/.trash
            path: /home/tom/git/agent/mlruns/.trash
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/0
            path: /home/tom/git/agent/mlruns/0
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/0
            parent: <Dir mlruns>
        finish pytest_collect_directory --> <Dir 0> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339
            path: /home/tom/git/agent/mlruns/808707796043473339
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339
            parent: <Dir mlruns>
        finish pytest_collect_directory --> <Dir 808707796043473339> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742
            path: /home/tom/git/agent/mlruns/875387668209616742
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742
            parent: <Dir mlruns>
        finish pytest_collect_directory --> <Dir 875387668209616742> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns' lenresult=3 outcome='passed'> [hook]
    genitems <Dir 0> [collection]
      pytest_collectstart [hook]
          collector: <Dir 0>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 0>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/0/meta.yaml
            path: /home/tom/git/agent/mlruns/0/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 0>
            file_path: /home/tom/git/agent/mlruns/0/meta.yaml
            path: /home/tom/git/agent/mlruns/0/meta.yaml
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/0' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/0' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir 808707796043473339> [collection]
      pytest_collectstart [hook]
          collector: <Dir 808707796043473339>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 808707796043473339>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03
            parent: <Dir 808707796043473339>
        finish pytest_collect_directory --> <Dir 1ea6adb2e2534430aebaa85599adec03> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7
            parent: <Dir 808707796043473339>
        finish pytest_collect_directory --> <Dir 24166762419f4bea9c852751ae82d4a7> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30
            parent: <Dir 808707796043473339>
        finish pytest_collect_directory --> <Dir 6242a44404dc41ba8ee091135c478f30> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392
            parent: <Dir 808707796043473339>
        finish pytest_collect_directory --> <Dir 9d7def4eb65d49409e3a32136b7d8392> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960
            parent: <Dir 808707796043473339>
        finish pytest_collect_directory --> <Dir d2b66516a23d4079959be3b477e04960> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11
            parent: <Dir 808707796043473339>
        finish pytest_collect_directory --> <Dir e0606ddf484946b3b02d3e69f1fc7b11> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a
            parent: <Dir 808707796043473339>
        finish pytest_collect_directory --> <Dir ebd2fbeaf62d45b39720cae757a1646a> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f
            parent: <Dir 808707796043473339>
        finish pytest_collect_directory --> <Dir f18dd501bb024817bcd8724dca867c9f> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 808707796043473339>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/meta.yaml
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339' lenresult=8 outcome='passed'> [hook]
    genitems <Dir 1ea6adb2e2534430aebaa85599adec03> [collection]
      pytest_collectstart [hook]
          collector: <Dir 1ea6adb2e2534430aebaa85599adec03>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 1ea6adb2e2534430aebaa85599adec03>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts
            parent: <Dir 1ea6adb2e2534430aebaa85599adec03>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 1ea6adb2e2534430aebaa85599adec03>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics
            parent: <Dir 1ea6adb2e2534430aebaa85599adec03>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params
            parent: <Dir 1ea6adb2e2534430aebaa85599adec03>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags
            parent: <Dir 1ea6adb2e2534430aebaa85599adec03>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir optimized_dspy_program_final> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir artifacts>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir artifacts>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir unoptimized_dspy_program> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts' lenresult=2 outcome='passed'> [hook]
    genitems <Dir optimized_dspy_program_final> [collection]
      pytest_collectstart [hook]
          collector: <Dir optimized_dspy_program_final>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir optimized_dspy_program_final>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data
            parent: <Dir optimized_dspy_program_final>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/optimized_dspy_program_final' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir unoptimized_dspy_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir unoptimized_dspy_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir unoptimized_dspy_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data
            parent: <Dir unoptimized_dspy_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts/unoptimized_dspy_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/artifacts' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/time_improvement_percent
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/time_improvement_percent
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/time_improvement_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics/time_improvement_seconds
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_max_tokens
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_max_tokens
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_temperature
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/llm_temperature
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/optimized_program_final_question_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/optimized_program_final_question_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/optimized_program_final_question_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/optimized_program_final_question_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_bsize
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_bsize
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_num_threads
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/simba_num_threads
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/student_program_unoptimized_question_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/student_program_unoptimized_question_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/student_program_unoptimized_question_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params/student_program_unoptimized_question_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/dspy_optimizer
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/dspy_optimizer
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/evaluation_type
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/evaluation_type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/evaluation_type
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/evaluation_type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.log-model.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.log-model.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/optimized_program_final_status_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/optimized_program_final_status_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/optimized_program_final_status_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/optimized_program_final_status_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/optimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/optimized_program_logged
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/optimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/optimized_program_logged
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/simba_compilation_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/simba_compilation_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/student_program_unoptimized_status_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/student_program_unoptimized_status_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/student_program_unoptimized_status_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/student_program_unoptimized_status_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/unoptimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/unoptimized_program_logged
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/unoptimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags/unoptimized_program_logged
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/1ea6adb2e2534430aebaa85599adec03' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir 24166762419f4bea9c852751ae82d4a7> [collection]
      pytest_collectstart [hook]
          collector: <Dir 24166762419f4bea9c852751ae82d4a7>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 24166762419f4bea9c852751ae82d4a7>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts
            parent: <Dir 24166762419f4bea9c852751ae82d4a7>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 24166762419f4bea9c852751ae82d4a7>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics
            parent: <Dir 24166762419f4bea9c852751ae82d4a7>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params
            parent: <Dir 24166762419f4bea9c852751ae82d4a7>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags
            parent: <Dir 24166762419f4bea9c852751ae82d4a7>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir optimized_program> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir unoptimized_program> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts' lenresult=2 outcome='passed'> [hook]
    genitems <Dir optimized_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir optimized_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir optimized_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data
            parent: <Dir optimized_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/optimized_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir unoptimized_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir unoptimized_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir unoptimized_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data
            parent: <Dir unoptimized_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts/unoptimized_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/artifacts' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/optimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/optimized_time_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/optimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/optimized_time_seconds
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/time_improvement_percent
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/time_improvement_percent
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/time_improvement_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/time_improvement_seconds
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/unoptimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/unoptimized_time_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/unoptimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics/unoptimized_time_seconds
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_max_tokens
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_max_tokens
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_temperature
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/llm_temperature
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_bsize
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_bsize
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_num_threads
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params/simba_num_threads
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/dspy_optimizer
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/dspy_optimizer
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.log-model.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.log-model.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/optimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/optimized_program_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/optimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/optimized_program_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/simba_compilation_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/simba_compilation_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/unoptimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/unoptimized_program_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/unoptimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags/unoptimized_program_status
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/24166762419f4bea9c852751ae82d4a7' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir 6242a44404dc41ba8ee091135c478f30> [collection]
      pytest_collectstart [hook]
          collector: <Dir 6242a44404dc41ba8ee091135c478f30>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 6242a44404dc41ba8ee091135c478f30>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts
            parent: <Dir 6242a44404dc41ba8ee091135c478f30>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 6242a44404dc41ba8ee091135c478f30>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics
            parent: <Dir 6242a44404dc41ba8ee091135c478f30>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params
            parent: <Dir 6242a44404dc41ba8ee091135c478f30>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags
            parent: <Dir 6242a44404dc41ba8ee091135c478f30>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir optimized_dspy_program_final> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir artifacts>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir artifacts>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir unoptimized_dspy_program> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts' lenresult=2 outcome='passed'> [hook]
    genitems <Dir optimized_dspy_program_final> [collection]
      pytest_collectstart [hook]
          collector: <Dir optimized_dspy_program_final>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir optimized_dspy_program_final>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data
            parent: <Dir optimized_dspy_program_final>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/optimized_dspy_program_final' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir unoptimized_dspy_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir unoptimized_dspy_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir unoptimized_dspy_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data
            parent: <Dir unoptimized_dspy_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts/unoptimized_dspy_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/artifacts' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/time_improvement_percent
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/time_improvement_percent
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/time_improvement_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics/time_improvement_seconds
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_max_tokens
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_max_tokens
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_temperature
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/llm_temperature
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/optimized_program_final_question_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/optimized_program_final_question_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/optimized_program_final_question_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/optimized_program_final_question_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_bsize
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_bsize
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_num_threads
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/simba_num_threads
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/student_program_unoptimized_question_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/student_program_unoptimized_question_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/student_program_unoptimized_question_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params/student_program_unoptimized_question_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/dspy_optimizer
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/dspy_optimizer
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/evaluation_type
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/evaluation_type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/evaluation_type
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/evaluation_type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.log-model.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.log-model.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/optimized_program_final_status_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/optimized_program_final_status_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/optimized_program_final_status_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/optimized_program_final_status_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/optimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/optimized_program_logged
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/optimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/optimized_program_logged
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/simba_compilation_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/simba_compilation_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/student_program_unoptimized_status_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/student_program_unoptimized_status_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/student_program_unoptimized_status_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/student_program_unoptimized_status_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/unoptimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/unoptimized_program_logged
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/unoptimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags/unoptimized_program_logged
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/6242a44404dc41ba8ee091135c478f30' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir 9d7def4eb65d49409e3a32136b7d8392> [collection]
      pytest_collectstart [hook]
          collector: <Dir 9d7def4eb65d49409e3a32136b7d8392>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 9d7def4eb65d49409e3a32136b7d8392>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts
            parent: <Dir 9d7def4eb65d49409e3a32136b7d8392>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 9d7def4eb65d49409e3a32136b7d8392>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics
            parent: <Dir 9d7def4eb65d49409e3a32136b7d8392>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params
            parent: <Dir 9d7def4eb65d49409e3a32136b7d8392>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags
            parent: <Dir 9d7def4eb65d49409e3a32136b7d8392>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir optimized_program> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir unoptimized_program> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts' lenresult=2 outcome='passed'> [hook]
    genitems <Dir optimized_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir optimized_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir optimized_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data
            parent: <Dir optimized_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/optimized_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir unoptimized_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir unoptimized_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir unoptimized_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data
            parent: <Dir unoptimized_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts/unoptimized_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/artifacts' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/optimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/optimized_time_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/optimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/optimized_time_seconds
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/time_improvement_percent
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/time_improvement_percent
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/time_improvement_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/time_improvement_seconds
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/unoptimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/unoptimized_time_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/unoptimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics/unoptimized_time_seconds
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_max_tokens
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_max_tokens
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_temperature
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/llm_temperature
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_bsize
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_bsize
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_num_threads
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params/simba_num_threads
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/dspy_optimizer
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/dspy_optimizer
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.log-model.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.log-model.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/optimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/optimized_program_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/optimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/optimized_program_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/simba_compilation_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/simba_compilation_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/unoptimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/unoptimized_program_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/unoptimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags/unoptimized_program_status
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/9d7def4eb65d49409e3a32136b7d8392' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir d2b66516a23d4079959be3b477e04960> [collection]
      pytest_collectstart [hook]
          collector: <Dir d2b66516a23d4079959be3b477e04960>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir d2b66516a23d4079959be3b477e04960>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts
            parent: <Dir d2b66516a23d4079959be3b477e04960>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir d2b66516a23d4079959be3b477e04960>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics
            parent: <Dir d2b66516a23d4079959be3b477e04960>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params
            parent: <Dir d2b66516a23d4079959be3b477e04960>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags
            parent: <Dir d2b66516a23d4079959be3b477e04960>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir optimized_dspy_program_final> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir artifacts>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir artifacts>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir unoptimized_dspy_program> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts' lenresult=2 outcome='passed'> [hook]
    genitems <Dir optimized_dspy_program_final> [collection]
      pytest_collectstart [hook]
          collector: <Dir optimized_dspy_program_final>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir optimized_dspy_program_final>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data
            parent: <Dir optimized_dspy_program_final>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/input_example.json
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/input_example.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/input_example.json
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/input_example.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/requirements.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/serving_input_example.json
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/serving_input_example.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/serving_input_example.json
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/serving_input_example.json
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/optimized_dspy_program_final' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir unoptimized_dspy_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir unoptimized_dspy_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir unoptimized_dspy_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data
            parent: <Dir unoptimized_dspy_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/input_example.json
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/input_example.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/input_example.json
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/input_example.json
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/serving_input_example.json
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/serving_input_example.json
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/serving_input_example.json
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/serving_input_example.json
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts/unoptimized_dspy_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/artifacts' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/time_improvement_percent
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/time_improvement_percent
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/time_improvement_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics/time_improvement_seconds
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_max_tokens
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_max_tokens
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_temperature
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/llm_temperature
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/optimized_program_final_question_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/optimized_program_final_question_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/optimized_program_final_question_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/optimized_program_final_question_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_bsize
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_bsize
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_num_threads
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/simba_num_threads
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/student_program_unoptimized_question_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/student_program_unoptimized_question_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/student_program_unoptimized_question_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params/student_program_unoptimized_question_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/dspy_optimizer
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/dspy_optimizer
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/evaluation_type
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/evaluation_type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/evaluation_type
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/evaluation_type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.log-model.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.log-model.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/optimized_program_final_status_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/optimized_program_final_status_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/optimized_program_final_status_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/optimized_program_final_status_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/optimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/optimized_program_logged
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/optimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/optimized_program_logged
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/simba_compilation_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/simba_compilation_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/student_program_unoptimized_status_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/student_program_unoptimized_status_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/student_program_unoptimized_status_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/student_program_unoptimized_status_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/unoptimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/unoptimized_program_logged
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/unoptimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags/unoptimized_program_logged
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/d2b66516a23d4079959be3b477e04960' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir e0606ddf484946b3b02d3e69f1fc7b11> [collection]
      pytest_collectstart [hook]
          collector: <Dir e0606ddf484946b3b02d3e69f1fc7b11>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir e0606ddf484946b3b02d3e69f1fc7b11>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts
            parent: <Dir e0606ddf484946b3b02d3e69f1fc7b11>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir e0606ddf484946b3b02d3e69f1fc7b11>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics
            parent: <Dir e0606ddf484946b3b02d3e69f1fc7b11>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params
            parent: <Dir e0606ddf484946b3b02d3e69f1fc7b11>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags
            parent: <Dir e0606ddf484946b3b02d3e69f1fc7b11>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir optimized_dspy_program_final> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir artifacts>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_program_final_answer_optimized_final_evaluation.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir artifacts>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/student_program_unoptimized_answer_unoptimized_evaluation.txt
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir unoptimized_dspy_program> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts' lenresult=2 outcome='passed'> [hook]
    genitems <Dir optimized_dspy_program_final> [collection]
      pytest_collectstart [hook]
          collector: <Dir optimized_dspy_program_final>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir optimized_dspy_program_final>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data
            parent: <Dir optimized_dspy_program_final>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_dspy_program_final>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/optimized_dspy_program_final' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir unoptimized_dspy_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir unoptimized_dspy_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir unoptimized_dspy_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data
            parent: <Dir unoptimized_dspy_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_dspy_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts/unoptimized_dspy_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/artifacts' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/optimized_program_final_time_seconds_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/student_program_unoptimized_time_seconds_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/time_improvement_percent
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/time_improvement_percent
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/time_improvement_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics/time_improvement_seconds
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_max_tokens
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_max_tokens
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_temperature
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/llm_temperature
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/optimized_program_final_question_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/optimized_program_final_question_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/optimized_program_final_question_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/optimized_program_final_question_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_bsize
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_bsize
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_num_threads
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/simba_num_threads
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/student_program_unoptimized_question_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/student_program_unoptimized_question_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/student_program_unoptimized_question_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params/student_program_unoptimized_question_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/dspy_optimizer
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/dspy_optimizer
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/evaluation_type
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/evaluation_type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/evaluation_type
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/evaluation_type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.log-model.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.log-model.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/optimized_program_final_status_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/optimized_program_final_status_optimized_final_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/optimized_program_final_status_optimized_final_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/optimized_program_final_status_optimized_final_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/optimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/optimized_program_logged
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/optimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/optimized_program_logged
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/simba_compilation_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/simba_compilation_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/student_program_unoptimized_status_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/student_program_unoptimized_status_unoptimized_evaluation
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/student_program_unoptimized_status_unoptimized_evaluation
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/student_program_unoptimized_status_unoptimized_evaluation
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/unoptimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/unoptimized_program_logged
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/unoptimized_program_logged
            path: /home/tom/git/agent/mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags/unoptimized_program_logged
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/e0606ddf484946b3b02d3e69f1fc7b11' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir ebd2fbeaf62d45b39720cae757a1646a> [collection]
      pytest_collectstart [hook]
          collector: <Dir ebd2fbeaf62d45b39720cae757a1646a>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir ebd2fbeaf62d45b39720cae757a1646a>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts
            parent: <Dir ebd2fbeaf62d45b39720cae757a1646a>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir ebd2fbeaf62d45b39720cae757a1646a>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics
            parent: <Dir ebd2fbeaf62d45b39720cae757a1646a>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params
            parent: <Dir ebd2fbeaf62d45b39720cae757a1646a>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags
            parent: <Dir ebd2fbeaf62d45b39720cae757a1646a>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir optimized_program> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir unoptimized_program> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts' lenresult=2 outcome='passed'> [hook]
    genitems <Dir optimized_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir optimized_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir optimized_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data
            parent: <Dir optimized_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/optimized_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir unoptimized_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir unoptimized_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir unoptimized_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data
            parent: <Dir unoptimized_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts/unoptimized_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/artifacts' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/optimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/optimized_time_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/optimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/optimized_time_seconds
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/time_improvement_percent
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/time_improvement_percent
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/time_improvement_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/time_improvement_seconds
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/unoptimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/unoptimized_time_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/unoptimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics/unoptimized_time_seconds
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_max_tokens
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_max_tokens
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_temperature
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/llm_temperature
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_bsize
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_bsize
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_num_threads
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params/simba_num_threads
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/dspy_optimizer
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/dspy_optimizer
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.log-model.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.log-model.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/optimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/optimized_program_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/optimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/optimized_program_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/simba_compilation_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/simba_compilation_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/unoptimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/unoptimized_program_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/unoptimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags/unoptimized_program_status
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/ebd2fbeaf62d45b39720cae757a1646a' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir f18dd501bb024817bcd8724dca867c9f> [collection]
      pytest_collectstart [hook]
          collector: <Dir f18dd501bb024817bcd8724dca867c9f>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir f18dd501bb024817bcd8724dca867c9f>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts
            parent: <Dir f18dd501bb024817bcd8724dca867c9f>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir f18dd501bb024817bcd8724dca867c9f>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/meta.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics
            parent: <Dir f18dd501bb024817bcd8724dca867c9f>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params
            parent: <Dir f18dd501bb024817bcd8724dca867c9f>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags
            parent: <Dir f18dd501bb024817bcd8724dca867c9f>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir optimized_program> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program
            parent: <Dir artifacts>
        finish pytest_collect_directory --> <Dir unoptimized_program> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts' lenresult=2 outcome='passed'> [hook]
    genitems <Dir optimized_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir optimized_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir optimized_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data
            parent: <Dir optimized_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir optimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/optimized_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir unoptimized_program> [collection]
      pytest_collectstart [hook]
          collector: <Dir unoptimized_program>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir unoptimized_program>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/MLmodel
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/MLmodel
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/MLmodel
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/conda.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/conda.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/conda.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data
            parent: <Dir unoptimized_program>
        finish pytest_collect_directory --> <Dir data> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/python_env.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/python_env.yaml
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/python_env.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/requirements.txt
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir unoptimized_program>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/requirements.txt
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/requirements.txt
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program' lenresult=1 outcome='passed'> [hook]
    genitems <Dir data> [collection]
      pytest_collectstart [hook]
          collector: <Dir data>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir data>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data/model.pkl
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir data>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data/model.pkl
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data/model.pkl
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program/data' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts/unoptimized_program' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/artifacts' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/optimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/optimized_time_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/optimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/optimized_time_seconds
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/time_improvement_percent
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/time_improvement_percent
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/time_improvement_percent
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/time_improvement_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/time_improvement_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/time_improvement_seconds
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/unoptimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/unoptimized_time_seconds
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/unoptimized_time_seconds
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics/unoptimized_time_seconds
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_max_tokens
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_max_tokens
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_max_tokens
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_model_name
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_temperature
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_temperature
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/llm_temperature
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_bsize
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_bsize
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_bsize
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_num_threads
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_num_threads
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params/simba_num_threads
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/dspy_optimizer
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/dspy_optimizer
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/dspy_optimizer
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.log-model.history
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.log-model.history
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.log-model.history
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/optimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/optimized_program_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/optimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/optimized_program_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/simba_compilation_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/simba_compilation_status
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/simba_compilation_status
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/unoptimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/unoptimized_program_status
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/unoptimized_program_status
            path: /home/tom/git/agent/mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags/unoptimized_program_status
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339/f18dd501bb024817bcd8724dca867c9f' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/808707796043473339' lenresult=8 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir 875387668209616742> [collection]
      pytest_collectstart [hook]
          collector: <Dir 875387668209616742>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 875387668209616742>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed
            parent: <Dir 875387668209616742>
        finish pytest_collect_directory --> <Dir 0ed8cf97bc184590a7c6488303e3e3ed> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403
            parent: <Dir 875387668209616742>
        finish pytest_collect_directory --> <Dir 574d53ffbf1442279d630fb1b8054403> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/meta.yaml
            path: /home/tom/git/agent/mlruns/875387668209616742/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 875387668209616742>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/meta.yaml
            path: /home/tom/git/agent/mlruns/875387668209616742/meta.yaml
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742' lenresult=2 outcome='passed'> [hook]
    genitems <Dir 0ed8cf97bc184590a7c6488303e3e3ed> [collection]
      pytest_collectstart [hook]
          collector: <Dir 0ed8cf97bc184590a7c6488303e3e3ed>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 0ed8cf97bc184590a7c6488303e3e3ed>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/artifacts
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/artifacts
            parent: <Dir 0ed8cf97bc184590a7c6488303e3e3ed>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/meta.yaml
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 0ed8cf97bc184590a7c6488303e3e3ed>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/meta.yaml
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics
            parent: <Dir 0ed8cf97bc184590a7c6488303e3e3ed>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params
            parent: <Dir 0ed8cf97bc184590a7c6488303e3e3ed>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags
            parent: <Dir 0ed8cf97bc184590a7c6488303e3e3ed>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/artifacts' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/artifacts' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics/optimization_completed
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics/optimization_completed
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics/optimization_completed
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics/optimization_completed
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics/test_gan_score
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics/test_gan_score
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir metrics>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics/test_gan_score
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics/test_gan_score
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/llm_model_name
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/llm_model_name
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/num_train_examples
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/num_train_examples
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/num_train_examples
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/num_train_examples
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/0ed8cf97bc184590a7c6488303e3e3ed' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir 574d53ffbf1442279d630fb1b8054403> [collection]
      pytest_collectstart [hook]
          collector: <Dir 574d53ffbf1442279d630fb1b8054403>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir 574d53ffbf1442279d630fb1b8054403>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/artifacts
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/artifacts
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/artifacts
            parent: <Dir 574d53ffbf1442279d630fb1b8054403>
        finish pytest_collect_directory --> <Dir artifacts> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/meta.yaml
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/meta.yaml
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir 574d53ffbf1442279d630fb1b8054403>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/meta.yaml
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/meta.yaml
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/metrics
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/metrics
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/metrics
            parent: <Dir 574d53ffbf1442279d630fb1b8054403>
        finish pytest_collect_directory --> <Dir metrics> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params
            parent: <Dir 574d53ffbf1442279d630fb1b8054403>
        finish pytest_collect_directory --> <Dir params> [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_directory [hook]
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags
            parent: <Dir 574d53ffbf1442279d630fb1b8054403>
        finish pytest_collect_directory --> <Dir tags> [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403' lenresult=4 outcome='passed'> [hook]
    genitems <Dir artifacts> [collection]
      pytest_collectstart [hook]
          collector: <Dir artifacts>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir artifacts>
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/artifacts' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/artifacts' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir metrics> [collection]
      pytest_collectstart [hook]
          collector: <Dir metrics>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir metrics>
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/metrics' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/metrics' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir params> [collection]
      pytest_collectstart [hook]
          collector: <Dir params>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir params>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/llm_model_name
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/llm_model_name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/llm_model_name
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/llm_model_name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/num_train_examples
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/num_train_examples
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/num_train_examples
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/num_train_examples
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/simba_max_demos
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/simba_max_demos
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/simba_max_demos
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/simba_max_steps
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir params>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/simba_max_steps
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params/simba_max_steps
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/params' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tags> [collection]
      pytest_collectstart [hook]
          collector: <Dir tags>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tags>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.runName
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.runName
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.runName
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.git.commit
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.git.commit
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.git.commit
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.name
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.name
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.name
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.type
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.type
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.source.type
        finish pytest_collect_file --> [] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.user
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tags>
            file_path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.user
            path: /home/tom/git/agent/mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags/mlflow.user
        finish pytest_collect_file --> [] [hook]
      finish pytest_make_collect_report --> <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags' lenresult=0 outcome='passed'> [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403/tags' lenresult=0 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742/574d53ffbf1442279d630fb1b8054403' lenresult=4 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns/875387668209616742' lenresult=2 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'mlruns' lenresult=3 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_shell_wrapper.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_shell_wrapper.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_shell_wrapper.py>
      find_module called for: test_shell_wrapper [assertion]
      matched test file '/home/tom/git/agent/test_shell_wrapper.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/test_shell_wrapper.py [assertion]
      early skip of rewriting module: shell_wrapper [assertion]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: @py_builtins
            obj: <module 'builtins' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: @pytest_ar
            obj: <module '_pytest.assertion.rewrite' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/assertion/rewrite.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: asyncio
            obj: <module 'asyncio' from '/home/tom/.pyenv/versions/3.11.10/lib/python3.11/asyncio/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: os
            obj: <module 'os' (frozen)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: tempfile
            obj: <module 'tempfile' from '/home/tom/.pyenv/versions/3.11.10/lib/python3.11/tempfile.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: pytest
            obj: <module 'pytest' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/pytest/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: __warningregistry__
            obj: {'version': 10, ('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 6): True, ('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 17): True, ('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 27): True, ('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 35): True, ('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 52): True, ('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 61): True, ('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 69): True}
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: pytestmark
            obj: MarkDecorator(mark=Mark(name='timeout', args=(10,), kwargs={'method': 'thread'}))
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: ShellWrapper
            obj: <class 'shell_wrapper.ShellWrapper'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: shell_wrapper
            obj: <pytest_fixture(<function shell_wrapper at 0x7f613d496f20>)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: test_shell_start_stop
            obj: <function test_shell_start_stop at 0x7f613d496a20>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613d4d7750>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_shell_start_stop>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: test_execute_simple_command
            obj: <function test_execute_simple_command at 0x7f613d496d40>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613dbf7490>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_execute_simple_command>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: test_cd_command
            obj: <function test_cd_command at 0x7f613d497060>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613d450590>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_cd_command>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: test_cd_nonexistent_directory
            obj: <function test_cd_nonexistent_directory at 0x7f613d497100>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613d4e50d0>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_cd_nonexistent_directory>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: test_command_with_error
            obj: <function test_command_with_error at 0x7f613d4971a0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613d4e54d0>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_command_with_error>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_shell_wrapper.py>
            name: test_concurrent_commands
            obj: <function test_concurrent_commands at 0x7f613d497240>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613d4e5390>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_concurrent_commands>] [hook]
      finish pytest_make_collect_report --> <CollectReport 'test_shell_wrapper.py' lenresult=6 outcome='passed'> [hook]
    genitems <Function test_shell_start_stop> [collection]
      pytest_itemcollected [hook]
          item: <Function test_shell_start_stop>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_execute_simple_command> [collection]
      pytest_itemcollected [hook]
          item: <Function test_execute_simple_command>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_cd_command> [collection]
      pytest_itemcollected [hook]
          item: <Function test_cd_command>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_cd_nonexistent_directory> [collection]
      pytest_itemcollected [hook]
          item: <Function test_cd_nonexistent_directory>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_command_with_error> [collection]
      pytest_itemcollected [hook]
          item: <Function test_command_with_error>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_concurrent_commands> [collection]
      pytest_itemcollected [hook]
          item: <Function test_concurrent_commands>
      finish pytest_itemcollected --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'test_shell_wrapper.py' lenresult=6 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_textual_task_manager.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_textual_task_manager.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_textual_task_manager.py>
      find_module called for: test_textual_task_manager [assertion]
      matched test file '/home/tom/git/agent/test_textual_task_manager.py' [assertion]
      _read_pyc(/home/tom/git/agent/test_textual_task_manager.py): out of date [assertion]
      rewriting PosixPath('/home/tom/git/agent/test_textual_task_manager.py') [assertion]
      finish pytest_make_collect_report --> <CollectReport 'test_textual_task_manager.py' lenresult=0 outcome='failed'> [hook]
      pytest_exception_interact [hook]
          node: <Module test_textual_task_manager.py>
          call: <CallInfo when='collect' excinfo=<ExceptionInfo CollectError(ExceptionChainRepr(reprtraceback=ReprTraceback(reprentries=[ReprEntry(lines=['    mod = import_path('], r...me/tom/git/agent/test_textual_task_manager.py", line 107\n    ```python\n    ^\nSyntaxError: invalid syntax'), None)])) tblen=7>>
          report: <CollectReport 'test_textual_task_manager.py' lenresult=0 outcome='failed'>
      finish pytest_exception_interact --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'test_textual_task_manager.py' lenresult=0 outcome='failed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Dir tests> [collection]
      pytest_collectstart [hook]
          collector: <Dir tests>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Dir tests>
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/__pycache__
            path: /home/tom/git/agent/tests/__pycache__
        finish pytest_ignore_collect --> True [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_active_learning.py
            path: /home/tom/git/agent/tests/test_active_learning.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_active_learning.py
            path: /home/tom/git/agent/tests/test_active_learning.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_active_learning.py
              path: /home/tom/git/agent/tests/test_active_learning.py
          finish pytest_pycollect_makemodule --> <Module test_active_learning.py> [hook]
        finish pytest_collect_file --> [<Module test_active_learning.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_coding_agent_repl.py
            path: /home/tom/git/agent/tests/test_coding_agent_repl.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_coding_agent_repl.py
            path: /home/tom/git/agent/tests/test_coding_agent_repl.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_coding_agent_repl.py
              path: /home/tom/git/agent/tests/test_coding_agent_repl.py
          finish pytest_pycollect_makemodule --> <Module test_coding_agent_repl.py> [hook]
        finish pytest_collect_file --> [<Module test_coding_agent_repl.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_interactive_chat.py
            path: /home/tom/git/agent/tests/test_interactive_chat.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_interactive_chat.py
            path: /home/tom/git/agent/tests/test_interactive_chat.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_interactive_chat.py
              path: /home/tom/git/agent/tests/test_interactive_chat.py
          finish pytest_pycollect_makemodule --> <Module test_interactive_chat.py> [hook]
        finish pytest_collect_file --> [<Module test_interactive_chat.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_iterative_improvement_elo.py
            path: /home/tom/git/agent/tests/test_iterative_improvement_elo.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_iterative_improvement_elo.py
            path: /home/tom/git/agent/tests/test_iterative_improvement_elo.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_iterative_improvement_elo.py
              path: /home/tom/git/agent/tests/test_iterative_improvement_elo.py
          finish pytest_pycollect_makemodule --> <Module test_iterative_improvement_elo.py> [hook]
        finish pytest_collect_file --> [<Module test_iterative_improvement_elo.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_memory_gan.py
            path: /home/tom/git/agent/tests/test_memory_gan.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_memory_gan.py
            path: /home/tom/git/agent/tests/test_memory_gan.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_memory_gan.py
              path: /home/tom/git/agent/tests/test_memory_gan.py
          finish pytest_pycollect_makemodule --> <Module test_memory_gan.py> [hook]
        finish pytest_collect_file --> [<Module test_memory_gan.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_minimal_dspy_import.py
            path: /home/tom/git/agent/tests/test_minimal_dspy_import.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_minimal_dspy_import.py
            path: /home/tom/git/agent/tests/test_minimal_dspy_import.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_minimal_dspy_import.py
              path: /home/tom/git/agent/tests/test_minimal_dspy_import.py
          finish pytest_pycollect_makemodule --> <Module test_minimal_dspy_import.py> [hook]
        finish pytest_collect_file --> [<Module test_minimal_dspy_import.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_online_optimization.py
            path: /home/tom/git/agent/tests/test_online_optimization.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_online_optimization.py
            path: /home/tom/git/agent/tests/test_online_optimization.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_online_optimization.py
              path: /home/tom/git/agent/tests/test_online_optimization.py
          finish pytest_pycollect_makemodule --> <Module test_online_optimization.py> [hook]
        finish pytest_collect_file --> [<Module test_online_optimization.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_self_review_agent.py
            path: /home/tom/git/agent/tests/test_self_review_agent.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_self_review_agent.py
            path: /home/tom/git/agent/tests/test_self_review_agent.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_self_review_agent.py
              path: /home/tom/git/agent/tests/test_self_review_agent.py
          finish pytest_pycollect_makemodule --> <Module test_self_review_agent.py> [hook]
        finish pytest_collect_file --> [<Module test_self_review_agent.py>] [hook]
        pytest_ignore_collect [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            collection_path: /home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py
            path: /home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py
        finish pytest_ignore_collect --> None [hook]
        pytest_collect_file [hook]
            parent: <Dir tests>
            file_path: /home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py
            path: /home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py
          pytest_pycollect_makemodule [hook]
              parent: <Dir tests>
              module_path: /home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py
              path: /home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py
          finish pytest_pycollect_makemodule --> <Module test_taskwarrior_dspy_agent.py> [hook]
        finish pytest_collect_file --> [<Module test_taskwarrior_dspy_agent.py>] [hook]
      finish pytest_make_collect_report --> <CollectReport 'tests' lenresult=9 outcome='passed'> [hook]
    genitems <Module test_active_learning.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_active_learning.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_active_learning.py>
      find_module called for: test_active_learning [assertion]
      matched test file '/home/tom/git/agent/tests/test_active_learning.py' [assertion]
      _read_pyc(/home/tom/git/agent/tests/test_active_learning.py): out of date [assertion]
      rewriting PosixPath('/home/tom/git/agent/tests/test_active_learning.py') [assertion]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_active_learning.py' lenresult=0 outcome='failed'> [hook]
      pytest_exception_interact [hook]
          node: <Module test_active_learning.py>
          call: <CallInfo when='collect' excinfo=<ExceptionInfo CollectError(ExceptionChainRepr(reprtraceback=ReprTraceback(reprentries=[ReprEntry(lines=['    mod = import_path('], r...line 1\n    versions pytest-8.4.0, python-3.11.10.final.0\n             ^^^^^^\nSyntaxError: invalid syntax'), None)])) tblen=7>>
          report: <CollectReport 'tests/test_active_learning.py' lenresult=0 outcome='failed'>
      finish pytest_exception_interact --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_active_learning.py' lenresult=0 outcome='failed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_coding_agent_repl.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_coding_agent_repl.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_coding_agent_repl.py>
      find_module called for: test_coding_agent_repl [assertion]
      matched test file '/home/tom/git/agent/tests/test_coding_agent_repl.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/tests/test_coding_agent_repl.py [assertion]
      early skip of rewriting module: dspy [assertion]
      early skip of rewriting module: dspy.predict [assertion]
      early skip of rewriting module: dspy.predict.aggregation [assertion]
      early skip of rewriting module: dspy.dsp [assertion]
      early skip of rewriting module: dspy.dsp.utils [assertion]
      early skip of rewriting module: dspy.dsp.utils.dpr [assertion]
      early skip of rewriting module: regex [assertion]
      early skip of rewriting module: regex.regex [assertion]
      early skip of rewriting module: regex._regex_core [assertion]
      early skip of rewriting module: regex._regex [assertion]
      early skip of rewriting module: regex.DEFAULT_VERSION [assertion]
      early skip of rewriting module: dspy.dsp.utils.metrics [assertion]
      early skip of rewriting module: dspy.dsp.utils.utils [assertion]
      early skip of rewriting module: tqdm [assertion]
      early skip of rewriting module: tqdm._monitor [assertion]
      early skip of rewriting module: tqdm._tqdm_pandas [assertion]
      early skip of rewriting module: tqdm.cli [assertion]
      early skip of rewriting module: tqdm.std [assertion]
      early skip of rewriting module: tqdm.utils [assertion]
      early skip of rewriting module: tqdm.version [assertion]
      early skip of rewriting module: tqdm._dist_ver [assertion]
      early skip of rewriting module: tqdm.gui [assertion]
      early skip of rewriting module: dspy.dsp.utils.settings [assertion]
      early skip of rewriting module: dspy.primitives [assertion]
      early skip of rewriting module: dspy.primitives.assertions [assertion]
      early skip of rewriting module: dspy.primitives.example [assertion]
      early skip of rewriting module: dspy.primitives.module [assertion]
      early skip of rewriting module: cloudpickle [assertion]
      early skip of rewriting module: cloudpickle.cloudpickle [assertion]
      early skip of rewriting module: pickle [assertion]
      early skip of rewriting module: _compat_pickle [assertion]
      early skip of rewriting module: _pickle [assertion]
      early skip of rewriting module: org [assertion]
      early skip of rewriting module: ujson [assertion]
      early skip of rewriting module: dspy.utils [assertion]
      early skip of rewriting module: requests [assertion]
      early skip of rewriting module: urllib3 [assertion]
      early skip of rewriting module: urllib3.exceptions [assertion]
      early skip of rewriting module: http [assertion]
      early skip of rewriting module: http.client [assertion]
      early skip of rewriting module: urllib3._base_connection [assertion]
      early skip of rewriting module: urllib3.util [assertion]
      early skip of rewriting module: urllib3.util.connection [assertion]
      early skip of rewriting module: urllib3.util.timeout [assertion]
      early skip of rewriting module: urllib3.util.request [assertion]
      early skip of rewriting module: urllib3.util.util [assertion]
      early skip of rewriting module: brotlicffi [assertion]
      early skip of rewriting module: brotli [assertion]
      early skip of rewriting module: zstandard [assertion]
      early skip of rewriting module: urllib3.util.response [assertion]
      early skip of rewriting module: urllib3.util.retry [assertion]
      early skip of rewriting module: urllib3.util.ssl_ [assertion]
      early skip of rewriting module: hashlib [assertion]
      early skip of rewriting module: _hashlib [assertion]
      early skip of rewriting module: _blake2 [assertion]
      early skip of rewriting module: hmac [assertion]
      early skip of rewriting module: urllib3.util.url [assertion]
      early skip of rewriting module: urllib3.util.ssltransport [assertion]
      early skip of rewriting module: urllib3.util.wait [assertion]
      early skip of rewriting module: urllib3._collections [assertion]
      early skip of rewriting module: urllib3._version [assertion]
      early skip of rewriting module: urllib3.connectionpool [assertion]
      early skip of rewriting module: queue [assertion]
      early skip of rewriting module: _queue [assertion]
      early skip of rewriting module: urllib3._request_methods [assertion]
      early skip of rewriting module: urllib3.filepost [assertion]
      early skip of rewriting module: urllib3.fields [assertion]
      early skip of rewriting module: mimetypes [assertion]
      early skip of rewriting module: _winapi [assertion]
      early skip of rewriting module: winreg [assertion]
      early skip of rewriting module: urllib3.response [assertion]
      early skip of rewriting module: brotlicffi [assertion]
      early skip of rewriting module: brotli [assertion]
      early skip of rewriting module: zstandard [assertion]
      early skip of rewriting module: urllib3.connection [assertion]
      early skip of rewriting module: urllib3.http2 [assertion]
      early skip of rewriting module: urllib3.http2.probe [assertion]
      early skip of rewriting module: urllib3.util.ssl_match_hostname [assertion]
      early skip of rewriting module: urllib3.util.proxy [assertion]
      early skip of rewriting module: urllib3.poolmanager [assertion]
      early skip of rewriting module: requests.exceptions [assertion]
      early skip of rewriting module: requests.compat [assertion]
      early skip of rewriting module: chardet [assertion]
      early skip of rewriting module: charset_normalizer [assertion]
      early skip of rewriting module: charset_normalizer.api [assertion]
      early skip of rewriting module: charset_normalizer.cd [assertion]
      early skip of rewriting module: charset_normalizer.constant [assertion]
      early skip of rewriting module: charset_normalizer.md [assertion]
      early skip of rewriting module: charset_normalizer.md__mypyc [assertion]
      early skip of rewriting module: charset_normalizer.utils [assertion]
      early skip of rewriting module: _multibytecodec [assertion]
      early skip of rewriting module: charset_normalizer.models [assertion]
      early skip of rewriting module: charset_normalizer.legacy [assertion]
      early skip of rewriting module: charset_normalizer.version [assertion]
      early skip of rewriting module: simplejson [assertion]
      early skip of rewriting module: http.cookiejar [assertion]
      early skip of rewriting module: urllib.request [assertion]
      early skip of rewriting module: urllib.error [assertion]
      early skip of rewriting module: urllib.response [assertion]
      early skip of rewriting module: http.cookies [assertion]
      early skip of rewriting module: chardet [assertion]
      early skip of rewriting module: requests.packages [assertion]
      early skip of rewriting module: idna [assertion]
      early skip of rewriting module: idna.core [assertion]
      early skip of rewriting module: idna.idnadata [assertion]
      early skip of rewriting module: idna.intranges [assertion]
      early skip of rewriting module: idna.package_data [assertion]
      early skip of rewriting module: requests.utils [assertion]
      early skip of rewriting module: requests.certs [assertion]
      early skip of rewriting module: certifi [assertion]
      early skip of rewriting module: certifi.core [assertion]
      early skip of rewriting module: requests.__version__ [assertion]
      early skip of rewriting module: requests._internal_utils [assertion]
      early skip of rewriting module: requests.cookies [assertion]
      early skip of rewriting module: requests.structures [assertion]
      early skip of rewriting module: importlib.readers [assertion]
      early skip of rewriting module: importlib.resources.readers [assertion]
      early skip of rewriting module: importlib.resources._itertools [assertion]
      early skip of rewriting module: requests.api [assertion]
      early skip of rewriting module: requests.sessions [assertion]
      early skip of rewriting module: requests.adapters [assertion]
      early skip of rewriting module: requests.auth [assertion]
      early skip of rewriting module: requests.models [assertion]
      early skip of rewriting module: encodings.idna [assertion]
      early skip of rewriting module: stringprep [assertion]
      early skip of rewriting module: requests.hooks [assertion]
      early skip of rewriting module: requests.status_codes [assertion]
      early skip of rewriting module: urllib3.contrib [assertion]
      early skip of rewriting module: urllib3.contrib.socks [assertion]
      early skip of rewriting module: socks [assertion]
      early skip of rewriting module: dspy.streaming [assertion]
      early skip of rewriting module: dspy.streaming.messages [assertion]
      early skip of rewriting module: dspy.utils.callback [assertion]
      early skip of rewriting module: dspy.streaming.streamify [assertion]
      early skip of rewriting module: litellm [assertion]
      early skip of rewriting module: litellm.llms [assertion]
      early skip of rewriting module: litellm.llms.custom_httpx [assertion]
      early skip of rewriting module: litellm.llms.custom_httpx.http_handler [assertion]
      early skip of rewriting module: httpx [assertion]
      early skip of rewriting module: httpx.__version__ [assertion]
      early skip of rewriting module: httpx._api [assertion]
      early skip of rewriting module: httpx._client [assertion]
      early skip of rewriting module: httpx._auth [assertion]
      early skip of rewriting module: httpx._exceptions [assertion]
      early skip of rewriting module: httpx._models [assertion]
      early skip of rewriting module: httpx._content [assertion]
      early skip of rewriting module: httpx._multipart [assertion]
      early skip of rewriting module: httpx._types [assertion]
      early skip of rewriting module: httpx._utils [assertion]
      early skip of rewriting module: httpx._decoders [assertion]
      early skip of rewriting module: brotli [assertion]
      early skip of rewriting module: brotlicffi [assertion]
      early skip of rewriting module: zstandard [assertion]
      early skip of rewriting module: httpx._status_codes [assertion]
      early skip of rewriting module: httpx._urls [assertion]
      early skip of rewriting module: httpx._urlparse [assertion]
      early skip of rewriting module: httpx._config [assertion]
      early skip of rewriting module: httpx._transports [assertion]
      early skip of rewriting module: httpx._transports.asgi [assertion]
      early skip of rewriting module: httpx._transports.base [assertion]
      early skip of rewriting module: httpx._transports.default [assertion]
      early skip of rewriting module: httpx._transports.mock [assertion]
      early skip of rewriting module: httpx._transports.wsgi [assertion]
      early skip of rewriting module: httpx._main [assertion]
      early skip of rewriting module: click [assertion]
      early skip of rewriting module: click.core [assertion]
      early skip of rewriting module: click.types [assertion]
      early skip of rewriting module: click._compat [assertion]
      early skip of rewriting module: click.exceptions [assertion]
      early skip of rewriting module: click.globals [assertion]
      early skip of rewriting module: click.utils [assertion]
      early skip of rewriting module: click.formatting [assertion]
      early skip of rewriting module: click.parser [assertion]
      early skip of rewriting module: click.termui [assertion]
      early skip of rewriting module: click.decorators [assertion]
      early skip of rewriting module: rich [assertion]
      early skip of rewriting module: rich._extension [assertion]
      early skip of rewriting module: rich.console [assertion]
      early skip of rewriting module: getpass [assertion]
      early skip of rewriting module: termios [assertion]
      early skip of rewriting module: html [assertion]
      early skip of rewriting module: html.entities [assertion]
      early skip of rewriting module: rich._null_file [assertion]
      early skip of rewriting module: rich.errors [assertion]
      early skip of rewriting module: rich.themes [assertion]
      early skip of rewriting module: rich.default_styles [assertion]
      early skip of rewriting module: rich.style [assertion]
      early skip of rewriting module: rich.color [assertion]
      early skip of rewriting module: colorsys [assertion]
      early skip of rewriting module: rich._palettes [assertion]
      early skip of rewriting module: rich.palette [assertion]
      early skip of rewriting module: rich.color_triplet [assertion]
      early skip of rewriting module: rich.repr [assertion]
      early skip of rewriting module: rich.terminal_theme [assertion]
      early skip of rewriting module: rich.theme [assertion]
      early skip of rewriting module: configparser [assertion]
      early skip of rewriting module: rich._emoji_replace [assertion]
      early skip of rewriting module: rich._emoji_codes [assertion]
      early skip of rewriting module: rich._export_format [assertion]
      early skip of rewriting module: rich._fileno [assertion]
      early skip of rewriting module: rich._log_render [assertion]
      early skip of rewriting module: rich.text [assertion]
      early skip of rewriting module: rich._loop [assertion]
      early skip of rewriting module: rich._pick [assertion]
      early skip of rewriting module: rich._wrap [assertion]
      early skip of rewriting module: rich.cells [assertion]
      early skip of rewriting module: rich._cell_widths [assertion]
      early skip of rewriting module: rich.align [assertion]
      early skip of rewriting module: rich.constrain [assertion]
      early skip of rewriting module: rich.jupyter [assertion]
      early skip of rewriting module: rich.segment [assertion]
      early skip of rewriting module: rich.measure [assertion]
      early skip of rewriting module: rich.protocol [assertion]
      early skip of rewriting module: rich.containers [assertion]
      early skip of rewriting module: rich.control [assertion]
      early skip of rewriting module: rich.emoji [assertion]
      early skip of rewriting module: rich.highlighter [assertion]
      early skip of rewriting module: rich.markup [assertion]
      early skip of rewriting module: rich.pager [assertion]
      early skip of rewriting module: rich.pretty [assertion]
      early skip of rewriting module: attr [assertion]
      early skip of rewriting module: attr.converters [assertion]
      early skip of rewriting module: attr._compat [assertion]
      early skip of rewriting module: attr._make [assertion]
      early skip of rewriting module: attr._config [assertion]
      early skip of rewriting module: attr.setters [assertion]
      early skip of rewriting module: attr.exceptions [assertion]
      early skip of rewriting module: attr.filters [assertion]
      early skip of rewriting module: attr.validators [assertion]
      early skip of rewriting module: attr._cmp [assertion]
      early skip of rewriting module: attr._funcs [assertion]
      early skip of rewriting module: attr._next_gen [assertion]
      early skip of rewriting module: attr._version_info [assertion]
      early skip of rewriting module: rich.abc [assertion]
      early skip of rewriting module: rich.region [assertion]
      early skip of rewriting module: rich.scope [assertion]
      early skip of rewriting module: rich.panel [assertion]
      early skip of rewriting module: rich.box [assertion]
      early skip of rewriting module: rich.padding [assertion]
      early skip of rewriting module: rich.table [assertion]
      early skip of rewriting module: rich._ratio [assertion]
      early skip of rewriting module: fractions [assertion]
      early skip of rewriting module: rich.screen [assertion]
      early skip of rewriting module: rich.styled [assertion]
      early skip of rewriting module: rich.progress [assertion]
      early skip of rewriting module: mmap [assertion]
      early skip of rewriting module: rich.filesize [assertion]
      early skip of rewriting module: rich.live [assertion]
      early skip of rewriting module: rich.file_proxy [assertion]
      early skip of rewriting module: rich.ansi [assertion]
      early skip of rewriting module: rich.live_render [assertion]
      early skip of rewriting module: rich.progress_bar [assertion]
      early skip of rewriting module: rich.spinner [assertion]
      early skip of rewriting module: rich._spinners [assertion]
      early skip of rewriting module: rich.syntax [assertion]
      early skip of rewriting module: pygments.style [assertion]
      early skip of rewriting module: aiohttp [assertion]
      early skip of rewriting module: aiohttp.hdrs [assertion]
      early skip of rewriting module: multidict [assertion]
      early skip of rewriting module: multidict._abc [assertion]
      early skip of rewriting module: multidict._compat [assertion]
      early skip of rewriting module: multidict._multidict [assertion]
      early skip of rewriting module: aiohttp.client [assertion]
      early skip of rewriting module: yarl [assertion]
      early skip of rewriting module: yarl._query [assertion]
      early skip of rewriting module: yarl._quoters [assertion]
      early skip of rewriting module: yarl._quoting [assertion]
      early skip of rewriting module: yarl._quoting_c [assertion]
      early skip of rewriting module: yarl._url [assertion]
      early skip of rewriting module: propcache [assertion]
      early skip of rewriting module: propcache.api [assertion]
      early skip of rewriting module: propcache._helpers [assertion]
      early skip of rewriting module: propcache._helpers_c [assertion]
      early skip of rewriting module: yarl._parse [assertion]
      early skip of rewriting module: yarl._path [assertion]
      early skip of rewriting module: aiohttp.http [assertion]
      early skip of rewriting module: aiohttp.http_exceptions [assertion]
      early skip of rewriting module: aiohttp.typedefs [assertion]
      early skip of rewriting module: aiohttp.http_parser [assertion]
      early skip of rewriting module: aiohttp.base_protocol [assertion]
      early skip of rewriting module: aiohttp.client_exceptions [assertion]
      early skip of rewriting module: aiohttp.helpers [assertion]
      early skip of rewriting module: netrc [assertion]
      early skip of rewriting module: aiohttp.log [assertion]
      early skip of rewriting module: aiohttp.tcp_helpers [assertion]
      early skip of rewriting module: aiohttp.compression_utils [assertion]
      early skip of rewriting module: brotlicffi [assertion]
      early skip of rewriting module: brotli [assertion]
      early skip of rewriting module: aiohttp.http_writer [assertion]
      early skip of rewriting module: aiohttp.abc [assertion]
      early skip of rewriting module: aiohttp._cookie_helpers [assertion]
      early skip of rewriting module: aiohttp._http_writer [assertion]
      early skip of rewriting module: aiohttp.streams [assertion]
      early skip of rewriting module: aiohttp._http_parser [assertion]
      early skip of rewriting module: aiohttp.http_websocket [assertion]
      early skip of rewriting module: aiohttp._websocket [assertion]
      early skip of rewriting module: aiohttp._websocket.helpers [assertion]
      early skip of rewriting module: aiohttp._websocket.models [assertion]
      early skip of rewriting module: aiohttp._websocket.mask [assertion]
      early skip of rewriting module: aiohttp._websocket.reader [assertion]
      early skip of rewriting module: aiohttp._websocket.reader_c [assertion]
      early skip of rewriting module: aiohttp._websocket.writer [assertion]
      early skip of rewriting module: aiohttp.payload [assertion]
      early skip of rewriting module: aiohttp.client_middlewares [assertion]
      early skip of rewriting module: aiohttp.client_reqrep [assertion]
      early skip of rewriting module: aiohttp.multipart [assertion]
      early skip of rewriting module: aiohttp.formdata [assertion]
      early skip of rewriting module: aiohttp.client_ws [assertion]
      early skip of rewriting module: aiohttp.connector [assertion]
      early skip of rewriting module: aiohappyeyeballs [assertion]
      early skip of rewriting module: aiohappyeyeballs.impl [assertion]
      early skip of rewriting module: aiohappyeyeballs._staggered [assertion]
      early skip of rewriting module: aiohappyeyeballs.types [assertion]
      early skip of rewriting module: aiohappyeyeballs.utils [assertion]
      early skip of rewriting module: aiohttp.client_proto [assertion]
      early skip of rewriting module: aiohttp.resolver [assertion]
      early skip of rewriting module: aiodns [assertion]
      early skip of rewriting module: aiohttp.cookiejar [assertion]
      early skip of rewriting module: aiohttp.tracing [assertion]
      early skip of rewriting module: aiosignal [assertion]
      early skip of rewriting module: frozenlist [assertion]
      early skip of rewriting module: frozenlist._frozenlist [assertion]
      early skip of rewriting module: aiohttp.client_middleware_digest_auth [assertion]
      early skip of rewriting module: aiohttp.payload_streamer [assertion]
      early skip of rewriting module: litellm._logging [assertion]
      early skip of rewriting module: litellm.constants [assertion]
      early skip of rewriting module: litellm.litellm_core_utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.logging_utils [assertion]
      early skip of rewriting module: litellm.types [assertion]
      early skip of rewriting module: litellm.types.utils [assertion]
      early skip of rewriting module: openai [assertion]
      early skip of rewriting module: openai.types [assertion]
      early skip of rewriting module: openai.types.batch [assertion]
      early skip of rewriting module: openai._models [assertion]
      early skip of rewriting module: pydantic [assertion]
      early skip of rewriting module: pydantic._migration [assertion]
      early skip of rewriting module: pydantic.version [assertion]
      early skip of rewriting module: pydantic_core [assertion]
      early skip of rewriting module: pydantic_core._pydantic_core [assertion]
      early skip of rewriting module: pydantic_core.core_schema [assertion]
      early skip of rewriting module: pydantic.errors [assertion]
      early skip of rewriting module: typing_inspection [assertion]
      early skip of rewriting module: typing_inspection.introspection [assertion]
      early skip of rewriting module: typing_inspection.typing_objects [assertion]
      early skip of rewriting module: pydantic._internal [assertion]
      early skip of rewriting module: pydantic._internal._repr [assertion]
      early skip of rewriting module: pydantic._internal._typing_extra [assertion]
      early skip of rewriting module: pydantic._internal._namespace_utils [assertion]
      early skip of rewriting module: pydantic.fields [assertion]
      early skip of rewriting module: annotated_types [assertion]
      early skip of rewriting module: pydantic._internal._validators [assertion]
      early skip of rewriting module: zoneinfo [assertion]
      early skip of rewriting module: zoneinfo._tzpath [assertion]
      early skip of rewriting module: sysconfig [assertion]
      early skip of rewriting module: _sysconfigdata__linux_x86_64-linux-gnu [assertion]
      early skip of rewriting module: zoneinfo._common [assertion]
      early skip of rewriting module: _zoneinfo [assertion]
      early skip of rewriting module: pydantic._internal._import_utils [assertion]
      early skip of rewriting module: pydantic.types [assertion]
      early skip of rewriting module: pydantic._internal._fields [assertion]
      early skip of rewriting module: pydantic.warnings [assertion]
      early skip of rewriting module: pydantic._internal._generics [assertion]
      early skip of rewriting module: pydantic._internal._core_utils [assertion]
      early skip of rewriting module: pydantic._internal._forward_ref [assertion]
      early skip of rewriting module: pydantic._internal._utils [assertion]
      early skip of rewriting module: pydantic._internal._config [assertion]
      early skip of rewriting module: pydantic.aliases [assertion]
      early skip of rewriting module: pydantic._internal._internal_dataclass [assertion]
      early skip of rewriting module: pydantic.config [assertion]
      early skip of rewriting module: pydantic._internal._docs_extraction [assertion]
      early skip of rewriting module: pydantic.annotated_handlers [assertion]
      early skip of rewriting module: pydantic.json_schema [assertion]
      early skip of rewriting module: pydantic._internal._core_metadata [assertion]
      early skip of rewriting module: pydantic._internal._decorators [assertion]
      early skip of rewriting module: pydantic._internal._mock_val_ser [assertion]
      early skip of rewriting module: pydantic.plugin [assertion]
      early skip of rewriting module: pydantic.plugin._schema_validator [assertion]
      early skip of rewriting module: pydantic._internal._schema_generation_shared [assertion]
      early skip of rewriting module: openai._types [assertion]
      early skip of rewriting module: pydantic.main [assertion]
      early skip of rewriting module: pydantic._internal._model_construction [assertion]
      early skip of rewriting module: pydantic._internal._generate_schema [assertion]
      early skip of rewriting module: pydantic.functional_validators [assertion]
      early skip of rewriting module: pydantic._internal._discriminated_union [assertion]
      early skip of rewriting module: pydantic._internal._known_annotated_metadata [assertion]
      early skip of rewriting module: pydantic._internal._schema_gather [assertion]
      early skip of rewriting module: pydantic._internal._signature [assertion]
      early skip of rewriting module: openai._utils [assertion]
      early skip of rewriting module: openai._utils._logs [assertion]
      early skip of rewriting module: openai._utils._utils [assertion]
      early skip of rewriting module: openai._compat [assertion]
      early skip of rewriting module: pydantic.v1 [assertion]
      early skip of rewriting module: pydantic.v1.dataclasses [assertion]
      early skip of rewriting module: pydantic.v1.class_validators [assertion]
      early skip of rewriting module: pydantic.v1.errors [assertion]
      early skip of rewriting module: pydantic.v1.typing [assertion]
      early skip of rewriting module: pydantic.v1.utils [assertion]
      early skip of rewriting module: pydantic.v1.version [assertion]
      early skip of rewriting module: cython [assertion]
      early skip of rewriting module: pydantic.v1.config [assertion]
      early skip of rewriting module: pydantic.v1.error_wrappers [assertion]
      early skip of rewriting module: pydantic.v1.json [assertion]
      early skip of rewriting module: pydantic.v1.color [assertion]
      early skip of rewriting module: pydantic.v1.networks [assertion]
      early skip of rewriting module: pydantic.v1.validators [assertion]
      early skip of rewriting module: pydantic.v1.datetime_parse [assertion]
      early skip of rewriting module: pydantic.v1.types [assertion]
      early skip of rewriting module: pydantic.v1.fields [assertion]
      early skip of rewriting module: pydantic.v1.main [assertion]
      early skip of rewriting module: pydantic.v1.parse [assertion]
      early skip of rewriting module: pydantic.v1.schema [assertion]
      early skip of rewriting module: pydantic.v1.annotated_types [assertion]
      early skip of rewriting module: pydantic.v1.decorator [assertion]
      early skip of rewriting module: pydantic.v1.env_settings [assertion]
      early skip of rewriting module: pydantic.v1.tools [assertion]
      early skip of rewriting module: pydantic.plugin._loader [assertion]
      early skip of rewriting module: openai._utils._sync [assertion]
      early skip of rewriting module: openai._utils._proxy [assertion]
      early skip of rewriting module: openai._utils._typing [assertion]
      early skip of rewriting module: openai._utils._streams [assertion]
      early skip of rewriting module: openai._utils._transform [assertion]
      early skip of rewriting module: openai._files [assertion]
      early skip of rewriting module: openai._utils._reflection [assertion]
      early skip of rewriting module: openai._constants [assertion]
      early skip of rewriting module: pydantic.type_adapter [assertion]
      early skip of rewriting module: pydantic._internal._serializers [assertion]
      early skip of rewriting module: openai.types.batch_error [assertion]
      early skip of rewriting module: openai.types.shared [assertion]
      early skip of rewriting module: openai.types.shared.metadata [assertion]
      early skip of rewriting module: openai.types.shared.reasoning [assertion]
      early skip of rewriting module: openai.types.shared.reasoning_effort [assertion]
      early skip of rewriting module: openai.types.shared.all_models [assertion]
      early skip of rewriting module: openai.types.shared.chat_model [assertion]
      early skip of rewriting module: openai.types.shared.error_object [assertion]
      early skip of rewriting module: openai.types.shared.compound_filter [assertion]
      early skip of rewriting module: openai.types.shared.comparison_filter [assertion]
      early skip of rewriting module: openai.types.shared.responses_model [assertion]
      early skip of rewriting module: openai.types.shared.function_definition [assertion]
      early skip of rewriting module: openai.types.shared.function_parameters [assertion]
      early skip of rewriting module: openai.types.shared.response_format_text [assertion]
      early skip of rewriting module: openai.types.shared.response_format_json_object [assertion]
      early skip of rewriting module: openai.types.shared.response_format_json_schema [assertion]
      early skip of rewriting module: openai.types.batch_request_counts [assertion]
      early skip of rewriting module: openai.types.image [assertion]
      early skip of rewriting module: openai.types.model [assertion]
      early skip of rewriting module: openai.types.upload [assertion]
      early skip of rewriting module: openai.types.file_object [assertion]
      early skip of rewriting module: openai.types.embedding [assertion]
      early skip of rewriting module: openai.types.chat_model [assertion]
      early skip of rewriting module: openai.types.completion [assertion]
      early skip of rewriting module: openai.types.completion_usage [assertion]
      early skip of rewriting module: openai.types.completion_choice [assertion]
      early skip of rewriting module: openai.types.moderation [assertion]
      early skip of rewriting module: openai.types.audio_model [assertion]
      early skip of rewriting module: openai.types.image_model [assertion]
      early skip of rewriting module: openai.types.file_content [assertion]
      early skip of rewriting module: openai.types.file_deleted [assertion]
      early skip of rewriting module: openai.types.file_purpose [assertion]
      early skip of rewriting module: openai.types.vector_store [assertion]
      early skip of rewriting module: openai.types.model_deleted [assertion]
      early skip of rewriting module: openai.types.embedding_model [assertion]
      early skip of rewriting module: openai.types.images_response [assertion]
      early skip of rewriting module: openai.types.eval_list_params [assertion]
      early skip of rewriting module: openai.types.file_list_params [assertion]
      early skip of rewriting module: openai.types.moderation_model [assertion]
      early skip of rewriting module: openai.types.batch_list_params [assertion]
      early skip of rewriting module: openai.types.image_edit_params [assertion]
      early skip of rewriting module: openai.types.eval_create_params [assertion]
      early skip of rewriting module: openai.types.shared_params [assertion]
      early skip of rewriting module: openai.types.shared_params.metadata [assertion]
      early skip of rewriting module: openai.types.shared_params.reasoning [assertion]
      early skip of rewriting module: openai.types.shared_params.chat_model [assertion]
      early skip of rewriting module: openai.types.shared_params.compound_filter [assertion]
      early skip of rewriting module: openai.types.shared_params.comparison_filter [assertion]
      early skip of rewriting module: openai.types.shared_params.responses_model [assertion]
      early skip of rewriting module: openai.types.shared_params.reasoning_effort [assertion]
      early skip of rewriting module: openai.types.shared_params.function_definition [assertion]
      early skip of rewriting module: openai.types.shared_params.function_parameters [assertion]
      early skip of rewriting module: openai.types.shared_params.response_format_text [assertion]
      early skip of rewriting module: openai.types.shared_params.response_format_json_object [assertion]
      early skip of rewriting module: openai.types.shared_params.response_format_json_schema [assertion]
      early skip of rewriting module: openai.types.graders [assertion]
      early skip of rewriting module: openai.types.graders.multi_grader [assertion]
      early skip of rewriting module: openai.types.graders.python_grader [assertion]
      early skip of rewriting module: openai.types.graders.label_model_grader [assertion]
      early skip of rewriting module: openai.types.responses [assertion]
      early skip of rewriting module: openai.types.responses.tool [assertion]
      early skip of rewriting module: openai.types.responses.computer_tool [assertion]
      early skip of rewriting module: openai.types.responses.function_tool [assertion]
      early skip of rewriting module: openai.types.responses.web_search_tool [assertion]
      early skip of rewriting module: openai.types.responses.file_search_tool [assertion]
      early skip of rewriting module: openai.types.responses.response [assertion]
      early skip of rewriting module: openai.types.responses.response_error [assertion]
      early skip of rewriting module: openai.types.responses.response_usage [assertion]
      early skip of rewriting module: openai.types.responses.response_status [assertion]
      early skip of rewriting module: openai.types.responses.tool_choice_types [assertion]
      early skip of rewriting module: openai.types.responses.tool_choice_options [assertion]
      early skip of rewriting module: openai.types.responses.response_output_item [assertion]
      early skip of rewriting module: openai.types.responses.response_output_message [assertion]
      early skip of rewriting module: openai.types.responses.response_output_text [assertion]
      early skip of rewriting module: openai.types.responses.response_output_refusal [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_item [assertion]
      early skip of rewriting module: openai.types.responses.response_computer_tool_call [assertion]
      early skip of rewriting module: openai.types.responses.response_function_tool_call [assertion]
      early skip of rewriting module: openai.types.responses.response_function_web_search [assertion]
      early skip of rewriting module: openai.types.responses.response_file_search_tool_call [assertion]
      early skip of rewriting module: openai.types.responses.response_code_interpreter_tool_call [assertion]
      early skip of rewriting module: openai.types.responses.response_text_config [assertion]
      early skip of rewriting module: openai.types.responses.response_format_text_config [assertion]
      early skip of rewriting module: openai.types.responses.response_format_text_json_schema_config [assertion]
      early skip of rewriting module: openai.types.responses.tool_choice_function [assertion]
      early skip of rewriting module: openai.types.responses.tool_param [assertion]
      early skip of rewriting module: openai.types.responses.computer_tool_param [assertion]
      early skip of rewriting module: openai.types.responses.function_tool_param [assertion]
      early skip of rewriting module: openai.types.responses.web_search_tool_param [assertion]
      early skip of rewriting module: openai.types.responses.file_search_tool_param [assertion]
      early skip of rewriting module: openai.types.chat [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_message [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_audio [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_message_tool_call [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_token_logprob [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_role [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_tool [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_chunk [assertion]
      early skip of rewriting module: openai.types.chat.completion_list_params [assertion]
      early skip of rewriting module: openai.types.chat.parsed_chat_completion [assertion]
      early skip of rewriting module: openai.types.chat.parsed_function_tool_call [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_deleted [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_modality [assertion]
      early skip of rewriting module: openai.types.chat.completion_create_params [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_tool_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_audio_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_message_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_tool_message_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_content_part_text_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_user_message_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_content_part_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_content_part_image_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_content_part_input_audio_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_system_message_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_function_message_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_assistant_message_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_message_tool_call_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_content_part_refusal_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_developer_message_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_stream_options_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_prediction_content_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_tool_choice_option_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_named_tool_choice_param [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_function_call_option_param [assertion]
      early skip of rewriting module: openai.types.chat.completion_update_params [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_store_message [assertion]
      early skip of rewriting module: openai.types.chat.chat_completion_reasoning_effort [assertion]
      early skip of rewriting module: openai.types.responses.response_item [assertion]
      early skip of rewriting module: openai.types.responses.response_input_message_item [assertion]
      early skip of rewriting module: openai.types.responses.response_input_message_content_list [assertion]
      early skip of rewriting module: openai.types.responses.response_input_content [assertion]
      early skip of rewriting module: openai.types.responses.response_input_file [assertion]
      early skip of rewriting module: openai.types.responses.response_input_text [assertion]
      early skip of rewriting module: openai.types.responses.response_input_image [assertion]
      early skip of rewriting module: openai.types.responses.response_function_tool_call_item [assertion]
      early skip of rewriting module: openai.types.responses.response_computer_tool_call_output_item [assertion]
      early skip of rewriting module: openai.types.responses.response_computer_tool_call_output_screenshot [assertion]
      early skip of rewriting module: openai.types.responses.response_function_tool_call_output_item [assertion]
      early skip of rewriting module: openai.types.responses.parsed_response [assertion]
      early skip of rewriting module: openai.types.responses.easy_input_message [assertion]
      early skip of rewriting module: openai.types.responses.response_item_list [assertion]
      early skip of rewriting module: openai.types.responses.response_includable [assertion]
      early skip of rewriting module: openai.types.responses.response_error_event [assertion]
      early skip of rewriting module: openai.types.responses.response_input_param [assertion]
      early skip of rewriting module: openai.types.responses.easy_input_message_param [assertion]
      early skip of rewriting module: openai.types.responses.response_input_message_content_list_param [assertion]
      early skip of rewriting module: openai.types.responses.response_input_file_param [assertion]
      early skip of rewriting module: openai.types.responses.response_input_text_param [assertion]
      early skip of rewriting module: openai.types.responses.response_input_image_param [assertion]
      early skip of rewriting module: openai.types.responses.response_output_message_param [assertion]
      early skip of rewriting module: openai.types.responses.response_output_text_param [assertion]
      early skip of rewriting module: openai.types.responses.response_output_refusal_param [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_item_param [assertion]
      early skip of rewriting module: openai.types.responses.response_computer_tool_call_param [assertion]
      early skip of rewriting module: openai.types.responses.response_function_tool_call_param [assertion]
      early skip of rewriting module: openai.types.responses.response_function_web_search_param [assertion]
      early skip of rewriting module: openai.types.responses.response_file_search_tool_call_param [assertion]
      early skip of rewriting module: openai.types.responses.response_code_interpreter_tool_call_param [assertion]
      early skip of rewriting module: openai.types.responses.response_computer_tool_call_output_screenshot_param [assertion]
      early skip of rewriting module: openai.types.responses.response_failed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_queued_event [assertion]
      early skip of rewriting module: openai.types.responses.response_stream_event [assertion]
      early skip of rewriting module: openai.types.responses.response_created_event [assertion]
      early skip of rewriting module: openai.types.responses.response_completed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_text_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_audio_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_incomplete_event [assertion]
      early skip of rewriting module: openai.types.responses.response_text_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_audio_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_in_progress_event [assertion]
      early skip of rewriting module: openai.types.responses.response_refusal_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_refusal_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_mcp_call_failed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_output_item_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_content_part_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_output_item_added_event [assertion]
      early skip of rewriting module: openai.types.responses.response_content_part_added_event [assertion]
      early skip of rewriting module: openai.types.responses.response_mcp_call_completed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_mcp_call_in_progress_event [assertion]
      early skip of rewriting module: openai.types.responses.response_audio_transcript_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_mcp_list_tools_failed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_audio_transcript_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_summary_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_mcp_call_arguments_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_summary_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_image_gen_call_completed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_mcp_call_arguments_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_mcp_list_tools_completed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_image_gen_call_generating_event [assertion]
      early skip of rewriting module: openai.types.responses.response_web_search_call_completed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_web_search_call_searching_event [assertion]
      early skip of rewriting module: openai.types.responses.response_file_search_call_completed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_file_search_call_searching_event [assertion]
      early skip of rewriting module: openai.types.responses.response_image_gen_call_in_progress_event [assertion]
      early skip of rewriting module: openai.types.responses.response_mcp_list_tools_in_progress_event [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_summary_part_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_summary_text_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_web_search_call_in_progress_event [assertion]
      early skip of rewriting module: openai.types.responses.response_file_search_call_in_progress_event [assertion]
      early skip of rewriting module: openai.types.responses.response_function_call_arguments_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_image_gen_call_partial_image_event [assertion]
      early skip of rewriting module: openai.types.responses.response_output_text_annotation_added_event [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_summary_part_added_event [assertion]
      early skip of rewriting module: openai.types.responses.response_reasoning_summary_text_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_function_call_arguments_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_code_interpreter_call_code_done_event [assertion]
      early skip of rewriting module: openai.types.responses.response_code_interpreter_call_completed_event [assertion]
      early skip of rewriting module: openai.types.responses.response_code_interpreter_call_code_delta_event [assertion]
      early skip of rewriting module: openai.types.responses.response_code_interpreter_call_in_progress_event [assertion]
      early skip of rewriting module: openai.types.responses.response_code_interpreter_call_interpreting_event [assertion]
      early skip of rewriting module: openai.types.responses.input_item_list_params [assertion]
      early skip of rewriting module: openai.types.responses.response_create_params [assertion]
      early skip of rewriting module: openai.types.responses.tool_choice_types_param [assertion]
      early skip of rewriting module: openai.types.responses.response_text_config_param [assertion]
      early skip of rewriting module: openai.types.responses.response_format_text_config_param [assertion]
      early skip of rewriting module: openai.types.responses.response_format_text_json_schema_config_param [assertion]
      early skip of rewriting module: openai.types.responses.tool_choice_function_param [assertion]
      early skip of rewriting module: openai.types.responses.response_retrieve_params [assertion]
      early skip of rewriting module: openai.types.responses.response_input_item_param [assertion]
      early skip of rewriting module: openai.types.responses.response_input_content_param [assertion]
      early skip of rewriting module: openai.types.graders.score_model_grader [assertion]
      early skip of rewriting module: openai.types.graders.string_check_grader [assertion]
      early skip of rewriting module: openai.types.graders.text_similarity_grader [assertion]
      early skip of rewriting module: openai.types.graders.multi_grader_param [assertion]
      early skip of rewriting module: openai.types.graders.python_grader_param [assertion]
      early skip of rewriting module: openai.types.graders.label_model_grader_param [assertion]
      early skip of rewriting module: openai.types.graders.score_model_grader_param [assertion]
      early skip of rewriting module: openai.types.graders.string_check_grader_param [assertion]
      early skip of rewriting module: openai.types.graders.text_similarity_grader_param [assertion]
      early skip of rewriting module: openai.types.eval_list_response [assertion]
      early skip of rewriting module: openai.types.eval_custom_data_source_config [assertion]
      early skip of rewriting module: openai.types.eval_stored_completions_data_source_config [assertion]
      early skip of rewriting module: openai.types.eval_update_params [assertion]
      early skip of rewriting module: openai.types.file_create_params [assertion]
      early skip of rewriting module: openai.types.batch_create_params [assertion]
      early skip of rewriting module: openai.types.eval_create_response [assertion]
      early skip of rewriting module: openai.types.eval_delete_response [assertion]
      early skip of rewriting module: openai.types.eval_update_response [assertion]
      early skip of rewriting module: openai.types.upload_create_params [assertion]
      early skip of rewriting module: openai.types.vector_store_deleted [assertion]
      early skip of rewriting module: openai.types.audio_response_format [assertion]
      early skip of rewriting module: openai.types.container_list_params [assertion]
      early skip of rewriting module: openai.types.image_generate_params [assertion]
      early skip of rewriting module: openai.types.eval_retrieve_response [assertion]
      early skip of rewriting module: openai.types.file_chunking_strategy [assertion]
      early skip of rewriting module: openai.types.other_file_chunking_strategy_object [assertion]
      early skip of rewriting module: openai.types.static_file_chunking_strategy_object [assertion]
      early skip of rewriting module: openai.types.static_file_chunking_strategy [assertion]
      early skip of rewriting module: openai.types.upload_complete_params [assertion]
      early skip of rewriting module: openai.types.container_create_params [assertion]
      early skip of rewriting module: openai.types.container_list_response [assertion]
      early skip of rewriting module: openai.types.embedding_create_params [assertion]
      early skip of rewriting module: openai.types.completion_create_params [assertion]
      early skip of rewriting module: openai.types.moderation_create_params [assertion]
      early skip of rewriting module: openai.types.moderation_multi_modal_input_param [assertion]
      early skip of rewriting module: openai.types.moderation_text_input_param [assertion]
      early skip of rewriting module: openai.types.moderation_image_url_input_param [assertion]
      early skip of rewriting module: openai.types.vector_store_list_params [assertion]
      early skip of rewriting module: openai.types.container_create_response [assertion]
      early skip of rewriting module: openai.types.create_embedding_response [assertion]
      early skip of rewriting module: openai.types.moderation_create_response [assertion]
      early skip of rewriting module: openai.types.vector_store_create_params [assertion]
      early skip of rewriting module: openai.types.file_chunking_strategy_param [assertion]
      early skip of rewriting module: openai.types.auto_file_chunking_strategy_param [assertion]
      early skip of rewriting module: openai.types.static_file_chunking_strategy_object_param [assertion]
      early skip of rewriting module: openai.types.static_file_chunking_strategy_param [assertion]
      early skip of rewriting module: openai.types.vector_store_search_params [assertion]
      early skip of rewriting module: openai.types.vector_store_update_params [assertion]
      early skip of rewriting module: openai.types.container_retrieve_response [assertion]
      early skip of rewriting module: openai.types.vector_store_search_response [assertion]
      early skip of rewriting module: openai.types.websocket_connection_options [assertion]
      early skip of rewriting module: openai.types.image_create_variation_params [assertion]
      early skip of rewriting module: openai._client [assertion]
      early skip of rewriting module: openai._exceptions [assertion]
      early skip of rewriting module: openai._qs [assertion]
      early skip of rewriting module: openai._version [assertion]
      early skip of rewriting module: openai._streaming [assertion]
      early skip of rewriting module: openai._base_client [assertion]
      early skip of rewriting module: distro [assertion]
      early skip of rewriting module: distro.distro [assertion]
      early skip of rewriting module: openai._response [assertion]
      early skip of rewriting module: openai._legacy_response [assertion]
      early skip of rewriting module: openai._utils._resources_proxy [assertion]
      early skip of rewriting module: openai.lib [assertion]
      early skip of rewriting module: openai.lib._tools [assertion]
      early skip of rewriting module: openai.lib._pydantic [assertion]
      early skip of rewriting module: openai.lib._parsing [assertion]
      early skip of rewriting module: openai.lib._parsing._completions [assertion]
      early skip of rewriting module: openai.lib.azure [assertion]
      early skip of rewriting module: openai.version [assertion]
      early skip of rewriting module: openai.lib._old_api [assertion]
      early skip of rewriting module: openai.lib.streaming [assertion]
      early skip of rewriting module: openai.lib.streaming._assistants [assertion]
      early skip of rewriting module: openai.types.beta [assertion]
      early skip of rewriting module: openai.types.beta.thread [assertion]
      early skip of rewriting module: openai.types.beta.assistant [assertion]
      early skip of rewriting module: openai.types.beta.assistant_tool [assertion]
      early skip of rewriting module: openai.types.beta.function_tool [assertion]
      early skip of rewriting module: openai.types.beta.file_search_tool [assertion]
      early skip of rewriting module: openai.types.beta.code_interpreter_tool [assertion]
      early skip of rewriting module: openai.types.beta.assistant_response_format_option [assertion]
      early skip of rewriting module: openai.types.beta.thread_deleted [assertion]
      early skip of rewriting module: openai.types.beta.assistant_deleted [assertion]
      early skip of rewriting module: openai.types.beta.function_tool_param [assertion]
      early skip of rewriting module: openai.types.beta.assistant_tool_param [assertion]
      early skip of rewriting module: openai.types.beta.file_search_tool_param [assertion]
      early skip of rewriting module: openai.types.beta.code_interpreter_tool_param [assertion]
      early skip of rewriting module: openai.types.beta.thread_create_params [assertion]
      early skip of rewriting module: openai.types.beta.threads [assertion]
      early skip of rewriting module: openai.types.beta.threads.run [assertion]
      early skip of rewriting module: openai.types.beta.threads.run_status [assertion]
      early skip of rewriting module: openai.types.beta.assistant_tool_choice_option [assertion]
      early skip of rewriting module: openai.types.beta.assistant_tool_choice [assertion]
      early skip of rewriting module: openai.types.beta.assistant_tool_choice_function [assertion]
      early skip of rewriting module: openai.types.beta.threads.required_action_function_tool_call [assertion]
      early skip of rewriting module: openai.types.beta.threads.text [assertion]
      early skip of rewriting module: openai.types.beta.threads.annotation [assertion]
      early skip of rewriting module: openai.types.beta.threads.file_path_annotation [assertion]
      early skip of rewriting module: openai.types.beta.threads.file_citation_annotation [assertion]
      early skip of rewriting module: openai.types.beta.threads.message [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_content [assertion]
      early skip of rewriting module: openai.types.beta.threads.text_content_block [assertion]
      early skip of rewriting module: openai.types.beta.threads.refusal_content_block [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_url_content_block [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_url [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_file_content_block [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_file [assertion]
      early skip of rewriting module: openai.types.beta.threads.text_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.annotation_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.file_path_delta_annotation [assertion]
      early skip of rewriting module: openai.types.beta.threads.file_citation_delta_annotation [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_content_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.text_delta_block [assertion]
      early skip of rewriting module: openai.types.beta.threads.refusal_delta_block [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_url_delta_block [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_url_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_file_delta_block [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_file_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_url_param [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_deleted [assertion]
      early skip of rewriting module: openai.types.beta.threads.run_list_params [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_file_param [assertion]
      early skip of rewriting module: openai.types.beta.threads.run_create_params [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.run_step [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.tool_calls_step_details [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.tool_call [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.function_tool_call [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.file_search_tool_call [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.code_interpreter_tool_call [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.message_creation_step_details [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.run_step_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.tool_call_delta_object [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.tool_call_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.function_tool_call_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.file_search_tool_call_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.code_interpreter_tool_call_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.code_interpreter_logs [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.code_interpreter_output_image [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.run_step_delta_message_delta [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.run_step_include [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.step_list_params [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.run_step_delta_event [assertion]
      early skip of rewriting module: openai.types.beta.threads.runs.step_retrieve_params [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_content_part_param [assertion]
      early skip of rewriting module: openai.types.beta.threads.text_content_block_param [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_url_content_block_param [assertion]
      early skip of rewriting module: openai.types.beta.threads.image_file_content_block_param [assertion]
      early skip of rewriting module: openai.types.beta.assistant_tool_choice_option_param [assertion]
      early skip of rewriting module: openai.types.beta.assistant_tool_choice_param [assertion]
      early skip of rewriting module: openai.types.beta.assistant_tool_choice_function_param [assertion]
      early skip of rewriting module: openai.types.beta.assistant_response_format_option_param [assertion]
      early skip of rewriting module: openai.types.beta.threads.run_update_params [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_delta_event [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_list_params [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_create_params [assertion]
      early skip of rewriting module: openai.types.beta.threads.message_update_params [assertion]
      early skip of rewriting module: openai.types.beta.threads.run_submit_tool_outputs_params [assertion]
      early skip of rewriting module: openai.types.beta.thread_update_params [assertion]
      early skip of rewriting module: openai.types.beta.assistant_list_params [assertion]
      early skip of rewriting module: openai.types.beta.assistant_stream_event [assertion]
      early skip of rewriting module: openai.types.beta.assistant_create_params [assertion]
      early skip of rewriting module: openai.types.beta.assistant_update_params [assertion]
      early skip of rewriting module: openai.types.beta.thread_create_and_run_params [assertion]
      early skip of rewriting module: openai._module_client [assertion]
      early skip of rewriting module: openai.types.audio [assertion]
      early skip of rewriting module: openai.types.audio.translation [assertion]
      early skip of rewriting module: openai.types.audio.speech_model [assertion]
      early skip of rewriting module: openai.types.audio.transcription [assertion]
      early skip of rewriting module: openai.types.audio.transcription_word [assertion]
      early skip of rewriting module: openai.types.audio.translation_verbose [assertion]
      early skip of rewriting module: openai.types.audio.transcription_segment [assertion]
      early skip of rewriting module: openai.types.audio.speech_create_params [assertion]
      early skip of rewriting module: openai.types.audio.transcription_include [assertion]
      early skip of rewriting module: openai.types.audio.transcription_verbose [assertion]
      early skip of rewriting module: openai.types.audio.translation_create_params [assertion]
      early skip of rewriting module: openai.types.audio.transcription_stream_event [assertion]
      early skip of rewriting module: openai.types.audio.transcription_text_done_event [assertion]
      early skip of rewriting module: openai.types.audio.transcription_text_delta_event [assertion]
      early skip of rewriting module: openai.types.audio.transcription_create_params [assertion]
      early skip of rewriting module: openai.types.audio.translation_create_response [assertion]
      early skip of rewriting module: openai.types.audio.transcription_create_response [assertion]
      early skip of rewriting module: litellm.types.llms [assertion]
      early skip of rewriting module: litellm.types.llms.base [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.core_helpers [assertion]
      early skip of rewriting module: litellm.types.llms.openai [assertion]
      early skip of rewriting module: openai.pagination [assertion]
      early skip of rewriting module: openai.types.fine_tuning [assertion]
      early skip of rewriting module: openai.types.fine_tuning.dpo_method [assertion]
      early skip of rewriting module: openai.types.fine_tuning.dpo_hyperparameters [assertion]
      early skip of rewriting module: openai.types.fine_tuning.fine_tuning_job [assertion]
      early skip of rewriting module: openai.types.fine_tuning.supervised_method [assertion]
      early skip of rewriting module: openai.types.fine_tuning.supervised_hyperparameters [assertion]
      early skip of rewriting module: openai.types.fine_tuning.reinforcement_method [assertion]
      early skip of rewriting module: openai.types.fine_tuning.reinforcement_hyperparameters [assertion]
      early skip of rewriting module: openai.types.fine_tuning.fine_tuning_job_wandb_integration_object [assertion]
      early skip of rewriting module: openai.types.fine_tuning.fine_tuning_job_wandb_integration [assertion]
      early skip of rewriting module: openai.types.fine_tuning.job_list_params [assertion]
      early skip of rewriting module: openai.types.fine_tuning.dpo_method_param [assertion]
      early skip of rewriting module: openai.types.fine_tuning.dpo_hyperparameters_param [assertion]
      early skip of rewriting module: openai.types.fine_tuning.job_create_params [assertion]
      early skip of rewriting module: openai.types.fine_tuning.supervised_method_param [assertion]
      early skip of rewriting module: openai.types.fine_tuning.supervised_hyperparameters_param [assertion]
      early skip of rewriting module: openai.types.fine_tuning.reinforcement_method_param [assertion]
      early skip of rewriting module: openai.types.fine_tuning.reinforcement_hyperparameters_param [assertion]
      early skip of rewriting module: openai.types.fine_tuning.fine_tuning_job_event [assertion]
      early skip of rewriting module: openai.types.fine_tuning.job_list_events_params [assertion]
      early skip of rewriting module: openai.types.fine_tuning.fine_tuning_job_integration [assertion]
      early skip of rewriting module: litellm.types.responses [assertion]
      early skip of rewriting module: litellm.types.responses.main [assertion]
      early skip of rewriting module: litellm.types.guardrails [assertion]
      early skip of rewriting module: litellm.types.rerank [assertion]
      early skip of rewriting module: litellm.types.llms.custom_http [assertion]
      early skip of rewriting module: litellm._version [assertion]
      early skip of rewriting module: importlib_metadata [assertion]
      early skip of rewriting module: importlib_metadata._meta [assertion]
      early skip of rewriting module: importlib_metadata._collections [assertion]
      early skip of rewriting module: importlib_metadata._compat [assertion]
      early skip of rewriting module: importlib_metadata._functools [assertion]
      early skip of rewriting module: importlib_metadata._itertools [assertion]
      early skip of rewriting module: importlib_metadata._typing [assertion]
      early skip of rewriting module: importlib_metadata.compat [assertion]
      early skip of rewriting module: importlib_metadata.compat.py39 [assertion]
      early skip of rewriting module: importlib_metadata.compat.py311 [assertion]
      early skip of rewriting module: zipp [assertion]
      early skip of rewriting module: zipp._functools [assertion]
      early skip of rewriting module: zipp.compat [assertion]
      early skip of rewriting module: zipp.compat.py310 [assertion]
      early skip of rewriting module: zipp.glob [assertion]
      early skip of rewriting module: zipp.compat.py313 [assertion]
      early skip of rewriting module: zipp.compat.overlay [assertion]
      early skip of rewriting module: importlib_metadata._adapters [assertion]
      early skip of rewriting module: email.policy [assertion]
      early skip of rewriting module: email.headerregistry [assertion]
      early skip of rewriting module: email._header_value_parser [assertion]
      early skip of rewriting module: email.contentmanager [assertion]
      early skip of rewriting module: importlib_metadata._text [assertion]
      early skip of rewriting module: litellm.caching [assertion]
      early skip of rewriting module: litellm.caching.caching [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.model_param_helper [assertion]
      early skip of rewriting module: litellm.types.caching [assertion]
      early skip of rewriting module: litellm.caching.base_cache [assertion]
      early skip of rewriting module: litellm.caching.disk_cache [assertion]
      early skip of rewriting module: litellm.caching.dual_cache [assertion]
      early skip of rewriting module: concurrent.futures.thread [assertion]
      early skip of rewriting module: litellm.caching.in_memory_cache [assertion]
      early skip of rewriting module: litellm.caching.redis_cache [assertion]
      early skip of rewriting module: litellm.types.services [assertion]
      early skip of rewriting module: litellm.caching.qdrant_semantic_cache [assertion]
      early skip of rewriting module: litellm.caching.redis_cluster_cache [assertion]
      early skip of rewriting module: litellm.caching.redis_semantic_cache [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.prompt_templates [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.prompt_templates.common_utils [assertion]
      early skip of rewriting module: litellm.caching.s3_cache [assertion]
      early skip of rewriting module: litellm.caching.llm_caching_handler [assertion]
      early skip of rewriting module: litellm.types.llms.bedrock [assertion]
      early skip of rewriting module: litellm.proxy [assertion]
      early skip of rewriting module: litellm.proxy._types [assertion]
      early skip of rewriting module: litellm.types.integrations [assertion]
      early skip of rewriting module: litellm.types.integrations.slack_alerting [assertion]
      early skip of rewriting module: litellm.types.router [assertion]
      early skip of rewriting module: litellm.exceptions [assertion]
      early skip of rewriting module: litellm.types.completion [assertion]
      early skip of rewriting module: litellm.types.embedding [assertion]
      early skip of rewriting module: litellm.types.llms.vertex_ai [assertion]
      early skip of rewriting module: litellm.proxy.types_utils [assertion]
      early skip of rewriting module: litellm.proxy.types_utils.utils [assertion]
      early skip of rewriting module: litellm.types.proxy [assertion]
      early skip of rewriting module: litellm.types.proxy.management_endpoints [assertion]
      early skip of rewriting module: litellm.types.proxy.management_endpoints.ui_sso [assertion]
      early skip of rewriting module: litellm.integrations [assertion]
      early skip of rewriting module: litellm.integrations.custom_logger [assertion]
      early skip of rewriting module: litellm.types.integrations.argilla [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.logging_callback_manager [assertion]
      early skip of rewriting module: litellm.integrations.additional_logging_utils [assertion]
      early skip of rewriting module: litellm.types.integrations.base_health_check [assertion]
      early skip of rewriting module: dotenv [assertion]
      early skip of rewriting module: dotenv.main [assertion]
      early skip of rewriting module: dotenv.parser [assertion]
      early skip of rewriting module: dotenv.variables [assertion]
      early skip of rewriting module: litellm.secret_managers [assertion]
      early skip of rewriting module: litellm.secret_managers.main [assertion]
      early skip of rewriting module: litellm.secret_managers.get_azure_ad_token_provider [assertion]
      early skip of rewriting module: litellm.types.secret_managers [assertion]
      early skip of rewriting module: litellm.types.secret_managers.get_azure_ad_token_provider [assertion]
      early skip of rewriting module: litellm.llms.custom_httpx.aiohttp_transport [assertion]
      early skip of rewriting module: httpcore [assertion]
      early skip of rewriting module: httpcore._api [assertion]
      early skip of rewriting module: httpcore._models [assertion]
      early skip of rewriting module: httpcore._sync [assertion]
      early skip of rewriting module: httpcore._sync.connection [assertion]
      early skip of rewriting module: httpcore._backends [assertion]
      early skip of rewriting module: httpcore._backends.sync [assertion]
      early skip of rewriting module: httpcore._exceptions [assertion]
      early skip of rewriting module: httpcore._utils [assertion]
      early skip of rewriting module: httpcore._backends.base [assertion]
      early skip of rewriting module: httpcore._ssl [assertion]
      early skip of rewriting module: httpcore._synchronization [assertion]
      early skip of rewriting module: trio [assertion]
      early skip of rewriting module: httpcore._trace [assertion]
      early skip of rewriting module: httpcore._sync.http11 [assertion]
      early skip of rewriting module: h11 [assertion]
      early skip of rewriting module: h11._connection [assertion]
      early skip of rewriting module: h11._events [assertion]
      early skip of rewriting module: h11._abnf [assertion]
      early skip of rewriting module: h11._headers [assertion]
      early skip of rewriting module: h11._util [assertion]
      early skip of rewriting module: h11._readers [assertion]
      early skip of rewriting module: h11._receivebuffer [assertion]
      early skip of rewriting module: h11._state [assertion]
      early skip of rewriting module: h11._writers [assertion]
      early skip of rewriting module: h11._version [assertion]
      early skip of rewriting module: httpcore._sync.interfaces [assertion]
      early skip of rewriting module: httpcore._sync.connection_pool [assertion]
      early skip of rewriting module: httpcore._sync.http_proxy [assertion]
      early skip of rewriting module: httpcore._sync.http2 [assertion]
      early skip of rewriting module: h2 [assertion]
      early skip of rewriting module: httpcore._sync.socks_proxy [assertion]
      early skip of rewriting module: socksio [assertion]
      early skip of rewriting module: httpcore._async [assertion]
      early skip of rewriting module: httpcore._async.connection [assertion]
      early skip of rewriting module: httpcore._backends.auto [assertion]
      early skip of rewriting module: httpcore._async.http11 [assertion]
      early skip of rewriting module: httpcore._async.interfaces [assertion]
      early skip of rewriting module: httpcore._async.connection_pool [assertion]
      early skip of rewriting module: httpcore._async.http_proxy [assertion]
      early skip of rewriting module: httpcore._async.http2 [assertion]
      early skip of rewriting module: h2 [assertion]
      early skip of rewriting module: httpcore._async.socks_proxy [assertion]
      early skip of rewriting module: socksio [assertion]
      early skip of rewriting module: httpcore._backends.mock [assertion]
      early skip of rewriting module: httpcore._backends.anyio [assertion]
      early skip of rewriting module: httpcore._backends.trio [assertion]
      early skip of rewriting module: trio [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.get_model_cost_map [assertion]
      early skip of rewriting module: litellm.timeout [assertion]
      early skip of rewriting module: litellm.cost_calculator [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_cost_calc [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_cost_calc.tool_call_cost_tracking [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_cost_calc.utils [assertion]
      early skip of rewriting module: litellm.utils [assertion]
      early skip of rewriting module: tiktoken [assertion]
      early skip of rewriting module: tiktoken.core [assertion]
      early skip of rewriting module: tiktoken._tiktoken [assertion]
      early skip of rewriting module: tiktoken.model [assertion]
      early skip of rewriting module: tiktoken.registry [assertion]
      early skip of rewriting module: pkgutil [assertion]
      early skip of rewriting module: tiktoken_ext [assertion]
      early skip of rewriting module: tokenizers [assertion]
      early skip of rewriting module: tokenizers.tokenizers [assertion]
      early skip of rewriting module: tokenizers.implementations [assertion]
      early skip of rewriting module: tokenizers.implementations.base_tokenizer [assertion]
      early skip of rewriting module: tokenizers.decoders [assertion]
      early skip of rewriting module: tokenizers.models [assertion]
      early skip of rewriting module: tokenizers.normalizers [assertion]
      early skip of rewriting module: tokenizers.pre_tokenizers [assertion]
      early skip of rewriting module: tokenizers.processors [assertion]
      early skip of rewriting module: tokenizers.implementations.bert_wordpiece [assertion]
      early skip of rewriting module: tokenizers.implementations.byte_level_bpe [assertion]
      early skip of rewriting module: tokenizers.implementations.char_level_bpe [assertion]
      early skip of rewriting module: tokenizers.implementations.sentencepiece_bpe [assertion]
      early skip of rewriting module: tokenizers.implementations.sentencepiece_unigram [assertion]
      early skip of rewriting module: litellm._service_logger [assertion]
      early skip of rewriting module: litellm.integrations.datadog [assertion]
      early skip of rewriting module: litellm.integrations.datadog.datadog [assertion]
      early skip of rewriting module: litellm.integrations.custom_batch_logger [assertion]
      early skip of rewriting module: litellm.types.integrations.datadog [assertion]
      early skip of rewriting module: litellm.integrations.opentelemetry [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.safe_json_dumps [assertion]
      early skip of rewriting module: litellm.integrations.prometheus_services [assertion]
      early skip of rewriting module: litellm.types.integrations.prometheus [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.audio_utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.audio_utils.utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.json_validation_rule [assertion]
      early skip of rewriting module: litellm.llms.gemini [assertion]
      early skip of rewriting module: litellm.caching._internal_lru_cache [assertion]
      early skip of rewriting module: litellm.caching.caching_handler [assertion]
      early skip of rewriting module: litellm.integrations.custom_guardrail [assertion]
      early skip of rewriting module: litellm.integrations.vector_stores [assertion]
      early skip of rewriting module: litellm.integrations.vector_stores.base_vector_store [assertion]
      early skip of rewriting module: litellm.integrations.custom_prompt_management [assertion]
      early skip of rewriting module: litellm.integrations.prompt_management_base [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.credential_accessor [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.default_encoding [assertion]
      early skip of rewriting module: tiktoken_ext.openai_public [assertion]
      early skip of rewriting module: tiktoken.load [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.exception_mapping_utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.get_litellm_params [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.get_llm_provider_logic [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.get_supported_openai_params [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_request_utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_response_utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_response_utils.convert_dict_to_response [assertion]
      early skip of rewriting module: litellm.types.llms.databricks [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_response_utils.get_headers [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_response_utils.get_api_base [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_response_utils.get_formatted_prompt [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.llm_response_utils.response_metadata [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.redact_messages [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.rules [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.streaming_handler [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.thread_pool_executor [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.token_counter [assertion]
      early skip of rewriting module: litellm.llms.bedrock [assertion]
      early skip of rewriting module: litellm.llms.bedrock.common_utils [assertion]
      early skip of rewriting module: litellm.llms.base_llm [assertion]
      early skip of rewriting module: litellm.llms.base_llm.anthropic_messages [assertion]
      early skip of rewriting module: litellm.llms.base_llm.anthropic_messages.transformation [assertion]
      early skip of rewriting module: litellm.types.llms.anthropic_messages [assertion]
      early skip of rewriting module: litellm.types.llms.anthropic_messages.anthropic_response [assertion]
      early skip of rewriting module: litellm.types.llms.anthropic [assertion]
      early skip of rewriting module: pydantic.deprecated [assertion]
      early skip of rewriting module: pydantic.deprecated.class_validators [assertion]
      early skip of rewriting module: pydantic._internal._decorators_v1 [assertion]
      early skip of rewriting module: litellm.llms.base_llm.audio_transcription [assertion]
      early skip of rewriting module: litellm.llms.base_llm.audio_transcription.transformation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.chat [assertion]
      early skip of rewriting module: litellm.llms.base_llm.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.base_utils [assertion]
      early skip of rewriting module: litellm.llms.base_llm.embedding [assertion]
      early skip of rewriting module: litellm.llms.base_llm.embedding.transformation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.image_edit [assertion]
      early skip of rewriting module: litellm.llms.base_llm.image_edit.transformation [assertion]
      early skip of rewriting module: litellm.types.images [assertion]
      early skip of rewriting module: litellm.types.images.main [assertion]
      early skip of rewriting module: litellm.llms.base_llm.image_generation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.image_generation.transformation [assertion]
      early skip of rewriting module: litellm.router_utils [assertion]
      early skip of rewriting module: litellm.router_utils.get_retry_from_policy [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.tokenizers [assertion]
      early skip of rewriting module: litellm.llms.base_llm.completion [assertion]
      early skip of rewriting module: litellm.llms.base_llm.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.files [assertion]
      early skip of rewriting module: litellm.llms.base_llm.files.transformation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.image_variations [assertion]
      early skip of rewriting module: litellm.llms.base_llm.image_variations.transformation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.realtime [assertion]
      early skip of rewriting module: litellm.llms.base_llm.realtime.transformation [assertion]
      early skip of rewriting module: litellm.types.realtime [assertion]
      early skip of rewriting module: litellm.llms.base_llm.rerank [assertion]
      early skip of rewriting module: litellm.llms.base_llm.rerank.transformation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.responses [assertion]
      early skip of rewriting module: litellm.llms.base_llm.responses.transformation [assertion]
      early skip of rewriting module: litellm.llms.anthropic [assertion]
      early skip of rewriting module: litellm.llms.anthropic.batches [assertion]
      early skip of rewriting module: litellm.llms.anthropic.batches.transformation [assertion]
      early skip of rewriting module: litellm.llms.anthropic.chat [assertion]
      early skip of rewriting module: litellm.llms.anthropic.chat.handler [assertion]
      early skip of rewriting module: litellm.llms.base [assertion]
      early skip of rewriting module: litellm.llms.anthropic.common_utils [assertion]
      early skip of rewriting module: litellm.llms.anthropic.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.anthropic.cost_calculation [assertion]
      early skip of rewriting module: litellm.llms.azure [assertion]
      early skip of rewriting module: litellm.llms.azure.cost_calculation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.image [assertion]
      early skip of rewriting module: litellm.llms.bedrock.image.cost_calculator [assertion]
      early skip of rewriting module: litellm.llms.databricks [assertion]
      early skip of rewriting module: litellm.llms.databricks.cost_calculator [assertion]
      early skip of rewriting module: litellm.llms.deepseek [assertion]
      early skip of rewriting module: litellm.llms.deepseek.cost_calculator [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.cost_calculator [assertion]
      early skip of rewriting module: litellm.llms.gemini.cost_calculator [assertion]
      early skip of rewriting module: litellm.llms.openai [assertion]
      early skip of rewriting module: litellm.llms.openai.cost_calculation [assertion]
      early skip of rewriting module: litellm.llms.together_ai [assertion]
      early skip of rewriting module: litellm.llms.together_ai.cost_calculator [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.cost_calculator [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.image_generation [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.image_generation.cost_calculator [assertion]
      early skip of rewriting module: litellm.responses [assertion]
      early skip of rewriting module: litellm.responses.utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.litellm_logging [assertion]
      early skip of rewriting module: litellm.batches [assertion]
      early skip of rewriting module: litellm.batches.batch_utils [assertion]
      early skip of rewriting module: litellm.integrations.agentops [assertion]
      early skip of rewriting module: litellm.integrations.agentops.agentops [assertion]
      early skip of rewriting module: litellm.integrations.anthropic_cache_control_hook [assertion]
      early skip of rewriting module: litellm.types.integrations.anthropic_cache_control_hook [assertion]
      early skip of rewriting module: litellm.integrations.arize [assertion]
      early skip of rewriting module: litellm.integrations.arize.arize [assertion]
      early skip of rewriting module: litellm.integrations.arize._utils [assertion]
      early skip of rewriting module: litellm.types.integrations.arize [assertion]
      early skip of rewriting module: litellm.integrations.deepeval [assertion]
      early skip of rewriting module: litellm.integrations.deepeval.deepeval [assertion]
      early skip of rewriting module: litellm.integrations.deepeval.api [assertion]
      early skip of rewriting module: litellm.integrations.deepeval.types [assertion]
      early skip of rewriting module: litellm.integrations.deepeval.utils [assertion]
      early skip of rewriting module: litellm.integrations.mlflow [assertion]
      early skip of rewriting module: litellm.integrations.vector_stores.bedrock_vector_store [assertion]
      early skip of rewriting module: litellm.llms.bedrock.base_aws_llm [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.dd_tracing [assertion]
      early skip of rewriting module: litellm.types.integrations.rag [assertion]
      early skip of rewriting module: litellm.types.integrations.rag.bedrock_knowledgebase [assertion]
      early skip of rewriting module: litellm.types.vector_stores [assertion]
      early skip of rewriting module: litellm.integrations.argilla [assertion]
      early skip of rewriting module: litellm.integrations.arize.arize_phoenix [assertion]
      early skip of rewriting module: litellm.types.integrations.arize_phoenix [assertion]
      early skip of rewriting module: litellm.integrations.athina [assertion]
      early skip of rewriting module: litellm.integrations.azure_storage [assertion]
      early skip of rewriting module: litellm.integrations.azure_storage.azure_storage [assertion]
      early skip of rewriting module: litellm.llms.azure.common_utils [assertion]
      early skip of rewriting module: litellm.llms.openai.common_utils [assertion]
      early skip of rewriting module: litellm.integrations.braintrust_logging [assertion]
      early skip of rewriting module: litellm.integrations.datadog.datadog_llm_obs [assertion]
      early skip of rewriting module: litellm.types.integrations.datadog_llm_obs [assertion]
      early skip of rewriting module: litellm.integrations.dynamodb [assertion]
      early skip of rewriting module: litellm.integrations.galileo [assertion]
      early skip of rewriting module: litellm.integrations.gcs_bucket [assertion]
      early skip of rewriting module: litellm.integrations.gcs_bucket.gcs_bucket [assertion]
      early skip of rewriting module: litellm.integrations.gcs_bucket.gcs_bucket_base [assertion]
      early skip of rewriting module: litellm.types.integrations.gcs_bucket [assertion]
      early skip of rewriting module: litellm.integrations.gcs_pubsub [assertion]
      early skip of rewriting module: litellm.integrations.gcs_pubsub.pub_sub [assertion]
      early skip of rewriting module: litellm.integrations.greenscale [assertion]
      early skip of rewriting module: litellm.integrations.helicone [assertion]
      early skip of rewriting module: litellm.integrations.humanloop [assertion]
      early skip of rewriting module: litellm.integrations.lago [assertion]
      early skip of rewriting module: litellm.integrations.langfuse [assertion]
      early skip of rewriting module: litellm.integrations.langfuse.langfuse [assertion]
      early skip of rewriting module: packaging [assertion]
      early skip of rewriting module: packaging.version [assertion]
      early skip of rewriting module: packaging._structures [assertion]
      early skip of rewriting module: litellm.types.integrations.langfuse [assertion]
      early skip of rewriting module: litellm.integrations.langfuse.langfuse_handler [assertion]
      early skip of rewriting module: litellm.integrations.langfuse.langfuse_prompt_management [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.asyncify [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.specialty_caches [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.specialty_caches.dynamic_logging_cache [assertion]
      early skip of rewriting module: litellm.integrations.langsmith [assertion]
      early skip of rewriting module: litellm.types.integrations.langsmith [assertion]
      early skip of rewriting module: litellm.integrations.literal_ai [assertion]
      early skip of rewriting module: litellm.integrations.logfire_logger [assertion]
      early skip of rewriting module: litellm.integrations.lunary [assertion]
      early skip of rewriting module: litellm.integrations.openmeter [assertion]
      early skip of rewriting module: litellm.integrations.opik [assertion]
      early skip of rewriting module: litellm.integrations.opik.opik [assertion]
      early skip of rewriting module: litellm.integrations.opik.utils [assertion]
      early skip of rewriting module: litellm.integrations.prometheus [assertion]
      early skip of rewriting module: litellm.integrations.prompt_layer [assertion]
      early skip of rewriting module: litellm.integrations.s3 [assertion]
      early skip of rewriting module: litellm.integrations.s3_v2 [assertion]
      early skip of rewriting module: litellm.types.integrations.s3_v2 [assertion]
      early skip of rewriting module: litellm.integrations.supabase [assertion]
      early skip of rewriting module: litellm.integrations.traceloop [assertion]
      early skip of rewriting module: litellm.integrations.weights_biases [assertion]
      early skip of rewriting module: wandb [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.initialize_dynamic_callback_params [assertion]
      early skip of rewriting module: litellm_enterprise [assertion]
      early skip of rewriting module: litellm.llms.custom_llm [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.converse_handler [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_handler [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.prompt_templates.factory [assertion]
      early skip of rewriting module: jinja2 [assertion]
      early skip of rewriting module: jinja2.bccache [assertion]
      early skip of rewriting module: jinja2.environment [assertion]
      early skip of rewriting module: markupsafe [assertion]
      early skip of rewriting module: markupsafe._speedups [assertion]
      early skip of rewriting module: jinja2.nodes [assertion]
      early skip of rewriting module: jinja2.utils [assertion]
      early skip of rewriting module: jinja2.compiler [assertion]
      early skip of rewriting module: jinja2.exceptions [assertion]
      early skip of rewriting module: jinja2.idtracking [assertion]
      early skip of rewriting module: jinja2.visitor [assertion]
      early skip of rewriting module: jinja2.optimizer [assertion]
      early skip of rewriting module: jinja2.defaults [assertion]
      early skip of rewriting module: jinja2.filters [assertion]
      early skip of rewriting module: jinja2.async_utils [assertion]
      early skip of rewriting module: jinja2.runtime [assertion]
      early skip of rewriting module: jinja2.tests [assertion]
      early skip of rewriting module: jinja2.lexer [assertion]
      early skip of rewriting module: jinja2._identifier [assertion]
      early skip of rewriting module: jinja2.parser [assertion]
      early skip of rewriting module: jinja2.loaders [assertion]
      early skip of rewriting module: jinja2.sandbox [assertion]
      early skip of rewriting module: litellm.types.llms.ollama [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.prompt_templates.image_handling [assertion]
      early skip of rewriting module: litellm.types.llms.cohere [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.converse_transformation [assertion]
      early skip of rewriting module: litellm.llms.openai_like [assertion]
      early skip of rewriting module: litellm.llms.openai_like.chat [assertion]
      early skip of rewriting module: litellm.llms.openai_like.chat.handler [assertion]
      early skip of rewriting module: litellm.llms.databricks.streaming_utils [assertion]
      early skip of rewriting module: litellm.llms.openai.chat [assertion]
      early skip of rewriting module: litellm.llms.openai.chat.gpt_transformation [assertion]
      early skip of rewriting module: litellm.llms.base_llm.base_model_iterator [assertion]
      early skip of rewriting module: litellm.llms.openai.openai [assertion]
      early skip of rewriting module: litellm.llms.openai.chat.o_series_transformation [assertion]
      early skip of rewriting module: litellm.llms.openai_like.common_utils [assertion]
      early skip of rewriting module: litellm.llms.openai_like.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.aiohttp_openai [assertion]
      early skip of rewriting module: litellm.llms.aiohttp_openai.chat [assertion]
      early skip of rewriting module: litellm.llms.aiohttp_openai.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.galadriel [assertion]
      early skip of rewriting module: litellm.llms.galadriel.chat [assertion]
      early skip of rewriting module: litellm.llms.galadriel.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.github [assertion]
      early skip of rewriting module: litellm.llms.github.chat [assertion]
      early skip of rewriting module: litellm.llms.github.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.empower [assertion]
      early skip of rewriting module: litellm.llms.empower.chat [assertion]
      early skip of rewriting module: litellm.llms.empower.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.huggingface [assertion]
      early skip of rewriting module: litellm.llms.huggingface.chat [assertion]
      early skip of rewriting module: litellm.llms.huggingface.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.huggingface.common_utils [assertion]
      early skip of rewriting module: litellm.llms.huggingface.embedding [assertion]
      early skip of rewriting module: litellm.llms.huggingface.embedding.transformation [assertion]
      early skip of rewriting module: litellm.llms.oobabooga [assertion]
      early skip of rewriting module: litellm.llms.oobabooga.chat [assertion]
      early skip of rewriting module: litellm.llms.oobabooga.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.oobabooga.common_utils [assertion]
      early skip of rewriting module: litellm.llms.maritalk [assertion]
      early skip of rewriting module: litellm.llms.openrouter [assertion]
      early skip of rewriting module: litellm.llms.openrouter.chat [assertion]
      early skip of rewriting module: litellm.llms.openrouter.chat.transformation [assertion]
      early skip of rewriting module: litellm.types.llms.openrouter [assertion]
      early skip of rewriting module: litellm.llms.openrouter.common_utils [assertion]
      early skip of rewriting module: litellm.llms.datarobot [assertion]
      early skip of rewriting module: litellm.llms.datarobot.chat [assertion]
      early skip of rewriting module: litellm.llms.datarobot.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.groq [assertion]
      early skip of rewriting module: litellm.llms.groq.stt [assertion]
      early skip of rewriting module: litellm.llms.groq.stt.transformation [assertion]
      early skip of rewriting module: litellm.llms.anthropic.completion [assertion]
      early skip of rewriting module: litellm.llms.anthropic.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.triton [assertion]
      early skip of rewriting module: litellm.llms.triton.completion [assertion]
      early skip of rewriting module: litellm.llms.triton.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.triton.common_utils [assertion]
      early skip of rewriting module: litellm.llms.triton.embedding [assertion]
      early skip of rewriting module: litellm.llms.triton.embedding.transformation [assertion]
      early skip of rewriting module: litellm.llms.huggingface.rerank [assertion]
      early skip of rewriting module: litellm.llms.huggingface.rerank.transformation [assertion]
      early skip of rewriting module: litellm.llms.databricks.chat [assertion]
      early skip of rewriting module: litellm.llms.databricks.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.databricks.common_utils [assertion]
      early skip of rewriting module: litellm.llms.databricks.embed [assertion]
      early skip of rewriting module: litellm.llms.databricks.embed.transformation [assertion]
      early skip of rewriting module: litellm.llms.predibase [assertion]
      early skip of rewriting module: litellm.llms.predibase.chat [assertion]
      early skip of rewriting module: litellm.llms.predibase.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.predibase.common_utils [assertion]
      early skip of rewriting module: litellm.llms.replicate [assertion]
      early skip of rewriting module: litellm.llms.replicate.chat [assertion]
      early skip of rewriting module: litellm.llms.replicate.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.replicate.common_utils [assertion]
      early skip of rewriting module: litellm.llms.cohere [assertion]
      early skip of rewriting module: litellm.llms.cohere.completion [assertion]
      early skip of rewriting module: litellm.llms.cohere.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.cohere.common_utils [assertion]
      early skip of rewriting module: litellm.llms.snowflake [assertion]
      early skip of rewriting module: litellm.llms.snowflake.chat [assertion]
      early skip of rewriting module: litellm.llms.snowflake.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.cohere.rerank [assertion]
      early skip of rewriting module: litellm.llms.cohere.rerank.transformation [assertion]
      early skip of rewriting module: litellm.llms.cohere.rerank_v2 [assertion]
      early skip of rewriting module: litellm.llms.cohere.rerank_v2.transformation [assertion]
      early skip of rewriting module: litellm.llms.azure_ai [assertion]
      early skip of rewriting module: litellm.llms.azure_ai.rerank [assertion]
      early skip of rewriting module: litellm.llms.azure_ai.rerank.transformation [assertion]
      early skip of rewriting module: litellm.llms.infinity [assertion]
      early skip of rewriting module: litellm.llms.infinity.rerank [assertion]
      early skip of rewriting module: litellm.llms.infinity.rerank.transformation [assertion]
      early skip of rewriting module: litellm.llms.infinity.common_utils [assertion]
      early skip of rewriting module: litellm.llms.jina_ai [assertion]
      early skip of rewriting module: litellm.llms.jina_ai.rerank [assertion]
      early skip of rewriting module: litellm.llms.jina_ai.rerank.transformation [assertion]
      early skip of rewriting module: litellm.llms.clarifai [assertion]
      early skip of rewriting module: litellm.llms.clarifai.chat [assertion]
      early skip of rewriting module: litellm.llms.clarifai.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.clarifai.common_utils [assertion]
      early skip of rewriting module: litellm.llms.ai21 [assertion]
      early skip of rewriting module: litellm.llms.ai21.chat [assertion]
      early skip of rewriting module: litellm.llms.ai21.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.meta_llama [assertion]
      early skip of rewriting module: litellm.llms.meta_llama.chat [assertion]
      early skip of rewriting module: litellm.llms.meta_llama.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through.messages [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through.messages.transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.messages [assertion]
      early skip of rewriting module: litellm.llms.bedrock.messages.invoke_transformations [assertion]
      early skip of rewriting module: litellm.llms.bedrock.messages.invoke_transformations.anthropic_claude3_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.base_invoke_transformation [assertion]
      early skip of rewriting module: litellm.llms.together_ai.chat [assertion]
      early skip of rewriting module: litellm.llms.together_ai.completion [assertion]
      early skip of rewriting module: litellm.llms.together_ai.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.openai.completion [assertion]
      early skip of rewriting module: litellm.llms.openai.completion.utils [assertion]
      early skip of rewriting module: litellm.llms.openai.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.cloudflare [assertion]
      early skip of rewriting module: litellm.llms.cloudflare.chat [assertion]
      early skip of rewriting module: litellm.llms.cloudflare.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.novita [assertion]
      early skip of rewriting module: litellm.llms.novita.chat [assertion]
      early skip of rewriting module: litellm.llms.novita.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.deprecated_providers [assertion]
      early skip of rewriting module: litellm.llms.deprecated_providers.palm [assertion]
      early skip of rewriting module: litellm.llms.nlp_cloud [assertion]
      early skip of rewriting module: litellm.llms.nlp_cloud.chat [assertion]
      early skip of rewriting module: litellm.llms.nlp_cloud.chat.handler [assertion]
      early skip of rewriting module: litellm.llms.nlp_cloud.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.nlp_cloud.common_utils [assertion]
      early skip of rewriting module: litellm.llms.petals [assertion]
      early skip of rewriting module: litellm.llms.petals.completion [assertion]
      early skip of rewriting module: litellm.llms.petals.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.petals.common_utils [assertion]
      early skip of rewriting module: litellm.llms.deprecated_providers.aleph_alpha [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.gemini [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.gemini.vertex_and_google_ai_studio_gemini [assertion]
      early skip of rewriting module: litellm.types.llms.gemini [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.common_utils [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_llm_base [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.gemini.transformation [assertion]
      early skip of rewriting module: litellm.types.files [assertion]
      early skip of rewriting module: litellm.llms.gemini.common_utils [assertion]
      early skip of rewriting module: litellm.llms.gemini.chat [assertion]
      early skip of rewriting module: litellm.llms.gemini.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_embeddings [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_embeddings.transformation [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_embeddings.types [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_partner_models [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_partner_models.anthropic [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_partner_models.anthropic.transformation [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_partner_models.llama3 [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_partner_models.llama3.transformation [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_partner_models.ai21 [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_partner_models.ai21.transformation [assertion]
      early skip of rewriting module: litellm.llms.ollama [assertion]
      early skip of rewriting module: litellm.llms.ollama.chat [assertion]
      early skip of rewriting module: litellm.llms.ollama.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.ollama.common_utils [assertion]
      early skip of rewriting module: litellm.llms.ollama.completion [assertion]
      early skip of rewriting module: litellm.llms.ollama.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.sagemaker [assertion]
      early skip of rewriting module: litellm.llms.sagemaker.completion [assertion]
      early skip of rewriting module: litellm.llms.sagemaker.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.sagemaker.common_utils [assertion]
      early skip of rewriting module: litellm.llms.sagemaker.chat [assertion]
      early skip of rewriting module: litellm.llms.sagemaker.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.amazon_ai21_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.amazon_nova_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.anthropic_claude2_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.anthropic_claude3_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.amazon_cohere_transformation [assertion]
      early skip of rewriting module: litellm.llms.cohere.chat [assertion]
      early skip of rewriting module: litellm.llms.cohere.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.amazon_llama_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.amazon_deepseek_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.amazon_mistral_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.chat.invoke_transformations.amazon_titan_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.image.amazon_stability1_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.image.amazon_stability3_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.image.amazon_nova_canvas_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.embed [assertion]
      early skip of rewriting module: litellm.llms.bedrock.embed.amazon_titan_g1_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.embed.amazon_titan_multimodal_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.embed.amazon_titan_v2_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.embed.cohere_transformation [assertion]
      early skip of rewriting module: litellm.llms.cohere.embed [assertion]
      early skip of rewriting module: litellm.llms.cohere.embed.transformation [assertion]
      early skip of rewriting module: litellm.llms.openai.image_variations [assertion]
      early skip of rewriting module: litellm.llms.openai.image_variations.transformation [assertion]
      early skip of rewriting module: litellm.llms.deepinfra [assertion]
      early skip of rewriting module: litellm.llms.deepinfra.chat [assertion]
      early skip of rewriting module: litellm.llms.deepinfra.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.deepgram [assertion]
      early skip of rewriting module: litellm.llms.deepgram.audio_transcription [assertion]
      early skip of rewriting module: litellm.llms.deepgram.audio_transcription.transformation [assertion]
      early skip of rewriting module: litellm.llms.deepgram.common_utils [assertion]
      early skip of rewriting module: litellm.llms.topaz [assertion]
      early skip of rewriting module: litellm.llms.topaz.common_utils [assertion]
      early skip of rewriting module: litellm.llms.topaz.image_variations [assertion]
      early skip of rewriting module: litellm.llms.topaz.image_variations.transformation [assertion]
      early skip of rewriting module: litellm.llms.groq.chat [assertion]
      early skip of rewriting module: litellm.llms.groq.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.voyage [assertion]
      early skip of rewriting module: litellm.llms.voyage.embedding [assertion]
      early skip of rewriting module: litellm.llms.voyage.embedding.transformation [assertion]
      early skip of rewriting module: litellm.llms.infinity.embedding [assertion]
      early skip of rewriting module: litellm.llms.infinity.embedding.transformation [assertion]
      early skip of rewriting module: litellm.llms.azure_ai.chat [assertion]
      early skip of rewriting module: litellm.llms.azure_ai.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.mistral [assertion]
      early skip of rewriting module: litellm.llms.mistral.mistral_chat_transformation [assertion]
      early skip of rewriting module: litellm.types.llms.mistral [assertion]
      early skip of rewriting module: litellm.llms.openai.responses [assertion]
      early skip of rewriting module: litellm.llms.openai.responses.transformation [assertion]
      early skip of rewriting module: litellm.llms.azure.responses [assertion]
      early skip of rewriting module: litellm.llms.azure.responses.transformation [assertion]
      early skip of rewriting module: litellm.llms.openai.transcriptions [assertion]
      early skip of rewriting module: litellm.llms.openai.transcriptions.whisper_transformation [assertion]
      early skip of rewriting module: litellm.llms.openai.transcriptions.gpt_transformation [assertion]
      early skip of rewriting module: litellm.llms.openai.chat.gpt_audio_transformation [assertion]
      early skip of rewriting module: litellm.llms.nvidia_nim [assertion]
      early skip of rewriting module: litellm.llms.nvidia_nim.chat [assertion]
      early skip of rewriting module: litellm.llms.nvidia_nim.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.nvidia_nim.embed [assertion]
      early skip of rewriting module: litellm.llms.featherless_ai [assertion]
      early skip of rewriting module: litellm.llms.featherless_ai.chat [assertion]
      early skip of rewriting module: litellm.llms.featherless_ai.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.cerebras [assertion]
      early skip of rewriting module: litellm.llms.cerebras.chat [assertion]
      early skip of rewriting module: litellm.llms.sambanova [assertion]
      early skip of rewriting module: litellm.llms.sambanova.chat [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.chat [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.common_utils [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.completion [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.audio_transcription [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.audio_transcription.transformation [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.embed [assertion]
      early skip of rewriting module: litellm.llms.fireworks_ai.embed.fireworks_ai_transformation [assertion]
      early skip of rewriting module: litellm.llms.friendliai [assertion]
      early skip of rewriting module: litellm.llms.friendliai.chat [assertion]
      early skip of rewriting module: litellm.llms.friendliai.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.jina_ai.embedding [assertion]
      early skip of rewriting module: litellm.llms.jina_ai.embedding.transformation [assertion]
      early skip of rewriting module: litellm.llms.xai [assertion]
      early skip of rewriting module: litellm.llms.xai.chat [assertion]
      early skip of rewriting module: litellm.llms.xai.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.xai.common_utils [assertion]
      early skip of rewriting module: litellm.llms.volcengine [assertion]
      early skip of rewriting module: litellm.llms.codestral [assertion]
      early skip of rewriting module: litellm.llms.codestral.completion [assertion]
      early skip of rewriting module: litellm.llms.codestral.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.azure.azure [assertion]
      early skip of rewriting module: litellm.llms.azure.chat [assertion]
      early skip of rewriting module: litellm.llms.azure.chat.gpt_transformation [assertion]
      early skip of rewriting module: litellm.types.llms.azure [assertion]
      early skip of rewriting module: litellm.llms.azure.completion [assertion]
      early skip of rewriting module: litellm.llms.azure.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.hosted_vllm [assertion]
      early skip of rewriting module: litellm.llms.hosted_vllm.chat [assertion]
      early skip of rewriting module: litellm.llms.hosted_vllm.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.llamafile [assertion]
      early skip of rewriting module: litellm.llms.llamafile.chat [assertion]
      early skip of rewriting module: litellm.llms.llamafile.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.litellm_proxy [assertion]
      early skip of rewriting module: litellm.llms.litellm_proxy.chat [assertion]
      early skip of rewriting module: litellm.llms.litellm_proxy.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.vllm [assertion]
      early skip of rewriting module: litellm.llms.vllm.completion [assertion]
      early skip of rewriting module: litellm.llms.vllm.completion.transformation [assertion]
      early skip of rewriting module: litellm.llms.deepseek.chat [assertion]
      early skip of rewriting module: litellm.llms.deepseek.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.lm_studio [assertion]
      early skip of rewriting module: litellm.llms.lm_studio.chat [assertion]
      early skip of rewriting module: litellm.llms.lm_studio.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.lm_studio.embed [assertion]
      early skip of rewriting module: litellm.llms.lm_studio.embed.transformation [assertion]
      early skip of rewriting module: litellm.llms.nscale [assertion]
      early skip of rewriting module: litellm.llms.nscale.chat [assertion]
      early skip of rewriting module: litellm.llms.nscale.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.perplexity [assertion]
      early skip of rewriting module: litellm.llms.perplexity.chat [assertion]
      early skip of rewriting module: litellm.llms.perplexity.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.azure.chat.o_series_transformation [assertion]
      early skip of rewriting module: litellm.llms.watsonx [assertion]
      early skip of rewriting module: litellm.llms.watsonx.completion [assertion]
      early skip of rewriting module: litellm.llms.watsonx.completion.transformation [assertion]
      early skip of rewriting module: litellm.types.llms.watsonx [assertion]
      early skip of rewriting module: litellm.llms.watsonx.common_utils [assertion]
      early skip of rewriting module: litellm.llms.watsonx.chat [assertion]
      early skip of rewriting module: litellm.llms.watsonx.chat.transformation [assertion]
      early skip of rewriting module: litellm.llms.watsonx.embed [assertion]
      early skip of rewriting module: litellm.llms.watsonx.embed.transformation [assertion]
      early skip of rewriting module: litellm.llms.nebius [assertion]
      early skip of rewriting module: litellm.llms.nebius.chat [assertion]
      early skip of rewriting module: litellm.llms.nebius.chat.transformation [assertion]
      early skip of rewriting module: litellm.main [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.health_check_utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.mock_functions [assertion]
      early skip of rewriting module: litellm.realtime_api [assertion]
      early skip of rewriting module: litellm.realtime_api.main [assertion]
      early skip of rewriting module: litellm.llms.custom_httpx.llm_http_handler [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.realtime_streaming [assertion]
      early skip of rewriting module: litellm.responses.streaming_iterator [assertion]
      early skip of rewriting module: litellm.llms.azure.realtime [assertion]
      early skip of rewriting module: litellm.llms.azure.realtime.handler [assertion]
      early skip of rewriting module: litellm.llms.openai.realtime [assertion]
      early skip of rewriting module: litellm.llms.openai.realtime.handler [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.fallback_utils [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.streaming_chunk_builder_utils [assertion]
      early skip of rewriting module: litellm.llms.baseten [assertion]
      early skip of rewriting module: litellm.llms.azure.audio_transcriptions [assertion]
      early skip of rewriting module: litellm.llms.azure.chat.o_series_handler [assertion]
      early skip of rewriting module: litellm.llms.azure.completion.handler [assertion]
      early skip of rewriting module: litellm.llms.azure_ai.embed [assertion]
      early skip of rewriting module: litellm.llms.azure_ai.embed.handler [assertion]
      early skip of rewriting module: litellm.types.llms.azure_ai [assertion]
      early skip of rewriting module: litellm.llms.azure_ai.embed.cohere_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.embed.embedding [assertion]
      early skip of rewriting module: litellm.llms.cohere.embed.handler [assertion]
      early skip of rewriting module: litellm.llms.cohere.embed.v1_transformation [assertion]
      early skip of rewriting module: litellm.llms.bedrock.image.image_handler [assertion]
      early skip of rewriting module: litellm.llms.codestral.completion.handler [assertion]
      early skip of rewriting module: litellm.llms.custom_httpx.aiohttp_handler [assertion]
      early skip of rewriting module: litellm.llms.databricks.embed.handler [assertion]
      early skip of rewriting module: litellm.llms.openai_like.embedding [assertion]
      early skip of rewriting module: litellm.llms.openai_like.embedding.handler [assertion]
      early skip of rewriting module: litellm.llms.groq.chat.handler [assertion]
      early skip of rewriting module: litellm.llms.huggingface.embedding.handler [assertion]
      early skip of rewriting module: litellm.llms.ollama.completion.handler [assertion]
      early skip of rewriting module: litellm.llms.oobabooga.chat.oobabooga [assertion]
      early skip of rewriting module: litellm.llms.openai.completion.handler [assertion]
      early skip of rewriting module: litellm.llms.openai.image_variations.handler [assertion]
      early skip of rewriting module: litellm.llms.openai.transcriptions.handler [assertion]
      early skip of rewriting module: litellm.llms.petals.completion.handler [assertion]
      early skip of rewriting module: litellm.llms.predibase.chat.handler [assertion]
      early skip of rewriting module: litellm.llms.replicate.chat.handler [assertion]
      early skip of rewriting module: litellm.llms.sagemaker.chat.handler [assertion]
      early skip of rewriting module: litellm.llms.sagemaker.completion.handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_non_gemini [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.gemini_embeddings [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.gemini_embeddings.batch_embed_content_handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.gemini_embeddings.batch_embed_content_transformation [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.image_generation.image_generation_handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.multimodal_embeddings [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.multimodal_embeddings.embedding_handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.multimodal_embeddings.transformation [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.text_to_speech [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.text_to_speech.text_to_speech_handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_ai_partner_models.main [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_embeddings.embedding_handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_model_garden [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.vertex_model_garden.main [assertion]
      early skip of rewriting module: litellm.llms.vllm.completion.handler [assertion]
      early skip of rewriting module: litellm.llms.watsonx.chat.handler [assertion]
      early skip of rewriting module: litellm.budget_manager [assertion]
      early skip of rewriting module: litellm.proxy.proxy_cli [assertion]
      early skip of rewriting module: litellm.router [assertion]
      early skip of rewriting module: litellm.router_strategy [assertion]
      early skip of rewriting module: litellm.router_strategy.budget_limiter [assertion]
      early skip of rewriting module: litellm.litellm_core_utils.duration_parser [assertion]
      early skip of rewriting module: litellm.router_strategy.tag_based_routing [assertion]
      early skip of rewriting module: litellm.router_utils.cooldown_callbacks [assertion]
      early skip of rewriting module: litellm.router_strategy.least_busy [assertion]
      early skip of rewriting module: litellm.router_strategy.lowest_cost [assertion]
      early skip of rewriting module: litellm.router_strategy.lowest_latency [assertion]
      early skip of rewriting module: litellm.router_strategy.lowest_tpm_rpm [assertion]
      early skip of rewriting module: litellm.router_strategy.lowest_tpm_rpm_v2 [assertion]
      early skip of rewriting module: litellm.router_strategy.base_routing_strategy [assertion]
      early skip of rewriting module: litellm.router_strategy.simple_shuffle [assertion]
      early skip of rewriting module: litellm.router_utils.add_retry_fallback_headers [assertion]
      early skip of rewriting module: litellm.router_utils.batch_utils [assertion]
      early skip of rewriting module: litellm.router_utils.client_initalization_utils [assertion]
      early skip of rewriting module: litellm.router_utils.clientside_credential_handler [assertion]
      early skip of rewriting module: litellm.router_utils.cooldown_cache [assertion]
      early skip of rewriting module: litellm.router_utils.cooldown_handlers [assertion]
      early skip of rewriting module: litellm.router_utils.router_callbacks [assertion]
      early skip of rewriting module: litellm.router_utils.router_callbacks.track_deployment_metrics [assertion]
      early skip of rewriting module: litellm.router_utils.fallback_event_handlers [assertion]
      early skip of rewriting module: litellm.router_utils.handle_error [assertion]
      early skip of rewriting module: litellm.router_utils.pre_call_checks [assertion]
      early skip of rewriting module: litellm.router_utils.pre_call_checks.prompt_caching_deployment_check [assertion]
      early skip of rewriting module: litellm.router_utils.prompt_caching_cache [assertion]
      early skip of rewriting module: litellm.router_utils.pre_call_checks.responses_api_deployment_check [assertion]
      early skip of rewriting module: litellm.scheduler [assertion]
      early skip of rewriting module: litellm.router_utils.pattern_match_deployments [assertion]
      early skip of rewriting module: litellm.assistants [assertion]
      early skip of rewriting module: litellm.assistants.main [assertion]
      early skip of rewriting module: litellm.llms.azure.assistants [assertion]
      early skip of rewriting module: litellm.assistants.utils [assertion]
      early skip of rewriting module: litellm.batches.main [assertion]
      early skip of rewriting module: litellm.llms.azure.batches [assertion]
      early skip of rewriting module: litellm.llms.azure.batches.handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.batches [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.batches.handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.batches.transformation [assertion]
      early skip of rewriting module: litellm.images [assertion]
      early skip of rewriting module: litellm.images.main [assertion]
      early skip of rewriting module: litellm.images.utils [assertion]
      early skip of rewriting module: litellm.batch_completion [assertion]
      early skip of rewriting module: litellm.batch_completion.main [assertion]
      early skip of rewriting module: litellm.rerank_api [assertion]
      early skip of rewriting module: litellm.rerank_api.main [assertion]
      early skip of rewriting module: litellm.llms.bedrock.rerank [assertion]
      early skip of rewriting module: litellm.llms.bedrock.rerank.handler [assertion]
      early skip of rewriting module: litellm.llms.bedrock.rerank.transformation [assertion]
      early skip of rewriting module: litellm.llms.together_ai.rerank [assertion]
      early skip of rewriting module: litellm.llms.together_ai.rerank.handler [assertion]
      early skip of rewriting module: litellm.llms.together_ai.rerank.transformation [assertion]
      early skip of rewriting module: litellm.rerank_api.rerank_utils [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through.messages.handler [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through.adapters [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through.adapters.transformation [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through.adapters.streaming_iterator [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through.adapters.handler [assertion]
      early skip of rewriting module: litellm.llms.anthropic.experimental_pass_through.messages.utils [assertion]
      early skip of rewriting module: litellm.responses.main [assertion]
      early skip of rewriting module: litellm.responses.litellm_completion_transformation [assertion]
      early skip of rewriting module: litellm.responses.litellm_completion_transformation.handler [assertion]
      early skip of rewriting module: litellm.responses.litellm_completion_transformation.streaming_iterator [assertion]
      early skip of rewriting module: litellm.responses.litellm_completion_transformation.transformation [assertion]
      early skip of rewriting module: litellm_enterprise [assertion]
      early skip of rewriting module: litellm.fine_tuning [assertion]
      early skip of rewriting module: litellm.fine_tuning.main [assertion]
      early skip of rewriting module: litellm.llms.azure.fine_tuning [assertion]
      early skip of rewriting module: litellm.llms.azure.fine_tuning.handler [assertion]
      early skip of rewriting module: litellm.llms.openai.fine_tuning [assertion]
      early skip of rewriting module: litellm.llms.openai.fine_tuning.handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.fine_tuning [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.fine_tuning.handler [assertion]
      early skip of rewriting module: litellm.types.fine_tuning [assertion]
      early skip of rewriting module: litellm.files [assertion]
      early skip of rewriting module: litellm.files.main [assertion]
      early skip of rewriting module: litellm.llms.azure.files [assertion]
      early skip of rewriting module: litellm.llms.azure.files.handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.files [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.files.handler [assertion]
      early skip of rewriting module: litellm.llms.vertex_ai.files.transformation [assertion]
      early skip of rewriting module: litellm.types.adapter [assertion]
      early skip of rewriting module: litellm.anthropic_interface [assertion]
      early skip of rewriting module: litellm.anthropic_interface.messages [assertion]
      early skip of rewriting module: litellm.vector_stores [assertion]
      early skip of rewriting module: litellm.vector_stores.vector_store_registry [assertion]
      early skip of rewriting module: litellm.types.llms.custom_llm [assertion]
      early skip of rewriting module: litellm.passthrough [assertion]
      early skip of rewriting module: litellm.passthrough.main [assertion]
      early skip of rewriting module: litellm.passthrough.utils [assertion]
      early skip of rewriting module: dspy.primitives.prediction [assertion]
      early skip of rewriting module: dspy.streaming.streaming_listener [assertion]
      early skip of rewriting module: dspy.adapters [assertion]
      early skip of rewriting module: dspy.adapters.base [assertion]
      early skip of rewriting module: json_repair [assertion]
      early skip of rewriting module: json_repair.json_repair [assertion]
      early skip of rewriting module: json_repair.json_parser [assertion]
      early skip of rewriting module: json_repair.json_context [assertion]
      early skip of rewriting module: json_repair.object_comparer [assertion]
      early skip of rewriting module: json_repair.string_file_wrapper [assertion]
      early skip of rewriting module: dspy.adapters.types [assertion]
      early skip of rewriting module: dspy.adapters.types.audio [assertion]
      early skip of rewriting module: dspy.adapters.types.base_type [assertion]
      early skip of rewriting module: pydantic.functional_serializers [assertion]
      early skip of rewriting module: soundfile [assertion]
      early skip of rewriting module: dspy.adapters.types.history [assertion]
      early skip of rewriting module: dspy.adapters.types.image [assertion]
      early skip of rewriting module: PIL [assertion]
      early skip of rewriting module: dspy.adapters.types.tool [assertion]
      early skip of rewriting module: jsonschema [assertion]
      early skip of rewriting module: jsonschema._format [assertion]
      early skip of rewriting module: jsonschema.exceptions [assertion]
      early skip of rewriting module: attrs [assertion]
      early skip of rewriting module: attrs.converters [assertion]
      early skip of rewriting module: attrs.exceptions [assertion]
      early skip of rewriting module: attrs.filters [assertion]
      early skip of rewriting module: attrs.setters [assertion]
      early skip of rewriting module: attrs.validators [assertion]
      early skip of rewriting module: referencing [assertion]
      early skip of rewriting module: referencing._core [assertion]
      early skip of rewriting module: rpds [assertion]
      early skip of rewriting module: rpds.rpds [assertion]
      early skip of rewriting module: referencing.exceptions [assertion]
      early skip of rewriting module: referencing._attrs [assertion]
      early skip of rewriting module: referencing.typing [assertion]
      early skip of rewriting module: jsonschema._utils [assertion]
      early skip of rewriting module: fqdn [assertion]
      early skip of rewriting module: rfc3987 [assertion]
      early skip of rewriting module: rfc3986_validator [assertion]
      early skip of rewriting module: rfc3339_validator [assertion]
      early skip of rewriting module: webcolors [assertion]
      early skip of rewriting module: jsonpointer [assertion]
      early skip of rewriting module: uri_template [assertion]
      early skip of rewriting module: isoduration [assertion]
      early skip of rewriting module: jsonschema._types [assertion]
      early skip of rewriting module: jsonschema.validators [assertion]
      early skip of rewriting module: jsonschema_specifications [assertion]
      early skip of rewriting module: referencing.jsonschema [assertion]
      early skip of rewriting module: jsonschema_specifications._core [assertion]
      early skip of rewriting module: jsonschema._keywords [assertion]
      early skip of rewriting module: jsonschema._legacy_keywords [assertion]
      early skip of rewriting module: jsonschema._typing [assertion]
      early skip of rewriting module: jsonschema.protocols [assertion]
      early skip of rewriting module: dspy.signatures [assertion]
      early skip of rewriting module: dspy.signatures.field [assertion]
      early skip of rewriting module: dspy.signatures.signature [assertion]
      early skip of rewriting module: dspy.adapters.chat_adapter [assertion]
      early skip of rewriting module: dspy.adapters.utils [assertion]
      early skip of rewriting module: dspy.signatures.utils [assertion]
      early skip of rewriting module: dspy.clients [assertion]
      early skip of rewriting module: dspy.clients.base_lm [assertion]
      early skip of rewriting module: dspy.utils.inspect_history [assertion]
      early skip of rewriting module: dspy.clients.cache [assertion]
      early skip of rewriting module: cachetools [assertion]
      early skip of rewriting module: cachetools.keys [assertion]
      early skip of rewriting module: diskcache [assertion]
      early skip of rewriting module: diskcache.core [assertion]
      early skip of rewriting module: pickletools [assertion]
      early skip of rewriting module: sqlite3 [assertion]
      early skip of rewriting module: sqlite3.dbapi2 [assertion]
      early skip of rewriting module: _sqlite3 [assertion]
      early skip of rewriting module: diskcache.fanout [assertion]
      early skip of rewriting module: diskcache.persistent [assertion]
      early skip of rewriting module: diskcache.recipes [assertion]
      early skip of rewriting module: diskcache.djangocache [assertion]
      early skip of rewriting module: django [assertion]
      early skip of rewriting module: dspy.clients.embedding [assertion]
      early skip of rewriting module: numpy [assertion]
      early skip of rewriting module: numpy.version [assertion]
      early skip of rewriting module: numpy._expired_attrs_2_0 [assertion]
      early skip of rewriting module: numpy._globals [assertion]
      early skip of rewriting module: numpy._utils [assertion]
      early skip of rewriting module: numpy._utils._convertions [assertion]
      early skip of rewriting module: numpy._distributor_init [assertion]
      early skip of rewriting module: numpy._distributor_init_local [assertion]
      early skip of rewriting module: numpy.__config__ [assertion]
      early skip of rewriting module: numpy._core [assertion]
      early skip of rewriting module: numpy._core.multiarray [assertion]
      early skip of rewriting module: numpy._core._multiarray_umath [assertion]
      early skip of rewriting module: numpy.exceptions [assertion]
      early skip of rewriting module: numpy._core._exceptions [assertion]
      early skip of rewriting module: numpy._core.printoptions [assertion]
      early skip of rewriting module: numpy.dtypes [assertion]
      early skip of rewriting module: numpy._core.overrides [assertion]
      early skip of rewriting module: numpy._utils._inspect [assertion]
      early skip of rewriting module: numpy._core.umath [assertion]
      early skip of rewriting module: numpy._core.numerictypes [assertion]
      early skip of rewriting module: numpy._core._dtype [assertion]
      early skip of rewriting module: numpy._core._string_helpers [assertion]
      early skip of rewriting module: numpy._core._type_aliases [assertion]
      early skip of rewriting module: numpy._core._machar [assertion]
      early skip of rewriting module: numpy._core._ufunc_config [assertion]
      early skip of rewriting module: numpy._core.fromnumeric [assertion]
      early skip of rewriting module: numpy._core._methods [assertion]
      early skip of rewriting module: numpy._core.einsumfunc [assertion]
      early skip of rewriting module: numpy._core.numeric [assertion]
      early skip of rewriting module: numpy._core.shape_base [assertion]
      early skip of rewriting module: numpy._core._asarray [assertion]
      early skip of rewriting module: numpy._core.arrayprint [assertion]
      early skip of rewriting module: numpy._core.function_base [assertion]
      early skip of rewriting module: numpy._core.getlimits [assertion]
      early skip of rewriting module: numpy._core.memmap [assertion]
      early skip of rewriting module: numpy._core.records [assertion]
      early skip of rewriting module: numpy._core._add_newdocs [assertion]
      early skip of rewriting module: numpy._core._add_newdocs_scalars [assertion]
      early skip of rewriting module: numpy._core._dtype_ctypes [assertion]
      early skip of rewriting module: numpy._core._internal [assertion]
      early skip of rewriting module: ctypes [assertion]
      early skip of rewriting module: _ctypes [assertion]
      early skip of rewriting module: ctypes._endian [assertion]
      early skip of rewriting module: numpy._pytesttester [assertion]
      early skip of rewriting module: numpy.lib [assertion]
      early skip of rewriting module: numpy.lib._arraypad_impl [assertion]
      early skip of rewriting module: numpy.lib._index_tricks_impl [assertion]
      early skip of rewriting module: numpy.matrixlib [assertion]
      early skip of rewriting module: numpy.matrixlib.defmatrix [assertion]
      early skip of rewriting module: numpy.linalg [assertion]
      early skip of rewriting module: numpy.linalg._linalg [assertion]
      early skip of rewriting module: numpy._typing [assertion]
      early skip of rewriting module: numpy._typing._array_like [assertion]
      early skip of rewriting module: numpy._typing._nbit_base [assertion]
      early skip of rewriting module: numpy._typing._nested_sequence [assertion]
      early skip of rewriting module: numpy._typing._shape [assertion]
      early skip of rewriting module: numpy._typing._char_codes [assertion]
      early skip of rewriting module: numpy._typing._dtype_like [assertion]
      early skip of rewriting module: numpy._typing._nbit [assertion]
      early skip of rewriting module: numpy._typing._scalars [assertion]
      early skip of rewriting module: numpy._typing._ufunc [assertion]
      early skip of rewriting module: numpy.lib._twodim_base_impl [assertion]
      early skip of rewriting module: numpy.lib._stride_tricks_impl [assertion]
      early skip of rewriting module: numpy.lib.array_utils [assertion]
      early skip of rewriting module: numpy.lib._array_utils_impl [assertion]
      early skip of rewriting module: numpy.linalg._umath_linalg [assertion]
      early skip of rewriting module: numpy.linalg.linalg [assertion]
      early skip of rewriting module: numpy.lib._function_base_impl [assertion]
      early skip of rewriting module: numpy.lib._histograms_impl [assertion]
      early skip of rewriting module: numpy.lib.stride_tricks [assertion]
      early skip of rewriting module: numpy.lib._arraysetops_impl [assertion]
      early skip of rewriting module: numpy.lib._arrayterator_impl [assertion]
      early skip of rewriting module: numpy.lib._nanfunctions_impl [assertion]
      early skip of rewriting module: numpy.lib._npyio_impl [assertion]
      early skip of rewriting module: numpy.lib.format [assertion]
      early skip of rewriting module: numpy.lib._format_impl [assertion]
      early skip of rewriting module: numpy.lib._utils_impl [assertion]
      early skip of rewriting module: numpy.lib._datasource [assertion]
      early skip of rewriting module: numpy.lib._iotools [assertion]
      early skip of rewriting module: numpy.lib._polynomial_impl [assertion]
      early skip of rewriting module: numpy.lib._type_check_impl [assertion]
      early skip of rewriting module: numpy.lib._ufunclike_impl [assertion]
      early skip of rewriting module: numpy.lib._shape_base_impl [assertion]
      early skip of rewriting module: numpy.lib._version [assertion]
      early skip of rewriting module: numpy.lib.introspect [assertion]
      early skip of rewriting module: numpy.lib.mixins [assertion]
      early skip of rewriting module: numpy.lib.npyio [assertion]
      early skip of rewriting module: numpy.lib.scimath [assertion]
      early skip of rewriting module: numpy.lib._scimath_impl [assertion]
      early skip of rewriting module: numpy._array_api_info [assertion]
      early skip of rewriting module: dspy.clients.lm [assertion]
      early skip of rewriting module: asyncer [assertion]
      early skip of rewriting module: asyncer._main [assertion]
      early skip of rewriting module: asyncer._compat [assertion]
      early skip of rewriting module: dspy.clients.openai [assertion]
      early skip of rewriting module: dspy.clients.provider [assertion]
      early skip of rewriting module: dspy.clients.utils_finetune [assertion]
      early skip of rewriting module: dspy.utils.caching [assertion]
      early skip of rewriting module: dspy.utils.exceptions [assertion]
      early skip of rewriting module: dspy.adapters.json_adapter [assertion]
      early skip of rewriting module: dspy.adapters.two_step_adapter [assertion]
      early skip of rewriting module: dspy.utils.asyncify [assertion]
      early skip of rewriting module: dspy.utils.dummies [assertion]
      early skip of rewriting module: dspy.utils.saving [assertion]
      early skip of rewriting module: dspy.primitives.program [assertion]
      early skip of rewriting module: magicattr [assertion]
      early skip of rewriting module: dspy.predict.parallel [assertion]
      early skip of rewriting module: dspy.utils.parallelizer [assertion]
      early skip of rewriting module: dspy.utils.usage_tracker [assertion]
      early skip of rewriting module: dspy.primitives.python_interpreter [assertion]
      early skip of rewriting module: dspy.predict.best_of_n [assertion]
      early skip of rewriting module: dspy.predict.predict [assertion]
      early skip of rewriting module: dspy.predict.parameter [assertion]
      early skip of rewriting module: dspy.predict.chain_of_thought [assertion]
      early skip of rewriting module: dspy.predict.chain_of_thought_with_hint [assertion]
      early skip of rewriting module: dspy.predict.code_act [assertion]
      early skip of rewriting module: dspy.predict.program_of_thought [assertion]
      early skip of rewriting module: dspy.predict.react [assertion]
      early skip of rewriting module: dspy.predict.knn [assertion]
      early skip of rewriting module: dspy.predict.multi_chain_comparison [assertion]
      early skip of rewriting module: dspy.predict.refine [assertion]
      early skip of rewriting module: dspy.retrieve [assertion]
      early skip of rewriting module: dspy.retrieve.retrieve [assertion]
      early skip of rewriting module: dspy.teleprompt [assertion]
      early skip of rewriting module: dspy.teleprompt.avatar_optimizer [assertion]
      early skip of rewriting module: dspy.predict.avatar [assertion]
      early skip of rewriting module: dspy.predict.avatar.avatar [assertion]
      early skip of rewriting module: dspy.predict.avatar.models [assertion]
      early skip of rewriting module: dspy.predict.avatar.signatures [assertion]
      early skip of rewriting module: dspy.teleprompt.teleprompt [assertion]
      early skip of rewriting module: dspy.teleprompt.bettertogether [assertion]
      early skip of rewriting module: dspy.teleprompt.bootstrap_finetune [assertion]
      early skip of rewriting module: dspy.evaluate [assertion]
      early skip of rewriting module: dspy.evaluate.auto_evaluation [assertion]
      early skip of rewriting module: dspy.evaluate.evaluate [assertion]
      early skip of rewriting module: IPython [assertion]
      early skip of rewriting module: dspy.evaluate.metrics [assertion]
      early skip of rewriting module: dspy.teleprompt.random_search [assertion]
      early skip of rewriting module: dspy.teleprompt.bootstrap [assertion]
      early skip of rewriting module: dspy.teleprompt.vanilla [assertion]
      early skip of rewriting module: dspy.teleprompt.copro_optimizer [assertion]
      early skip of rewriting module: dspy.teleprompt.ensemble [assertion]
      early skip of rewriting module: dspy.teleprompt.infer_rules [assertion]
      early skip of rewriting module: dspy.teleprompt.knn_fewshot [assertion]
      early skip of rewriting module: dspy.teleprompt.mipro_optimizer_v2 [assertion]
      early skip of rewriting module: dspy.propose [assertion]
      early skip of rewriting module: dspy.propose.grounded_proposer [assertion]
      early skip of rewriting module: dspy.propose.dataset_summary_generator [assertion]
      early skip of rewriting module: dspy.propose.utils [assertion]
      early skip of rewriting module: IPython [assertion]
      early skip of rewriting module: dspy.teleprompt.utils [assertion]
      early skip of rewriting module: IPython [assertion]
      early skip of rewriting module: dspy.propose.propose_base [assertion]
      early skip of rewriting module: dspy.teleprompt.simba [assertion]
      early skip of rewriting module: dspy.teleprompt.simba_utils [assertion]
      early skip of rewriting module: dspy.teleprompt.teleprompt_optuna [assertion]
      early skip of rewriting module: dspy.retrievers [assertion]
      early skip of rewriting module: dspy.retrievers.embeddings [assertion]
      early skip of rewriting module: dspy.utils.unbatchify [assertion]
      early skip of rewriting module: dspy.utils.logging_utils [assertion]
      early skip of rewriting module: logging.config [assertion]
      early skip of rewriting module: logging.handlers [assertion]
      early skip of rewriting module: socketserver [assertion]
      early skip of rewriting module: dspy.dsp.colbertv2 [assertion]
      early skip of rewriting module: dspy.__metadata__ [assertion]
      early skip of rewriting module: unittest.mock [assertion]
      early skip of rewriting module: coding_agent_repl [assertion]
      early skip of rewriting module: textual [assertion]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_coding_agent_repl.py' lenresult=0 outcome='failed'> [hook]
      pytest_exception_interact [hook]
          node: <Module test_coding_agent_repl.py>
          call: <CallInfo when='collect' excinfo=<ExceptionInfo CollectError("ImportError while importing test module '/home/tom/git/agent/tests/test_coding_agent_repl.py'.\nHint: ma...py:5: in <module>\n    from textual.app import App, ComposeResult\nE   ModuleNotFoundError: No module named 'textual'") tblen=7>>
          report: <CollectReport 'tests/test_coding_agent_repl.py' lenresult=0 outcome='failed'>
      finish pytest_exception_interact --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_coding_agent_repl.py' lenresult=0 outcome='failed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_interactive_chat.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_interactive_chat.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_interactive_chat.py>
      find_module called for: test_interactive_chat [assertion]
      matched test file '/home/tom/git/agent/tests/test_interactive_chat.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/tests/test_interactive_chat.py [assertion]
      early skip of rewriting module: interactive_chat [assertion]
      early skip of rewriting module: textual [assertion]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_interactive_chat.py' lenresult=0 outcome='failed'> [hook]
      pytest_exception_interact [hook]
          node: <Module test_interactive_chat.py>
          call: <CallInfo when='collect' excinfo=<ExceptionInfo CollectError("ImportError while importing test module '/home/tom/git/agent/tests/test_interactive_chat.py'.\nHint: mak...py:3: in <module>\n    from textual.app import App, ComposeResult\nE   ModuleNotFoundError: No module named 'textual'") tblen=7>>
          report: <CollectReport 'tests/test_interactive_chat.py' lenresult=0 outcome='failed'>
      finish pytest_exception_interact --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_interactive_chat.py' lenresult=0 outcome='failed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_iterative_improvement_elo.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_iterative_improvement_elo.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_iterative_improvement_elo.py>
      find_module called for: test_iterative_improvement_elo [assertion]
      matched test file '/home/tom/git/agent/tests/test_iterative_improvement_elo.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/tests/test_iterative_improvement_elo.py [assertion]
      early skip of rewriting module: iterative_improvement_elo [assertion]
      early skip of rewriting module: simpledspy [assertion]
      early skip of rewriting module: simpledspy.module_caller [assertion]
      early skip of rewriting module: simpledspy.module_factory [assertion]
      early skip of rewriting module: simpledspy.optimization_manager [assertion]
      early skip of rewriting module: simpledspy.metrics [assertion]
      early skip of rewriting module: simpledspy.logger [assertion]
      early skip of rewriting module: simpledspy.settings [assertion]
      early skip of rewriting module: simpledspy.pipeline_manager [assertion]
      early skip of rewriting module: model_map [assertion]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: @py_builtins
            obj: <module 'builtins' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: @pytest_ar
            obj: <module '_pytest.assertion.rewrite' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/assertion/rewrite.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: pytest
            obj: <module 'pytest' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/pytest/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: __warningregistry__
            obj: {'version': 67, ('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 4): True}
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: pytestmark
            obj: MarkDecorator(mark=Mark(name='timeout', args=(10,), kwargs={'method': 'thread'}))
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: os
            obj: <module 'os' (frozen)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: sys
            obj: <module 'sys' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: sample_version
            obj: <function sample_version at 0x7f60f8c1c720>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: get_random_opponent
            obj: <function get_random_opponent at 0x7f60f8c1cc20>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: update_elo_ratings
            obj: <function update_elo_ratings at 0x7f60f8c1ccc0>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: iterative_improvement_elo
            obj: <function iterative_improvement_elo at 0x7f60f8c1cd60>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: patch
            obj: <function patch at 0x7f60f8b8fb00>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: MagicMock
            obj: <class 'unittest.mock.MagicMock'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: np
            obj: <module 'numpy' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/numpy/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: random
            obj: <module 'random' from '/home/tom/.pyenv/versions/3.11.10/lib/python3.11/random.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: predict
            obj: <simpledspy.module_caller.Predict object at 0x7f60f8bbad50>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: chain_of_thought
            obj: <simpledspy.module_caller.ChainOfThought object at 0x7f60f8bc1550>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_sample_version
            obj: <function test_sample_version at 0x7f60f8bfaa20>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8d5a290>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_sample_version>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_sample_version_empty_list
            obj: <function test_sample_version_empty_list at 0x7f60f8bfac00>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8bbbbd0>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_sample_version_empty_list>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_sample_version_single_item
            obj: <function test_sample_version_single_item at 0x7f60f8c1cea0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8bb8350>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_sample_version_single_item>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_get_random_opponent
            obj: <function test_get_random_opponent at 0x7f60f8c1cf40>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f61373094d0>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_get_random_opponent>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_get_random_opponent_only_two
            obj: <function test_get_random_opponent_only_two at 0x7f60f8c1cfe0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8c781d0>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_get_random_opponent_only_two>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_update_elo_ratings
            obj: <function test_update_elo_ratings at 0x7f60f8c1d080>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f9033e10>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_update_elo_ratings>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_update_elo_ratings_high_k
            obj: <function test_update_elo_ratings_high_k at 0x7f60f8c1d120>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8ba3b50>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_update_elo_ratings_high_k>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_update_elo_ratings_expected_win
            obj: <function test_update_elo_ratings_expected_win at 0x7f60f8c1d1c0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8ba1250>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_update_elo_ratings_expected_win>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_update_elo_ratings_upset
            obj: <function test_update_elo_ratings_upset at 0x7f60f8c1d260>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8ba2dd0>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_update_elo_ratings_upset>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_iterative_improvement_flow
            obj: <function test_iterative_improvement_flow at 0x7f60f8c1d3a0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8ba2dd0>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_iterative_improvement_flow>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_elo_ranking_order
            obj: <function test_elo_ranking_order at 0x7f60f8c1d4e0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613d1e1210>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_elo_ranking_order>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_thread_safety
            obj: <function test_thread_safety at 0x7f60f8c1d620>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8bc3390>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_thread_safety>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_exception_handling
            obj: <function test_exception_handling at 0x7f60f8c1d760>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8bc3850>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_exception_handling>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_iterative_improvement_elo.py>
            name: test_large_iterations
            obj: <function test_large_iterations at 0x7f60f8c1d9e0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8ba9bd0>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_large_iterations>] [hook]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_iterative_improvement_elo.py' lenresult=14 outcome='passed'> [hook]
    genitems <Function test_sample_version> [collection]
      pytest_itemcollected [hook]
          item: <Function test_sample_version>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_sample_version_empty_list> [collection]
      pytest_itemcollected [hook]
          item: <Function test_sample_version_empty_list>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_sample_version_single_item> [collection]
      pytest_itemcollected [hook]
          item: <Function test_sample_version_single_item>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_get_random_opponent> [collection]
      pytest_itemcollected [hook]
          item: <Function test_get_random_opponent>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_get_random_opponent_only_two> [collection]
      pytest_itemcollected [hook]
          item: <Function test_get_random_opponent_only_two>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_update_elo_ratings> [collection]
      pytest_itemcollected [hook]
          item: <Function test_update_elo_ratings>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_update_elo_ratings_high_k> [collection]
      pytest_itemcollected [hook]
          item: <Function test_update_elo_ratings_high_k>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_update_elo_ratings_expected_win> [collection]
      pytest_itemcollected [hook]
          item: <Function test_update_elo_ratings_expected_win>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_update_elo_ratings_upset> [collection]
      pytest_itemcollected [hook]
          item: <Function test_update_elo_ratings_upset>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_iterative_improvement_flow> [collection]
      pytest_itemcollected [hook]
          item: <Function test_iterative_improvement_flow>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_elo_ranking_order> [collection]
      pytest_itemcollected [hook]
          item: <Function test_elo_ranking_order>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_thread_safety> [collection]
      pytest_itemcollected [hook]
          item: <Function test_thread_safety>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_exception_handling> [collection]
      pytest_itemcollected [hook]
          item: <Function test_exception_handling>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_large_iterations> [collection]
      pytest_itemcollected [hook]
          item: <Function test_large_iterations>
      finish pytest_itemcollected --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_iterative_improvement_elo.py' lenresult=14 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_memory_gan.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_memory_gan.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_memory_gan.py>
      find_module called for: test_memory_gan [assertion]
      matched test file '/home/tom/git/agent/tests/test_memory_gan.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/tests/test_memory_gan.py [assertion]
      early skip of rewriting module: dspy_programs [assertion]
      early skip of rewriting module: dspy_programs.memory_gan [assertion]
      early skip of rewriting module: mlflow [assertion]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_memory_gan.py' lenresult=0 outcome='failed'> [hook]
      pytest_exception_interact [hook]
          node: <Module test_memory_gan.py>
          call: <CallInfo when='collect' excinfo=<ExceptionInfo CollectError("ImportError while importing test module '/home/tom/git/agent/tests/test_memory_gan.py'.\nHint: make sure...an\ndspy_programs/memory_gan.py:16: in <module>\n    import mlflow\nE   ModuleNotFoundError: No module named 'mlflow'") tblen=7>>
          report: <CollectReport 'tests/test_memory_gan.py' lenresult=0 outcome='failed'>
      finish pytest_exception_interact --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_memory_gan.py' lenresult=0 outcome='failed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_minimal_dspy_import.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_minimal_dspy_import.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_minimal_dspy_import.py>
      find_module called for: test_minimal_dspy_import [assertion]
      matched test file '/home/tom/git/agent/tests/test_minimal_dspy_import.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/tests/test_minimal_dspy_import.py [assertion]
      early skip of rewriting module: dspy_programs.value_network [assertion]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_minimal_dspy_import.py>
            name: @py_builtins
            obj: <module 'builtins' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_minimal_dspy_import.py>
            name: @pytest_ar
            obj: <module '_pytest.assertion.rewrite' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/assertion/rewrite.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_minimal_dspy_import.py>
            name: dspy
            obj: <module 'dspy' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/dspy/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_minimal_dspy_import.py>
            name: ValueNetwork
            obj: <class 'dspy_programs.value_network.ValueNetwork'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_minimal_dspy_import.py>
            name: test_placeholder
            obj: <function test_placeholder at 0x7f60f8eb8040>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8a7a290>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_placeholder>] [hook]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_minimal_dspy_import.py' lenresult=1 outcome='passed'> [hook]
    genitems <Function test_placeholder> [collection]
      pytest_itemcollected [hook]
          item: <Function test_placeholder>
      finish pytest_itemcollected --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_minimal_dspy_import.py' lenresult=1 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_online_optimization.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_online_optimization.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_online_optimization.py>
      find_module called for: test_online_optimization [assertion]
      matched test file '/home/tom/git/agent/tests/test_online_optimization.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/tests/test_online_optimization.py [assertion]
      early skip of rewriting module: online_optimization_system [assertion]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: @py_builtins
            obj: <module 'builtins' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: @pytest_ar
            obj: <module '_pytest.assertion.rewrite' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/assertion/rewrite.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: pytest
            obj: <module 'pytest' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/pytest/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: __warningregistry__
            obj: {'version': 76, ('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 2): True, ('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 33): True, ('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 53): True}
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: pytestmark
            obj: MarkDecorator(mark=Mark(name='timeout', args=(10,), kwargs={'method': 'thread'}))
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: asyncio
            obj: <module 'asyncio' from '/home/tom/.pyenv/versions/3.11.10/lib/python3.11/asyncio/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: time
            obj: <module 'time' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: os
            obj: <module 'os' (frozen)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: sys
            obj: <module 'sys' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: MagicMock
            obj: <class 'unittest.mock.MagicMock'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: patch
            obj: <function patch at 0x7f60f8b8fb00>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: OnlineOptimizationSystem
            obj: <class 'online_optimization_system.OnlineOptimizationSystem'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: AsyncModelManager
            obj: <class 'online_optimization_system.AsyncModelManager'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: OptimizationRequest
            obj: <class 'online_optimization_system.OptimizationRequest'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: InferenceResult
            obj: <class 'online_optimization_system.InferenceResult'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: dspy
            obj: <module 'dspy' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/dspy/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: MockModule
            obj: <class 'test_online_optimization.MockModule'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: mock_system
            obj: <pytest_fixture(<function mock_system at 0x7f613d2ef600>)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: test_inference_returns_result
            obj: <function test_inference_returns_result at 0x7f60f8c1dd00>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613d1e1490>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_inference_returns_result>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: test_model_hot_swap
            obj: <function test_model_hot_swap at 0x7f60f8c1dda0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f613b315e50>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_model_hot_swap>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: test_graceful_degradation
            obj: <function test_graceful_degradation at 0x7f60f8c1de40>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f61372ac710>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_graceful_degradation>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: test_optimization_trigger_data_batch
            obj: <function test_optimization_trigger_data_batch at 0x7f60f8c1dee0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8ba3590>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_optimization_trigger_data_batch>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: test_optimization_trigger_performance
            obj: <function test_optimization_trigger_performance at 0x7f60f8c1df80>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8ba3090>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_optimization_trigger_performance>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_online_optimization.py>
            name: test_optimization_completion
            obj: <function test_optimization_completion at 0x7f60f8c1e020>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f6137309850>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_optimization_completion>] [hook]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_online_optimization.py' lenresult=6 outcome='passed'> [hook]
    genitems <Function test_inference_returns_result> [collection]
      pytest_itemcollected [hook]
          item: <Function test_inference_returns_result>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_model_hot_swap> [collection]
      pytest_itemcollected [hook]
          item: <Function test_model_hot_swap>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_graceful_degradation> [collection]
      pytest_itemcollected [hook]
          item: <Function test_graceful_degradation>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_optimization_trigger_data_batch> [collection]
      pytest_itemcollected [hook]
          item: <Function test_optimization_trigger_data_batch>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_optimization_trigger_performance> [collection]
      pytest_itemcollected [hook]
          item: <Function test_optimization_trigger_performance>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_optimization_completion> [collection]
      pytest_itemcollected [hook]
          item: <Function test_optimization_completion>
      finish pytest_itemcollected --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_online_optimization.py' lenresult=6 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_self_review_agent.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_self_review_agent.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_self_review_agent.py>
      find_module called for: test_self_review_agent [assertion]
      matched test file '/home/tom/git/agent/tests/test_self_review_agent.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/tests/test_self_review_agent.py [assertion]
      early skip of rewriting module: self_review_agent [assertion]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: @py_builtins
            obj: <module 'builtins' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: @pytest_ar
            obj: <module '_pytest.assertion.rewrite' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/_pytest/assertion/rewrite.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: pytest
            obj: <module 'pytest' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/pytest/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: __warningregistry__
            obj: {'version': 76, ('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html', <class 'pytest.PytestUnknownMarkWarning'>, 4): True}
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: pytestmark
            obj: MarkDecorator(mark=Mark(name='timeout', args=(10,), kwargs={'method': 'thread'}))
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: os
            obj: <module 'os' (frozen)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: sys
            obj: <module 'sys' (built-in)>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: SelfReviewAgent
            obj: <class 'self_review_agent.SelfReviewAgent'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: dspy
            obj: <module 'dspy' from '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/dspy/__init__.py'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: patch
            obj: <function patch at 0x7f60f8b8fb00>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: MagicMock
            obj: <class 'unittest.mock.MagicMock'>
        finish pytest_pycollect_makeitem --> None [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: test_self_review_agent_initialization
            obj: <function test_self_review_agent_initialization at 0x7f60f8c1e3e0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8c43c10>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_self_review_agent_initialization>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: test_self_review_flow
            obj: <function test_self_review_flow at 0x7f60f8c1e8e0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8c41590>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_self_review_flow>] [hook]
        pytest_pycollect_makeitem [hook]
            collector: <Module test_self_review_agent.py>
            name: test_self_review_early_stop
            obj: <function test_self_review_early_stop at 0x7f60f8c1eac0>
          pytest_generate_tests [hook]
              metafunc: <_pytest.python.Metafunc object at 0x7f60f8c43850>
          finish pytest_generate_tests --> [] [hook]
        finish pytest_pycollect_makeitem --> [<Function test_self_review_early_stop>] [hook]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_self_review_agent.py' lenresult=3 outcome='passed'> [hook]
    genitems <Function test_self_review_agent_initialization> [collection]
      pytest_itemcollected [hook]
          item: <Function test_self_review_agent_initialization>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_self_review_flow> [collection]
      pytest_itemcollected [hook]
          item: <Function test_self_review_flow>
      finish pytest_itemcollected --> [] [hook]
    genitems <Function test_self_review_early_stop> [collection]
      pytest_itemcollected [hook]
          item: <Function test_self_review_early_stop>
      finish pytest_itemcollected --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_self_review_agent.py' lenresult=3 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
    genitems <Module test_taskwarrior_dspy_agent.py> [collection]
      pytest_collectstart [hook]
          collector: <Module test_taskwarrior_dspy_agent.py>
      finish pytest_collectstart --> [] [hook]
      pytest_make_collect_report [hook]
          collector: <Module test_taskwarrior_dspy_agent.py>
      find_module called for: test_taskwarrior_dspy_agent [assertion]
      matched test file '/home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py' [assertion]
      found cached rewritten pyc for /home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py [assertion]
      early skip of rewriting module: taskwarrior_dspy_agent [assertion]
      finish pytest_make_collect_report --> <CollectReport 'tests/test_taskwarrior_dspy_agent.py' lenresult=0 outcome='failed'> [hook]
      pytest_exception_interact [hook]
          node: <Module test_taskwarrior_dspy_agent.py>
          call: <CallInfo when='collect' excinfo=<ExceptionInfo CollectError("ImportError while importing test module '/home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py'.\nHin...tError: cannot import name 'setup_dspy' from 'taskwarrior_dspy_agent' (/home/tom/git/agent/taskwarrior_dspy_agent.py)") tblen=7>>
          report: <CollectReport 'tests/test_taskwarrior_dspy_agent.py' lenresult=0 outcome='failed'>
      finish pytest_exception_interact --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests/test_taskwarrior_dspy_agent.py' lenresult=0 outcome='failed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport 'tests' lenresult=9 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collectreport [hook]
          report: <CollectReport '.' lenresult=7 outcome='passed'>
      finish pytest_collectreport --> [] [hook]
      pytest_collection_modifyitems [hook]
          session: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=6 testscollected=0>
          config: <_pytest.config.Config object at 0x7f613db31910>
          items: [<Function test_shell_start_stop>, <Function test_execute_simple_command>, <Function test_cd_command>, <Function test_cd_nonexistent_directory>, <Function test_command_with_error>, <Function test_concurrent_commands>, <Function test_sample_version>, <Function test_sample_version_empty_list>, <Function test_sample_version_single_item>, <Function test_get_random_opponent>, <Function test_get_random_opponent_only_two>, <Function test_update_elo_ratings>, <Function test_update_elo_ratings_high_k>, <Function test_update_elo_ratings_expected_win>, <Function test_update_elo_ratings_upset>, <Function test_iterative_improvement_flow>, <Function test_elo_ranking_order>, <Function test_thread_safety>, <Function test_exception_handling>, <Function test_large_iterations>, <Function test_placeholder>, <Function test_inference_returns_result>, <Function test_model_hot_swap>, <Function test_graceful_degradation>, <Function test_optimization_trigger_data_batch>, <Function test_optimization_trigger_performance>, <Function test_optimization_completion>, <Function test_self_review_agent_initialization>, <Function test_self_review_flow>, <Function test_self_review_early_stop>]
      finish pytest_collection_modifyitems --> [] [hook]
      pytest_collection_finish [hook]
          session: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=6 testscollected=0>
        pytest_report_collectionfinish [hook]
            config: <_pytest.config.Config object at 0x7f613db31910>
            items: [<Function test_shell_start_stop>, <Function test_execute_simple_command>, <Function test_cd_command>, <Function test_cd_nonexistent_directory>, <Function test_command_with_error>, <Function test_concurrent_commands>, <Function test_sample_version>, <Function test_sample_version_empty_list>, <Function test_sample_version_single_item>, <Function test_get_random_opponent>, <Function test_get_random_opponent_only_two>, <Function test_update_elo_ratings>, <Function test_update_elo_ratings_high_k>, <Function test_update_elo_ratings_expected_win>, <Function test_update_elo_ratings_upset>, <Function test_iterative_improvement_flow>, <Function test_elo_ranking_order>, <Function test_thread_safety>, <Function test_exception_handling>, <Function test_large_iterations>, <Function test_placeholder>, <Function test_inference_returns_result>, <Function test_model_hot_swap>, <Function test_graceful_degradation>, <Function test_optimization_trigger_data_batch>, <Function test_optimization_trigger_performance>, <Function test_optimization_completion>, <Function test_self_review_agent_initialization>, <Function test_self_review_flow>, <Function test_self_review_early_stop>]
            start_path: /home/tom/git/agent
            startdir: /home/tom/git/agent
        finish pytest_report_collectionfinish --> [] [hook]
      finish pytest_collection_finish --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/test_shell_wrapper.py', lineno : 6, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/test_shell_wrapper.py', lineno : 17, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/test_shell_wrapper.py', lineno : 27, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/test_shell_wrapper.py', lineno : 35, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/test_shell_wrapper.py', lineno : 52, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/test_shell_wrapper.py', lineno : 61, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/test_shell_wrapper.py', lineno : 69, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_coding_agent_repl.py', lineno : 4, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PydanticDeprecatedSince20('Support for class-based `config` is deprecated, use ConfigDict instead.'), category : 'PydanticDeprecatedSince20', filename : '/home/tom/.cache/pypoetry/virtualenvs/simpledspy-MXii_-6N-py3.11/lib/python3.11/site-packages/pydantic/_internal/_config.py', lineno : 323, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_interactive_chat.py', lineno : 4, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_iterative_improvement_elo.py', lineno : 4, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_memory_gan.py', lineno : 2, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_online_optimization.py', lineno : 2, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_online_optimization.py', lineno : 33, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.asyncio - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_online_optimization.py', lineno : 53, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_self_review_agent.py', lineno : 4, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
      pytest_warning_recorded [hook]
          warning_message: {message : PytestUnknownMarkWarning('Unknown pytest.mark.timeout - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html'), category : 'PytestUnknownMarkWarning', filename : '/home/tom/git/agent/tests/test_taskwarrior_dspy_agent.py', lineno : 3, line : None}
          nodeid: 
          when: collect
          location: None
      finish pytest_warning_recorded --> [] [hook]
    finish pytest_collection --> None [hook]
    pytest_runtestloop [hook]
        session: <Session  exitstatus=<ExitCode.OK: 0> testsfailed=6 testscollected=30>
    pytest_keyboard_interrupt [hook]
        excinfo: <ExceptionInfo Interrupted('6 errors during collection') tblen=15>
    finish pytest_keyboard_interrupt --> [] [hook]
    pytest_sessionfinish [hook]
        session: <Session  exitstatus=<ExitCode.INTERRUPTED: 2> testsfailed=6 testscollected=30>
        exitstatus: 2
      pytest_terminal_summary [hook]
          terminalreporter: <_pytest.terminal.TerminalReporter object at 0x7f613d4530d0>
          exitstatus: 2
          config: <_pytest.config.Config object at 0x7f613db31910>
        pytest_report_teststatus [hook]
            report: <CollectReport 'test_textual_task_manager.py' lenresult=0 outcome='failed'>
            config: <_pytest.config.Config object at 0x7f613db31910>
        finish pytest_report_teststatus --> ('error', 'E', 'ERROR') [hook]
        pytest_report_teststatus [hook]
            report: <CollectReport 'tests/test_active_learning.py' lenresult=0 outcome='failed'>
            config: <_pytest.config.Config object at 0x7f613db31910>
        finish pytest_report_teststatus --> ('error', 'E', 'ERROR') [hook]
        pytest_report_teststatus [hook]
            report: <CollectReport 'tests/test_coding_agent_repl.py' lenresult=0 outcome='failed'>
            config: <_pytest.config.Config object at 0x7f613db31910>
        finish pytest_report_teststatus --> ('error', 'E', 'ERROR') [hook]
        pytest_report_teststatus [hook]
            report: <CollectReport 'tests/test_interactive_chat.py' lenresult=0 outcome='failed'>
            config: <_pytest.config.Config object at 0x7f613db31910>
        finish pytest_report_teststatus --> ('error', 'E', 'ERROR') [hook]
        pytest_report_teststatus [hook]
            report: <CollectReport 'tests/test_memory_gan.py' lenresult=0 outcome='failed'>
            config: <_pytest.config.Config object at 0x7f613db31910>
        finish pytest_report_teststatus --> ('error', 'E', 'ERROR') [hook]
        pytest_report_teststatus [hook]
            report: <CollectReport 'tests/test_taskwarrior_dspy_agent.py' lenresult=0 outcome='failed'>
            config: <_pytest.config.Config object at 0x7f613db31910>
        finish pytest_report_teststatus --> ('error', 'E', 'ERROR') [hook]
      finish pytest_terminal_summary --> [] [hook]
    finish pytest_sessionfinish --> [] [hook]
    pytest_unconfigure [hook]
        config: <_pytest.config.Config object at 0x7f613db31910>
    finish pytest_unconfigure --> [] [hook]
