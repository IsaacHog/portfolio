@echo off
title shots_kambi
:start
echo --------------------Starting shots_kambi scripts--------------------
python kambi.py
echo --------------------Restarting shots_kambi scripts--------------------
timeout 2
goto start