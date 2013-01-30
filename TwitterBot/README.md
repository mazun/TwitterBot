TwitterBot
==========
You can create bot of twitter with Python easily.

Requirement
-----------
+ Tweepy

How to use
----------
    class MyBot(TwitterBot):
      def __init__(self, auth):
        TwitterBot.__init__(self, auth)
      ...
    
    auth = tweepy.OAuthHandler(...)
    ...
    bot  = MyBot(auth)
    bot.run()

### Callback functions(methods) are bellow: ###
+ process_status(status)
+ process_follow(user)
+ par_second_event
+ par_minute_event
+ par_hour_event
