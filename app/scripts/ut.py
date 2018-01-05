#from timeparsing import timestr_to_minutes, minutes_to_timestr, mins_to_time
#from intersections import intersection_minutes, total_free_time
import timeparsing as TP
import intersections as IN
#from pympler import tracker
#tr = tracker.SummaryTracker()

import random

#tr.print_diff()


MAX_USERS = 2
MAX_INTERVALS = 1
MAX_RANGE_MINUTES = 10079

daymins = {'Monday':0, 'Tuesday':1440, 'Wednesday':2280, 'Thursday':4320, 'Friday':5760, 'Saturday':7200, 'Sunday':8640}
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

class I:
	def __init__(self, sd='Monday', st='12:00am', ed='Monday', et='12:01am'):
		self.sd = sd
		self.st = st
		self.ed = ed
		self.et = et

	def __repr__(self):
		return "({}, {}, {}, {})".format(self.sd, self.st, self.ed, self.et)

	def tuprepr(self):
		return (self.sd, self.st, self.ed, self.et)

class U:
	def __init__(self):
		self.num_intervals = 0
		self.intervals = []

	def __repr__(self):
		return "{} intervals: {}".format(self.num_intervals, self.intervals)

def ut_users():
	users = []
	if MAX_USERS < 2:
		return users
	for u in range(random.randint(2, MAX_USERS)):
		temp = U()
		temp.num_intervals = random.randint(1, MAX_INTERVALS)
		for i in range(temp.num_intervals):
			sd = random.choice(days)
			st = daymins[sd]
			st = random.randint(st, st+1439)
			duration = random.randint(1, MAX_RANGE_MINUTES)
			et = st + duration
			ed = days[(et / 1440) % 7]
			(sd, st), (ed, et) = TP.mins_to_time(st), TP.mins_to_time(et)
			x = I(sd, st, ed, et)
			temp.intervals.append(x.tuprepr())
		users.append(temp)

	return users

#	curr_best = (None, None, 0)

#	random.shuffle(users)
#	me = users.pop()
#	my_times = TP.timestr_to_minutes(me.intervals)
#	for u in users:
#		x = my_times
#		your_times = TP.timestr_to_minutes(u.intervals)
#		inter_mins = IN.intersection_minutes(x, your_times)
#		total = IN.total_free_time(inter_mins)
#		if total > curr_best[2]:
#			curr_best = (u, inter_mins, total)
#
#	if curr_best[0]:
#		return curr_best[2], TP.minutes_to_timestr(curr_best[1])
#	return False

#tr.print_diff()



