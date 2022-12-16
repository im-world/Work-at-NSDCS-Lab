"""
This provides a set of useful generic types for the gdsMill interface. 
"""

import tech                           #process technology parameters
import debug                          #facilitates debugging 
from utils import snap_to_grid        #returns (x,y) coordinates to match grid settings

class geometry:
    """
    A specific path, shape, or text geometry. Base class for shared
    items.
    """
    def __init__(self):
        """ By default, everything has no size. """
        self.width = 0
        self.height = 0

    def __str__(self):
        """ override print function output """
        debug.error("__str__ must be overridden by all geometry types.",1)

    def __repr__(self):
        """ override print function output """
        debug.error("__repr__ must be overridden by all geometry types.",1)


class instance(geometry):
    """
    An instance of an instance/module with a specified location and
    rotation
    """
    def __init__(self, name, mod, offset, mirror, rotate):
        """Initializes an instance to represent a module"""
        geometry.__init__(self)
        self.name = name
        self.mod = mod
        self.gds = mod.gds
        self.rotate = rotate
        self.offset = snap_to_grid(offset)
        self.mirror = mirror



    def gds_write_file(self, newLayout):
        """Recursively writes all the sub-modules in this instance"""
        debug.info(3, "writing instance:" + self.name)
        # make sure to write out my module/structure 
        # (it will only be written the first time though)
        self.mod.gds_write_file(self.gds)
        # now write an instance of my module/structure
        newLayout.addInstance(self.gds,
                              offsetInMicrons=self.offset,
                              mirror=self.mirror,
                              rotate=self.rotate)

    def __str__(self):
        """ override print function output """
        return "inst: " + self.name + " mod=" + self.mod.name

    def __repr__(self):
        """ override print function output """
        return "( inst: " + self.name + " @" + str(self.offset) + " mod=" + self.mod.name + " " + self.mirror + " R=" + str(self.rotate) + ")"

class path(geometry):
    """Represents a Path"""

    def __init__(self, layerNumber, coordinates, path_width):
        """Initializes a path for the specified layer"""
        geometry.__init__(self)
        self.name = "path"
        self.layerNumber = layerNumber
        self.coordinates = map(lambda x: [x[0], x[1]], coordinates)
        self.coordinates = snap_to_grid(self.coordinates)
        self.path_width = path_width

        # FIXME figure out the width/height. This type of path is not
        # supported right now. It might not work in gdsMill.
        assert(0)

    def gds_write_file(self, newLayout):
        """Writes the path to GDS"""
        debug.info(3, "writing path (" + str(self.layerNumber) +  "):" + self.coordinates)
        newLayout.addPath(layerNumber=self.layerNumber,
                          purposeNumber=0,
                          coordinates=self.coordinates,
                          width=self.path_width)

    def __str__(self):
        """ override print function output """
        return "path: layer=" + self.layerNumber + " w=" + self.width

    def __repr__(self):
        """ override print function output """
        return "( path: layer=" + self.layerNumber + " w=" + self.width + " coords=" + str(self.coordinates) + " )"


class label(geometry):
    """Represents a text label"""

    def __init__(self, text, layerNumber, offset, zoom=1):
        """Initializes a text label for specified layer"""
        geometry.__init__(self)
        self.name = "label"
        self.text = text
        self.layerNumber = layerNumber
        self.offset = snap_to_grid(offset)
        self.zoom = zoom
        self.size = 0

    def gds_write_file(self, newLayout):
        """Writes the text label to GDS"""
        debug.info(3, "writing label (" + str(self.layerNumber) + "):" + self.text)
        newLayout.addText(text=self.text,
                          layerNumber=self.layerNumber,
                          purposeNumber=0,
                          offsetInMicrons=self.offset,
                          magnification=self.zoom,
                          rotate=None)

    def __str__(self):
        """ override print function output """
        return "label: " + self.text + " layer=" + str(self.layerNumber)

    def __repr__(self):
        """ override print function output """
        return "( label: " + self.text + " @" + str(self.offset) + " layer=" + self.layerNumber + " )"

class rectangle(geometry):
    """Represents a rectangular shape"""

    def __init__(self, layerNumber, offset, width, height):
        """Initializes a rectangular shape for specified layer"""
        geometry.__init__(self)
        self.name = "rect"
        self.layerNumber = layerNumber
        self.offset = snap_to_grid(offset)
        self.size = snap_to_grid([width, height])
        self.width = self.size[0]
        self.height = self.size[1]

    def gds_write_file(self, newLayout):
        """Writes the rectangular shape to GDS"""
        snapped_offset=snap_to_grid(self.offset)
        debug.info(3, "writing rectangle (" + str(self.layerNumber) + "):" 
                   + str(self.width) + "x" + str(self.height) + " @ " + str(snapped_offset))
        newLayout.addBox(layerNumber=self.layerNumber,
                         purposeNumber=0,
                         offsetInMicrons=snapped_offset,
                         width=self.width,
                         height=self.height,
                         center=False)

    def __str__(self):
        """ override print function output """
        return "rect: @" + str(self.offset) + " " + str(self.width) + "x" + str(self.height) + " layer=" +str(self.layerNumber)

    def __repr__(self):
        """ override print function output """
        return "( rect: @" + str(self.offset) + " " + str(self.width) + "x" + str(self.height) + " layer=" + str(self.layerNumber) + " )"
