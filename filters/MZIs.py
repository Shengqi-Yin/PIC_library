from filters.MMIs import MMI1X2
from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk","basic","coupler"])
from functions.env import *
from MMIs import MMI1X2, MMI2X2
from basic.waveguides import *
from basic.tapers import *
from coupler.grating_couplers import GC_foc,GC_std, GC_rib
##############################################
rib_o = PLATFORM("SOI").rib_o

@gf.cell(check_ports=False)
def MZI(splitter:ComponentSpec=MMI1X2,
        combiner:ComponentSpec|None=MMI2X2,
        delta_length: int|float = 40,
        length_x: int|float = 200,
        length_y: int|float = 2,
        length_heater: int|float = 200,
        radius: int|float = 30,
        xsection: CrossSection = None,
        splitter_port = ["o2","o3"],
        combiner_port = ["o1","o2"],
        input_port = ["o1"],
        output_port = ["o3","o4"],
        labels:list[str]|str=None,
        labels_size: int|float = 10,
        filament:bool=True,
        isolation:bool=False,
        pads:bool=True,
        dual_arms: bool=False,
        via: bool=True,
        doped_xsection: CrossSection= None,
        dummy_gap_feature: list[int|float] = [4, 7.8, 9.1, 22, 4], # gap for up and down arms, and separation between
        **kwargs,
        )->Component:
    """ Define a Mach-Zender interferometer with/without heater """
    # validation #
    if via and filament:
        filament = False
        gf.logger.info(f"automatic turn off the filament segment, only leave via section for doping modulation")
    if radius < xsection.radius_min:
        gf.logger.warning(f"radius {radius} is less than radius_min limitation")
    if combiner is None:
        combiner = splitter
    if (filament or isolation) and length_x<=10:
        gf.logger.error(f"minimum straight length in horizontal should be larger than 10 um, but you have {length_x} um")
    if length_heater and length_heater>length_x:
        gf.logger.warning(f"heater length ({length_heater} um) is shorter than length_x ({length_x} um). Auto correction length x")
        length_x = length_heater
    if length_heater is None:
        if filament or isolation:
            gf.logger.warning(
            f"Missing length heater parameter. Auto adding")
            length_heater = length_x
    print(length_x)
    # ---  layout  --- #
    x_offset = radius * 4 + length_x # setup the offset
    c = gf.Component()
    if isinstance(splitter,Component):
        spl, comb = c.add_ref(splitter),  c.add_ref(combiner)
    else:
        spl, comb = c.add_ref(splitter(xsection=xsection)), c.add_ref(combiner(xsection=xsection))
    comb.dxmin, comb.dy = spl.dxmax+x_offset, spl.dy # central alignment combiner to splitter
    # check if there is misalignment with the port
    y_offset = spl.ports[splitter_port[0]].dy - comb.ports[combiner_port[0]].dy
    # create up and down arm by path
    for i in range(2):
        p1,p2,p3 = gf.Path(),gf.Path(),gf.Path()
        # --- left section ---#
        p1 = gf.path.arc(radius=radius,angle=90)
        p1 += gf.path.straight(length=length_y+abs(y_offset)) if y_offset < 0 else gf.path.straight(length=length_y)
        if i == 1: # additional section for the delta_length
            p1 += gf.path.straight(length=delta_length/2)
        p1 += gf.path.arc(radius=radius,angle=-90)
        p1 += gf.path.straight(length=0.5 * (length_x - length_heater))
        # --- middle section ---#
        if filament or isolation:
            straight = waveguide_with_heater(length=length_heater,wg_xsection=xsection,
                                             filament=filament,isolation=isolation,pads=pads,**kwargs)
            p2 += gf.path.straight(length=length_heater)
        elif via:
            dual_arms = True
            straight = waveguide_with_doping(length=length_heater,wg_xsection=doped_xsection,**kwargs)
        else:
            p1 += gf.path.straight(length=length_x)
        # --- right section --- #
        p3 += gf.path.straight(length=0.5 * (length_x - length_heater))
        p3 += gf.path.arc(radius=radius,angle=-90)
        if i == 1: # addition section for the delta_length
            p3 += gf.path.straight(length=delta_length/2)
        p3 += gf.path.straight(length=length_y+abs(y_offset)) if y_offset > 0 else gf.path.straight(length=length_y)
        p3 += gf.path.arc(radius=radius,angle=90)
        # ===== connect three sections with both splitter and combiner ===== #
        if i == 0: # combine the upper arm
            up_arm1 = c.add_ref(p1.extrude(xsection))
            up_arm1.connect(port="o1",other=spl.ports[splitter_port[0]])
            up_arm2 = c.add_ref(p3.extrude(xsection))
            up_arm2.connect(port="o2", other=comb.ports[combiner_port[0]])
            if filament or isolation or via:
                up_straight = c.add_ref(straight)
                up_straight.connect(port="o1", other=up_arm1.ports["o2"])
        elif i == 1:# combine the lower arm
            down_arm1 = c.add_ref(p1.extrude(xsection)).mirror_y()
            down_arm1.connect(port="o1",other=spl.ports[splitter_port[1]])
            down_arm2 = c.add_ref(p3.extrude(xsection)).mirror_y()
            down_arm2.connect(port="o2", other=comb.ports[combiner_port[1]])
            if filament or isolation or via:
                if dual_arms:
                    down_straight = c.add_ref(straight).mirror_y()
                else:
                    down_straight = c.add_ref(p2.extrude(xsection))
                down_straight.connect(port="o1", other=down_arm1.ports["o2"])
        ## --- add additional layer for further pad connection --- ##
        if via:
            dgf = dummy_gap_feature.copy()
            dummy_layer = (1013, 0)
            arm1 = c.add_ref(gf.components.rectangle(size=(length_heater + 20, dgf[0]), layer=dummy_layer))  # up arm block
            arm2 = c.add_ref(gf.components.rectangle(size=(length_heater + 20, dgf[1]), layer=dummy_layer))  # down arm block
            # straight arm allocation
            if i == 0:
                arm1.dxmin, arm1.dy = up_straight.dxmin - 10, up_straight.ports["o1"].dy
                origin_x,origin_y = up_straight.ports["o1"].dx, up_straight.ports["o1"].dy
            else:
                arm1.dxmin, arm1.dy = down_straight.dxmin - 10, down_straight.ports["o1"].dy
                origin_x, origin_y = down_straight.ports["o1"].dx, down_straight.ports["o1"].dy
            arm2.dxmin, arm2.dymax = arm1.dxmin, arm1.dymin - dgf[2]
            # polygon arm allocation
            y_bias = 0.5 * (dgf[3] - dgf[2]) # bias from arm to y-branch
            x_bias = 50 # bias of y-branch
            for j in range(2): # 0 for left arm, 1 for right arm
                ptx1 = [((2 * j - 1) * x_bias, y_bias), (0, 0), (0, dgf[0]), ((2 * j - 1) * x_bias, y_bias + dgf[4])]
                ptx2 = [((2 * j - 1) * x_bias, -y_bias), (0, 0), (0, -dgf[1]), ((2 * j - 1) * x_bias, -y_bias - dgf[4])]
                if j == 0:
                    ptx1 = [(x - 10+origin_x, y+origin_y - dgf[0] / 2) for (x, y) in ptx1]
                    ptx2 = [(x - 10+origin_x, y+origin_y - dgf[0] / 2 - dgf[2]) for (x, y) in ptx2]
                else:
                    ptx1 = [(x + length_heater + 10+origin_x, y+origin_y - dgf[0] / 2) for (x, y) in ptx1]
                    ptx2 = [(x + length_heater + 10+origin_x, y+origin_y - dgf[0] / 2 - dgf[2]) for (x, y) in ptx2]
                arm1_con = c.add_polygon(points=ptx1, layer=dummy_layer)
                arm2_con = c.add_polygon(points=ptx2, layer=dummy_layer)
                c.add_port(name = f"d{i+1}_{j+1}",width = ptx1[3][1]-ptx1[0][1],orientation=90-90*(2*j-1),center=((ptx1[3][0]),0.5*(ptx1[3][1]+ptx1[0][1])),layer=dummy_layer)
                c.add_port(name = f"d{i+1}_{j+3}",width = -ptx2[3][1]+ptx2[0][1],orientation=90-90*(2*j-1),center=((ptx2[3][0]),0.5*(ptx2[3][1]+ptx2[0][1])),layer=dummy_layer)
    # --- add label for the further annotations --- #
    if labels:
        for i, label in enumerate(labels):
            txt = c.add_ref(gf.c.text(label,layer=xsection.layer,size=labels_size))
            txt.dx,txt.dy = up_arm1.dxmax,0-(labels_size+3)*i
    # --- add ports --- #
    for num,port in enumerate(input_port):
        c.add_port(name=f"o{num+1}",port = spl.ports[port])
    for count,port in enumerate(output_port):
        c.add_port(name=f"o{num+2+count}",port=comb.ports[port])
    if filament:
        c.add_port(name="e1",port=up_straight.ports["e1"])
        c.add_port(name="e2",port=up_straight.ports["e2"])
        if dual_arms:
            c.add_port(name="e3", port=down_straight.ports["e1"])
            c.add_port(name="e4", port=down_straight.ports["e2"])
    c.flatten()
    return c

