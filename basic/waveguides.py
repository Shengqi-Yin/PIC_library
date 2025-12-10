from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic"])
from functions.env import *
from pdk.CORNERSTONE import PLATFORM
from functions.pts_smoothed import spline
from basic.tapers import *
###################################################

@gf.cell()
def waveguide(width: int|float = None,
             length: int|float = 10,
             layer: LayerSpec = (10,0),
             xsection: CrossSectionSpec = rib_c)->Component:
    xsection = xsection_generator(width,layer,xsection)
    c = gf.Component()
    path = gf.path.straight(length=length)
    wg = c.add_ref(path.extrude(xsection))
    c.add_ports(wg.ports)
    c.flatten()
    # c.pprint_ports()
    return c

@gf.cell()
def bend90(width: int|float = None,
           radius: int|float = 30,
             length: int|float = 10,
             layer: LayerSpec = (10,0),
             xsection: CrossSectionSpec = rib_c)->Component:
    xsection = xsection_generator(width, layer, xsection)
    c = gf.Component()
    path = gf.path.arc(radius=radius,angle=90)
    wg = c.add_ref(path.extrude(xsection))
    c.add_ports(wg.ports)
    c.flatten()
    return c

@gf.cell
def crossing(xsection:CrossSectionSpec = strip_c,
             segments: float|tuple[float]| None = None,
             box: int|float = 5.0,
             npoints: int = None,
             **kwargs,
             )->Component:
    # --- validation and data normalisation --- #
    if segments:
        x = np.linspace(-box/2,0,len(segments))
        segments = [s*0.5 for s in segments]
        if npoints is None:
            npoints = len(segments)
        x1,y1 = spline(x,segments,npoints=npoints)
    else:
        width = xsection.width
        x1 = np.array([-box/2,-width/2,width/2,box/2])
        y1 = np.array([width/2,box/2,box/2,width/2])
    up_points = np.column_stack([x1,y1])
    down_points = up_points.copy()
    down_points[:,1] = -down_points[:,1]
    up_points = np.flipud(up_points)
    pts1 = np.vstack((down_points,up_points)) # left pts
    pts4,pts3 = pts1[:, [1, 0]],pts1.copy() # create down pts and copy
    pts3[:,0]=-pts1[:,0] #right pts
    pts2 = pts3[:, [1, 0]]
    # --- layout --- #
    c = gf.Component()
    c.add_polygon(pts1,layer=xsection.layer) # left section
    c.add_polygon(pts2, layer=xsection.layer)
    c.add_polygon(pts3, layer=xsection.layer)
    c.add_polygon(pts4, layer=xsection.layer)  # down section
    if len(xsection.sections)>1:
        for i,section in enumerate(xsection.sections):
            if i == 0:
                r = c.get_region(layer=section.layer)
                width_ref = section.width
                extend_width = 0
            else:
                delta_width = 0.5*(section.width - width_ref)
                r = r.sized(delta_width*1000)
                c.add_polygon(r,layer=section.layer)
                extend_width = max(extend_width,delta_width)
        for i in range(4):
            arm = c.add_ref(waveguide(length=extend_width,xsection=xsection))
            arm.dxmax, arm.dy = -box/2, 0
            arm.rotate(-90*i,center=(0,0))

    # --- add ports for the further step --- #
    x_sign, y_sign = [-1,0,1,0], [0,1,0,-1]
    for i in range(4):
        if len(xsection.sections) == 1:
            c.add_port(name=f"o{i+1}",orientation=180-90*i,width=xsection.width,layer=xsection.layer,center=((box/2)*x_sign[i],(box/2)*y_sign[i]))
        else:
            c.add_port(name=f"o{i + 1}", orientation=180 - 90 * i, width=xsection.width, layer=xsection.layer,
                       center=((box/2+extend_width) * x_sign[i], (box/2+extend_width) * y_sign[i]))
    c.flatten()
    return c

