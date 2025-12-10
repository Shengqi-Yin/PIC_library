from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic","coupler"])
from functions.env import *
from pads import pad_array
from coupler.grating_couplers import GC_std
##########################
strip_c = PLATFORM("SOI").c
layers = PLATFORM("SOI").layers

@gf.cell
def die_frame(size: tuple[int]=(11470,4900),
              type: str|None=None,
              layer: LayerSpec= layers["OUT"],
              **kwargs)->Component:
    if type:
        if type.lower() == "full":
            size= (11470,4900)
        elif type.lower() == "half":
            size = (5500,4900)
        elif type.lower() == "quadrant":
            size = (11470,15450)
        elif type.lower() == "all":
            size = (24157.5,32157.5)
    return gf.components.rectangle(size=size,layer=layers["OUT"],centered=True)
@gf.cell
def die_frame_template(gc_ref = GC_std,
                       xsection = strip_c,
                       n_channels: int = 16,
                       gc_pitch: int|float = 250,
                       **kwargs)->Component:
    c = gf.Component()
    outline = c.add_ref(die_frame(**kwargs))
    # --- add electrical pads --- #
    pad_up = c.add_ref(pad_array(**kwargs))
    pad_up.dxmin, pad_up.dymax = outline.dxmin+1045, outline.dymax-50
    c.add_ports(pad_up.ports)
    pad_down = c.add_ref(pad_array(ports="e2",count_from = 32,**kwargs))
    pad_down.dxmin, pad_down.dymin = outline.dxmin + 1045, outline.dymin+50
    c.add_ports(pad_down.ports)
    # --- add optical components --- #
    for i in range(n_channels): # add left grating coupler array
        gc_unit = c.add_ref(gc_ref().dup())
        gc_unit.dxmin, gc_unit.dy = outline.dxmin+420,0.5*gc_pitch*(n_channels-1)-gc_pitch*i
        c.add_port(name = f"o{i+1}",port = gc_unit.ports["o1"])
        c.add_port(name = f"vertical_{i+1}",port = gc_unit.ports["vertical_1"])
    for j in range(n_channels): # add left grating coupler array
        gc_unit = c.add_ref(gc_ref().dup().mirror_x())
        gc_unit.dxmax, gc_unit.dy = outline.dxmax-420,0.5*gc_pitch*(n_channels-1)-gc_pitch*j
        c.add_port(name = f"o{i+j+2}",port = gc_unit.ports["o1"])
        c.add_port(name=f"vertical_{i+j+2}", port=gc_unit.ports["vertical_1"])
    # --- self-alignment route connection --- #
    path = gf.path.straight(length=10)
    path += gf.path.arc(radius=30,angle=180)
    path += gf.path.straight(length=50+gc_unit.dxsize)
    path += gf.path.arc(radius=30,angle=90)
    path += gf.path.straight(length=60+c.ports["o1"].dy-c.ports["o16"].dy)
    path += gf.path.arc(radius=30,angle=90)
    path += gf.path.straight(length=50 + gc_unit.dxsize)
    path += gf.path.arc(radius=30, angle=180)
    path += gf.path.straight(length=10)
    route = c.add_ref(path.extrude(cross_section=xsection)) # left connection
    route.connect("o1",c.ports["o1"])
    route = c.add_ref(path.extrude(cross_section=xsection)) # right connection
    route.connect("o1", c.ports["o32"])
    c.flatten()
    return c

#################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("dies")
    c << die_frame_template()
    c.show()