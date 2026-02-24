"""
STAAD Parametric Floodwall Modeler - Enhanced with 3D Visualization
Generates 3D floodwall models composed of 1ft x 1ft plates
Components: Wall and Slab
Exports to STAAD Pro format (.std)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


class STAADFloodwallModelerPlus:
    def __init__(self, root):
        self.root = root
        self.root.title("STAAD Parametric Floodwall Modeler - Enhanced")
        self.root.geometry("1000x950")
        self.root.resizable(True, True)
        
        self.nodes = []
        self.plates = []
        self.node_counter = 1
        self.plate_counter = 1
        
        # Create GUI
        self.create_widgets()
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="STAAD Floodwall Modeler - 1ft x 1ft Plates", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Floodwall Parameters", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Wall Parameters
        wall_frame = ttk.LabelFrame(input_frame, text="Wall Component", padding="8")
        wall_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(wall_frame, text="Height (ft):").grid(row=0, column=0, sticky=tk.W)
        self.wall_height = ttk.Entry(wall_frame, width=10)
        self.wall_height.insert(0, "10")
        self.wall_height.grid(row=0, column=1, padx=5)
        
        ttk.Label(wall_frame, text="Width (ft):").grid(row=1, column=0, sticky=tk.W)
        self.wall_width = ttk.Entry(wall_frame, width=10)
        self.wall_width.insert(0, "20")
        self.wall_width.grid(row=1, column=1, padx=5)
        
        ttk.Label(wall_frame, text="Thickness (ft):").grid(row=2, column=0, sticky=tk.W)
        self.wall_thickness = ttk.Entry(wall_frame, width=10)
        self.wall_thickness.insert(0, "1")
        self.wall_thickness.grid(row=2, column=1, padx=5)
        
        # Slab Parameters
        slab_frame = ttk.LabelFrame(input_frame, text="Slab Component", padding="8")
        slab_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(slab_frame, text="Length (ft):").grid(row=0, column=0, sticky=tk.W)
        self.slab_length = ttk.Entry(slab_frame, width=10)
        self.slab_length.insert(0, "20")
        self.slab_length.grid(row=0, column=1, padx=5)
        
        ttk.Label(slab_frame, text="Width (ft):").grid(row=1, column=0, sticky=tk.W)
        self.slab_width = ttk.Entry(slab_frame, width=10)
        self.slab_width.insert(0, "15")
        self.slab_width.grid(row=1, column=1, padx=5)
        
        ttk.Label(slab_frame, text="Thickness (ft):").grid(row=2, column=0, sticky=tk.W)
        self.slab_thickness = ttk.Entry(slab_frame, width=10)
        self.slab_thickness.insert(0, "1.5")
        self.slab_thickness.grid(row=2, column=1, padx=5)
        
        # Material Properties
        material_frame = ttk.LabelFrame(input_frame, text="Material Properties", padding="8")
        material_frame.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(material_frame, text="Young's Modulus (ksi):").grid(row=0, column=0, sticky=tk.W)
        self.youngs_modulus = ttk.Entry(material_frame, width=10)
        self.youngs_modulus.insert(0, "3600")
        self.youngs_modulus.grid(row=0, column=1, padx=5)
        
        ttk.Label(material_frame, text="Poisson's Ratio:").grid(row=1, column=0, sticky=tk.W)
        self.poisson_ratio = ttk.Entry(material_frame, width=10)
        self.poisson_ratio.insert(0, "0.17")
        self.poisson_ratio.grid(row=1, column=1, padx=5)
        
        ttk.Label(material_frame, text="Density (pcf):").grid(row=2, column=0, sticky=tk.W)
        self.density = ttk.Entry(material_frame, width=10)
        self.density.insert(0, "150")
        self.density.grid(row=2, column=1, padx=5)
        
        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(button_frame, text="Generate Model", command=self.generate_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Visualize 3D", command=self.visualize_3d).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export to STAAD", command=self.export_staad).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Model", command=self.clear_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Statistics", command=self.view_statistics).pack(side=tk.LEFT, padx=5)
        
        # Output Frame
        output_frame = ttk.LabelFrame(main_frame, text="Model Information", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Text widget for output
        scrollbar = ttk.Scrollbar(output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.output_text = tk.Text(output_frame, height=20, width=120, yscrollcommand=scrollbar.set)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.output_text.yview)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def validate_inputs(self):
        """Validate input parameters"""
        try:
            wall_h = float(self.wall_height.get())
            wall_w = float(self.wall_width.get())
            wall_t = float(self.wall_thickness.get())
            slab_l = float(self.slab_length.get())
            slab_w = float(self.slab_width.get())
            slab_th = float(self.slab_thickness.get())
            
            if any(x <= 0 for x in [wall_h, wall_w, wall_t, slab_l, slab_w, slab_th]):
                messagebox.showerror("Error", "All dimensions must be positive!")
                return False
            return True
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
            return False
    
    def generate_model(self):
        """Generate the STAAD model"""
        if not self.validate_inputs():
            return
        
        # Clear previous model
        self.nodes = []
        self.plates = []
        self.node_counter = 1
        self.plate_counter = 1
        
        wall_h = float(self.wall_height.get())
        wall_w = float(self.wall_width.get())
        wall_t = float(self.wall_thickness.get())
        slab_l = float(self.slab_length.get())
        slab_w = float(self.slab_width.get())
        slab_th = float(self.slab_thickness.get())
        
        # Generate wall
        self.generate_wall(wall_h, wall_w, wall_t)
        
        # Generate slab (at base of wall)
        self.generate_slab(slab_l, slab_w, slab_th, wall_w)
        
        self.update_output()
        messagebox.showinfo("Success", f"Model generated!\nNodes: {len(self.nodes)}\nPlates: {len(self.plates)}")
    
    def generate_wall(self, height, width, thickness):
        """Generate wall component using 1ft x 1ft plates (Y-Z plane)"""
        plate_size = 1.0  # 1 ft x 1 ft plates
        
        # Calculate number of divisions
        height_divisions = int(height)
        width_divisions = int(width)
        
        # Generate nodes for wall (2D grid on Y-Z plane)
        # Y: width direction (0 to width)
        # Z: height direction (0 to height)
        node_map = {}
        
        for i in range(width_divisions + 1):
            for j in range(height_divisions + 1):
                x = 0.0  # All nodes at x=0
                y = i * plate_size
                z = j * plate_size
                node_id = self.node_counter
                self.nodes.append({
                    'id': node_id,
                    'x': x,
                    'y': y,
                    'z': z,
                    'component': 'wall'
                })
                node_map[(i, j)] = node_id
                self.node_counter += 1
        
        # Generate plates for wall (4-node elements)
        for i in range(width_divisions):
            for j in range(height_divisions):
                # Define 4 corners of plate element
                nodes_plate = [
                    node_map[(i, j)],
                    node_map[(i+1, j)],
                    node_map[(i+1, j+1)],
                    node_map[(i, j+1)]
                ]
                
                self.plates.append({
                    'id': self.plate_counter,
                    'nodes': nodes_plate,
                    'component': 'wall'
                })
                self.plate_counter += 1
    
    def generate_slab(self, length, width, thickness, wall_width):
        """Generate slab component at base of wall (X-Z plane for horizontal surface)"""
        plate_size = 1.0  # 1 ft x 1 ft plates
        
        # Calculate number of divisions
        length_divisions = int(length)
        width_divisions = int(width)
        
        # Position slab at base level (z=0)
        # X: length direction
        # Z: always at 0 (horizontal plane at base)
        z_offset = 0.0
        x_offset = -((length - wall_width) / 2)  # Center slab relative to wall
        y_offset = 0.0  # Start at y=0
        
        node_map = {}
        
        for i in range(length_divisions + 1):
            for j in range(width_divisions + 1):
                x = x_offset + i * plate_size
                y = y_offset + j * plate_size
                z = z_offset  # All nodes on horizontal plane (z=0)
                node_id = self.node_counter
                self.nodes.append({
                    'id': node_id,
                    'x': x,
                    'y': y,
                    'z': z,
                    'component': 'slab'
                })
                node_map[(i, j)] = node_id
                self.node_counter += 1
        
        # Generate plates for slab (4-node elements)
        for i in range(length_divisions):
            for j in range(width_divisions):
                nodes_plate = [
                    node_map[(i, j)],
                    node_map[(i+1, j)],
                    node_map[(i+1, j+1)],
                    node_map[(i, j+1)]
                ]
                
                self.plates.append({
                    'id': self.plate_counter,
                    'nodes': nodes_plate,
                    'component': 'slab'
                })
                self.plate_counter += 1
    
    def visualize_3d(self):
        """Create 3D visualization of the model"""
        if not self.nodes:
            messagebox.showerror("Error", "Please generate a model first!")
            return
        
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot wall elements
        wall_verts = []
        wall_color = 'lightblue'
        
        slab_verts = []
        slab_color = 'lightcoral'
        
        for plate in self.plates:
            # Get node coordinates
            verts = []
            for node_id in plate['nodes']:
                node = next(n for n in self.nodes if n['id'] == node_id)
                verts.append([node['x'], node['y'], node['z']])
            
            # Create hexahedron faces
            faces = [
                [verts[0], verts[1], verts[5], verts[4]],
                [verts[2], verts[3], verts[7], verts[6]],
                [verts[0], verts[3], verts[7], verts[4]],
                [verts[1], verts[2], verts[6], verts[5]],
                [verts[0], verts[1], verts[2], verts[3]],
                [verts[4], verts[5], verts[6], verts[7]]
            ]
            
            if plate['component'] == 'wall':
                wall_verts.extend(faces)
            else:
                slab_verts.extend(faces)
        
        # Add wall
        if wall_verts:
            wall_collection = Poly3DCollection(wall_verts, alpha=0.7, facecolor=wall_color, edgecolor='black', linewidth=0.5)
            ax.add_collection3d(wall_collection)
        
        # Add slab
        if slab_verts:
            slab_collection = Poly3DCollection(slab_verts, alpha=0.7, facecolor=slab_color, edgecolor='black', linewidth=0.5)
            ax.add_collection3d(slab_collection)
        
        # Set labels and limits
        ax.set_xlabel('X (ft)')
        ax.set_ylabel('Y (ft)')
        ax.set_zlabel('Z (ft)')
        ax.set_title('STAAD Floodwall Model - 3D View')
        
        # Set equal aspect ratio
        xs = [n['x'] for n in self.nodes]
        ys = [n['y'] for n in self.nodes]
        zs = [n['z'] for n in self.nodes]
        
        ax.set_xlim([min(xs), max(xs)])
        ax.set_ylim([min(ys), max(ys)])
        ax.set_zlim([min(zs), max(zs)])
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=wall_color, edgecolor='black', label='Wall'),
            Patch(facecolor=slab_color, edgecolor='black', label='Slab')
        ]
        ax.legend(handles=legend_elements, loc='upper left')
        
        plt.tight_layout()
        plt.show()
    
    def update_output(self):
        """Update output text widget"""
        self.output_text.delete(1.0, tk.END)
        
        output = "=" * 100 + "\n"
        output += "STAAD FLOODWALL MODEL\n"
        output += "=" * 100 + "\n\n"
        
        output += f"TOTAL NODES: {len(self.nodes)}\n"
        output += f"TOTAL ELEMENTS: {len(self.plates)}\n\n"
        
        # Component summary
        wall_nodes = len([n for n in self.nodes if n['component'] == 'wall'])
        slab_nodes = len([n for n in self.nodes if n['component'] == 'slab'])
        wall_plates = len([p for p in self.plates if p['component'] == 'wall'])
        slab_plates = len([p for p in self.plates if p['component'] == 'slab'])
        
        output += "COMPONENT SUMMARY:\n"
        output += "-" * 100 + "\n"
        output += f"Wall:  {wall_nodes:6d} nodes,  {wall_plates:6d} elements\n"
        output += f"Slab:  {slab_nodes:6d} nodes,  {slab_plates:6d} elements\n\n"
        
        # Bounding box
        if self.nodes:
            xs = [n['x'] for n in self.nodes]
            ys = [n['y'] for n in self.nodes]
            zs = [n['z'] for n in self.nodes]
            
            output += "BOUNDING BOX:\n"
            output += "-" * 100 + "\n"
            output += f"X Range: {min(xs):10.2f} to {max(xs):10.2f} ft (Length: {max(xs) - min(xs):.2f} ft)\n"
            output += f"Y Range: {min(ys):10.2f} to {max(ys):10.2f} ft (Length: {max(ys) - min(ys):.2f} ft)\n"
            output += f"Z Range: {min(zs):10.2f} to {max(zs):10.2f} ft (Height: {max(zs) - min(zs):.2f} ft)\n\n"
        
        # Sample nodes
        output += "SAMPLE NODES (first 15):\n"
        output += "-" * 100 + "\n"
        output += "Node ID        X (ft)        Y (ft)        Z (ft)    Component\n"
        output += "-" * 100 + "\n"
        for node in self.nodes[:15]:
            output += f"{node['id']:7d}  {node['x']:12.2f}  {node['y']:12.2f}  {node['z']:12.2f}    {node['component']:10s}\n"
        
        if len(self.nodes) > 15:
            output += f"... and {len(self.nodes) - 15} more nodes\n"
        
        self.output_text.insert(tk.END, output)
    
    def view_statistics(self):
        """Display detailed statistics"""
        if not self.nodes:
            messagebox.showwarning("No Model", "Please generate a model first!")
            return
        
        wall_nodes = len([n for n in self.nodes if n['component'] == 'wall'])
        slab_nodes = len([n for n in self.nodes if n['component'] == 'slab'])
        wall_plates = len([p for p in self.plates if p['component'] == 'wall'])
        slab_plates = len([p for p in self.plates if p['component'] == 'slab'])
        
        # Calculate volume
        wall_volume = wall_plates * 1.0  # Each element is 1 cu.ft
        slab_volume = slab_plates * 1.0
        
        stats = f"""
        MODEL STATISTICS
        ================
        
        NODES:
          Total: {len(self.nodes)}
          Wall:  {wall_nodes}
          Slab:  {slab_nodes}
        
        ELEMENTS (1 ft × 1 ft plates):
          Total: {len(self.plates)}
          Wall:  {wall_plates}
          Slab:  {slab_plates}
        
        VOLUME:
          Wall:  {wall_volume:.2f} cubic feet
          Slab:  {slab_volume:.2f} cubic feet
          Total: {wall_volume + slab_volume:.2f} cubic feet
        
        MATERIAL PROPERTIES:
          Young's Modulus: {self.youngs_modulus.get()} ksi
          Poisson's Ratio: {self.poisson_ratio.get()}
          Density: {self.density.get()} pcf
          
        PARAMETERS:
          Wall Height:    {self.wall_height.get()} ft
          Wall Width:     {self.wall_width.get()} ft
          Wall Thickness: {self.wall_thickness.get()} ft
          
          Slab Length:    {self.slab_length.get()} ft
          Slab Width:     {self.slab_width.get()} ft
          Slab Thickness: {self.slab_thickness.get()} ft
        """
        
        messagebox.showinfo("Model Statistics", stats)
    
    def clear_model(self):
        """Clear the current model"""
        self.nodes = []
        self.plates = []
        self.node_counter = 1
        self.plate_counter = 1
        self.output_text.delete(1.0, tk.END)
        messagebox.showinfo("Cleared", "Model cleared successfully!")
    
    def export_staad(self):
        """Export model to STAAD Pro format"""
        if not self.nodes:
            messagebox.showerror("Error", "Please generate a model first!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".std",
            filetypes=[("STAAD Files", "*.std"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w') as f:
                # STAAD Pro header
                f.write("STAAD PLANE\n")
                f.write("FLOODWALL MODEL - PARAMETRIC\n")
                f.write("UNITS FEET KIP\n\n")
                
                # Joint coordinates (changed from NODE COORDINATES)
                f.write("JOINT COORDINATES\n")
                for node in self.nodes:
                    f.write(f"{node['id']:6d}  {node['x']:12.4f}  {node['y']:12.4f}  {node['z']:12.4f}\n")
                
                f.write("\n")
                
                # Element definitions (4-node shell elements)
                f.write("ELEMENT INCIDENCES\n")
                for plate in self.plates:
                    nodes_str = "  ".join(f"{n}" for n in plate['nodes'])
                    f.write(f"{plate['id']:6d}  {nodes_str}\n")
                
                f.write("\nFINISH\n")
            
            messagebox.showinfo("Success", f"Model exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")


def main():
    root = tk.Tk()
    app = STAADFloodwallModelerPlus(root)
    root.mainloop()


if __name__ == "__main__":
    main()