#### advanced design BBs ######
@gf.cell(check_ports=False)
def waveguide_with_heater(wg_width: int|float = None,
                          length: int|float = 200,
                          wg_layer: LayerSpec = None,
                          wg_xsection: CrossSection = strip_c,
                          filament: bool = True,
                          fil_layer: LayerSpec = (39,0),
                          fil_width: int|float = 2,
                          wire_width : int|float = 50,
                          wire_length: int|float = 50,
                          isolation: bool = False,
                          iso_layer: LayerSpec = (46,0),
                          iso_gap: int|float = 2,
                          iso_width: int|float = 2,
                          pads: bool = True,
                          pad_layer: LayerSpec = (41,0),
                          pad_size:tuple|int|list|None = (100,100),
                          pad_offset:int|float= 50,
                          pad_gap:int|float= 50,
                          removal_waveguide: bool = False,
                          **kwargs,
                          )->Component:
    wg_xsection = xsection_generator(wg_width, wg_layer, wg_xsection)
    c = gf.Component()
    wg = c.add_ref(waveguide(length=length,xsection=wg_xsection).copy()) # load a fundamental waveguide as reference
    if removal_waveguide is False:
        c.add_ports(wg.ports)
    # --- generate a filament with the length of waveguide --- #
    if filament:
        if wire_length < (iso_width + iso_gap):
            print(
                f"Pad could by overlaped with isolation trench, please increase the wire length above {iso_layer + iso_gap} um")
        path = gf.path.straight(length=length)  # define a path for filament and isolation trenches
        cs_fil = cross_section(width=fil_width,layer=fil_layer)
        fil = c.add_ref(path.extrude(cs_fil))
        fil.dx = wg.dx
        for i in range(2): # left taper and right taper for layer filament and pad
            fil_taper = c.add_ref(taper(width1 = fil_width, width2=max(wire_width,fil_width),length=wire_length,layer = fil_layer,
                                        port_type = "electrical")).rotate(90)
            fil_circle = c.add_ref(gf.components.circle(radius=fil_width/2,layer=fil_layer))
            fil_taper.dx = fil_width/2 if i==0 else wg.dxmax-fil_width/2
            fil_taper.dymin,fil_circle.dy = fil.dymax,fil.dymax
            fil_circle.dx = fil_width if i==0 else wg.dxmax-fil_width
            # --- pad layer to overlap the geometry of heater filament --- #
            pad_taper = c.add_ref(taper(width1=fil_width, width2=max(wire_width,fil_width), length=wire_length, layer=pad_layer,
                                        port_type="electrical")).rotate(90)
            pad_taper.dx = fil_width / 2 if i == 0 else wg.dxmax - fil_width / 2
            pad_taper.dymin = fil.dymax
            if pads is None:
                # --- add port information as external connection for further wire connection --- #
                c.add_port(name=f"e{i+1}",port = pad_taper.ports["e2"],port_type="electrical")
        if pads:
            # --- add contact pads --- #
            if pad_offset < wire_length:
                print(f"pad offset should be larger than wire length")
                pad_offset = wire_length
            for i in range(2):
                pad = c.add_ref(gf.components.rectangle(size=pad_size,layer=pad_layer,port_type="pad"))
                pad.dx = wg.dx-(pad_size[0]/2+pad_gap/2)*2*(i%2-0.5)
                pad.dymin = fil.dymax+pad_offset
                if i == 0: # right pad
                    ptx_connecter = [(pad.dxmin,pad.dymin),(pad.dxmax,pad.dymin),
                                     (pad_taper.dxmax,pad_taper.dymax),(pad_taper.dxmin,pad_taper.dymax)]
                    connector = c.add_polygon(ptx_connecter,layer=pad_layer)
                if i ==1: # left pad
                    ptx_connecter2 =[]
                    for ptx in ptx_connecter:
                        ptx_connecter2.append((2*wg.dx-ptx[0],ptx[1]))
                    connector = c.add_polygon(ptx_connecter2,layer=pad_layer)
                c.add_port(name=f"e{i+1}",port=pad.ports["e2"])

    # --- generate a isolation trench following the length of the waveguide and avoid overlapping the filament patern ###
    if isolation:
        path = gf.path.straight(length=length-wire_width)  # define a path for filament and isolation trenches
        cs_iso = cross_section(width=iso_width,layer=iso_layer,offset=iso_gap+wg_xsection.width/2,
                               sections=[{"width":iso_width,"layer":iso_layer,"offset":-iso_gap-wg_xsection.width/2}])
        iso = c.add_ref(path.extrude(cs_iso))
        iso.dx = wg.dx
    c.flatten()
    # c.pprint_ports()
    if removal_waveguide:
        c.remove_layers([wg_xsection.layer])
    return c

