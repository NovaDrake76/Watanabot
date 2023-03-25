import subprocess
import time
import schedule

def post():
    # Run bot.py
    subprocess.run(['python', 'bot.py'])

    # Run connection.py
    subprocess.run(['python', 'connection.py'])

post()