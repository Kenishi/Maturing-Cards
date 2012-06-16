"""
Name: Maturing Cards
Filename: Maturing Cards.py
Version: 0.2
Author: Kenishi
Desc:	Generates a new graph that shows the number of cards that are maturing in a time frame
		Support at http://forum.koohii.com/viewtopic.php?id=9495
"""

import anki
from anki.hooks import wrap, addHook

###Constants###
DEBUG = False
debugOut = None

# Graph Bar Color
reviewMatureC = "#72a5d9"

def log(str):
	##USAGE: Debug logging, make sure a <deck name>.media folder exists in deck's root directory for log to be created
	##RETURNS: Nothing
	global debugOut
	
	if DEBUG:
		if not debugOut:
			debugOut = open("""D:\mr_debug.txt""", mode="a")
		debugOut.write(repr(str))
		debugOut.close()


def maturingGraph(*args, **kwargs):
	self = args[0]
	old = kwargs['_old']  ### Reference back to cardGraph()
	
	if self.type == 0:
		days = 30; chunk = 1
	elif self.type == 1:
		days = 52; chunk = 7
	else:
		days = None; chunk = 30
	return old(self) + _plotMaturingGraph(self, _maturedCards(self,days,chunk),
							days,
							_("Maturing Cards"))

def _plotMaturingGraph(self,data, days, title):
	if not data:
		return ""
	max_yaxis=0
	for (x,y) in data: # Unzip the data
		if y > max_yaxis:
			test = int(round((float(y)/10))*10)
			if test < y:
				max_yaxis = test + 10
			else:
				max_yaxis = test
				
	txt = self._title(_("Maturing Cards"),
					  _("Number of cards matured."))
	txt += self._graph(id="maturing", data=[dict(data=data, color=reviewMatureC)], conf=dict(xaxis=dict(max=0.5),yaxis=dict(min=0,max=max_yaxis)))

	return txt

def _maturedCards(self, num=7, chunk=1):
	lims = []
	if num is not None:
		lims.append("id > %d" % (
			(self.col.sched.dayCutoff-(num*chunk*86400))*1000))
	lim = self._revlogLimit()
	if lim:
		lims.append(lim)
	if lims:
		lim = "where " + " and ".join(lims)
	else:
		lim = ""
	if self.type == 0:
		tf = 60.0 # minutes
	else:
		tf = 3600.0 # hours
	if lim:
		return self.col.db.all("""
SELECT
(CAST((id/1000 - :cut) / 86400.0 as int))/:chunk as day,
COUNT(*) as count
FROM revlog %s and ivl > 21 and lastIvl <= 21
GROUP BY day ORDER by day""" % lim, cut=self.col.sched.dayCutoff, tf=tf, chunk=chunk)
	else:
		return self.col.db.all("""
SELECT
(CAST((id/1000 - :cut) / 86400.0 as int))/:chunk as day,
COUNT(*) as count
FROM revlog %s WHERE ivl > 21 and lastIvl <= 21
GROUP BY day ORDER by day""" % lim, cut=self.col.sched.dayCutoff, tf=tf, chunk=chunk)

anki.stats.CollectionStats.cardGraph = wrap(anki.stats.CollectionStats.cardGraph, maturingGraph, pos="")	