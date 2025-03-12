@echo off
:start
echo --------------------Starting cards_betway scripts--------------------
python betway.py
echo --------------------Restarting cards_betway scripts--------------------
timeout 2
goto start