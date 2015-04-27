**WARNING:** This is mayby the ugliest piece on software on planet eath. Maybe in the whole universe - but it does its job just fine!

----------

This script is used to sync two MPD instances. One is the master (music.bingo in our case) and one is the slave (basementvibes.bingo). A little switch, directly attached to the host which is running this script (a raspberry pi), is for toggeling between sync mode and manual mode.

 - Manual mode allows the user to add and play his own music on the slave MPD.
 - Sync mode plays the exact music, as the master MPD instance.
    - For this feature, the second MPD instance needs the same database as the master instance. To achieve this, we use a so called ["Satellite setup"](http://www.musicpd.org/doc/user/advanced_config.html#satellite).

There are several issues, that need to be fixed, to be not the uglies piece of software someone can imagine:

 1. Dynamic configuration
    - Custom address and port for the master instance.
    - Custom address and port for the slave instance (most of the time, it's localhost anyway).
 2. Eventbased
    - In an older version of this script, i've used the idle command of the MPDLib. Unfortunately this blocks an instant detection of the sync-switch.
    - Maybe there is a way to get a event from the gpio package if a gpio gets toggled?
    - An multithreaded implementation (one thread for mpd-idle and one for the gpio event) should solve this problem.
 3. Stability
    - There are quite a few cases in which this script can crash with funny error messages.
    - The current workaround is to restart it on every crash (take a look at mpdsync.service).
 4. Modularity
    - The switch condition for manual and sync mode should be a module or a function, which the user (you!) can change.
    - This way the switch could be a real switch, a webinterface, a TCP-package or whatever you can imagine/program.
