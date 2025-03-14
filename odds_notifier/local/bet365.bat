@echo off
title shots_365
:start
echo --------------------Starting shots_365 scripts--------------------
python bet365.py
echo --------------------Restarting shots_365 scripts--------------------
timeout 2
goto start