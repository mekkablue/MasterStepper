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
from AppKit import NSEvent, NSNotFound, NSShiftKeyMask, NSAlternateKeyMask, NSControlKeyMask


@objc.python_method
def recalibrateViewPort(tab):
	# Algorithm by Tim Ahrens
	vp = tab.viewPort
	content = tab.bounds
	layer = tab.activeLayer()
	if layer:
		layerWidth = layer.width
	else:
		layerWidth = 100
	if vp.origin.x + vp.size.width < content.origin.x + content.size.width:
		vp.origin.x = tab.selectedLayerOrigin.x + 0.5 * (layerWidth * tab.scale - vp.size.width)
		tab.viewPort = vp

@objc.python_method
def activateLayer(offset=1, repeated=False):
	thisFont = Glyphs.font
	if thisFont:
		thisTab = thisFont.currentTab
		if thisTab:
			textLength = len([l for l in thisFont.currentTab.layers])
			thisTab.textCursor = (thisTab.textCursor + offset) % textLength
			if thisFont.selectedLayers: # avoid newline
				thisFont.tool = "SelectTool"
				recalibrateViewPort(thisTab)
			elif not repeated: # avoid endless loop
				activateLayer(offset=offset, repeated=True)
	
@objc.python_method
def showAllMastersOfGlyphInCurrentTab(thisGlyphName, withAccents=False):
	thisFont = Glyphs.font
	thisGlyph = thisFont.glyphs[thisGlyphName]
	if thisGlyph:
		thisTab = thisFont.currentTab
		if not thisTab:
			thisTab = thisFont.newTab()
		
		if not withAccents:
			thisTab.layers = [l for l in thisGlyph.layers if l.isMasterLayer or l.isSpecialLayer]
		else:
			tabLayers = []
			for layer in thisGlyph.layers:
				if layer.isMasterLayer:
					mID = layer.associatedMasterId
					tabLayers.append(layer)
					compositeGlyphs = thisFont.glyphsContainingComponentWithName_masterId_(thisGlyphName, mID)
					for compositeGlyph in compositeGlyphs:
						tabLayers.append(compositeGlyph.layers[mID])
				elif layer.isSpecialLayer:
					tabLayers.append(layer)
				tabLayers.append(GSControlLayer.newline())
			tabLayers.pop() # remove last newline
			thisTab.layers = tabLayers

		thisTab.textRange = 0
		if withAccents:
			thisTab.textCursor = 0
			thisFont.tool = "SelectTool"

@objc.python_method
def showAllMastersOfGlyphs(glyphNames, openNewTab=True, avoidDuplicates=True):
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
def nextGlyphFromFontView(offset=1):
	thisFont = Glyphs.font
	if thisFont.selectedLayers:
		activeGlyph = thisFont.selectedLayers[0].parent
		currentTab = thisFont.currentTab
		if not currentTab:
			currentTab = thisFont.newTab()
		controller = thisFont.currentTab.windowController()
		glyphsInFontView = controller.valueForKey_("glyphsController").arrangedObjects()
		idx = glyphsInFontView.indexOfObject_(activeGlyph)
		if idx < NSNotFound and 0 < idx + offset < glyphsInFontView.count():
			activeGlyph = glyphsInFontView[idx + offset]
			if activeGlyph:
				return activeGlyph.name
	return None

@objc.python_method
def glyphNameForIndexOffset(indexOffset):
	thisFont = Glyphs.font # frontmost font
	currentGlyph = thisFont.glyphs[0]
	currentTab = thisFont.currentTab
	if thisFont.selectedLayers:
		currentLayer = thisFont.selectedLayers[0]
		currentGlyph = currentLayer.parent
	elif currentTab and currentTab.layers and currentTab.layersCursor:
		currentLayer = currentTab.layers[currentTab.layersCursor-1]
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

	@objc.IBAction
	def stepGlyphs_(self, sender=None):
		if sender == self.forwardField:
			move = 1
		elif sender == self.backwardField:
			move = -1
		
		newGlyphName = None
		
		keysPressed = NSEvent.modifierFlags()
		ctrlKeyPressed = keysPressed & NSControlKeyMask == NSControlKeyMask
		shiftKeyPressed = keysPressed & NSShiftKeyMask == NSShiftKeyMask
		optionKeyPressed = keysPressed & NSAlternateKeyMask == NSAlternateKeyMask
		
		if ctrlKeyPressed:
			activateLayer(offset=move)
			return
		
		if shiftKeyPressed:
			newGlyphName = nextGlyphFromFontView(move)
		
		if not newGlyphName:
			newGlyphName = glyphNameForIndexOffset(move)

		if newGlyphName:
			showAllMastersOfGlyphInCurrentTab(newGlyphName, withAccents=optionKeyPressed)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
