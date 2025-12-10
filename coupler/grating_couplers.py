from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic"])
from functions.env import *
from functions.pts_grating_coupler import grating_tooth_pts,grating_taper_pts,RAD2DEG,DEG2RAD
from basic.waveguides import waveguide
##################################################
strip_c = PLATFORM("SOI").c
rib_c = PLATFORM("SOI").rib_c

@gf.cell
def _etch_grating(
    ap: float | None = None,
    bp: float | None = None,
    lp: float | None = None,
    offset: int | float | None=None,
    inner: float | None=None,
    taper_angle: float | None = None,
    length: int | float | None = None,
    layer: LayerSpec | None = None,
    pitch: float | None = None,
    duty: float | None = None,
    cycles: int | None = None,
    pos: Union[int,Sequence[int]] | None=None,
    tooth: Union[int,Sequence[int]] | None=None,
    bias: float =1.0,
):
    c = gf.Component()
    """Returns a linear or curved grating sturcure.
    Args:
        ap: major-semi-axis of elliptic arc
        bp: minor-semi-axis of elliptic arc
        lp: length of straight line
        offset: to be define
        inner: define the minimum grating structure (um)
        taper_angle: of the grating sturcture
        layer: of processing
        pitch: period of the tooth
        duty: ratio of etch width and pitch
        cycles: number of the etching tooth
        pos: position of the inner coordinate
        tooth: width of the tooth
    .. code::
            ________
    |_Dark_| light  |___

    <---- pitch ---->
           <- duty ->
    """

    if lp is not None and ap is None and bp is None: # linear mode
        if taper_angle is None and length is not None:
            xp_0 = length
        elif taper_angle is not None:
            xp_0 = 0.5*lp/tan(taper_angle/2*DEG2RAD)
        xp_0 = inner if inner>=xp_0 else xp_0
        if pos is None and tooth is None:
            pos = [pitch*i+xp_0+offset for i in range(cycles)]
            tooth = [pitch*duty for i in range (cycles)]
    elif lp is None and ap is not None and bp is not None: # elliptical mode
        ratio = bp/ap
        if inner is not None and inner > 0:
            ap_0=inner
        else:
            ap_0=ap
        if pos is None:
            pos = [pitch*i+ap_0 for i in range(cycles)]
            tooth = [pitch*duty for i in range (cycles)]
    cycles = cycles if pos is None and tooth is None else len(pos)
    gf.logger.warning(f"Check pos and tooth number, them are not matched") if len(pos)!=len(tooth) else None

    if any(pos[i]>=pos[i+1] for i in range(len(tooth)-1)):
        gf.logger.warning(f"Suggest to input the position and tooth width following the positive coordinate")
        zipped = list(zip(pos,tooth))
        sorted_zipped = sorted(zipped, key=lambda x: x[0])
        sorted_pos,sorted_tooth = zip(*sorted_zipped)
        pos,tooth = sorted_pos,sorted_tooth
        if any(tooth[i]+pos[i]>=pos[i+1] for i in range(len(pos)-1)):
            gf.logger.error(f"Wrong etching width input. Please check the input value.")

    gf.logger.warning(f"Check tooth position, the minimum arc is located in the taper range.") if min(pos)<inner else None

    for i in range(cycles): #linear grating
        if (lp is not None) and (ap is None) and (bp is None):
            pts = grating_tooth_pts(lp=lp,xp=pos[i],width=tooth[i],bias=bias)
            c.add_polygon(pts, layer=layer)
        elif (ap is not None) and (bp is not None) and (lp is None): # curved grating
            pts = grating_tooth_pts(ap=pos[i],bp=pos[i]*ratio,xp=0,width=tooth[i],taper_angle=taper_angle,bias=bias)
            c.add_polygon(pts, layer=layer)
        else:
            gf.logger.warning(
                f"Check grating geometry, elliptical or straight"
            )

    return c

