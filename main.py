import subprocess
import time
import schedule

def post():
    # Run bot.py
    subprocess.run(['python', 'bot.py'])

    # Run connection.py
    subprocess.run(['python', 'connection.py'])

#post every 4h
# schedule.every(4).hours.do(post)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

post()
    