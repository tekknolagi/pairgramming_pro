# interface for parsing time strings into minutes from start of week
# also used for error checking interval form inputs

# this is not elegant or fast, but i think it works

# public list needed for various functions, i wish this language had const
days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

MINS_PER_HOUR = 60
MINS_PER_DAY = 1440
MINS_PER_WEEK = 10080
SUNDAY_MINUTES = 8640

HOURS_PER_DAY = 24
NOON = 12

assert(MINS_PER_HOUR * HOURS_PER_DAY == MINS_PER_DAY)

# possibly needs more error checking
# gets the 45 from '1:45am'
def parse_mins(s):
	after = s.split(':')[1]
	if len(after) != 4 and len(after) != 2:
		raise Exception('illformed time: bad minutes')
	mins = int((s.partition(':')[2])[:2])
	if mins >= MINS_PER_HOUR:
		raise Exception('too many minutes')
	elif mins < 0:
		raise Exception('negative minutes')
	else:
		return mins

# number of minutes that have elapsed since beginning of week until beginning of day d
def parse_day(d):
	if (d.lower()) in days:
		return (days.index(d.lower())) * MINS_PER_DAY
	else:
		raise Exception("not a day")

# takes time as string, returns hours in terms of minutes, 
# works for military or otherwise
def parse_hours(s):
	temp = (s.replace(' ','')).split(':')
	if len(temp) is not 2:
		raise Exception("illformed time: need exactly one ':'")
	hours = 0
	try:
		hours = int(temp[0])
	except Exception:
		raise Exception('illformed time: strange hours')
	mins, m = int(filter(lambda x: x.isdigit(), temp[-1])), filter(lambda x: not x.isdigit(), temp[-1])
	if hours > HOURS_PER_DAY:
		raise Exception('time > 24 hours')
	elif hours < HOURS_PER_DAY and hours > NOON:
		if m != "":
			raise Exception("'can't mix military time and am/pm")
		elif m != "pm" and m != "":
			raise Exception('extra characters')
	elif hours == HOURS_PER_DAY:
		hours = 0
	elif hours == NOON and m == "am":
		hours = 0
	elif hours < 0:
		raise Exception('negative time')
		#error_exit("negative time")
	elif m == "pm":
		if hours != NOON:
			hours += NOON
	hours *= MINS_PER_HOUR
	return hours

# jank helper function
def mins_to_time(n):
	m = "am"
	temp = int(n) % MINS_PER_WEEK
	dt = days[temp / MINS_PER_DAY]
	hours = temp % MINS_PER_DAY
	hours /= MINS_PER_HOUR
	if hours >= NOON:
		m = "pm"
	hours %= NOON
	if hours == 0:
		hours = NOON
	mins = temp % MINS_PER_HOUR
	mins = str(mins)
	if len(mins) == 1:
		mins = "0"+mins
	return (dt.title(), str(hours)+':'+mins+m)

# does the work of timestr_to_minutes
# could be public too tbh, this is useful
def to_min_interval(t):
	(ds, s, de, e) = t
	shour, ehour = parse_hours(s), parse_hours(e)
	sday, eday = parse_day(ds), parse_day(de)
	sm, em = parse_mins(s), parse_mins(e)
	sm, em = sm + shour + sday, em + ehour + eday

	if sday == 8640 and eday == 0:
		em += MINS_PER_WEEK

	diff = em - sm
	if diff is 0:
		raise Exception('intervals of length 0 not allowed, please remove from schedule')
	elif diff < 0:
		raise Exception('negative interval')

	return sm, em

# takes list of tuples (sd, st, ed, et)
def timestr_to_minutes(tx):
	return map(to_min_interval, tx)

# takes list of tuples (st, et) both in minutes from start of week
def minutes_to_timestr(l):
	unzipped = map(list, zip(*l))
	sx, ex = [], []
	if unzipped:
		sx, ex = unzipped[0], unzipped[-1]
	temp = zip(map(mins_to_time, sx), map(mins_to_time, ex))
	return map(lambda x: (x[0][0], x[0][1], x[1][0], x[1][1]), temp)