@gf.cell(check_ports=False)
def MZI_racetrack(splitter:ComponentSpec=MMI1X2,
        combiner:ComponentSpec|None=MMI2X2,
        delta_length: int|float = 40,
        length_x: int|float = 200,
        length_y: int|float = 2,
        length_heater: int|float = 200,
        radius: int|float = 30,
        xsection: CrossSection = strip_c,
        splitter_port = ["o2","o3"],
        combiner_port = ["o1","o2"],
        input_port = ["o1"],
        output_port = ["o3","o4"],
        labels:list[str]|str=None,
        labels_size: int|float = 10,
        filament:bool=True,
        isolation:bool=False,
        pads:bool=True,
        dual_arms: bool=True,
        **kwargs,
        )->Component:
    """ Define a Mach-Zender interferometer with/without heater """
    # validation #
    if radius < xsection.radius_min:
        raise ValueError(f"radius {radius} is less than radius_min limitation")
    if combiner is None:
        combiner = splitter
    if (filament or isolation) and length_x<=10:
        raise ValueError(f"minimum straight length in horizontal should be larger than 10 um, but you have {length_x} um")
    if length_heater and length_heater>length_x:
        gf.logger.warning(f"heater length ({length_heater} um) is longer than length_x ({length_x} um). Auto correction length x")
        length_x = length_heater
    if length_heater is None:
        if filament or isolation:
            gf.logger.warning(f"Missing length heater parameter. Auto adding")
            length_heater = length_x
    # ---  layout  --- #
    c = gf.Component()
    if isinstance(splitter,Component):
        spl, comb = c.add_ref(splitter).mirror_x(),  c.add_ref(combiner).mirror_x()
    else:
        spl, comb = c.add_ref(splitter(xsection=xsection)).mirror_x(), c.add_ref(combiner(xsection=xsection)).mirror_x()
    x_offset = length_x + spl.dxsize + comb.dxsize
    comb.dxmax, comb.dy = spl.dxmin+x_offset, spl.dy # central alignment combiner to splitter
    # check if there is misalignment with the port
    y_offset = spl.ports[splitter_port[0]].dy - comb.ports[combiner_port[0]].dy
    # create up and down arm by path
    for i in range(2):
        p1,p2,p3 = gf.Path(),gf.Path(),gf.Path()
        # --- left section ---#
        p1 = gf.path.arc(radius=radius,angle=-90)
        p1 += gf.path.straight(length=length_y+abs(y_offset)) if y_offset < 0 else gf.path.straight(length=length_y)
        if i == 1: # additional section for the delta_length
            p1 += gf.path.straight(length=delta_length/2)
        p1 += gf.path.arc(radius=radius,angle=-90)
        p1 += gf.path.straight(length=0.5*(x_offset-length_heater))
        # --- middle section ---#
        if filament or isolation:
            straight = waveguide_with_heater(length=length_heater,wg_xsection=xsection,
                                             filament=filament,isolation=isolation,pads=pads,**kwargs)
            p2 += gf.path.straight(length=length_heater)
        else:
            p1 += gf.path.straight(length=length_x)
        # --- right section --- #
        p3 = gf.path.straight(length=0.5 * (x_offset - length_heater))
        p3 += gf.path.arc(radius=radius,angle=-90)
        if i == 1: # addition section for the delta_length
            p3 += gf.path.straight(length=delta_length/2)
        p3 += gf.path.straight(length=length_y+abs(y_offset)) if y_offset > 0 else gf.path.straight(length=length_y)
        p3 += gf.path.arc(radius=radius,angle=-90)
        # ===== connect three sections with both splitter and combiner ===== #
        if i == 0: # combine the upper arm
            up_arm1 = c.add_ref(p1.extrude(xsection))
            up_arm1.connect(port="o1",other=spl.ports[splitter_port[0]])
            up_arm2 = c.add_ref(p3.extrude(xsection))
            up_arm2.connect(port="o2", other=comb.ports[combiner_port[0]])
            if filament or isolation:
                up_straight = c.add_ref(straight)
                up_straight.connect(port="o1", other=up_arm1.ports["o2"])
        elif i == 1:# combine the lower arm
            down_arm1 = c.add_ref(p1.extrude(xsection)).mirror_y()
            down_arm1.connect(port="o1",other=spl.ports[splitter_port[1]])
            down_arm2 = c.add_ref(p3.extrude(xsection)).mirror_y()
            down_arm2.connect(port="o2", other=comb.ports[combiner_port[1]])
            if filament or isolation:
                if dual_arms:
                    down_straight = c.add_ref(straight).mirror_y()
                else:
                    down_straight = c.add_ref(p2.extrude(xsection))
                down_straight.connect(port="o1", other=down_arm1.ports["o2"])
    # --- add label for the further annotations --- #
    if labels:
        for i, label in enumerate(labels):
            txt = c.add_ref(gf.c.text(label,layer=xsection.layer,size=labels_size))
            txt.dx,txt.dy = up_arm1.dxmax,0-(labels_size+3)*i
    # --- add ports --- #
    for num,port in enumerate(input_port):
        c.add_port(name=f"o{num+1}",port = spl.ports[port])
    for count,port in enumerate(output_port):
        c.add_port(name=f"o{num+2+count}",port=comb.ports[port])
    if filament:
        c.add_port(name="e1",port=up_straight.ports["e1"])
        c.add_port(name="e2",port=up_straight.ports["e2"])
        if dual_arms:
            c.add_port(name="e3", port=down_straight.ports["e1"])
            c.add_port(name="e4", port=down_straight.ports["e2"])
    # c.flatten()
    return c



##########################################
if __name__ == "__main__":
    strip_c = PLATFORM("SOI").c
    rib_c = PLATFORM("SOI").rib_c
    rib_c_pn = PLATFORM("SOI").rib_c_pn
    rib_o = PLATFORM("SOI").rib_o
    rib_o_pn = PLATFORM("SOI").rib_o_pn

    # gf.clear_cache()
    c = gf.Component("MZI")
    unit = c << MZI(doped_xsection = rib_o_pn,via_width=5,length_heater=1000,delta_length=160)
    c.show()
    c.pprint_ports()