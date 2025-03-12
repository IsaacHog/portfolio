@echo off
:start
echo --------------------Starting cards_kambi scripts--------------------
python kambi.py
echo --------------------Restarting cards_kambi scripts--------------------
timeout 2
goto start