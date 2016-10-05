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
