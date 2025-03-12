@echo off
:start
echo --------------------Starting cards_comeon scripts--------------------
python comeon.py
echo --------------------Restarting cards_comeon scripts--------------------
timeout 2
goto start