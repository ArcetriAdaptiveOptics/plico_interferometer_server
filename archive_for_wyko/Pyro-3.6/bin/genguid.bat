@echo off
python -O -tt -c "import Pyro.util,sys; Pyro.util.genguid_scripthelper(sys.argv[1:])" %*
