@echo off
:start
echo --------------------Starting cards_coolbet scripts--------------------
python coolbet.py
echo --------------------Restarting cards_coolbet scripts--------------------
timeout 2
goto start