@gf.cell
def _etch_taper(
    width: float=0.5,
    ap: float | None=None,
    bp: float | None=None,
    lp: float | None=None,
    xp: float | None=None,
    backend: float | None=None,
    taper_angle: float | None=None,
    length: int|float | None=None,
    layer: LayerSpec | None = None,
    m: float | None=None,
    npoints: int | None=None,
):
    c = gf.Component()
    """
    Args:
        width: of the waveguide and I/O port
        ap: major-radius of an elliptic arc
        bp: minor-radius of an elliptic arc
        lp: length of a linear grating tooth
        xp: offset along the x positive axis
        backend: end radius/distance of the grating taper region
        taper_angle: angle of taper
        length: length of taper
        layer: of processing
        m: hyperbola coefficient
        npoints: points to discribe a hyperbola arc

    """
    if lp is None and bp is not None and ap is not None:
        pts = grating_taper_pts(width=width,ap=ap,bp=bp,backend=backend,xp=xp,taper_angle=taper_angle,m=m,npoints=npoints)
        c.add_polygon(pts,layer=layer)
    elif ap is None and bp is None and lp is not None:
        if length is not None:
            pts = grating_taper_pts(width=width,lp=lp,xp=xp,backend=backend,length=length,m=m,npoints=npoints)
        else:
            pts = grating_taper_pts(width=width,lp=lp,xp=xp,backend=backend,taper_angle=taper_angle,m=m,npoints=npoints)
        c.add_polygon(pts,layer=layer)

    c.add_port(name="o1", center=(c.dxmin, 0), width=width, orientation=180, layer=layer,port_type="optical")##############
    # c.pprint_ports()
    return c


@gf.cell
def grating_coupler(
        width: float = 0.5,
        ap: float | None = None,
        bp: float | None = None,
        lp: float | None = None,
        offset: int | float = 0,
        inner: float = 0,
        backend: float | None = None,
        taper_angle: float | None = None,
        taper_length: int | float | None = None,
        layer: LayerSpecs = [(3,0),(6,0)],  # taper, tooth
        pitch: float = 0.63,
        duty: float = 0.5,
        cycles: int = 30,
        pos: Union[int, Sequence[int]] | None = None,
        tooth: Union[int, Sequence[int]] | None = None,
        hyperbola: float = 1.0,
        npoints: int = 201,
        bias: float = 1.0,
        rib: int | float | None = None,
        xsection: CrossSectionSpec | None = None,
        **kwargs,
):
    c = gf.Component()
    """Returns a linear or curved grating sturcure.

    Args:
        ap: major-semi-axis of elliptic arc
        bp: minor-semi-axis of elliptic arc
        lp: length of straight line
        offset: to be define
        inner: define the minimum grating structure (um)
        backend: distance of the end arc structure
        taper_angle: of the grating sturcture
        layer: of processing
        pitch: period of the tooth
        duty: ratio of etch width and pitch
        cycles: number of the etching tooth
        pos: manully define the position of etch regions
        tooth: manully defind the width of each etching
        hyperbola: coefficient of the taper shape, 1 is linear, 2 is parabola
        npoints:number of points to define the hyperbola curve
        bias: tooth region should slight over the grating region for overlap margin        
    """
    # --- validation --- #
    if rib is not None and len(layer) < 3:
        gf.logger.error(f"Missing layer definition! Require layer for rib.")
    if taper_angle is not None and (taper_angle <= 0 or taper_angle > 180):
        gf.logger.warning(
            f"curved grating angle should be less than 180. Got{taper_angle}."
        )
    if taper_angle is not None and taper_length is not None:
        gf.logger.error(f"Do not over-define the shape of taper! only need taper length/angle")
        return
    elif taper_length is not None and ap is not None and bp is not None:
        gf.logger.error(f"Missing key component, define a taper angle!")
        return
    elif taper_angle is None and taper_length is None:
        gf.logger.error(f"Missing key component, define a taper length or taper angle at least!")
        return

    if taper_length is None and taper_angle is not None and lp is not None:
        taper_length = lp / tan(taper_angle * DEG2RAD)
    if ap is not None and pos is not None:
        pos = [value + offset for value in pos]
    if lp is not None and pos is not None:
        pos = [value + offset + taper_length for value in pos]

    if xsection is not None:
        width,layer[0] = xsection.width, xsection.layer
        if len(xsection.sections)>1:
            rib = 0.5*(xsection.sections[1].width-xsection.width)
            if len(layer)>2:
                layer[2] = xsection.sections[1].layer
            else:
                layer.append(xsection.sections[1].layer)

    # ==== Layout initilization === ##
    Tooth = _etch_grating(
        ap=ap,
        bp=bp,
        lp=lp,
        offset=offset,
        inner=inner,
        taper_angle=taper_angle,
        length=taper_length,
        layer=layer[1],
        pitch=pitch,
        duty=duty,
        cycles=cycles,
        pos=pos,
        tooth=tooth,
        bias=bias,
    )

    GC_tooth = c.add_ref(Tooth)

    # if lp is not None:
    #     GC_tooth.movex(offset+taper_length)

    if backend is None:
        backend = ap if lp is None else lp
    if backend < float(GC_tooth.dxmax):
        backend += float(GC_tooth.dxmax)

    Taper = _etch_taper(
        width=width,
        ap=ap,
        bp=bp,
        lp=lp,
        xp=0,
        backend=backend,
        taper_angle=taper_angle,
        length=taper_length,
        layer=layer[0],
        m=hyperbola,
        npoints=npoints,
    )

    if rib is not None:
        c1 = gf.Component()
        GC_taper = c1.add_ref(Taper)
        r = c1.get_region(layer=xsection.layer)
        r = r.sized(rib * 1000)
        c1.add_polygon(r, layer=layer[2])
        c << c1
        extender = c << waveguide(xsection=xsection, length=rib)
        extender.connect(port="o2", other=GC_taper.ports["o1"])
        c.add_ports(ports=extender.ports)
    else:
        GC_taper = c.add_ref(Taper)
        c.add_ports(ports=GC_taper.ports)
    # -- add vertical output port -- #
    if offset is None:
        offset = 0
    if inner is None:
        inner = 0
    if lp:
        vertical_width = lp
        vertical_pos = taper_length+max(inner,offset)
    else:
        vertical_width = round(tan(taper_angle/2*DEG2RAD)*max(inner,offset),3)*2
        vertical_pos = max(ap,offset)
    c.add_port(name = "vertical_1",width= vertical_width,center=(vertical_pos,0),orientation=0,layer=layer[1],port_type="vertical_dual")
    return c

