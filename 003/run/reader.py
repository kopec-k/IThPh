import re
import sympy as sp
from sympy.physics.mechanics import dynamicsymbols
from lagrangian import LagrangianToC

def load_simulation(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    part_match = re.search(r"PARTICLES:\s*(\d+)", content)
    num_particles = int(part_match.group(1)) if part_match else 1

    coord_match = re.search(r"COORDINATES:\s*(.*)", content)
    param_match = re.search(r"PARAMETERS:\s*(.*)", content)
    lagr_match = re.search(r"LAGRANGIAN:\s*(.*)", content)
    trans_match = re.search(r"TRANSFORMATIONS:\s*(.*?)\s*LAGRANGIAN:", content, re.DOTALL)

    init_pos_match = re.search(r"INITIAL_POSITIONS:\s*(.*?)(?:INITIAL_VELOCITIES:|$)", content, re.DOTALL)
    init_vel_match = re.search(r"INITIAL_VELOCITIES:\s*(.*?)(?:$)", content, re.DOTALL)

    init_positions = []
    if init_pos_match:
        for line in init_pos_match.group(1).strip().split('\n'):
            if line.strip():
                init_positions.append([float(x) for x in line.split(',')])

    init_velocities = []
    if init_vel_match:
        for line in init_vel_match.group(1).strip().split('\n'):
            if line.strip():
                init_velocities.append([float(x) for x in line.split(',')])

    coord_names = [c.strip() for c in coord_match.group(1).split(",")]
    t = dynamicsymbols._t
    q = [dynamicsymbols(name) for name in coord_names]
    q_dot = [sp.diff(qi, t) for qi in q]

    local_dict = {}
    for name, qi, qdi in zip(coord_names, q, q_dot):
        local_dict[name] = qi
        local_dict[f"{name}_dot"] = qdi

    param_pairs = re.findall(r"(\w+)\s*=\s*([\d.]+)", param_match.group(1))
    subs_dict = {sp.Symbol(p_name): float(p_val) for p_name, p_val in param_pairs}

    expr_x, expr_y = "q[i].x", "q[i].y"
    if trans_match:
        for line in trans_match.group(1).strip().split("\n"):
            if "=" in line:
                var, expr = line.split("=")
                var = var.strip().upper()
                expr_str = expr.strip()
                for idx, name in enumerate(coord_names):
                    comp = 'x' if idx == 0 else 'y'
                    expr_str = re.sub(r'\b' + name + r'\b', f"q[i].{comp}", expr_str)
                expr_str = expr_str.replace("cos", "cosf").replace("sin", "sinf")
                if var == "X": expr_x = expr_str
                if var == "Y": expr_y = expr_str

    c_trans_code = f"""
void transform_to_cartesian(Vector2D* q, Vector2D* cart, size_t N) {{
    for(size_t i = 0; i < N; ++i) {{
        cart[i].x = {expr_x};
        cart[i].y = {expr_y};
    }}
}}
"""
    
    L = sp.sympify(lagr_match.group(1).strip(), locals=local_dict).subs(subs_dict)
    gen = LagrangianToC(L, q)
    gen.vectorType = "Vector2D"
    c_eom_code = gen.generate_c_function("eom_generated", collapse_constants=True)

    return c_eom_code + "\n" + c_trans_code, num_particles, init_positions, init_velocities