@echo off
:start
echo --------------------Starting cards_betinia scripts--------------------
python betinia.py
echo --------------------Restarting cards_betinia scripts--------------------
timeout 2
goto start