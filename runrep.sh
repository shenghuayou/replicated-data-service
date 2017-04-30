#!/bin/bash

osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python controller.py"'
osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python server.py 9999"'
osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python server.py 9998"'
osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python bot.py sheng addmoney100"'
osascript -e 'tell application "Terminal" to do script "cd Desktop/rep* && python bot.py sheng checkmoney"'