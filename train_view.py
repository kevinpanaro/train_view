import re
from os import path, pardir, walk, remove, mkdir
import json
import requests
from lxml import html
from datetime import datetime
import urllib2
import httplib
import urllib

TRAIN_DIR_NAME = "live_trains"
TRAINS_USER_JSON_NAME = "trains.json"
TRAIN_VIEW_JSON = "http://www3.septa.org/hackathon/TrainView/"
TRAIN_SCHEDULE_JSON = "http://www3.septa.org/hackathon/RRSchedules/"
PUSHOVER_CREDS = "pushover_creds.json"

HOME = path.abspath(path.join(__file__, pardir))
TRAINS_USER_JSON = path.join(HOME, TRAINS_USER_JSON_NAME)
TRAIN_DIR = path.join(HOME, TRAIN_DIR_NAME)

def trains_json(user_data = TRAINS_USER_JSON):
  '''Opens and returns user config file'''
  with open(user_data, 'r') as user_json:
    return json.loads(user_json.read())['train']

def get_train_view(site = TRAIN_VIEW_JSON):
  return json.load(urllib2.urlopen(site))

def get_train_schedule(train, site = TRAIN_SCHEDULE_JSON):
  return json.load(urllib2.urlopen(site + train))

def get_pushover_creds(creds = PUSHOVER_CREDS):
  with open(creds, 'r+') as user_creds:
    return json.loads(user_creds.read())

def train_has_come(time):
  '''returns true if the train has come
  if somehow you keep getting messages after 
  the train has already come check here first.'''
  try:
    train_time = datetime.strptime(time, '%I:%M %p').time()

    if datetime.now().time() > train_time:
      return True

    else:
      return False

  except:
    print "check train time format"
    return False

def get_user_trains(my_trains = trains_json()):
  '''reads users config file (trains.json) and returns 
  a list of the trains that are currently being "watched"
  also removes any folder in the live_trains directory 
  that should not be there, no internet is needed here.'''
  user_trains = []
  now = datetime.now().time()

  if TRAIN_DIR not in walk(HOME): # make directory in home folder if doesn't exist
    try:
      mkdir(TRAIN_DIR)

    except OSError:
      pass

  for train in my_trains:
    train_txt = train['number']
    train_txt_location = path.join(TRAIN_DIR, train_txt)
    start, end = train['times']

    if datetime.strptime(start, '%H:%M').time() < now and datetime.strptime(end, '%H:%M').time() > now:
      user_trains.append(train)

    else:
      for _, _, train_files in walk(TRAIN_DIR):
        if train_txt in train_files:
          remove(train_txt_location)

  return user_trains


def get_live_trains(train_view = get_train_view(), user_trains = get_user_trains()):
  '''Gets live train view data, and user data
  parses the live train data given the user data,
  returns clean list of dicts of trains and their data'''
  live_trains = []
  for user_train in user_trains:
    for train in train_view:

      if user_train['number'] == train['trainno']:
        live_trains.append({"train_number":   train['trainno'],
                            "train_dest":     train['dest'],
                            "train_late":     train['late'],
                            "train_nextstop": train['nextstop'],
                            "train_source":   train['SOURCE'],
                            "user_notify_start":  user_train['times'][0],
                            "user_notify_stop":   user_train['times'][1],
                            "user_start":         user_train['start'],
                            "user_stop":          user_train['stop'],
                            "user_friendly_name": user_train['friendly_name']})

  return live_trains


def get_status_2(live_trains = get_live_trains()):
  pass

def get_status(live_trains = get_live_trains()):
  '''Takes clean parsed train list
  creates a directoy for a live train
  returns list of dicts of whether or not the train status changed'''
  update_status = {}
  live_trains_update = []
  for train in live_trains:
    train_number_txt = train["train_number"]
    train_lateness = path.join(TRAIN_DIR, train_number_txt)

    for _, _, train_files in walk(TRAIN_DIR):

      if train_number_txt not in train_files:

        with open(train_lateness,'w') as train_txt:
          train_txt.write(str(train['train_late']))
          update_status = {'train_update': True}

      elif train_number_txt in train_files:

        with open(train_lateness, 'r+') as train_txt:
          train_previous_late = train_txt.readline()

          if str(train_previous_late) != str(train['train_late']):
            train_txt.seek(0)
            train_txt.truncate()
            train_txt.write(str(train['train_late']))
            update_status = {'train_update': True}

          else:
            update_status = {'train_update': False}

      train.update(update_status)
      live_trains_update.append(train)

  return live_trains_update

def create_message(status = get_status()):
  '''creates string to be pushed to device'''
  updated_trains = []

  for train_status in status:
    live_train_data = get_train_schedule(train_status['train_number'])
    train_lateness = path.join(TRAIN_DIR, train_status['train_number'])

    if train_status['train_update']:
      for stops in live_train_data:
        if stops['station'] == train_status['user_start']:
          depart = stops['est_tm']

          if train_has_come(stops['est_tm']): # train already came
            changing_eta = get_changing_eta()
            try:
              for updated_train in changing_eta:
                updated_trains.append(updated_train)
            except Exception as e:
              print e

        elif stops['station'] == train_status['user_stop']:
          arrive = stops['est_tm']

      updated_train = "\nLateness: %s min late\nDepart:\t %s @ %s\nArrive:\t %s @ %s" % (train_status['train_late'], train_status['user_start'], depart, train_status['user_stop'], arrive)
      updated_trains.append(updated_train)

  return updated_trains if len(updated_trains) != 0 else None

def get_changing_eta(status = get_status()):
  updated_trains = []

  for train_status in status:
    live_train_data = get_train_schedule(train_status['train_number'])
    train_lateness = path.join(TRAIN_DIR, train_status['train_number'])

    for stops in live_train_data:
      if stops['station'] == train_status['user_stop']:
        with open(train_lateness, 'r+') as train_txt:
          try:
            if train_has_come(stops['est_tm']): # train already reached destination
              return 

            elif datetime.strptime(train_txt.readline(), '%I:%M %p').time() != datetime.strptime(stops['est_tm']):
              updated_trains.append("\nNew Arrival Time: %s @ %s" % (stops['station'], stops['est_tm']))

          except Exception as e:
            print e

          finally:
            train_txt.seek(0)
            train_txt.truncate()
            train_txt.write(str(stops['train_late']))

  return updated_trains if len(updated_trains) != 0 else None

def pprint(data = create_message()):
  try:
    for item in data:
      print item
  except TypeError:
    return

def soft_reset():
  pass

pprint()

def notify_iphone(data = create_message()):
  try:
    for message in data:
      conn = httplib.HTTPSConnection("api.pushover.net:443")
      conn.request("POST", "/1/messages.json",
        urllib.urlencode({
          "token": get_pushover_creds()['token'],
          "user": get_pushover_creds()['user'],
          "message": message,
        }), { "Content-type": "application/x-www-form-urlencoded" })
      conn.getresponse()

  except Exception as e:
    print e

# notify_iphone()