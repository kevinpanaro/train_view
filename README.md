Septa Train View Notifier
=
*live update notifications send to you phone, run on a raspberry pi*

notifications are handled by [pushover](https://pushover.net/) which costs 5$ for 7500 notifications per month. (240-250 a day). You could probably set up twitter DMs, for free, or use pushbullet, but I liked pushover because it's pretty instant and reliable.

Home Assistant actually runs the script, as an automation, however there are plenty of ways to run a script on a raspberry pi. I just use HA so I decided it would be easier for me to do it that way.

TODO:
- Add ability to determine if you made the train (not sure how though, pushover does allow callbacks.)
- Add Next to Arrive notification, in case you miss your train (callbacks).
- Clean up code in general, add a soft reset that removes live_trains.
	- maybe add a live_trains directory cleaner (clean @ 3 AM)
- Add logging (oops)
- Clean trains.json to remove un-used items.

FILES:
- train\_view.py 				: main script. once the trains.json is setup with train number, notification times and pushove\_creds.
- trains.json 					: the config file. number is the train number, times is the start (first) and end (second) times you want to be notified about the trains, start and stop locations are self explanitory, friendly\_name and scheduled\_time are deprecated.
- pushover_creds.json.sample 	: token and user keys for pushover.
- station\_id\_name.csv 			: Station ID (not used) and Station Name (how Septa will post it in their API) for each station. You have to use this spelling for your start/stop locations. trainview.septa.org uses different conventions, so it's important to use these. (Chestnut HE => Chestnut Hill East)