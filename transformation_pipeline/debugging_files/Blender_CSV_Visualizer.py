import bpy
import csv

# Path to your CSV file
csv_file_path = "/home/manuel/HIWI/LARA/L01_S01_R22.csv"

# Function to create point cloud mesh
def create_point_cloud(points, name="PointCloud", scale=0.001):
    # Create a new mesh and object
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    
    # Link the object to the scene
    bpy.context.collection.objects.link(obj)
    
    # Create vertices
    vertices = [(float(x)*scale, float(y)*scale, float(z)*scale) for _, _, _, x, y, z in points]
    
    # Create mesh from vertices
    mesh.from_pydata(vertices, [], [])
    mesh.update()
    
    return obj

# Function to update point cloud based on the current frame
def update_point_cloud(frame_number):
    # Read CSV file
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        # Skip to the correct line for the current frame
        for i, row in enumerate(reader):
            if i == frame_number + 5:
                # Parse points from the row
                points = [tuple(row[i:i+6]) for i in range(2, len(row), 6)]
                # Clear existing point clouds
                for obj in bpy.data.objects:
                    if "PointCloud" in obj.name:
                        bpy.data.objects.remove(obj, do_unlink=True)
                # Create a new point cloud
                create_point_cloud(points)
                break

# Set the frame change handler
def frame_change_handler(scene):
    update_point_cloud(scene.frame_current)

# Set the initial point cloud
update_point_cloud(0)

# Add the frame change handler
bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(frame_change_handler)

