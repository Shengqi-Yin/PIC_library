from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk"])
from functions.env import *
###########################################
strip_c = PLATFORM("SOI").c # load cornerstone pdk SOI platform cband strip

def coupler(width: int|float = None,
            layer: LayerSpec = None,
            lc: int|float = 5,
            radius: int|float = 30,
            gap: int|float = 0.5,
            xsection: CrossSection = strip_c,
            asymmetric: bool = False,
            labels: list|str|None = None,
            labels_size: int|float = 10,
            )->Component:
    c = gf.Component()
    xsection = xsection_generator(width,layer,xsection)
    path =gf.path.arc(radius=radius,angle=-90)
    path += gf.path.arc(radius=radius,angle=90)
    path += gf.path.straight(length=lc)
    path += gf.path.arc(radius=radius,angle=90)
    path += gf.path.arc(radius=radius,angle=-90)
    wg1 = c.add_ref(path.extrude(xsection))
    wg1.dymin = gap/2
    c.add_ports(wg1.ports) # add port info for the up arm
    if asymmetric:
        path = gf.path.straight(length=lc+radius*4)
    wg2 = c.add_ref(path.extrude(xsection)).mirror_y()
    wg2.dymax = -gap/2
    c.add_port(name="o3",port = wg2.ports["o1"]) # add port info for the down arm
    c.add_port(name="o4", port=wg2.ports["o2"])
    # add labels function for the further annotation
    if labels:
        for i,label in enumerate(labels):
            txt = c.add_ref(gf.c.text(text=f"{label}",layer=xsection.layer,size=labels_size))
            txt.dx, txt.dy = wg1.dx,wg1.dymin+max(radius,labels_size)+(labels_size+3)*i
    c.flatten()
    return c

###########################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("directional_coupler")
    c <<coupler()
    c.show()
    c.pprint_ports()