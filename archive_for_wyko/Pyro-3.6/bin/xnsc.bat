@echo off
python -O -tt -c "import Pyro.xnsc,sys; Pyro.xnsc.main(sys.argv[1:])" %*
