# === IMPORTS ===
# Standard library imports
from sys import argv

# Third party imports
import numpy as np

import sympy as sp
from sympy.physics.mechanics import dynamicsymbols

from reader import load_simulation

# Local imports
import cprototype as cp
import animation as anim
from ccompiler import CSharedLibraryCompiler

# === CONSTANTS ===

"""
if len(argv) > 1:
    try:
        NUMBER_OF_PARTICLES = int(argv[1]) # Number of particles read from command line
    except ValueError as e:
        print(e)
        NUMBER_OF_PARTICLES = np.random.randint(1,23)
        print(f"Number of particles is now set to randomly chosen: {NUMBER_OF_PARTICLES}")
else:
    NUMBER_OF_PARTICLES = 1      # Number of particles in the simulation
RADIUS              = 1    # Initial radius for particle placement
dt                  = 0.1   # Timestep for the simulation
"""

if len(argv) > 1:
    try:
        filename = argv[1]
    except ValueError as e:
        print(e)
        filename = "simulations/harmonic.txt"
        print(f"Filename is now set to default: {filename}")
else:
    print("No input file provided. Using default: 'input.txt'")
    filename = "simulations/harmonic.txt"

dt = 0.1   # Timestep for the simulation

# === INPUT ===

c_code_str, NUMBER_OF_PARTICLES, init_pos, init_vel = load_simulation(filename)

with open("../solver/solver.c", "r") as f:
    original_solver_code = f.read()

solver_code = original_solver_code + "\n\n" + c_code_str

with open("../solver/solver_generated.c", "w") as f:
    f.write(solver_code)

# === C LIBRARY LOADING ===
ccompiler = CSharedLibraryCompiler(source_file="../solver/solver_generated.c")
__solver_path = ccompiler.compile()
_libsolver = cp.EOMSolver(__solver_path, NUMBER_OF_PARTICLES, DIMENSIONS=2)

# ======================================================================================

# === C LIBRARY LOADING ===
# Define the path to the compiled C library (.so file)
# This assumes 'libsolver.so' is in a 'solve' directory one level *up*
# from the directory containing this Python script.
#ccompiler = CSharedLibraryCompiler(source_file="../solver/solver.c")
#__solver_path = ccompiler.compile()
#_libsolver    = cp.EOMSolver(__solver_path, NUMBER_OF_PARTICLES, DIMENSIONS=2)

# ======================================================================================

# === INITIAL CONDITIONS ===

gen_positions = [_libsolver.vector(x=init_pos[i][0], y=init_pos[i][1]) for i in range(NUMBER_OF_PARTICLES)]
velocities = [_libsolver.vector(x=init_vel[i][0], y=init_vel[i][1]) for i in range(NUMBER_OF_PARTICLES)]

cartesian_positions = [_libsolver.vector(x=0, y=0) for i in range(NUMBER_OF_PARTICLES)]

_libsolver.transform_to_cartesian(gen_positions, cartesian_positions, NUMBER_OF_PARTICLES)

# positions = [_libsolver.vector(x=RADIUS * np.cos(2 * np.pi * i / NUMBER_OF_PARTICLES),
#                                y=RADIUS * np.sin(2 * np.pi * i / NUMBER_OF_PARTICLES))
#              for i in range(NUMBER_OF_PARTICLES)]
# velocities = [_libsolver.vector(x=0, y=0) for i in range(NUMBER_OF_PARTICLES)]

# === TRANSFORMATION ===

def proxy_next_step(*args, **kwargs):
    _libsolver.step(gen_positions, velocities, dt)
    _libsolver.transform_to_cartesian(gen_positions, cartesian_positions, NUMBER_OF_PARTICLES)

    #print(f"Gen: {gen_positions[1]} Cart: {cartesian_positions[1]}")

# === PLOTTING SETUP ===
#ani = anim.Animation2D(vector_factory=_libsolver.vector,
#                       c_arr=_libsolver.c_arr,
#                       next_step=_libsolver.next_step,
#                       positions=positions,
#                       velocities=velocities,
#                       dt=dt,
#                       NUMBER_OF_PARTICLES=NUMBER_OF_PARTICLES)

ani = anim.Animation2D(vector_factory=_libsolver.vector,
                       c_arr=_libsolver.c_arr,
                       next_step=proxy_next_step,
                       positions=cartesian_positions,
                       velocities=velocities,
                       dt=dt,
                       NUMBER_OF_PARTICLES=NUMBER_OF_PARTICLES)

ani.create_canvas()

# === RUN ANIMATION ===
ani.run_animation()
