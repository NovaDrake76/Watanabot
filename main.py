import subprocess

def post():
    # Run bot.py
    subprocess.run(['python', 'bot.py'])

    # Run connection.py
    subprocess.run(['python', 'connection.py'])

post()

# #post every 1h
# schedule.every(1).hours.do(post)

# while True:
#     schedule.run_pending()
#     time.sleep(1)
    