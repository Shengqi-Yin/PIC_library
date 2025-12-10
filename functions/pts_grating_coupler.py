from env import *

###################################
RAD2DEG = 180.0 / np.pi
DEG2RAD = 1 / RAD2DEG

def ellipse_arc(
    a: float,
    b: float,
    x0: float,
    theta_min: float,
    theta_max: float,
    angle_step: float = 0.5,
) -> npt.NDArray[np.floating[Any]]:
    """Returns an elliptical arc.
    b = a *sqrt(1-e**2)
    An ellipse with a = b has zero eccentricity (is a circle)
    Args:
        a: ellipse semi-major axis.
        b: semi-minor axis.
        x0: in um.
        theta_min: in rad.
        theta_max: in rad.
        angle_step: in rad.
    """
    theta = np.arange(theta_min, theta_max + angle_step, angle_step) * DEG2RAD
    xs = a * np.cos(theta) + x0
    xs = gf.snap.snap_to_grid(xs)
    ys = b * np.sin(theta)
    ys = gf.snap.snap_to_grid(ys)
    return np.column_stack([xs, ys])

def straight_line(
        length: float,
        x0: float,
) -> npt.NDArray[np.floating[Any]]:
    """Returns a straight line.

    Args:
        length: of the line.
    """
    ys = np.linspace(-length/2,length/2,num=2)
    xs = (x0,x0)
    return np.column_stack([xs,ys])

def taper_arc(
    width: int|float| None=None,
    ap: float |None=None,
    bp: float | None=None,
    lp: float | None=None,
    backend: float | None=None,
    theta_min: float | None=None,
    theta_max: float | None=None,
    length: int|float| None=None,
    angle_step: float | None=None,
    m: float | int| None=None,
    npoints: int =201,
) -> npt.NDArray[np.floating[Any]]:
    x0 = 0
    y0 = width/2
    xs=[]
    ys=[]
    # xs.append(x0)
    # ys.append(y0)
    if length is None and theta_max is not None: #using angle define
        [x1,y1]=[(width/2/tan(abs(theta_max*DEG2RAD))),width/2]
    elif length is not None: # using length to define
        [x1,y1]=[x0,y0]
    if backend is None and ap is not None and lp is None:
        backend=ap
    elif backend is None and lp is not None and ap is None:
        backend=lp
    xs.append(x1)
    ys.append(y1)
    # print(xs,ys)
    if lp is None and ap is not None and bp is not None: # elliptical
        if backend is None:
            backend = ap
            gf.logger.warning(f"miss backend info. make it equal to ap")
        elif backend < ap:
            backend = ap
            gf.logger.warning(f"Backend value should be larger than ap")
        ratio = bp/ap
        [x2,y2]=[(ap*cos(abs(theta_max)*DEG2RAD)),(bp*sin(abs(theta_max)*DEG2RAD))]
        [x3,y3]=[(backend*cos(abs(theta_max)*DEG2RAD)),(backend*ratio*sin(abs(theta_max)*DEG2RAD))]
    elif lp is not None and ap is None and bp is None: # linear
        if length is not None:
            [x2,y2] = [length,lp/2]
        else:
            [x2,y2]=[(lp/2)/(tan(abs(theta_max*DEG2RAD))),lp/2]
        if backend is None:
            backend = x2
        elif backend < x2:
            backend = x2
        [x3,y3]=[backend,lp/2]
    else:
        gf.logger.warning(
                f"missing component infomation. require ap, bp or lp."
            )
    if m != 1:
        hyper_pts = hyperbola_arc(np.array([x1,y1]),np.array([x2,y2]),m=m,npoints=npoints)
        trimmed_hyper_pts = hyper_pts[1:-1]
        for coor in trimmed_hyper_pts:
            xs.append(coor[0])
            ys.append(coor[1])

    xs.append(x2)
    ys.append(y2)
    xs.append(x3)
    ys.append(y3)
    return np.column_stack([xs,ys])

