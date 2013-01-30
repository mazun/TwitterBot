#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
TwitterBot Library
"""

__author__ = '@y_mazun'
__status__ = 'developing'
__version__ = 'alpha'

import tweepy
import tweepy.streaming
import datetime
import json
from tweepy.models import Status
from tweepy.models import User
from datetime      import datetime
from datetime      import timedelta
from threading     import Thread
from threading     import Timer
from lib.override  import override

import logging

class TwitterBot:
  """
  Base class of Bot.

  Usage:
    class MyBot(TwitterBot):
      def __init__(self, auth):
        TwitterBot.__init__(self, auth)
      ...

    auth = tweepy.OAuthHandler(...)
    ...
    bot  = MyBot(auth)
    bot.run()

  Callback functions(methods) are bellow:
  - process_status(status)
  - process_follow(user)
  - par_second_event
  - par_minute_event
  - par_hour_event
  """

  class _Listener(tweepy.streaming.StreamListener):
    """
    Listener for twitter streaming api
    """
    def __init__(self, bot, api):
      self.bot = bot
      tweepy.streaming.StreamListener.__init__(self, api)

    @override
    def on_data(self, data):
      logging.debug(json.loads(data))

      if 'in_reply_to_status_id' in data:
        status = Status.parse(self.api, json.loads(data))
        if self.on_status(status) is False:
          return False
      elif 'delete' in data:
        delete = json.loads(data)['delete']['status']
        if self.on_delete(delete['id'], delete['user_id']) is False:
          return False
      elif 'limit' in data:
        if self.on_limit(json.loads(data)['limit']['track']) is False:
          return False
      elif 'event' in data:
        if self.on_event(json.loads(data)) is False:
          return False

    def on_event(self, event):
      if event['event'] == "follow":
        self.bot.process_follow(User.parse(self.api, event['source']))
      elif event['event'] == "":
        pass

    @override
    def on_status(self, status):
      status.created_at += timedelta(hours = 9)
      self.bot.process_status(status)

  def __init__(self, auth):
    self.api         = tweepy.API(auth_handler = auth)
    self._stream_api = tweepy.Stream(
            auth, TwitterBot._Listener(self, self.api),
            secure = True)
    self._auth       = auth

    # add timer event
    self._prev = datetime.now()
    t = Timer(1.0, self._timer_handler)
    t.setDaemon(True)
    t.start()

  def par_second_event(self):
    """
    Callback method to overide.
    Called every second (xx:xx:00).
    """
    pass

  def par_minute_event(self):
    """
    Callback method to overide.
    Called every minute (xx:00:00).
    """
    pass

  def par_hour_event(self):
    """
    Callback method to overide.
    Called every hour (00:00:00).
    """
    pass

  def _timer_event(self):
    """
    Call corresponding methods every second, minute, hour.
    - par_second_event
    - par_minute_event
    - par_hour_event
    """
    def daemonRun(f):
      t = Thread(target = f)
      t.setDaemon(True)
      t.start()

    now = datetime.now()

    if self._prev.second != now.second:
      daemonRun(self.par_second_event)

      if self._prev.minute != now.minute:
        daemonRun(self.par_minute_event)

        if self._prev.hour != now.hour:
          daemonRun(self.par_hour_event)

    self._prev = now

  def _timer_handler(self):
    self._timer_event()
    t = Timer(0.1, self._timer_handler)
    t.setDaemon(True)
    t.start()

  def run(self):
    """
    Start bot system (not asynchronous).
    """
    try:
      self._stream_api.userstream()
    except KeyboardInterrupt:
      pass

  def process_status(self, status):
    """
    Callback method to overide.
    process status.
    """
    print(u"{text}".format(text=status.text))
    print(u"{name}({screen}) {created} via {src}\n".format(
        name=status.author.name, screen=status.author.screen_name,
        created=status.created_at, src=status.source))

  def process_follow(self, user):
    pass
