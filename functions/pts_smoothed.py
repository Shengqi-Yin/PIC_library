from env import *
from scipy.interpolate import CubicSpline

#################################################
def spline(x:tuple[float,...]|None=None,
           y:tuple[float,...]|None=None,
           npoints:int=100,):
    cs = CubicSpline(x,y,bc_type='not-a-knot')
    x_eval = np.linspace(x[0],x[-1],npoints)
    y_eval = cs(x_eval)
    return x_eval, y_eval