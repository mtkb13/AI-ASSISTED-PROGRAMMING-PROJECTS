"""
STAAD.Pro Warehouse Frame Builder with GUI
Parametric warehouse structural frame generator with user-defined dimensions
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
import traceback
import math

try:
    from openstaadpy import os_analytical
    STAAD_AVAILABLE = True
except ImportError:
    STAAD_AVAILABLE = False


class WarehouseFrameBuilder:
    """Parametric warehouse frame builder for STAAD.Pro"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("STAAD.Pro Warehouse Frame Builder - Parametric Design")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize variables
        self.staad = None
        self.is_running = False
        
        # Create UI
        self.create_ui()
        
        # Check STAAD availability
        if not STAAD_AVAILABLE:
            self.log_message("WARNING: openstaadpy not found. Install it to use this tool.", "warning")
    
    def create_ui(self):
        """Create the user interface"""
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_command(label="Load Configuration", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Export Log", command=self.export_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Parameter Guide", command=self.show_guide)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Warehouse Frame Builder - Parametric Design", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # Left column - Geometry Parameters
        geometry_frame = ttk.LabelFrame(main_frame, text="Warehouse Geometry", padding="10")
        geometry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5), pady=(0, 10))
        
        row = 0
        # Length
        ttk.Label(geometry_frame, text="Length (ft):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.length_var = tk.StringVar(value="100")
        ttk.Entry(geometry_frame, textvariable=self.length_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Width
        ttk.Label(geometry_frame, text="Width (ft):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.width_var = tk.StringVar(value="60")
        ttk.Entry(geometry_frame, textvariable=self.width_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Eave Height
        ttk.Label(geometry_frame, text="Eave Height (ft):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.eave_height_var = tk.StringVar(value="20")
        ttk.Entry(geometry_frame, textvariable=self.eave_height_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Ridge Height
        ttk.Label(geometry_frame, text="Ridge Height (ft):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.ridge_height_var = tk.StringVar(value="28")
        ttk.Entry(geometry_frame, textvariable=self.ridge_height_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Bay Spacing
        ttk.Label(geometry_frame, text="Bay Spacing (ft):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.bay_spacing_var = tk.StringVar(value="25")
        ttk.Entry(geometry_frame, textvariable=self.bay_spacing_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Number of Bays
        ttk.Label(geometry_frame, text="Number of Bays:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.num_bays_var = tk.StringVar(value="4")
        ttk.Entry(geometry_frame, textvariable=self.num_bays_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Frame Type
        ttk.Label(geometry_frame, text="Frame Type:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.frame_type_var = tk.StringVar(value="Rigid Frame")
        frame_combo = ttk.Combobox(geometry_frame, textvariable=self.frame_type_var,
                                   values=["Rigid Frame", "Truss Frame", "Portal Frame"],
                                   state="readonly", width=13)
        frame_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Include Bracing
        self.bracing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(geometry_frame, text="Include Roof Bracing", 
                       variable=self.bracing_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        row += 1
        # Include Purlins
        self.purlins_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(geometry_frame, text="Include Roof Purlins", 
                       variable=self.purlins_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        row += 1
        # Purlin Spacing
        ttk.Label(geometry_frame, text="Purlin Spacing (ft):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.purlin_spacing_var = tk.StringVar(value="5")
        ttk.Entry(geometry_frame, textvariable=self.purlin_spacing_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Right column - Properties and Loads
        properties_frame = ttk.LabelFrame(main_frame, text="Properties & Loads", padding="10")
        properties_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0), pady=(0, 10))
        
        row = 0
        # Unit System
        ttk.Label(properties_frame, text="Unit System:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.unit_var = tk.StringVar(value="FEET-KIP")
        unit_combo = ttk.Combobox(properties_frame, textvariable=self.unit_var,
                                  values=["FEET-KIP", "INCHES-KIP", "METER-KN"],
                                  state="readonly", width=13)
        unit_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Column Section
        ttk.Label(properties_frame, text="Column Section:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.column_section_var = tk.StringVar(value="W12X72")
        ttk.Entry(properties_frame, textvariable=self.column_section_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Rafter Section
        ttk.Label(properties_frame, text="Rafter Section:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.rafter_section_var = tk.StringVar(value="W18X35")
        ttk.Entry(properties_frame, textvariable=self.rafter_section_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Purlin Section
        ttk.Label(properties_frame, text="Purlin Section:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.purlin_section_var = tk.StringVar(value="C8X11.5")
        ttk.Entry(properties_frame, textvariable=self.purlin_section_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Bracing Section
        ttk.Label(properties_frame, text="Bracing Section:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.bracing_section_var = tk.StringVar(value="L40404")
        ttk.Entry(properties_frame, textvariable=self.bracing_section_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        ttk.Separator(properties_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        row += 1
        # Dead Load
        ttk.Label(properties_frame, text="Dead Load (psf):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.dead_load_var = tk.StringVar(value="15")
        ttk.Entry(properties_frame, textvariable=self.dead_load_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Live Load
        ttk.Label(properties_frame, text="Live Load (psf):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.live_load_var = tk.StringVar(value="20")
        ttk.Entry(properties_frame, textvariable=self.live_load_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Wind Load
        ttk.Label(properties_frame, text="Wind Load (psf):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.wind_load_var = tk.StringVar(value="25")
        ttk.Entry(properties_frame, textvariable=self.wind_load_var, width=15).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        row += 1
        # Include Self Weight
        self.selfweight_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(properties_frame, text="Include Self Weight",
                       variable=self.selfweight_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        row += 1
        # Include Load Combinations
        self.load_combo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(properties_frame, text="Include Load Combinations",
                       variable=self.load_combo_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Control Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.preview_button = ttk.Button(button_frame, text="Preview Model Info",
                                        command=self.preview_model, width=18)
        self.preview_button.grid(row=0, column=0, padx=5)
        
        self.build_button = ttk.Button(button_frame, text="Build Model",
                                       command=self.build_model, width=15)
        self.build_button.grid(row=0, column=1, padx=5)
        
        self.analyze_button = ttk.Button(button_frame, text="Build & Analyze",
                                        command=self.build_and_analyze, width=15)
        self.analyze_button.grid(row=0, column=2, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear Log",
                                       command=self.clear_log, width=15)
        self.clear_button.grid(row=0, column=3, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Build Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15, width=100)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags
        self.log_text.tag_config('info', foreground='black')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('error', foreground='red')
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def log_message(self, message, tag='info'):
        """Add a message to the log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message, tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared.")
    
    def set_buttons_state(self, state):
        """Enable or disable buttons"""
        self.preview_button['state'] = state
        self.build_button['state'] = state
        self.analyze_button['state'] = state
    
    def validate_parameters(self):
        """Validate user input parameters"""
        errors = []
        warnings = []
        
        try:
            # Geometry validation
            length = float(self.length_var.get())
            if length <= 0 or length > 1000:
                errors.append("Length must be between 0 and 1000 ft")
            
            width = float(self.width_var.get())
            if width <= 0 or width > 500:
                errors.append("Width must be between 0 and 500 ft")
            
            eave_height = float(self.eave_height_var.get())
            if eave_height <= 0 or eave_height > 100:
                errors.append("Eave height must be between 0 and 100 ft")
            
            ridge_height = float(self.ridge_height_var.get())
            if ridge_height <= eave_height:
                errors.append("Ridge height must be greater than eave height")
            
            bay_spacing = float(self.bay_spacing_var.get())
            if bay_spacing <= 0 or bay_spacing > 50:
                errors.append("Bay spacing must be between 0 and 50 ft")
            
            num_bays = int(self.num_bays_var.get())
            if num_bays < 1 or num_bays > 20:
                errors.append("Number of bays must be between 1 and 20")
            
            # Check if bays fit in length
            if num_bays * bay_spacing > length:
                warnings.append(f"Bays may exceed length: {num_bays} × {bay_spacing} = {num_bays*bay_spacing} ft > {length} ft")
            
            # Load validation
            dead_load = float(self.dead_load_var.get())
            if dead_load < 0 or dead_load > 100:
                errors.append("Dead load must be between 0 and 100 psf")
            
            live_load = float(self.live_load_var.get())
            if live_load < 0 or live_load > 100:
                errors.append("Live load must be between 0 and 100 psf")
            
            wind_load = float(self.wind_load_var.get())
            if wind_load < 0 or wind_load > 100:
                errors.append("Wind load must be between 0 and 100 psf")
            
            # Purlin validation
            if self.purlins_var.get():
                purlin_spacing = float(self.purlin_spacing_var.get())
                if purlin_spacing <= 0 or purlin_spacing > 10:
                    errors.append("Purlin spacing must be between 0 and 10 ft")
            
        except ValueError as e:
            errors.append(f"Invalid numeric input: {str(e)}")
        
        return errors, warnings
    
    def preview_model(self):
        """Show preview of model parameters and calculated values"""
        errors, warnings = self.validate_parameters()
        
        if errors:
            error_msg = "Please fix these errors:\n\n" + "\n".join(f"• {e}" for e in errors)
            messagebox.showerror("Validation Errors", error_msg)
            return
        
        try:
            length = float(self.length_var.get())
            width = float(self.width_var.get())
            eave_height = float(self.eave_height_var.get())
            ridge_height = float(self.ridge_height_var.get())
            bay_spacing = float(self.bay_spacing_var.get())
            num_bays = int(self.num_bays_var.get())
            
            # Calculate model statistics
            num_frames = num_bays + 1
            nodes_per_frame = 4 if self.frame_type_var.get() == "Rigid Frame" else 5
            total_nodes = num_frames * nodes_per_frame
            
            # Estimate members
            columns = num_frames * 2
            rafters = num_frames * 2
            base_members = columns + rafters
            
            if self.purlins_var.get():
                purlin_spacing = float(self.purlin_spacing_var.get())
                num_purlin_lines = int(width / (2 * purlin_spacing)) * 2 + 1
                purlin_members = num_purlin_lines * num_bays
            else:
                purlin_members = 0
            
            if self.bracing_var.get():
                bracing_members = num_bays * 4  # Estimate
            else:
                bracing_members = 0
            
            total_members = base_members + purlin_members + bracing_members
            
            roof_slope = math.atan2(ridge_height - eave_height, width / 2) * 180 / math.pi
            
            preview_text = f"""Warehouse Frame Model Preview
{'='*50}

GEOMETRY:
• Building Length: {length} ft
• Building Width: {width} ft
• Eave Height: {eave_height} ft
• Ridge Height: {ridge_height} ft
• Roof Slope: {roof_slope:.1f}°
• Bay Spacing: {bay_spacing} ft
• Number of Bays: {num_bays}
• Number of Frames: {num_frames}
• Frame Type: {self.frame_type_var.get()}

MODEL SIZE:
• Total Nodes: ~{total_nodes}
• Column Members: {columns}
• Rafter Members: {rafters}
• Purlin Members: {purlin_members if self.purlins_var.get() else 'Not included'}
• Bracing Members: {bracing_members if self.bracing_var.get() else 'Not included'}
• Total Members: ~{total_members}

SECTIONS:
• Columns: {self.column_section_var.get()}
• Rafters: {self.rafter_section_var.get()}
• Purlins: {self.purlin_section_var.get()}
• Bracing: {self.bracing_section_var.get()}

LOADS:
• Dead Load: {self.dead_load_var.get()} psf
• Live Load: {self.live_load_var.get()} psf
• Wind Load: {self.wind_load_var.get()} psf
• Self Weight: {'Yes' if self.selfweight_var.get() else 'No'}
• Load Combinations: {'Yes' if self.load_combo_var.get() else 'No'}

NOTES:
• Supports NOT assigned - configure manually in STAAD.Pro
• Column bases typically: Fixed or Pinned
"""
            
            if warnings:
                preview_text += "\nWARNINGS:\n" + "\n".join(f"• {w}" for w in warnings)
            
            # Show preview in a new window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Model Preview")
            preview_window.geometry("600x700")
            
            text_widget = scrolledtext.ScrolledText(preview_window, wrap=tk.WORD, width=70, height=40)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(1.0, preview_text)
            text_widget.config(state=tk.DISABLED)
            
            ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error generating preview: {str(e)}")
    
    def build_model(self):
        """Build the STAAD model"""
        if not STAAD_AVAILABLE:
            messagebox.showerror("Error", "openstaadpy module not found!\n"
                               "Please install it first:\npip install openstaadpy")
            return
        
        if self.is_running:
            messagebox.showwarning("Warning", "A build process is already running!")
            return
        
        # Validate parameters
        errors, warnings = self.validate_parameters()
        
        if errors:
            error_msg = "Please fix these errors:\n\n" + "\n".join(f"• {e}" for e in errors)
            messagebox.showerror("Validation Errors", error_msg)
            return
        
        if warnings:
            warning_msg = "Configuration warnings:\n\n" + "\n".join(f"• {w}" for w in warnings)
            warning_msg += "\n\nDo you want to continue?"
            if not messagebox.askyesno("Warnings", warning_msg):
                return
        
        # Run in separate thread
        thread = threading.Thread(target=self._build_model_thread, args=(False,))
        thread.daemon = True
        thread.start()
    
    def build_and_analyze(self):
        """Build the model and run analysis"""
        if not STAAD_AVAILABLE:
            messagebox.showerror("Error", "openstaadpy module not found!\n"
                               "Please install it first:\npip install openstaadpy")
            return
        
        if self.is_running:
            messagebox.showwarning("Warning", "A build process is already running!")
            return
        
        # Validate parameters
        errors, warnings = self.validate_parameters()
        
        if errors:
            error_msg = "Please fix these errors:\n\n" + "\n".join(f"• {e}" for e in errors)
            messagebox.showerror("Validation Errors", error_msg)
            return
        
        if warnings:
            warning_msg = "Configuration warnings:\n\n" + "\n".join(f"• {w}" for w in warnings)
            warning_msg += "\n\nDo you want to continue?"
            if not messagebox.askyesno("Warnings", warning_msg):
                return
        
        # Run in separate thread
        thread = threading.Thread(target=self._build_model_thread, args=(True,))
        thread.daemon = True
        thread.start()
    
    def _build_model_thread(self, run_analysis):
        """Thread worker for building model"""
        self.is_running = True
        self.set_buttons_state('disabled')
        self.progress.start(10)
        
        try:
            self._execute_build(run_analysis)
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            self.log_message(error_msg, 'error')
            self.log_message(traceback.format_exc(), 'error')
            messagebox.showerror("Build Failed", error_msg)
        finally:
            self.progress.stop()
            self.set_buttons_state('normal')
            self.is_running = False
            self.status_var.set("Ready")
    
    def _execute_build(self, run_analysis):
        """Execute the warehouse model building process"""
        
        # Helper function for array conversion
        from array import array as pyarray
        
        def to_int_array(lst):
            """Convert Python list to COM-compatible integer array"""
            if isinstance(lst, list):
                return pyarray('l', lst)
            return lst
        
        self.log_message("="*60)
        self.log_message("Starting Warehouse Frame Model Build...", 'info')
        
        # Get parameters
        length = float(self.length_var.get())
        width = float(self.width_var.get())
        eave_height = float(self.eave_height_var.get())
        ridge_height = float(self.ridge_height_var.get())
        bay_spacing = float(self.bay_spacing_var.get())
        num_bays = int(self.num_bays_var.get())
        
        # Connect to STAAD
        self.status_var.set("Connecting to STAAD.Pro...")
        self.log_message("Connecting to STAAD.Pro...")
        
        try:
            self.staad = os_analytical.connect()
        except Exception as e:
            raise Exception(f"Failed to connect to STAAD.Pro. Make sure STAAD.Pro is running with an empty model.\nError: {str(e)}")
        
        geo = self.staad.Geometry
        prop = self.staad.Property
        load = self.staad.Load
        
        # Set units
        self.status_var.set("Setting units...")
        unit_system = self.unit_var.get()
        if unit_system == "FEET-KIP":
            self.staad.SetInputUnits(1, 0)
            self.log_message("Units set to: FEET-KIP", 'success')
        elif unit_system == "INCHES-KIP":
            self.staad.SetInputUnits(0, 0)
            self.log_message("Units set to: INCHES-KIP", 'success')
        else:
            self.staad.SetInputUnits(2, 1)
            self.log_message("Units set to: METER-KN", 'success')
        
        self.staad.SaveModel(True)
        
        # Generate nodes for warehouse frames
        self.status_var.set("Creating nodes...")
        self.log_message("Creating nodes for warehouse frames...")
        
        node_id = 1
        node_coords = {}
        num_frames = num_bays + 1
        
        for frame_num in range(num_frames):
            x = frame_num * bay_spacing
            
            # Left column base
            node_coords[node_id] = (x, 0, 0)
            node_id += 1
            
            # Left column top (eave)
            node_coords[node_id] = (x, eave_height, 0)
            node_id += 1
            
            # Ridge
            node_coords[node_id] = (x, ridge_height, width / 2)
            node_id += 1
            
            # Right column top (eave)
            node_coords[node_id] = (x, eave_height, width)
            node_id += 1
            
            # Right column base
            node_coords[node_id] = (x, 0, width)
            node_id += 1
        
        # Create nodes in STAAD
        for nid, (x, y, z) in node_coords.items():
            geo.CreateNode(nid, x, y, z)
        
        self.log_message(f"Created {len(node_coords)} nodes for {num_frames} frames", 'success')
        
        # Generate members
        self.status_var.set("Creating members...")
        self.log_message("Creating frame members...")
        
        member_id = 1
        member_incidence = {}
        column_members = []
        rafter_members = []
        
        for frame_num in range(num_frames):
            base_node = frame_num * 5 + 1
            
            # Left column
            n1 = base_node
            n2 = base_node + 1
            member_incidence[member_id] = (n1, n2)
            column_members.append(member_id)
            member_id += 1
            
            # Left rafter
            n1 = base_node + 1
            n2 = base_node + 2
            member_incidence[member_id] = (n1, n2)
            rafter_members.append(member_id)
            member_id += 1
            
            # Right rafter
            n1 = base_node + 2
            n2 = base_node + 3
            member_incidence[member_id] = (n1, n2)
            rafter_members.append(member_id)
            member_id += 1
            
            # Right column
            n1 = base_node + 3
            n2 = base_node + 4
            member_incidence[member_id] = (n1, n2)
            column_members.append(member_id)
            member_id += 1
        
        # Create purlins if requested
        purlin_members = []
        if self.purlins_var.get():
            self.log_message("Creating purlin members...")
            purlin_spacing = float(self.purlin_spacing_var.get())
            
            # Calculate purlin positions along roof slope
            num_purlins_per_side = int((width / 2) / purlin_spacing)
            
            for bay_num in range(num_bays):
                for side in [0, 1]:  # Left and right sides
                    for p in range(1, num_purlins_per_side):
                        # Calculate position
                        ratio = p / num_purlins_per_side
                        
                        if side == 0:  # Left side
                            base_node1 = bay_num * 5 + 2  # Left eave
                            ridge_node1 = bay_num * 5 + 3  # Ridge
                            base_node2 = (bay_num + 1) * 5 + 2
                            ridge_node2 = (bay_num + 1) * 5 + 3
                        else:  # Right side
                            base_node1 = bay_num * 5 + 3  # Ridge
                            ridge_node1 = bay_num * 5 + 4  # Right eave
                            base_node2 = (bay_num + 1) * 5 + 3
                            ridge_node2 = (bay_num + 1) * 5 + 4
                        
                        # Create intermediate nodes for purlins
                        x1 = bay_num * bay_spacing
                        x2 = (bay_num + 1) * bay_spacing
                        
                        y1 = node_coords[base_node1][1] + ratio * (node_coords[ridge_node1][1] - node_coords[base_node1][1])
                        z1 = node_coords[base_node1][2] + ratio * (node_coords[ridge_node1][2] - node_coords[base_node1][2])
                        
                        y2 = node_coords[base_node2][1] + ratio * (node_coords[ridge_node2][1] - node_coords[base_node2][1])
                        z2 = node_coords[base_node2][2] + ratio * (node_coords[ridge_node2][2] - node_coords[base_node2][2])
                        
                        # Create purlin nodes
                        purlin_node1 = node_id
                        node_coords[node_id] = (x1, y1, z1)
                        geo.CreateNode(node_id, x1, y1, z1)
                        node_id += 1
                        
                        purlin_node2 = node_id
                        node_coords[node_id] = (x2, y2, z2)
                        geo.CreateNode(node_id, x2, y2, z2)
                        node_id += 1
                        
                        # Create purlin member
                        member_incidence[member_id] = (purlin_node1, purlin_node2)
                        purlin_members.append(member_id)
                        member_id += 1
            
            self.log_message(f"Created {len(purlin_members)} purlin members", 'success')
        
        # Create bracing if requested
        bracing_members = []
        if self.bracing_var.get():
            self.log_message("Creating bracing members...")
            
            for bay_num in range(num_bays):
                # Roof X-bracing in each bay
                base_node = bay_num * 5 + 1
                
                # Left side X-brace
                n1 = base_node + 1  # Left eave of frame i
                n2 = base_node + 7  # Ridge of frame i+1
                member_incidence[member_id] = (n1, n2)
                bracing_members.append(member_id)
                member_id += 1
                
                n1 = base_node + 2  # Ridge of frame i
                n2 = base_node + 6  # Left eave of frame i+1
                member_incidence[member_id] = (n1, n2)
                bracing_members.append(member_id)
                member_id += 1
                
                # Right side X-brace
                n1 = base_node + 2  # Ridge of frame i
                n2 = base_node + 8  # Right eave of frame i+1
                member_incidence[member_id] = (n1, n2)
                bracing_members.append(member_id)
                member_id += 1
                
                n1 = base_node + 3  # Right eave of frame i
                n2 = base_node + 7  # Ridge of frame i+1
                member_incidence[member_id] = (n1, n2)
                bracing_members.append(member_id)
                member_id += 1
            
            self.log_message(f"Created {len(bracing_members)} bracing members", 'success')
        
        # Create all members in STAAD
        for mid, (n1, n2) in member_incidence.items():
            geo.CreateBeam(mid, n1, n2)
        
        self.log_message(f"Created {len(member_incidence)} total members", 'success')
        
        # Assign properties
        self.status_var.set("Assigning properties...")
        self.log_message("Assigning member properties...")
        
        cc = 1  # American country code
        
        column_section = self.column_section_var.get()
        rafter_section = self.rafter_section_var.get()
        purlin_section = self.purlin_section_var.get()
        bracing_section = self.bracing_section_var.get()
        
        # Create properties
        try:
            col_prop = prop.CreateBeamPropertyFromTable(cc, column_section, 0, 0.0, 0.0)
            prop.AssignBeamProperty(to_int_array(column_members), col_prop)
            self.log_message(f"Assigned {column_section} to {len(column_members)} columns", 'success')
        except Exception as e:
            self.log_message(f"Warning: Could not assign column section {column_section}: {str(e)}", 'warning')
        
        try:
            raft_prop = prop.CreateBeamPropertyFromTable(cc, rafter_section, 0, 0.0, 0.0)
            prop.AssignBeamProperty(to_int_array(rafter_members), raft_prop)
            self.log_message(f"Assigned {rafter_section} to {len(rafter_members)} rafters", 'success')
        except Exception as e:
            self.log_message(f"Warning: Could not assign rafter section {rafter_section}: {str(e)}", 'warning')
        
        if purlin_members:
            try:
                purl_prop = prop.CreateBeamPropertyFromTable(cc, purlin_section, 0, 0.0, 0.0)
                prop.AssignBeamProperty(to_int_array(purlin_members), purl_prop)
                self.log_message(f"Assigned {purlin_section} to {len(purlin_members)} purlins", 'success')
            except Exception as e:
                self.log_message(f"Warning: Could not assign purlin section {purlin_section}: {str(e)}", 'warning')
        
        if bracing_members:
            try:
                brac_prop = prop.CreateAnglePropertyFromTable(cc, bracing_section, 0, 0.0)
                prop.AssignBeamProperty(to_int_array(bracing_members), brac_prop)
                self.log_message(f"Assigned {bracing_section} to {len(bracing_members)} bracing", 'success')
            except Exception as e:
                self.log_message(f"Warning: Could not assign bracing section {bracing_section}: {str(e)}", 'warning')
        
        # Assign material
        all_members = list(member_incidence.keys())
        prop.AssignMaterialToMember("STEEL", to_int_array(all_members))
        self.log_message("Assigned STEEL material to all members", 'success')
        
        # NO SUPPORT ASSIGNMENT - User configures manually
        self.log_message("="*60, 'warning')
        self.log_message("IMPORTANT: Supports NOT assigned!", 'warning')
        self.log_message("Please configure supports manually in STAAD.Pro:", 'warning')
        self.log_message("  - Typical column bases: Fixed or Pinned supports", 'warning')
        self.log_message(f"  - Column base nodes: 1, 5, 10, 15, ... (every 5th node)", 'warning')
        self.log_message("="*60, 'warning')
        
        # Create load cases
        self.status_var.set("Creating load cases...")
        self.log_message("Creating load cases...")
        
        # Dead Load
        case_dl = load.CreateNewPrimaryLoadEx2("DEAD LOAD", 0, 1)
        load.SetLoadActive(case_dl)
        
        if self.selfweight_var.get():
            load.AddSelfWeightInXYZ(2, -1.0)
            self.log_message("Added self weight", 'success')
        
        # Additional dead loads on roof
        dead_load = float(self.dead_load_var.get())
        if dead_load > 0:
            # Apply to rafters
            load_per_ft = dead_load * bay_spacing / 1000  # Convert to kip/ft
            for mem in rafter_members:
                load.AddMemberUniformForce(to_int_array([mem]), 2, -load_per_ft, 0.0, 0.0, 0.0)
            self.log_message(f"Applied dead load: {dead_load} psf on roof", 'success')
        
        # Live Load
        live_load = float(self.live_load_var.get())
        if live_load > 0:
            case_ll = load.CreateNewPrimaryLoadEx2("LIVE LOAD", 0, 2)
            load.SetLoadActive(case_ll)
            load_per_ft = live_load * bay_spacing / 1000
            for mem in rafter_members:
                load.AddMemberUniformForce(to_int_array([mem]), 2, -load_per_ft, 0.0, 0.0, 0.0)
            self.log_message(f"Applied live load: {live_load} psf on roof", 'success')
        
        # Wind Load
        wind_load = float(self.wind_load_var.get())
        if wind_load > 0:
            case_wl = load.CreateNewPrimaryLoadEx2("WIND LOAD", 3, 3)
            load.SetLoadActive(case_wl)
            # Apply wind pressure on columns (simplified)
            wind_per_ft = wind_load * eave_height / 1000
            for mem in column_members:
                load.AddMemberUniformForce(to_int_array([mem]), 4, wind_per_ft, 0.0, 0.0, 0.0)
            self.log_message(f"Applied wind load: {wind_load} psf", 'success')
        
        # Load Combinations
        if self.load_combo_var.get():
            # 1.4 DL
            comb1 = load.CreateNewLoadCombination("1.4 DL", 4)
            load.AddLoadAndFactorToCombination(4, 1, 1.4)
            
            # 1.2 DL + 1.6 LL
            comb2 = load.CreateNewLoadCombination("1.2 DL + 1.6 LL", 5)
            load.AddLoadAndFactorToCombination(5, 1, 1.2)
            load.AddLoadAndFactorToCombination(5, 2, 1.6)
            
            # 1.2 DL + 1.0 LL + 1.0 WL
            comb3 = load.CreateNewLoadCombination("1.2 DL + 1.0 LL + 1.0 WL", 6)
            load.AddLoadAndFactorToCombination(6, 1, 1.2)
            load.AddLoadAndFactorToCombination(6, 2, 1.0)
            load.AddLoadAndFactorToCombination(6, 3, 1.0)
            
            self.log_message("Created LRFD load combinations", 'success')
        
        # Save model
        self.status_var.set("Saving model...")
        self.staad.SaveModel(True)
        self.log_message("Model saved successfully!", 'success')
        
        # Run analysis if requested
        if run_analysis:
            self.status_var.set("Running analysis...")
            self.log_message("Starting structural analysis...")
            self.log_message("WARNING: Analysis may fail without supports configured!", 'warning')
            try:
                self.staad.Command.PerformAnalysis(0)
                self.log_message("Analysis completed!", 'success')
            except Exception as e:
                self.log_message(f"Analysis failed (likely due to missing supports): {str(e)}", 'error')
        
        # Summary
        self.log_message("="*60, 'success')
        self.log_message("WAREHOUSE MODEL BUILD COMPLETE", 'success')
        self.log_message(f"Total Nodes: {len(node_coords)}", 'success')
        self.log_message(f"Total Members: {len(member_incidence)}", 'success')
        self.log_message(f"  - Columns: {len(column_members)}", 'success')
        self.log_message(f"  - Rafters: {len(rafter_members)}", 'success')
        if purlin_members:
            self.log_message(f"  - Purlins: {len(purlin_members)}", 'success')
        if bracing_members:
            self.log_message(f"  - Bracing: {len(bracing_members)}", 'success')
        self.log_message("="*60, 'success')
        self.log_message("NEXT STEP: Configure supports in STAAD.Pro!", 'warning')
        
        self.status_var.set("Build completed successfully!")
        messagebox.showinfo("Success", "Warehouse model built successfully!\n\n"
                           "IMPORTANT: Configure supports manually in STAAD.Pro before analysis.")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            import json
            from tkinter import filedialog
            
            config = {
                'length': self.length_var.get(),
                'width': self.width_var.get(),
                'eave_height': self.eave_height_var.get(),
                'ridge_height': self.ridge_height_var.get(),
                'bay_spacing': self.bay_spacing_var.get(),
                'num_bays': self.num_bays_var.get(),
                'frame_type': self.frame_type_var.get(),
                'unit_system': self.unit_var.get(),
                'column_section': self.column_section_var.get(),
                'rafter_section': self.rafter_section_var.get(),
                'purlin_section': self.purlin_section_var.get(),
                'bracing_section': self.bracing_section_var.get(),
                'dead_load': self.dead_load_var.get(),
                'live_load': self.live_load_var.get(),
                'wind_load': self.wind_load_var.get(),
                'bracing': self.bracing_var.get(),
                'purlins': self.purlins_var.get(),
                'purlin_spacing': self.purlin_spacing_var.get(),
                'selfweight': self.selfweight_var.get(),
                'load_combo': self.load_combo_var.get()
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Warehouse Configuration"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Success", "Configuration saved successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            import json
            from tkinter import filedialog
            
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Warehouse Configuration"
            )
            
            if filename:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                self.length_var.set(config.get('length', '100'))
                self.width_var.set(config.get('width', '60'))
                self.eave_height_var.set(config.get('eave_height', '20'))
                self.ridge_height_var.set(config.get('ridge_height', '28'))
                self.bay_spacing_var.set(config.get('bay_spacing', '25'))
                self.num_bays_var.set(config.get('num_bays', '4'))
                self.frame_type_var.set(config.get('frame_type', 'Rigid Frame'))
                self.unit_var.set(config.get('unit_system', 'FEET-KIP'))
                self.column_section_var.set(config.get('column_section', 'W12X72'))
                self.rafter_section_var.set(config.get('rafter_section', 'W18X35'))
                self.purlin_section_var.set(config.get('purlin_section', 'C8X11.5'))
                self.bracing_section_var.set(config.get('bracing_section', 'L40404'))
                self.dead_load_var.set(config.get('dead_load', '15'))
                self.live_load_var.set(config.get('live_load', '20'))
                self.wind_load_var.set(config.get('wind_load', '25'))
                self.bracing_var.set(config.get('bracing', True))
                self.purlins_var.set(config.get('purlins', True))
                self.purlin_spacing_var.set(config.get('purlin_spacing', '5'))
                self.selfweight_var.set(config.get('selfweight', True))
                self.load_combo_var.set(config.get('load_combo', True))
                
                messagebox.showinfo("Success", "Configuration loaded successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def export_log(self):
        """Export log to text file"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Log"
            )
            
            if filename:
                log_content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(log_content)
                messagebox.showinfo("Success", "Log exported successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export log: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """STAAD.Pro Warehouse Frame Builder v3.0

A parametric tool for generating warehouse 
structural frames in STAAD.Pro.

Features:
• Fully parametric design
• Configurable dimensions
• Multiple frame types
• Roof purlins and bracing
• Load generation
• Save/Load configurations

Note: Supports are NOT assigned by this tool.
Configure manually in STAAD.Pro.

© 2024 - Parametric Warehouse Edition"""
        messagebox.showinfo("About", about_text)
    
    def show_guide(self):
        """Show parameter guide dialog"""
        guide_text = """Parameter Guide:

GEOMETRY:
• Length: Overall building length
• Width: Building width (eave to eave)
• Eave Height: Column height
• Ridge Height: Peak of roof
• Bay Spacing: Distance between frames
• Number of Bays: Total bays in length

MEMBERS:
• Columns: Vertical support members
• Rafters: Sloped roof members
• Purlins: Longitudinal roof members
• Bracing: Diagonal stability members

LOADS (psf = pounds per square foot):
• Dead Load: Roofing, insulation weight
• Live Load: Snow, maintenance loads
• Wind Load: Lateral wind pressure

SUPPORTS:
• NOT assigned by this tool
• Configure manually in STAAD.Pro
• Typical: Fixed or Pinned at column bases
• Base nodes are multiples of 5 (1,5,10,...)"""
        messagebox.showinfo("Parameter Guide", guide_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = WarehouseFrameBuilder(root)
    root.mainloop()


if __name__ == "__main__":
    main()