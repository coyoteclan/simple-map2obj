import re
import os
import json
import sys
#from tabulate import tabulate
from modules.thirdparty.tabulate import tabulate
from modules.thirdparty.termcolor import termcolor
#from modules.utils import Vector3
from modules.utils import parse_planes
#from modules.utils import intersect_planes
from modules.utils import calculate_vertices

def merge_objs(output_file, input_files):
    vertex_offset = 0
    file_count = 0

    with open(output_file, 'w') as out_file:
        for obj_file in input_files:
            with open(obj_file, 'r') as in_file:
                for line in in_file:
                    if line.startswith('v '):  # Vertex data
                        out_file.write(line)
                        vertex_offset += 1
                    elif line.startswith('f '):  # Face data
                        face = line.split()
                        new_face = ['f']
                        for vertex in face[1:]:
                            """indices = list(map(int, vertex.split('/')))
                            indices[0] += vertex_offset  # Adjust vertex index
                            new_face.append('/'.join(map(str, indices)))"""
                            if file_count != 0:
                                vertex_offset = file_count * 8
                                vertex = str(int(vertex) + vertex_offset)
                            new_face.append(vertex)
                        out_file.write(' '.join(new_face) + '\n')
                    elif line.startswith('o ') or line.startswith('g ') or line.startswith('#'):
                        if line.endswith("Kazam"):
                            continue
                        out_file.write(line)  # Preserve object names, groups, and comments
                file_count += 1
    
    if not saveworkfiles:
        for file in input_files:
            os.remove(file)
        print("Removed working files")

    print(f"Merged OBJ file saved as {output_file}")

def create_obj(obj_filename, brushname, vertices, workingfiles):
    global godot
    workingfile = obj_filename[:-4] + "." + brushname + ".obj"
    
    if not os.path.isfile(workingfile):
        with open(workingfile, 'w') as obj_file:
            obj_file.write("# map to obj converter by Kazam\n")
            obj_file.close()
    
    with open(workingfile, 'a') as obj_file:
        obj_file.write(f"# Brush {brushname}\n")
        _brushname = brushname
        if godot:
            _brushname = brushname + "-col"
        obj_file.write(f"o {_brushname}\n")
        
        # Write vertices
        for vertex in vertices:
            obj_file.write(f"v {vertex[0] / 64} {vertex[2] / 64} {vertex[1] / 64}\n")
        
        # Write faces
        obj_file.write("f 1 2 4 3\n") # Bottom face 
        obj_file.write("f 5 7 8 6\n") # Top face 
        obj_file.write("f 1 5 7 3\n") # Side face 1 
        obj_file.write("f 2 6 8 4\n") # Side face 2 
        obj_file.write("f 3 7 8 4\n") # Side face 3 
        obj_file.write("f 1 2 6 5\n") # Side face 4
    
    workingfiles.append(workingfile)

def convert(filepath):
    with open(filepath, 'r') as file:
        map_data = file.readlines()
    
    brushes = {"Brushes": {}}
    
    for line in map_data:
        if line.startswith("// brush"):
            brush_data = []
            for i in range(6):
                brush_data.append(map_data[map_data.index(line) + 2 + i].strip())
            
            #brushes["Brushes"]["brush_"+line[-2]] = brush_data
            brush_id = re.split(" ", line.strip())[2]
            brushes["Brushes"]["brush_" + brush_id] = brush_data
        
    with open(filepath[:-3] + "json", 'w') as file:
        json.dump(brushes, file, indent=4)
        file.close()
    
    with open(filepath[:-3] + "json", 'r') as jsonfile:
        data = json.load(jsonfile)
        key = data.get("Brushes")
        workingfiles = []
        #keykey = key.get("brush_0")
        for keykey in key:
            keykeydata = key.get(keykey)
            
            planes = parse_planes(keykeydata)
            vertices = calculate_vertices(planes)
            objfile = filepath[:-3] + "obj"
            create_obj(objfile, keykey, vertices, workingfiles)
        
    merge_objs(filepath[:-3] + "obj", workingfiles)
    workingfiles = []

def init():
    global saveworkfiles
    global godot
    htable_head = [termcolor.colored("Option", "light_yellow"), termcolor.colored("Description", "light_blue")]
    htable_rows = [[termcolor.colored("-h, --help, --usage", "light_cyan"), termcolor.colored("Shows this help message.", "light_magenta")],
                   [termcolor.colored("-G, --godot", "light_cyan"), termcolor.colored("Adds \"-col\" prefix to object names.", "light_magenta")],
                   [termcolor.colored("-S, --save", "light_cyan"), termcolor.colored("Keep individual brush files.", "light_magenta")]]
    htable = tabulate(htable_rows, htable_head, tablefmt="fancy_grid")
    help = f"""CoD Map to Wavefront Obj converter.
{termcolor.colored("Discord", "blue")}: {termcolor.colored("kazam0180", "green")} 
{termcolor.colored("Options", "light_red")}: \n{htable}"""

    if not (len(sys.argv) < 2):
        for arg in sys.argv[1:]:
            if arg == "-h" or arg == "--help" or arg == "--usage":
                print(help)
                exit()
            elif arg == "-G" or arg == "--godot":
                godot = True
            elif arg == "-S" or arg == "--save":
                saveworkfiles = True
    
    table_head = [termcolor.colored("Option", "light_yellow"), termcolor.colored("Value", "light_blue")]
    table_rows = [[termcolor.colored("Save Working Files", "light_cyan"), termcolor.colored(str(saveworkfiles), "light_magenta")],
                  [termcolor.colored("Godot Collisions", "light_cyan"), termcolor.colored(str(godot), "light_magenta")]]
    table = tabulate(table_rows, table_head, stralign="center", tablefmt="fancy_grid")
    print(table)
    
    for root, _, files in os.walk(os.path.join(os.path.dirname(os.path.realpath(__file__)), "maps")):
        for file in files:
            if file.endswith(".map"):
                convert(os.path.join(root, file))

if __name__ == "__main__":
    global saveworkfiles
    global godot
    saveworkfiles = False
    godot = False
    init()

"""for root, _, files in os.walk(os.path.join(os.path.dirname(os.path.realpath(__file__)), "maps")):
    for file in files:
        if file.endswith(".map"):
            convert(os.path.join(root, file))"""
