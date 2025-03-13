@echo off
title shots_queue
:start
echo --------------------Starting shots_auto_add_to_queue scripts--------------------
python shots_auto_add_to_queue.py
echo --------------------Restarting shots_auto_add_to_queue scripts--------------------
timeout 2
goto start