def waveguide_with_doping(wg_width: int|float = None,
                          length: int|float = 1500,
                          wg_layer: LayerSpec = None,
                          wg_xsection: CrossSection = strip_c,
                          via_width: int|float = None,
                          via_min: int|float = 2.5,
                          via_layer: LayerSpec = (12,0),
                          reference_layer: LayerSpecs|None = ((11,0),(9,0)),
                          )->Component:
    # --- validateion --- #
    bias_max, bound_min = None, None #create a bias detector
    for sec in wg_xsection.sections:
        if sec.layer in reference_layer:
            width, offset = sec.width, sec.offset
            bias, bound= abs(offset)-width/2,abs(offset)+width/2
            if bias < 0:
                gf.logger.warning(f"reference layer crossing over the cental of waveguide, please check the cross section")
            bias_max = max(bias,bias_max) if bias_max else bias
            bound_min = min(bound,bound_min) if bound_min else bound
    if via_width:
        if bias_max > via_min:
            gf.logger.warning(f"via position cannot totally covered by doped region, please increase at least({-via_min+bias_max} um)")
        if bound_min < via_min+via_width:
            gf.logger.warning(f"via position cannot totally covered by doped region, please decrease width or minimum position")
    # --- layout --- #
    wg_xsection = xsection_generator(wg_width, wg_layer, wg_xsection)
    c = gf.Component()
    wg = c.add_ref(waveguide(length=length, xsection=wg_xsection).copy())  # load a fundamental waveguide as reference
    c.add_ports(wg.ports) # add waveguide IOs port
    if via_width: # add via holder if there have a definition of via
        for i in range(2):
            via_str_ref = gf.components.rectangle(size=(length-1-via_width,via_width),layer=via_layer).copy()
            via_circ_ref = gf.components.circle(radius=via_width/2,layer=via_layer).copy()
            via_str = c.add_ref(via_str_ref)
            via_circ_left, via_circ_right = c.add_ref(via_circ_ref), c.add_ref(via_circ_ref)
            via_str.dxmin, via_circ_left.dx, via_circ_right.dx = 0.5+via_width/2, 0.5+via_width/2, length-(0.5+via_width/2)
            y_position = (via_min+via_width/2)*(i*2-1)
            via_str.dy, via_circ_left.dy,via_circ_right.dy = y_position,y_position,y_position
    # # --- add additional layer for further pad connection --- #
    # dgf = dummy_gap_feature.copy()
    # dummy_layer = (1013,0)
    # arm1 = c.add_ref(gf.components.rectangle(size=(length+20,dgf[0]),layer=dummy_layer)) #up arm block
    # arm2 = c.add_ref(gf.components.rectangle(size=(length+20,dgf[1]),layer=dummy_layer)) # down arm block
    # arm1.dxmin, arm1.dy = wg.dxmin-10, wg.ports["o1"].dy
    # arm2.dxmin, arm2.dymax = arm1.dxmin, arm1.dymin-dgf[2]
    # y_bias = 0.5*(dgf[3]-dgf[2])
    # for i in range(2):
    #     ptx1 = [((2*i-1)*20,y_bias),(0,0),(0,dgf[0]),((2*i-1)*20,y_bias+dgf[4])]
    #     ptx2 = [((2*i-1)*20,-y_bias),(0,0),(0,-dgf[1]),((2*i-1)*20,-y_bias-dgf[4])]
    #     if i == 0:
    #         ptx1 = [(x-10, y-dgf[0]/2) for (x, y) in ptx1]
    #         ptx2 = [(x-10, y -dgf[0]/2- dgf[2]) for (x, y) in ptx2]
    #     else:
    #         ptx1 = [(x+length+10, y - dgf[0] / 2) for (x, y) in ptx1]
    #         ptx2 = [(x+length+10, y - dgf[0] / 2 - dgf[2]) for (x, y) in ptx2]
    #     arm1_con = c.add_polygon(points=ptx1, layer=dummy_layer)
    #     arm2_con = c.add_polygon(points=ptx2, layer=dummy_layer)
    c.flatten()
    return c


###################################################

if __name__ == "__main__":
    strip_c = PLATFORM("SOI").c  # load a cross section for strip waveguide
    rib_c = PLATFORM("SOI").rib_c
    rib_c_pn = PLATFORM("SOI").rib_c_pn
    gf.clear_cache()
    c = gf.Component("waveguides")
    # print(rib_c)
    # print(rib_c_pn)
    c << waveguide_with_doping(wg_xsection=rib_c_pn,via_width=5)
    c.show()
