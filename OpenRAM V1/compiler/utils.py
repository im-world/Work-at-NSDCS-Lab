import os
import gdsMill
import tech 
import globals

OPTS = globals.OPTS

def snap_to_grid(offset):
    """
    Changes the coodrinate to match the grid settings
    """
    #returns (x,y) coordinates for placement in layout
    
    grid = tech.drc["grid"]         #grid size
    x = offset[0]               
    y = offset[1]
    # this gets the nearest integer value
    xgrid = int(round(round((x / grid), 2), 0))
    ygrid = int(round(round((y / grid), 2), 0))
    xoff = xgrid * grid
    yoff = ygrid * grid
    out_offset = [xoff, yoff]
    return out_offset           #rounded-off in terms of grid size as base (closest n*grid size)
                                


def gdsPinToOffset(gdsPin):
    #calculates pin position from label borders
    
    boundary = gdsPin[2]
    return [0.5 * (boundary[0] + boundary[2]), 0.5 * (boundary[1] + boundary[3])]


def auto_measure_libcell(pin_list, name, units, layer):
    # returns cell measurements and pin positions
    
    cell_gds = OPTS.openram_tech + "gds_lib/" + str(name) + ".gds"
    
    # page 9 of gsdMill documentation
    cell_vlsi = gdsMill.VlsiLayout(units=units)
    reader = gdsMill.Gds2reader(cell_vlsi)
    reader.loadFromFile(cell_gds)                               #all GDS2 properties into cell_vlsi now    

    # page 30 of openRAM manual
    cell = {}
    measure_result = cell_vlsi.readLayoutBorder(layer)          #returns cell size (dimensions of boundary)
    if measure_result == None:
        measure_result = cell_vlsi.measureSize(name)            #find physical cell size if boundary not available
    [cell["width"], cell["height"]] = measure_result

    for pin in pin_list:
        cell[str(pin)] = gdsPinToOffset(cell_vlsi.readPin(str(pin)))    #returns (x, y) coordinates where pin must be placed
    return cell