@gf.cell
def grating_coupler_array(
    grating_couplers_func = grating_coupler,
    period_x: int = 127,
    period_y: int = 127,
    n_x: int=1,
    n_y: int=1,
    port_name: str = "o1",
    rotation: int = 0,
    centered: bool = True,
    **kwargs
):
    """Create a grating coupler array with auto-named ports
    Args:
        components: import the grating coupler module
        period: pitch of the cell array
        n: number of cell be called
        port_name: name of the input port
        rotation: of the grating coupler
        centered: if so, the whole array will be centre by (0,0)
        **kwargs: varibles be defined in the grating coupler module
    """
    c = gf.Component()
    params = {}
    params.update(kwargs)
    ports = {}

    for i in range(n_x):
        for j in range(n_y):
            gc_ref = grating_couplers_func(**params)
            gc = c.add_ref(gc_ref)
            gc.dxmin=0
            gc.drotate(rotation)
            delta_x=(i-(n_x-1)/2)*period_x if centered else i*period_x
            delta_y=(j-(n_y-1)/2)*period_y if centered else j*period_y
            gc.movex(delta_x).movey(delta_y)
            if n_x==1 and n_y==1:
                port_name_new = port_name
                c.add_port(name=f"vertical_1", port=gc.ports["vertical_1"])
            elif n_x==1 and n_y>1:
                port_name_new = f"o1_{j}"
                c.add_port(name=f"vertical_{j}", port=gc.ports["vertical_1"])
            elif n_x>1 and n_y==1:
                port_name_new = f"o1_{i}"
                c.add_port(name=f"vertical_{i}", port=gc.ports["vertical_1"])
            else:
                port_name_new = f"o1_{i}_{j}"
                c.add_port(name=f"vertical_{i}_{j}", port=gc.ports["vertical_1"])
            ports[port_name_new] = gc.ports[port_name] 
            c.add_port(port=gc.ports[port_name],name=port_name_new)

    c.flatten()
    return c

######## For testing and placeholding only #######
def GC_std(**kwargs)->Component:
    xsection = kwargs.pop("xsection", None)
    return grating_coupler_array(lp=10,xsection = xsection,xp=0,inner = 10,backend=10,pitch=0.63,duty_cycle=0.5,
                                 taper_length=200,**kwargs).mirror_x()
def GC_rib(**kwargs)->Component:
    xsection = kwargs.pop("xsection", rib_c)
    return grating_coupler_array(lp=10,xsection = xsection,xp=0,inner = 10,backend=10,pitch=0.63,duty_cycle=0.5,
                                 taper_length=200,**kwargs).mirror_x()
def GC_foc(**kwargs)->Component:
    xsection = kwargs.pop("xsection", None)
    return grating_coupler_array(ap=10,bp=10,inner=15,taper_angle=28,backend=10,pitch=0.63,duty_cycle=0.5,
                                 xsection=xsection,**kwargs).mirror_x()
##################################################
if __name__=="__main__":
    gf.clear_cache()
    c = gf.Component("grating coupler")
    c << GC_foc()
    c.show()