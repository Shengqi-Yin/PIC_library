from env import *

##########################################
def spiral_archimedean(
    min_bend_radius: float, separation: float, number_of_loops: float, npoints: int
) -> Path:
    """Returns an Archimedean spiral.
    Args:
        min_bend_radius: Inner radius of the spiral.
        separation: Separation between the loops in um.
        number_of_loops: number of loops.
        npoints: number of Points.
    """
    return Path(
        np.array(
            [
                (separation / np.pi * theta + min_bend_radius)
                * np.array((np.cos(theta), np.sin(theta)))
                for theta in np.linspace(0, number_of_loops * 2 * np.pi, npoints)
            ]
        )
    )

if __name__ == "__main__":
    print("")