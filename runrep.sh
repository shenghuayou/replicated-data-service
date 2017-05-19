#!/bin/bash

osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python local_controller.py"'
osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python local_server.py 9997"'
osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python local_server.py 9998"'
osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python local_bot.py sheng"'
osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python local_bot.py client1"'