def hyperbola_arc(
    start_point:npt.NDArray[np.float64],
    end_point:npt.NDArray[np.float64],
    m: float = 1.0,
    npoints: int | None=None,
) -> npt.NDArray[np.floating[Any]]:
    start_point = start_point.astype(np.float64)
    end_point = end_point.astype(np.float64)
    if start_point.ndim !=1 or len(start_point) not in [2]:
        raise ValueError(
            f"Expected a 1D array with 2 elements, but got shape {start_point.shape}"
        )
    elif end_point.ndim !=1 or len(end_point) not in [2]:
        raise ValueError(
            f"Expected a 1D array with 2 elements, but got shape {end_point.shape}"
        )
    [x_start,y_start]=start_point
    [x_end,y_end] = end_point
    L = x_end-x_start
    x = np.linspace(0,L,npoints)

    w0 = y_start
    wL = y_end
    alpha = (w0-wL)/(L**m)
    ys = alpha*(L-x)**m+wL
    xs = x+x_start

    return np.column_stack([xs,ys])


def straight_path(
        points: npt.NDArray[np.float64],
        width: float,
        centered: bool = False,
        spike_length: float64 | int | float = 0,
        grid: float | None = None,
) -> npt.NDArray[np.float64]:
    grid = grid or gf.kcl.dbu

    if isinstance(points, list):
        points = np.stack([(p[0], p[1]) for p in points], axis=0)

    if centered:
        offsets = np.column_stack((np.array([width, width]), np.array([0, 0]))) * 0.5
        points_back = np.flipud(points - offsets)
    else:
        offsets = np.column_stack((np.array([width, width]), np.array([0, 0])))
        points_back = np.flipud(points)

    if spike_length != 0:
        d = spike_length
        p_start_spike = points_back[-1] + 0.5 * d * np.array([1, -1])
        p_end_spike = points_back[0] + 0.5 * d * np.array([1, 1])

        pts = np.vstack((p_start_spike, points + offsets, p_end_spike, points_back))
    else:
        pts = np.vstack((points + offsets, points_back))

    return np.round(pts / grid) * grid


def curved_path(
        points: npt.NDArray[np.float64],
        width: float,
        with_manhattan_facing_angles: bool = True,
        centered: bool = False,
        spike_length: float64 | int | float = 0,
        start_angle: int | None = None,
        end_angle: int | None = None,
        grid: float | None = None,
) -> npt.NDArray[np.float64]:
    """ Extrude a path of 'width' along a curve defined by 'points'

    Args:
        points: numpy 2d array of shape (N,2).
        width: of the path to extrude.
        with_manhattan_facing_angles: snaps to manhattan angles.
        centered: tracing curved is located in centre, or as inner_boundary
        spike_length: in um.
        start_angle: in degrees.
        end_angle: in degrees.
        grid: in um.

    Returns:
        numpy 2d array of shape (2*N,2)

    """
    grid = grid or gf.kcl.dbu

    if isinstance(points, list):
        points = np.stack([(p[0], p[1]) for p in points], axis=0)

    a = angles_deg(points)
    if with_manhattan_facing_angles:
        _start_angle = snap_angle(a[0] + 180)
        _end_angle = snap_angle(a[-2])
    else:
        _start_angle = a[0] + 180
        _end_angle = a[-2]

    start_angle = start_angle if start_angle is not None else _start_angle
    end_angle = end_angle if end_angle is not None else _end_angle

    a2 = angles_rad(points) * 0.5
    a1 = np.roll(a2, 1)

    a2[-1] = end_angle * DEG2RAD - a2[-2]
    a1[0] = start_angle * DEG2RAD - a1[1]

    a_plus = a2 + a1
    cos_a_min = np.cos(a2 - a1)
    if centered:
        offsets = np.column_stack((-sin(a_plus) / cos_a_min, cos(a_plus) / cos_a_min)
                                  ) * (0.5 * width)
        points_back = np.flipud(points + offsets)
    else:
        offsets = np.column_stack((-sin(a_plus) / cos_a_min, cos(a_plus) / cos_a_min)
                                  ) * (width)
        points_back = np.flipud(points)

    if spike_length != 0:
        d = spike_length
        a_start = start_angle * DEG2RAD
        a_end = end_angle * DEG2RAD
        bias_start = 0 if centered else -offsets[0] / 2
        bias_end = 0 if centered else -offsets[-1] / 2
        p_start_spike = points[0] + bias_start + 0.5 * d * np.array([[cos(a_start), sin(a_start)]])
        p_end_spike = points[-1] + bias_end + 0.5 * d * np.array([[cos(a_end), sin(a_end)]])

        pts = np.vstack((p_start_spike, points - offsets, p_end_spike, points_back))
    else:
        pts = np.vstack((points - offsets, points_back))

    return np.round(pts / grid) * grid

