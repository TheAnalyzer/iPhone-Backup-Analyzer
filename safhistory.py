#!/usr/bin/env python

'''
 Analyzer for iPhone backup made by Apple iTunes

 (C)opyright 2011 Mario Piccinelli <mario.piccinelli@gmail.com>
 Released under MIT licence

 safhistory.py provides the code to show a TK window to browse through
 the binary PLIST file which holds the Safari history data in the iPhone Backup.

'''

# IMPORTS -----------------------------------------------------------------------------------------

from Tkinter import *
import sqlite3
import ttk
from datetime import datetime
import os
from string import *
from PIL import Image, ImageTk
import StringIO
import webbrowser

# GLOBALS -----------------------------------------------------------------------------------------

historytree = None
historywindow = None
filename = ""
titlefootertext = None
urlfootertext = None

# Called when the user clicks on the main tree list -----------------------------------------------

def OnClick(event):
	global historytree
	global titlefootertext, urlfootertext
	
	if (len(historytree.selection()) == 0): return;
	
	nodetitle = historytree.set(historytree.selection(), "title")
	titlefootertext.set(nodetitle)

	nodeurl = historytree.set(historytree.selection(), "url")
	nodeurlmaxlen = 100
	if (len(nodeurl) > nodeurlmaxlen):
		nodeurl = "%s [...]"%nodeurl[0:nodeurlmaxlen]
	urlfootertext.set(nodeurl)

# Called when the user double clicks on the main tree list -------------------------------------

def OnDoubleClick(event):
	global historytree
	global titlefootertext, urlfootertext
	
	if (len(historytree.selection()) == 0): return;

	nodeurl = historytree.set(historytree.selection(), "url")
	webbrowser.open(nodeurl)

# MAIN FUNCTION --------------------------------------------------------------------------------
	
