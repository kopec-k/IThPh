"""
A prototype Python script that demonstrates how to interface with a C library
"""

# === IMPORTS ===
# Numpy (https://numpy.org/)
# and ctypes (https://docs.python.org/3/library/ctypes.html)
import numpy as np
from ctypes import c_float, c_int, Structure, POINTER, byref, cdll


# === CTYPES STRUCTURE DEFINITION ===
class Vector2D(Structure):
    """
    A ctypes Structure to represent a 2D vector, allowing it
    to be passed to and from the C library.
    """
    _fields_ = [("x", c_float),
                ("y", c_float)]

    def __repr__(self):
        """String representation for debugging."""
        return f"({self.x:.4f}, {self.y:.4f})"

    def __call__(self, data, i):
        """
        A helper method to update a numpy array (for plotting)
        with this vector's data at a specific index 'i'.
        """
        data[i, :] = np.array((self.x, self.y))

class Vector3D(Structure):
    """
    A ctypes Structure to represent a 3D vector, allowing it
    to be passed to and from the C library.
    """
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("z", c_float)]

    def __repr__(self):
        """String representation for debugging."""
        return f"({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"

    def __call__(self, data, i):
        """
        A helper method to update a numpy array (for plotting)
        with this vector's data at a specific index 'i'.
        """
        data[i, :] = np.array((self.x, self.y, self.z))

class EOMSolver:
    def __init__(self, path, NUMBER_OF_PARTICLES=1, DIMENSIONS=1):
        """
        Load a C shared library from the specified path.
        """
        self.lib = cdll.LoadLibrary(path)
        self.NUMBER_OF_PARTICLES = NUMBER_OF_PARTICLES
        self.DIMENSIONS = DIMENSIONS
        if DIMENSIONS == 1:
            self.c_vec_ptr = POINTER(c_float)  # Alias for pointer to Vector1D
            self._prototype_1D()
        elif DIMENSIONS == 2:
            self.c_vec_ptr = POINTER(Vector2D) # Alias for pointer to Vector2D
            self._prototype_2D()
        elif DIMENSIONS == 3:
            self.c_vec_ptr = POINTER(Vector3D) # Alias for pointer to Vector3D
            self._prototype_3D()
        else:
            raise ValueError("DIMENSIONS must be 1, 2, or 3.")
        self.next_step.restype = None


    def _prototype_1D(self):
        """
        Prototype the 1D next step function from the C library.
        Assuming function
        `void next_1D(float* coord, float* vel, float* new_coord, float* new_vel, float dt, size_t N);`
        exists in the C library.
        (IN coord, IN vel, OUT new_(pos|vel), IN dt, IN N)
        """
        self.next_step = self.lib.next_1D
        self.c_arr = c_float *self.NUMBER_OF_PARTICLES # Alias for pointer to an array of Vector1D
        self.next_step.argtypes = [self.c_vec_ptr, self.c_vec_ptr,
                                   self.c_vec_ptr, self.c_vec_ptr, c_float, c_int]

    def _prototype_2D(self):
        """
        Prototype the 2D next step function from the C library.
        Assuming function
        `void next_2D(Vector2D* coord, Vector2D* vel, Vector2D* new_coord, Vector2D* new_vel, float dt, size_t N);`
        exists in the C library.
        """
        self.next_step = self.lib.next_2D
        self.c_arr = Vector2D*self.NUMBER_OF_PARTICLES # Alias for pointer to an array of Vector2D
        self.next_step.argtypes = [self.c_vec_ptr, self.c_vec_ptr,
                                   self.c_vec_ptr, self.c_vec_ptr, c_float, c_int]

    def _prototype_3D(self):
        """
        Prototype the 3D next step function from the C library.
        Assuming function
        `void next_3D(Vector3D* coord, Vector3D* vel, Vector3D* new_coord, Vector3D* new_vel, float dt, size_t N);`
        exists in the C library.
        """
        self.next_step = self.lib.next_3D
        self.c_arr= Vector3D*self.NUMBER_OF_PARTICLES # Alias for pointer to an array of Vector3D
        self.next_step.argtypes = [self.c_vec_ptr, self.c_vec_ptr,
                                   self.c_vec_ptr, self.c_vec_ptr, c_float, c_int]
        # assess function exists in the C library.

    def vector(self, x=0.0, y=0.0, z=0.0):
        """
        Create a new vector instance based on the specified DIMENSIONS.
        """
        if self.DIMENSIONS == 1:
            return c_float(x)
        elif self.DIMENSIONS == 2:
            return Vector2D(x=x, y=y)
        elif self.DIMENSIONS == 3:
            return Vector3D(x=x, y=y, z=z)
        else:
            raise ValueError("DIMENSIONS must be 1, 2, or 3.")

    def transform_to_cartesian(self, q_list, cart_list, N):
        try:
            func = self.lib.transform_to_cartesian
        except AttributeError:
            print("Warning: No function transform_to_cartesian")
            return

        func.argtypes = [self.c_vec_ptr, self.c_vec_ptr, c_int]
        func.restype = None

        q_arr = self.c_arr(*q_list)
        cart_arr = self.c_arr(*cart_list)
        func(q_arr, cart_arr, N)

        for i in range(N):
            cart_list[i].x = cart_arr[i].x
            cart_list[i].y = cart_arr[i].y
    
    def step(self, coord_list, vel_list, dt):
        size = self.NUMBER_OF_PARTICLES
        new_coords = self.c_arr(*coord_list)
        new_vels = self.c_arr(*vel_list)
        
        c_coords = self.c_arr(*coord_list)
        c_vels = self.c_arr(*vel_list)
        
        self.next_step(c_coords, c_vels, new_coords, new_vels, float(dt), size)
        
        for i in range(size):
            coord_list[i].x = new_coords[i].x
            coord_list[i].y = new_coords[i].y
            vel_list[i].x = new_vels[i].x
            vel_list[i].y = new_vels[i].y