def angles_rad(pts: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """Returns the angles (radians) of the connection between each point and the next."""
    _pts = np.roll(pts, -1, 0)
    return np.arctan2(_pts[:, 1] - pts[:, 1], _pts[:, 0] - pts[:, 0])

def angles_deg(pts: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """Returns the angles (degrees) of the connection between each point and the next."""
    return angles_rad(pts) * RAD2DEG

def snap_angle(a: float64) -> int:
    """Returns angle snapped along manhattan angle (0, 90, 180, 270).

    a: angle in deg
    Return angle snapped along manhattan angle
    """
    a = a % 360
    if -45 < a < 45:
        return 0
    elif 45 < a < 135:
        return 90
    elif 135 < a < 225:
        return 180
    elif 225 < a < 315:
        return 270
    else:
        return 0

def grating_tooth_pts(
    ap: float | None = None,
    bp: float | None = None,
    lp: float | None = None,
    xp: float | None = None,
    width: float = 0.5,
    taper_angle: float | None = None,
    centered: bool = False,
    spiked: bool = False,
    angle_step: float = 1.0,
    bias: float = 1.0,
) -> npt.NDArray[np.floating[Any]]:
    if ap is not None and bp is not None and lp is None:
        theta_min = -taper_angle / 2
        theta_max = taper_angle / 2
        backbone_points = ellipse_arc(ap, bp, xp, theta_min-bias, theta_max+bias, angle_step)
        spike_length = width if spiked else 0.0
        pts = curved_path(
            backbone_points,
            width,
            centered=centered,
            with_manhattan_facing_angles=False,
            spike_length=spike_length,
        )
    elif lp is not None:
        backbone_points = straight_line(length=lp+bias,x0=xp)
        spike_length = width if spiked else 0.0
        pts = straight_path(
            backbone_points,
            width,
            centered=centered,
            spike_length=spike_length,
        )
    return pts


def grating_taper_pts(
        width: float | None = None,
        ap: float | None = None,
        bp: float | None = None,
        lp: float | None = None,
        xp: float | None = None,
        backend: float | None = None,
        taper_angle: float | None = None,
        length: int | float | None = None,
        angle_step: float = 1.0,
        m: float = 1.0,
        npoints: int = 201,
) -> npt.NDArray[np.floating[Any]]:
    if taper_angle is not None:
        theta_min = -taper_angle / 2
        theta_max = taper_angle / 2
    if lp is None and ap is not None and bp is not None:
        ratio = bp / ap
        if backend is not None and backend > ap:
            major_radius = backend
            minor_radius = backend * ratio
        else:
            gf.logger.waring(f"need backend info or backend value too small")
        backbone_points = ellipse_arc(major_radius, minor_radius, xp, theta_min, theta_max, angle_step)
        upbone_points = taper_arc(width=width, ap=ap, bp=bp, backend=major_radius, theta_max=theta_max,
                                  theta_min=theta_min, m=m, npoints=npoints)
    elif lp is not None and ap is None and bp is None:
        backbone_points = straight_line(lp, backend)
        if length is not None:
            upbone_points = taper_arc(width=width, lp=lp, backend=backend, length=length, m=m, npoints=npoints)
        else:
            upbone_points = taper_arc(width=width, lp=lp, backend=backend, theta_min=theta_min, theta_max=theta_max,
                                      m=m, npoints=npoints)
    downbone_point = upbone_points.copy()
    downbone_point[:, 1] = -downbone_point[:, 1]
    upbone_points = np.flipud(upbone_points)
    pts = np.vstack((downbone_point, backbone_points, upbone_points))

    return pts



########### main panel ###############
if __name__ == "__main__":
    gf.clear_cache()
    c = gf.Component("test_pattern")
    pts = grating_taper_pts(width=0.5, lp=10, xp=0, backend=50, taper_angle=60, m=1.2)
    pts2 = grating_tooth_pts(width=0.5, lp=10, xp=0)
    c.add_polygon(pts, layer=(10, 0))
    c.add_polygon(pts2, layer=(6, 0))
    c.show()