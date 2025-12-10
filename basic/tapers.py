from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic"])
from functions.env import *
from functions.pts_grating_coupler import hyperbola_arc
from pdk.CORNERSTONE import PLATFORM
###################################################
strip_c = PLATFORM("SOI").c #load a cross section for strip waveguide
rib_c = PLATFORM("SOI").rib_c

@gf.cell()
def ramp(width1:int|float = 0.45,
         width2:int|float = 10,
         length:int|float = 20,
         m:float = 1.0,
         layer:LayerSpec = (10,0),
         port_type = "optical",
         npoints: int = 201,
         **kwargs) -> Component:
    c = gf.Component()
    # --- define the polygon by coordinates --- #
    start_points = np.array([0, width1])
    end_points = np.array([length, width2])
    npoints = 2 if m == 1.0 else npoints
    upbone_points = hyperbola_arc(start_point=start_points, end_point=end_points, m=m, npoints=npoints)
    downbone_points = [(length,0),(0,0)]
    pts = np.vstack((downbone_points, upbone_points))
    # --- return a ND-array ptx group --- #
    c.add_polygon(pts, layer=layer)
    if port_type == "optical":
        p1,p2 = "o1","o2"
    elif port_type in ("electrical","electrical_rf" ):
        p1,p2 = "e1", "e2"
    c.add_port(name=p1, center=(0, width1/2), width=width1, orientation=180, layer=layer,port_type=port_type)
    c.add_port(name=p2, center=(length, width2/2), width=width2, orientation=0, layer=layer, port_type=port_type)
    return c

@gf.cell()
def taper(width1: int|float = 0.45,
          width2: int|float = 1,
          length: int|float = 10,
          m:float = 1.0,
          layer: LayerSpec = (10,0),
          port_type = "optical",
          npoints: int = 201,
          )->Component:
    """Define and return a taper object with an optional hyperbola coefficient"""
    c = gf.Component()
    # --- define the polygon by coordinates --- #
    start_points = np.array([0, width1 / 2])
    end_points = np.array([length, width2 / 2])
    npoints = 2 if m == 1.0 else npoints
    upbone_points = hyperbola_arc(start_point=start_points, end_point=end_points, m=m, npoints=npoints)
    downbone_points = upbone_points.copy()
    downbone_points[:, 1] = -downbone_points[:, 1]
    upbone_points = np.flipud(upbone_points)
    pts = np.vstack((downbone_points, upbone_points))
    # --- return a ND-array ptx group --- #
    c.add_polygon(pts, layer=layer)
    if port_type == "optical":
        p1,p2 = "o1","o2"
    elif port_type in ("electrical","electrical_rf" ):
        p1,p2 = "e1", "e2"
    c.add_port(name=p1, center=(0, 0), width=width1, orientation=180, layer=layer,port_type=port_type)
    c.add_port(name=p2, center=(length, 0), width=width2, orientation=0, layer=layer, port_type=port_type)
    return c



@gf.cell(check_ports=False)
def waveguide_taper(xsection: CrossSection=strip_c,
                    width1: int|float = 0.45,
                    width2: int|float = 10,
                    **kwargs) -> Component:
    delta_width = width2 - width1
    c = gf.Component()
    for section in xsection.sections:
        width1 = section.width
        c.add_ref(taper(width1=width1,width2=width1+delta_width,layer=section.layer,**kwargs).copy())

    return c

@gf.cell(check_ports=False)
def waveguide_taper_Rib2Strip(strip_xsection: CrossSection=strip_c,
                        rib_xsection: CrossSection=rib_c,
                        extra_length: int|float = 5,
                        **kwargs,
                        )->Component:
    c = gf.Component()
    core = c.add_ref(taper(width1 = strip_xsection.width,width2 = strip_xsection.width,layer=strip_xsection.layer,**kwargs))
    rib = c.add_ref(taper(width1=rib_xsection.sections[1].width,width2 = rib_xsection.sections[0].width,
                          layer=rib_xsection.sections[1].layer,**kwargs))
    if extra_length:
        path = gf.path.straight(length=extra_length)
        rib_wg = c.add_ref(path.extrude(cross_section= rib_xsection))
        rib_wg.connect("o2",core.ports["o1"])
        strip_wg = c.add_ref(path.extrude(cross_section= strip_xsection))
        strip_wg.connect("o1",core.ports["o2"])
        c.add_port(name = "o1",port= rib_wg.ports["o1"])
        c.add_port(name="o2", port=strip_wg.ports["o2"])
    c.dx = c.dxsize/2
    return c


@gf.cell
def taper_sm2sm(element=taper,
               mmi_length: int|float=10.0,
               layer: LayerSpec=(10,0),
               width_sm: int|float = 1.2,
               width_mm: int|float = 2.5,
               taper_length: int|float=50,
               xsection: CrossSection=None,
               **kwargs,
               ) ->gf.Component:
    # --- validation --- #
    if xsection:
        width_sm = xsection.width
        layer = xsection.layer
    c = gf.Component()
    taper_in = c.add_ref(element(layer=layer,width1=width_sm,width2=width_mm,
                                 length=taper_length).dup())
    taper_out = c.add_ref(element(layer=layer,width1=width_sm,width2=width_mm,
                                  length=taper_length).dup()).mirror_x()
    mmi = c<<gf.components.rectangle(size=(width_mm,mmi_length),layer=layer,port_type="optical")
    mmi.connect("o2",taper_in.ports["o2"])
    taper_out.connect("o2",mmi.ports["o4"])
    c.add_port(port=taper_in.ports["o1"],name="o1",layer=layer)
    c.add_port(port=taper_out.ports["o1"],name="o2",layer=layer)
    return c


##################################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("tapers")
    c << ramp()
    c.show()