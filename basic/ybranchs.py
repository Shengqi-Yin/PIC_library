from path_manager import *
add_root_path()
add_submodule_path(["functions","pdk"])
from functions.env import *
##########################################
strip_c = PLATFORM("SOI").c

@gf.cell
def y_splitter(xsection:CrossSectionSpec= strip_c,
               offset_x: int|float = 40,
               offset_y: int|float = 20,
               **kwargs)->Component:
    c = gf.Component()
    # --- transferring to port for sband connection--- #
    c.add_port(name="o1",width=xsection.width,layer=xsection.layer,orientation=0,center=(0,0))
    c.add_port(name="o2",width=xsection.width,layer=xsection.layer,orientation=180,center=(offset_x,offset_y/2))
    c.add_port(name="o3",width=xsection.width, layer=xsection.layer, orientation=180, center=(offset_x, -offset_y / 2))
    # --- layout --- #
    for i in range(2):
        path = gf.routing.route_single_sbend(c,c.ports["o1"],c.ports[f"o{i+2}"],cross_section=xsection)
    c.ports.clear()
    c.add_port(name="o1", width=xsection.width, layer=xsection.layer, orientation=180, center=(0, 0))
    c.add_port(name="o2", width=xsection.width, layer=xsection.layer, orientation=0, center=(offset_x, offset_y / 2))
    c.add_port(name="o3", width=xsection.width, layer=xsection.layer, orientation=0, center=(offset_x, -offset_y / 2))
    c.flatten()
    return c


#########################################
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("y_branches")
    c << y_splitter()
    c.show()