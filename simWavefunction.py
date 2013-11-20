#!python
# -*- coding: utf-8 -*-
# filename : simWavefunction
# by SUNORU
import numpy as np
from numpy import *
import matplotlib.pyplot as plt

from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.mayavi.tools.mlab_scene_model import MlabSceneModel
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene

import threading
import os

orbitals={}
a0=0.529#e-11
orbitals['1s']="exp(-r/a0)"
orbitals['2s']="(2-r/a0)*exp(-r/(2*a0))"
orbitals['2pz']="r*exp(-r/(2*a0))*cos(theta)"
orbitals['2px']="r*exp(-r/(2*a0))*sin(theta)*cos(phi)"
orbitals['2py']="r*exp(-r/(2*a0))*sin(theta)*sin(phi)"
orbitals['3s']="(3-2*r/a0+2*r**2/(9*a0**2))*exp(-r/(3*a0))"
orbitals['3pz']="(2-r/(3*a0))*r*exp(-r/(3*a0))*cos(theta)"
orbitals['3px']="(2-r/(3*a0))*r*exp(-r/(3*a0))*sin(theta)*cos(phi)"
orbitals['3py']="(2-r/(3*a0))*r*exp(-r/(3*a0))*sin(theta)*sin(phi)"
orbitals['3d(z^2)']="(r**2)*exp(-r/(3*a0))*(3*cos(theta)**2-1)"
orbitals['3d(zx)']="(r**2)*exp(-r/(3*a0))*sin(theta)*cos(theta)*cos(phi)"
orbitals['3d(yz)']="(r**2)*exp(-r/(3*a0))*sin(theta)*cos(theta)*sin(phi)"
orbitals['3d(x^2-y^2)']="(r**2)*exp(-r/(3*a0))*sin(2*theta)*cos(2*phi)"
orbitals['3d(xy)']="(r**2)*exp(-r/(3*a0))*sin(2*theta)*sin(2*phi)"
orbitals['4f(z^3)']="r**3*exp(-r/(2*a0))*(5*cos(theta)**2-3*cos(theta))"
xd=list(orbitals.keys())
xd.sort()

class Debugger(threading.Thread):
	def run(self):
		while True:
			exec(raw_input())

class FieldViewer(HasTraits):
	"""三维标量场观察器"""

	orbi = Enum(xd)
	x0, x1 = Float(-1), Float(1)
	y0, y1 = Float(-1), Float(1)
	z0, z1 = Float(-1), Float(1)
	contours=Int(8)
	points = Int(100)
	autocontour = Bool(False)
	iabs = Bool(False)
	v0, v1 = Float(0.0), Float(1.0)
	contour = Range("v0", "v1", 0.2)
	function = orbitals["1ss"]
	# 标量场函数
	plotbutton = Button(u"描画")
	scene = Instance(MlabSceneModel, ())
	view = View(
		HSplit(
			VGroup(
				"contours",
				Item('autocontour', label=u"自动等值"),
				Item('iabs', label=u"取绝对值"),
				Item('orbi', label=u"值"),
				Item('plotbutton', show_label=False),
			),
		VGroup(
			Item(name='scene',
				editor=SceneEditor(scene_class=MayaviScene),
				resizable=True,
				height=300,
				width=350
			),
			Item('contour',
				editor=RangeEditor(format="%1.5f",
					low_name="v0", high_name="v1")
				), show_labels=False
			)
		),
		width = 500, resizable=True,
		title=u"三维标量场观察器"
	)
	
	def _plotbutton_fired(self):
		self.plot()
		
	def _orbi_changed(self):
		print self.function
		self.function=orbitals[self.orbi]
		print self.function

	def _autocontour_changed(self):
		if hasattr(self, "g"):
			self.g.contour.auto_contours = self.autocontour
			if not self.autocontour:
				self._contour_changed()
				
	def _contour_changed(self):
		if hasattr(self, "g"):
			if not self.g.contour.auto_contours:
				self.g.contour.contours = [self.contour]
				
	def plot(self):
		x, y, z = mgrid[
			-15:15:1j*self.points,
			-15:15:1j*self.points,
			-15:15:1j*self.points]
		
		r = sqrt(x*x+y*y+z*z)
		theta = arccos(z/r)
		phi = arctan(y/x)
		
		if self.iabs:
			scalars = abs(eval(self.function))
		else:
			scalars = eval(self.function)
		
		self.scene.mlab.clf()
		g = self.scene.mlab.contour3d(x,y,z, scalars, contours=self.contours, transparent=True)
		g.contour.auto_contours = self.autocontour
		
		self.scene.mlab.axes()
		
		self.g = g
		self.scalars = scalars
		self.v0 = np.min(scalars)
		self.v1 = np.max(scalars)
		print self.v0,self.v1

#debugger=Debugger()
#debugger.start()

#x1 = linspace(-5, 5, 1000)
#y1=(sqrt(1/(pi*a0**3))*exp(-x1/a0))**2
#plt.plot(x1,y1,label="$sqrt(1/(pi*a0**3))*exp(-r/a0))**2$",color="red",linewidth=2)
#plt.legend()
#plt.show()


app = FieldViewer()
app.configure_traits()

