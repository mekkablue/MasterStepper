# encoding: utf-8

###########################################################################################################
#
#
#	Palette Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *

@objc.python_method
def showAllMastersOfGlyphInCurrentTab( thisGlyphName ):
	thisFont = Glyphs.font
	thisGlyph = thisFont.glyphs[thisGlyphName]
	if thisGlyph:
		thisTab = thisFont.currentTab
		if not thisTab:
			thisTab = thisFont.newTab()
		
		thisTab.layers = [l for l in thisGlyph.layers if l.isMasterLayer or l.isSpecialLayer]
		# thisTab.textCursor = 0
		thisTab.textRange = 0

@objc.python_method
def showAllMastersOfGlyphs( glyphNames, openNewTab=True, avoidDuplicates=True ):
	if avoidDuplicates:
		glyphNamesSet = []
		[glyphNamesSet.append(g) for g in glyphNames if not g in glyphNamesSet]
		glyphNames = glyphNamesSet
	
	thisFont = Glyphs.font
	thisTab = thisFont.currentTab
	if openNewTab or not thisTab:
		thisTab = thisFont.newTab()
	thisTab.textRange = 0
	
	displayLayers = []
	for thisGlyphName in glyphNames:
		thisGlyph = thisFont.glyphs[thisGlyphName]
		if thisGlyph:
			displayLayers += [l for l in thisGlyph.layers if l.isMasterLayer or l.isSpecialLayer]
			displayLayers.append(GSControlLayer.newline())
	
	if len(displayLayers) > 1:
		displayLayers.pop(-1) # remove last newline
	
	thisTab.layers = displayLayers

@objc.python_method
def glyphNameForIndexOffset( indexOffset ):
	thisFont = Glyphs.font # frontmost font
	currentLayer = thisFont.selectedLayers[0]
	currentGlyph = currentLayer.parent
	glyphIndex = currentGlyph.glyphId()

	# open a new tab with the current glyph if opened from Font tab:
	if thisFont.currentTab:
		glyphIndex += indexOffset
	
	thisGlyph = thisFont.glyphs[ glyphIndex % len(thisFont.glyphs) ]
	if thisGlyph:
		return thisGlyph.name
	else:
		return None

class MasterStepper (PalettePlugin):
	dialog = objc.IBOutlet()
	forwardField = objc.IBOutlet()
	backwardField = objc.IBOutlet()

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({
			'en': 'Master Stepper',
			})
		
		# Load .nib dialog (without .extension)
		self.loadNib('IBdialog', __file__)

	# @objc.python_method
	# def start(self):
	# 	# Adding a callback for the 'GSUpdateInterface' event
	# 	Glyphs.addCallback(self.update, UPDATEINTERFACE)
	#
	# @objc.python_method
	# def __del__(self):
	# 	Glyphs.removeCallback(self.update)

	@objc.IBAction
	def stepGlyphs_(self, sender=None):
		if sender == self.forwardField:
			move = 1
		elif sender == self.backwardField:
			move = -1
		newGlyphName = glyphNameForIndexOffset(move)
		if newGlyphName:
			showAllMastersOfGlyphInCurrentTab( newGlyphName )

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