def history_window(filenamenew):
	global filename
	global historytree, textarea, historywindow
	global titlefootertext, urlfootertext
	
	filename = filenamenew
	
	#print("Filename: %s"%filename)
	
	if (not os.path.isfile(filename)):
		print("Invalid file name for Safari History database: %s"%filename)
		return
	
	# main window
	historywindow = Toplevel()
	historywindow.title('Safari History data')
	historywindow.focus_set()
	
	historywindow.grid_columnconfigure(0, weight=1)
	historywindow.grid_rowconfigure(1, weight=1)
	
	# header label
	contactstitle = Label(historywindow, text = "Safari History data from: " + filename, relief = RIDGE)
	contactstitle.grid(column = 0, row = 0, sticky="ew", padx=5, pady=5)

	# convert binary plist file into plain plist file
	history_tempfile = os.path.dirname(sys.argv[0]) + "/out.plist" #default name from perl script plutil.pl
	command = "perl \"" + os.path.dirname(sys.argv[0]) + "/plutil.pl\" \"%s\" "%filename
	os.system(command)
	
	# import main xml data from output file
	from xml.dom.minidom import parse
	historyxml = parse(history_tempfile)
	os.remove(history_tempfile)
	
	# main dictionary (contains anything else)
	maindicts = historyxml.getElementsByTagName('dict')
	if (len(maindicts) <= 0): 
		print("no main dict found in file")
		return
	maindict = maindicts[0]
	
	# reads a DICT node and returns a python dictionary with key-value pairs
	def readDict(dictNode):
		ritorno = {}
		
		# check if it really is a dict node
		if (dictNode.localName != "dict"):
			print("Node under test is not a dict (it is more likely a \"%s\")."%node.localName)
			return ritorno
		
		nodeKey = None
		for node in dictNode.childNodes:
			if (node.nodeType == node.TEXT_NODE): continue
			
			if (nodeKey == None):
				nodeKeyElement = node.firstChild
				if (nodeKeyElement == None):
					nodeKey = "-"
				else:
					nodeKey = node.firstChild.toxml()
			else:
				ritorno[nodeKey] = node
				nodeKey = None
		
		return ritorno

	# reads an ARRAY node and returns a python list with elements
	def readArray(arrayNode):
		ritorno = []
		
		# check if it really is a dict node
		if (arrayNode.localName != "array"):
			print("Node under test is not an array (it is more likely a \"%s\")."%node.localName)
			return ritorno
		
		for node in arrayNode.childNodes:
			if (node.nodeType == node.TEXT_NODE): continue
			ritorno.append(node)
		
		return ritorno

	outerDict = readDict(maindict)
	bookmarksArray = readArray(outerDict['WebHistoryDates'])
	
	bookmarks = []
	
	for element in bookmarksArray:
		
		bookmark = {}
		
		elementDict = readDict(element)
		
		bookmark['title'] = ""
		if ('title' in elementDict.keys()):
			bookmark['title'] = elementDict['title'].firstChild.toxml()
		
		bookmark['url'] = ""
		if ('-' in elementDict.keys()):
			bookmark['url'] = elementDict['-'].firstChild.toxml()
		
		bookmark['date'] = ""
		if ('lastVisitedDate' in elementDict.keys()):
			bookmark['date'] = elementDict['lastVisitedDate'].firstChild.toxml()
		
		bookmarks.append(bookmark)

	# tree
	historytree = ttk.Treeview(historywindow, columns=("title", "url"),
	    displaycolumns=("title", "url"))
	
	historytree.heading("#0", text="Date", anchor='w')
	historytree.heading("title", text="Title", anchor='w')
	historytree.heading("url", text="Url", anchor='w')
	
	historytree.column("#0", width=25)
	historytree.column("title", width=250)
	historytree.column("url", width=300)	
	
	historytree.grid(column = 0, row = 1, sticky="ewns")
	
	# details box
	detailsbox = Frame(historywindow, bd=2, relief=RAISED);
	detailsbox.grid(column = 0, row = 2, sticky="ew", padx=5, pady=5)
	detailsbox.grid_columnconfigure(1, weight=1)
	
	titlefooterlabel = Label(detailsbox, text = 'Title:', relief = RIDGE, width=10)
	titlefooterlabel.grid(column = 0, row = 0, sticky="ew", padx=2, pady=2)	
	titlefootertext = StringVar()
	titlefooter = Label(detailsbox, textvariable = titlefootertext, relief = RIDGE, anchor = 'w')
	titlefooter.grid(column = 1, row = 0, sticky="ew", padx=2, pady=2)
	titlefootertext.set("mille")

	urlfooterlabel = Label(detailsbox, text = 'URL:', relief = RIDGE, width=10)
	urlfooterlabel.grid(column = 0, row = 1, sticky="ew", padx=2, pady=2)	
	urlfootertext = StringVar()
	urlfooter = Label(detailsbox, textvariable = urlfootertext, relief = RIDGE, anchor = 'w')
	urlfooter.grid(column = 1, row = 1, sticky="ew", padx=2, pady=2)
	urlfootertext.set("mille")
		
	# footer label
	footerlabel = StringVar()
	contactsfooter = Label(historywindow, textvariable = footerlabel, relief = RIDGE)
	contactsfooter.grid(column = 0, row = 3, sticky="ew", padx=5, pady=5)
	
	# destroy window when closed
	historywindow.protocol("WM_DELETE_WINDOW", historywindow.destroy)

	# footer statistics
	footerlabel.set("Found %s Safari history records"%(len(bookmarks)))
	
	# populating bookmarks tree	
	for bookmark in bookmarks:
		timestamp = float(bookmark['date']) + 978307200 #JAN 1 1970
		convtimestamp = datetime.fromtimestamp(int(timestamp))
		historytree.insert(
			'',
			'end',
			text = convtimestamp,
			values = (
				bookmark['title'],
				bookmark['url']
			)
		)
	
	historytree.bind("<ButtonRelease-1>", OnClick)
	historytree.bind("<Double-Button-1>", OnDoubleClick)