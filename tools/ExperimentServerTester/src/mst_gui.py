# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Dec 17 2009)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.grid

###########################################################################
## Class MainFrameBase
###########################################################################

class MainFrameBase ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"WebLab-Deusto Experiment Server Tester", pos = wx.DefaultPosition, size = wx.Size( 611,507 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.Colour( 221, 232, 249 ) )
		
		mainBoxSizer = wx.BoxSizer( wx.VERTICAL )
		
		serverSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Server" ), wx.HORIZONTAL )
		
		self.mHostLabel = wx.StaticText( self, wx.ID_ANY, u"Host:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mHostLabel.Wrap( -1 )
		serverSizer.Add( self.mHostLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.mHostText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		serverSizer.Add( self.mHostText, 3, wx.ALL, 5 )
		
		self.mPortLabel = wx.StaticText( self, wx.ID_ANY, u"Port:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mPortLabel.Wrap( -1 )
		serverSizer.Add( self.mPortLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.mPortText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		serverSizer.Add( self.mPortText, 1, wx.ALL, 5 )
		
		self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"URI:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText10.Wrap( -1 )
		serverSizer.Add( self.m_staticText10, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.mUriText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		serverSizer.Add( self.mUriText, 0, wx.ALL, 5 )
		
		self.mConnectButton = wx.Button( self, wx.ID_ANY, u"Connect", wx.DefaultPosition, wx.DefaultSize, 0 )
		serverSizer.Add( self.mConnectButton, 0, wx.ALL, 5 )
		
		mainBoxSizer.Add( serverSizer, 0, wx.EXPAND, 5 )
		
		tabsSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.mNotebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mCommandsTab = wx.Panel( self.mNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.mCommandsTab.SetBackgroundColour( wx.Colour( 221, 254, 216 ) )
		
		commandsSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		mCmdOtherCtrlsSizer = wx.BoxSizer( wx.VERTICAL )
		
		bSizer15 = wx.BoxSizer( wx.VERTICAL )
		
		mCmdOtherCtrlsSizer.Add( bSizer15, 1, wx.EXPAND, 5 )
		
		mCmdsTabFileSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText6 = wx.StaticText( self.mCommandsTab, wx.ID_ANY, u"Content:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText6.Wrap( -1 )
		mCmdsTabFileSizer.Add( self.m_staticText6, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		bSizer18 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.mFilePickerPath = wx.TextCtrl( self.mCommandsTab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.mFilePickerPath, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.mFilePickerButton = wx.Button( self.mCommandsTab, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.mFilePickerButton, 1, wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mCmdsTabFileSizer.Add( bSizer18, 0, wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_staticText7 = wx.StaticText( self.mCommandsTab, wx.ID_ANY, u"FileInfo:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		mCmdsTabFileSizer.Add( self.m_staticText7, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.mFileInfoText = wx.TextCtrl( self.mCommandsTab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		mCmdsTabFileSizer.Add( self.mFileInfoText, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mCmdOtherCtrlsSizer.Add( mCmdsTabFileSizer, 1, wx.EXPAND|wx.ALL, 5 )
		
		mCmdsTabCommandSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.mCommandLabel = wx.StaticText( self.mCommandsTab, wx.ID_ANY, u"Command:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mCommandLabel.Wrap( -1 )
		mCmdsTabCommandSizer.Add( self.mCommandLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.mCommandText = wx.TextCtrl( self.mCommandsTab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		mCmdsTabCommandSizer.Add( self.mCommandText, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		mCmdOtherCtrlsSizer.Add( mCmdsTabCommandSizer, 1, wx.EXPAND|wx.ALL, 5 )
		
		bSizer16 = wx.BoxSizer( wx.VERTICAL )
		
		mCmdOtherCtrlsSizer.Add( bSizer16, 1, wx.EXPAND, 5 )
		
		commandsSizer.Add( mCmdOtherCtrlsSizer, 1, wx.EXPAND, 5 )
		
		mCmdButtonsSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.mStartExperimentButton = wx.Button( self.mCommandsTab, wx.ID_ANY, u"> start_experiment()", wx.DefaultPosition, wx.DefaultSize, 0 )
		mCmdButtonsSizer.Add( self.mStartExperimentButton, 1, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5 )
		
		self.mSendFileButton = wx.Button( self.mCommandsTab, wx.ID_ANY, u"> send_file()", wx.DefaultPosition, wx.DefaultSize, 0 )
		mCmdButtonsSizer.Add( self.mSendFileButton, 1, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5 )
		
		self.mSendCommand = wx.Button( self.mCommandsTab, wx.ID_ANY, u"> send_command()", wx.DefaultPosition, wx.DefaultSize, 0 )
		mCmdButtonsSizer.Add( self.mSendCommand, 1, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5 )
		
		self.mDisposeButton = wx.Button( self.mCommandsTab, wx.ID_ANY, u"> dispose()", wx.DefaultPosition, wx.DefaultSize, 0 )
		mCmdButtonsSizer.Add( self.mDisposeButton, 1, wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, 5 )
		
		commandsSizer.Add( mCmdButtonsSizer, 0, wx.EXPAND, 5 )
		
		self.mCommandsTab.SetSizer( commandsSizer )
		self.mCommandsTab.Layout()
		commandsSizer.Fit( self.mCommandsTab )
		self.mNotebook.AddPage( self.mCommandsTab, u"Commands", False )
		self.mScriptsTab = wx.Panel( self.mNotebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.mScriptsTab.SetBackgroundColour( wx.Colour( 221, 254, 216 ) )
		
		scriptsSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.mScriptLabel = wx.StaticText( self.mScriptsTab, wx.ID_ANY, u"Script:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mScriptLabel.Wrap( -1 )
		scriptsSizer.Add( self.mScriptLabel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		bSizer181 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.mScriptPickerPath = wx.TextCtrl( self.mScriptsTab, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer181.Add( self.mScriptPickerPath, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
		
		self.mScriptPickerButton = wx.Button( self.mScriptsTab, wx.ID_ANY, u"...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer181.Add( self.mScriptPickerButton, 1, wx.ALIGN_CENTER_VERTICAL, 5 )
		
		scriptsSizer.Add( bSizer181, 1, wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.mRunScriptButton = wx.Button( self.mScriptsTab, wx.ID_ANY, u"Run Script", wx.DefaultPosition, wx.DefaultSize, 0 )
		scriptsSizer.Add( self.mRunScriptButton, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.mScriptsTab.SetSizer( scriptsSizer )
		self.mScriptsTab.Layout()
		scriptsSizer.Fit( self.mScriptsTab )
		self.mNotebook.AddPage( self.mScriptsTab, u"Scripts", True )
		
		tabsSizer.Add( self.mNotebook, 1, wx.EXPAND |wx.ALL, 5 )
		
		mainBoxSizer.Add( tabsSizer, 1, wx.EXPAND, 5 )
		
		logSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.mLogGrid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.mLogGrid.CreateGrid( 0, 2 )
		self.mLogGrid.EnableEditing( False )
		self.mLogGrid.EnableGridLines( True )
		self.mLogGrid.EnableDragGridSize( False )
		self.mLogGrid.SetMargins( 0, 0 )
		
		# Columns
		self.mLogGrid.SetColSize( 0, 80 )
		self.mLogGrid.SetColSize( 1, 80 )
		self.mLogGrid.EnableDragColMove( False )
		self.mLogGrid.EnableDragColSize( False )
		self.mLogGrid.SetColLabelSize( 30 )
		self.mLogGrid.SetColLabelValue( 0, u"Sent" )
		self.mLogGrid.SetColLabelValue( 1, u"Received" )
		self.mLogGrid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.mLogGrid.EnableDragRowSize( False )
		self.mLogGrid.SetRowLabelSize( 80 )
		self.mLogGrid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.mLogGrid.SetDefaultCellBackgroundColour( wx.Colour( 255, 255, 221 ) )
		self.mLogGrid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		logSizer.Add( self.mLogGrid, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		mainBoxSizer.Add( logSizer, 1, wx.EXPAND, 5 )
		
		buttonsSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.mCleanLogButton = wx.Button( self, wx.ID_ANY, u"Clean Log", wx.DefaultPosition, wx.DefaultSize, 0 )
		buttonsSizer.Add( self.mCleanLogButton, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
		
		mainBoxSizer.Add( buttonsSizer, 0, wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_RIGHT, 5 )
		
		self.SetSizer( mainBoxSizer )
		self.Layout()
		self.mStatusBar = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		
		# Connect Events
		self.Bind( wx.EVT_ACTIVATE, self.OnActivate )
		self.Bind( wx.EVT_ACTIVATE_APP, self.OnActivateApp )
		self.Bind( wx.EVT_CLOSE, self.OnClose )
		self.Bind( wx.EVT_ENTER_WINDOW, self.OnEnterWindow )
		self.Bind( wx.EVT_ICONIZE, self.OnIconize )
		self.Bind( wx.EVT_IDLE, self.OnIdle )
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		self.mHostText.Bind( wx.EVT_TEXT, self.OnHostText )
		self.mHostText.Bind( wx.EVT_TEXT_ENTER, self.OnHostTextEnter )
		self.mPortText.Bind( wx.EVT_CHAR, self.OnPortChar )
		self.mPortText.Bind( wx.EVT_TEXT, self.OnPortText )
		self.mPortText.Bind( wx.EVT_TEXT_ENTER, self.OnPortTextEnter )
		self.mConnectButton.Bind( wx.EVT_BUTTON, self.OnConnect )
		self.mFilePickerButton.Bind( wx.EVT_BUTTON, self.OnFilePickerButtonClicked )
		self.mFileInfoText.Bind( wx.EVT_TEXT, self.OnFileInfoText )
		self.mFileInfoText.Bind( wx.EVT_TEXT_ENTER, self.OnFileInfoTextEnter )
		self.mCommandText.Bind( wx.EVT_TEXT, self.OnCommandText )
		self.mCommandText.Bind( wx.EVT_TEXT_ENTER, self.OnCommandTextEnter )
		self.mStartExperimentButton.Bind( wx.EVT_BUTTON, self.OnStartExperiment )
		self.mSendFileButton.Bind( wx.EVT_BUTTON, self.OnSendFile )
		self.mSendCommand.Bind( wx.EVT_BUTTON, self.OnSendCommand )
		self.mDisposeButton.Bind( wx.EVT_BUTTON, self.OnDispose )
		self.mScriptPickerButton.Bind( wx.EVT_BUTTON, self.OnScriptPickerButtonClicked )
		self.mRunScriptButton.Bind( wx.EVT_BUTTON, self.OnRunScript )
		self.mLogGrid.Bind( wx.grid.EVT_GRID_CELL_CHANGE, self.OnLogCellChange )
		self.mLogGrid.Bind( wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnLogCellLeftClick )
		self.mLogGrid.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnLogCellRightClick )
		self.mLogGrid.Bind( wx.grid.EVT_GRID_SELECT_CELL, self.OnLogSelectCell )
		self.mLogGrid.Bind( wx.EVT_KILL_FOCUS, self.OnLogKillFocus )
		self.mLogGrid.Bind( wx.EVT_PAINT, self.OnLogPaint )
		self.mLogGrid.Bind( wx.EVT_SET_FOCUS, self.OnLogSetFocus )
		self.mLogGrid.Bind( wx.EVT_SIZE, self.OnLogSize )
		self.mLogGrid.Bind( wx.EVT_UPDATE_UI, self.OnLogUpdateUI )
		self.mCleanLogButton.Bind( wx.EVT_BUTTON, self.OnCleanLog )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnActivate( self, event ):
		event.Skip()
	
	def OnActivateApp( self, event ):
		event.Skip()
	
	def OnClose( self, event ):
		event.Skip()
	
	def OnEnterWindow( self, event ):
		event.Skip()
	
	def OnIconize( self, event ):
		event.Skip()
	
	def OnIdle( self, event ):
		event.Skip()
	
	def OnPaint( self, event ):
		event.Skip()
	
	def OnHostText( self, event ):
		event.Skip()
	
	def OnHostTextEnter( self, event ):
		event.Skip()
	
	def OnPortChar( self, event ):
		event.Skip()
	
	def OnPortText( self, event ):
		event.Skip()
	
	def OnPortTextEnter( self, event ):
		event.Skip()
	
	def OnConnect( self, event ):
		event.Skip()
	
	def OnFilePickerButtonClicked( self, event ):
		event.Skip()
	
	def OnFileInfoText( self, event ):
		event.Skip()
	
	def OnFileInfoTextEnter( self, event ):
		event.Skip()
	
	def OnCommandText( self, event ):
		event.Skip()
	
	def OnCommandTextEnter( self, event ):
		event.Skip()
	
	def OnStartExperiment( self, event ):
		event.Skip()
	
	def OnSendFile( self, event ):
		event.Skip()
	
	def OnSendCommand( self, event ):
		event.Skip()
	
	def OnDispose( self, event ):
		event.Skip()
	
	def OnScriptPickerButtonClicked( self, event ):
		event.Skip()
	
	def OnRunScript( self, event ):
		event.Skip()
	
	def OnLogCellChange( self, event ):
		event.Skip()
	
	def OnLogCellLeftClick( self, event ):
		event.Skip()
	
	def OnLogCellRightClick( self, event ):
		event.Skip()
	
	def OnLogSelectCell( self, event ):
		event.Skip()
	
	def OnLogKillFocus( self, event ):
		event.Skip()
	
	def OnLogPaint( self, event ):
		event.Skip()
	
	def OnLogSetFocus( self, event ):
		event.Skip()
	
	def OnLogSize( self, event ):
		event.Skip()
	
	def OnLogUpdateUI( self, event ):
		event.Skip()
	
	def OnCleanLog( self, event ):
		event.Skip()
	

###########################################################################
## Class LogViewerBase
###########################################################################

class LogViewerBase ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Log Viewer", pos = wx.DefaultPosition, size = wx.Size( 400,500 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.RESIZE_BORDER )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.Colour( 216, 228, 248 ) )
		
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		
		bSizer16 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Time / Num:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		bSizer16.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		self.mTimeNumText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		self.mTimeNumText.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )
		
		bSizer16.Add( self.mTimeNumText, 0, wx.ALL|wx.EXPAND, 5 )
		
		mainSizer.Add( bSizer16, 0, wx.EXPAND, 5 )
		
		bSizer14 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Sent:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		bSizer14.Add( self.m_staticText7, 0, wx.ALL, 5 )
		
		self.mSentText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		self.mSentText.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )
		
		bSizer14.Add( self.mSentText, 1, wx.ALL|wx.EXPAND, 5 )
		
		mainSizer.Add( bSizer14, 1, wx.EXPAND, 5 )
		
		bSizer15 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Received:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		bSizer15.Add( self.m_staticText8, 0, wx.ALL, 5 )
		
		self.mReceivedText = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		self.mReceivedText.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )
		
		bSizer15.Add( self.mReceivedText, 1, wx.ALL|wx.EXPAND, 5 )
		
		mainSizer.Add( bSizer15, 1, wx.EXPAND, 5 )
		
		bSizer17 = wx.BoxSizer( wx.VERTICAL )
		
		self.mClose = wx.Button( self, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.mClose, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
		
		mainSizer.Add( bSizer17, 0, wx.EXPAND, 5 )
		
		self.SetSizer( mainSizer )
		self.Layout()
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.OnClose )
		self.mClose.Bind( wx.EVT_BUTTON, self.OnCloseClicked )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnClose( self, event ):
		event.Skip()
	
	def OnCloseClicked( self, event ):
		event.Skip()
	

