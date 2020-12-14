# Duo Lingo Slack Messenger

This is a weekend project I build to help friends and family compete against each other in Duolingo, since apparently
They removed the ability for you to compete against friends. So this records what your friends stats are and yours to a local 
json file and as long as you run it daily it will send Slack messages to you telling you who won for the day, and 
if you kept up a streak. 

I run this using a cron job like this: 
```shell
0 18 * * * ****enter path to python***** ***enter full path to duoTracker*****/duoTracker/main.py reminder >>~/cron.log 2>&1 
45 23 * * * ****enter path to python***** ***enter full path to duoTracker*****/duoTracker/main.py user-stats >>~/cron.log 2>&1
```

The first task sends out a reminder at 6PM every day to practice... while the second one runs at 11:45PM and pulls all the 
progress for the day, stores it in your local file, and sends out a slack update letting you know the progress for the day. 

Lastly you will need to set up the .env file for this to work. I've included `.env.example` it should be self-explanatory.
You will need to rename this file to `.env` for it to work properly. 

Happy coding. :) 