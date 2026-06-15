# === IMPORTS ===
# Standard library imports
from sys import argv

# Third party imports
import numpy as np

import sympy as sp
from sympy.physics.mechanics import dynamicsymbols

from reader import read_input

# Local imports
import cprototype as cp
import animation as anim
from ccompiler import CSharedLibraryCompiler

# === CONSTANTS ===
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
dt                  = 1   # Timestep for the simulation

# === INPUT ===

c_code_str = read_input()

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
positions = [_libsolver.vector(x=RADIUS * np.cos(2 * np.pi * i / NUMBER_OF_PARTICLES),
                               y=RADIUS * np.sin(2 * np.pi * i / NUMBER_OF_PARTICLES))
             for i in range(NUMBER_OF_PARTICLES)]
velocities = [_libsolver.vector(x=0, y=0) for i in range(NUMBER_OF_PARTICLES)]

# === PLOTTING SETUP ===
ani = anim.Animation2D(vector_factory=_libsolver.vector,
                       c_arr=_libsolver.c_arr,
                       next_step=_libsolver.next_step,
                       positions=positions,
                       velocities=velocities,
                       dt=dt,
                       NUMBER_OF_PARTICLES=NUMBER_OF_PARTICLES)
ani.create_canvas()

# === RUN ANIMATION ===
ani.run_animation()
