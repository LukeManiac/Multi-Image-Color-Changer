import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
from os.path import basename as filename

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")
        self.root.resizable(False, False)

        self.images = []  # Stores dictionaries with image data
        self.open_toplevels = {}  # Track open Toplevels by a unique key
        self.custom_colors = {}  # Track changed colors of images
        self.selected_image_index = None

        # Frames for layout
        self.left_frame = tk.Frame(self.root)
        self.right_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Image Listbox
        self.image_listbox = tk.Listbox(self.left_frame, selectmode=tk.EXTENDED, width=40)
        self.image_listbox.pack(pady=10, padx=10, fill=tk.Y)
        self.image_listbox.bind("<<ListboxSelect>>", self.on_image_select)

        # Add/Delete buttons
        self.add_button = tk.Button(self.left_frame, text="Add Image", command=self.add_image)
        self.add_button.pack(pady=5)

        self.delete_button = tk.Button(self.left_frame, text="Delete Image", command=self.delete_image, state=tk.DISABLED)
        self.delete_button.pack(pady=5)

        self.clear_button = tk.Button(self.left_frame, text="Clear All Images", command=self.clear_all_images, state=tk.DISABLED)
        self.clear_button.pack(pady=5)

        self.reset_changes_button = tk.Button(self.left_frame, text="Reset Changes", command=self.reset_changes, state=tk.DISABLED)
        self.reset_changes_button.pack(pady=5)

        self.reset_all_changes_button = tk.Button(self.left_frame, text="Reset All Changes", command=self.reset_all_changes, state=tk.DISABLED)
        self.reset_all_changes_button.pack(pady=5)

        self.resize_label = tk.Label(self.left_frame, text="Resize Factor:")
        self.resize_label.pack(pady=5)
        
        self.resize_factor = tk.IntVar(value=1)
        self.resize_spinbox = tk.Spinbox(self.left_frame, values=(1, 2, 4, 8), width=5, textvariable=self.resize_factor, state="readonly")
        self.resize_spinbox.pack(pady=5)

        self.resize_note = tk.Label(self.left_frame, text="To apply resize factor,\nreclick the image you\nwere just editing.")
        self.resize_note.pack(pady=5)

        # Image Preview Panels
        self.original_preview_label = tk.Label(self.right_frame, text="Original Image")
        self.original_preview_label.pack()
        self.original_preview = tk.Label(self.right_frame)
        self.original_preview.pack(pady=5)
        self.original_preview.bind("<Button-1>", self.on_original_preview_click)

        self.edited_preview_label = tk.Label(self.right_frame, text="Edited Image")
        self.edited_preview_label.pack()
        self.edited_preview = tk.Label(self.right_frame)
        self.edited_preview.pack(pady=5)
        self.edited_preview.bind("<Button-1>", self.on_edited_preview_click)

        # Colors Listbox
        self.colors_label = tk.Label(self.right_frame, text="Colors")
        self.colors_label.pack(pady=5)

        self.colors_listbox = tk.Listbox(self.right_frame, selectmode=tk.SINGLE, width=40)
        self.colors_listbox.pack(pady=5)

        self.edit_color_button = tk.Button(self.right_frame, text="Edit Color", command=self.edit_color, state=tk.DISABLED)
        self.edit_color_button.pack(pady=5)

        # Edit All Colors Button
        self.edit_all_colors_button = tk.Button(self.right_frame, text="Edit All Colors", command=self.edit_all_colors, state=tk.DISABLED)
        self.edit_all_colors_button.pack(pady=5)

        # Save Buttons
        self.save_button = tk.Button(self.right_frame, text="Save Image", command=self.save_image, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.save_as_button = tk.Button(self.right_frame, text="Save Image As", command=self.save_image_as, state=tk.DISABLED)
        self.save_as_button.pack(pady=5)

        self.save_all_button = tk.Button(self.right_frame, text="Save All Images", command=self.save_all_images, state=tk.DISABLED)
        self.save_all_button.pack(pady=5, fill=tk.X)

        self.colors_listbox.bind("<Double-1>", self.edit_color)
        self.image_listbox.bind("<Double-1>", self.edit_all_colors)

    def change_states(self, state):
        self.delete_button.config(state=state)
        self.clear_button.config(state=state)
        self.edit_color_button.config(state=state)
        self.edit_all_colors_button.config(state=state)
        self.reset_changes_button.config(state=state)
        self.reset_all_changes_button.config(state=state)
        self.save_button.config(state=state)
        self.save_as_button.config(state=state)
        self.save_all_button.config(state=state)

    def num_to_words(self, num):
        # Words for the numbers 0-19
        ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
        
        # Words for the tens 20, 30, ..., 90
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        
        # Words for the hundreds, thousands, etc.
        thousands = ["", "thousand", "million", "billion", "trillion"]

        # Function to convert numbers less than 1000 into words
        def convert_hundreds(n):
            if n == 0:
                return ""
            elif n < 20:
                return ones[n]
            elif n < 100:
                return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
            else:
                return ones[n // 100] + " hundred" + (" and " + convert_hundreds(n % 100) if n % 100 != 0 else "")

        # If the number is 0
        if num == 0:
            return "zero"
        
        words = []
        idx = 0

        # Break the number into groups of thousands
        while num > 0:
            if num % 1000 != 0:
                words.append(convert_hundreds(num % 1000) + (" " + thousands[idx] if thousands[idx] else ""))
            num //= 1000
            idx += 1
        
        return ', '.join(reversed(words)).strip()

    def add_image(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PNG Files", "*.png")])
        if file_paths:
            try:
                for file_path in file_paths:
                    image = Image.open(file_path).convert("RGBA")
                    self.images.append({
                        "path": file_path,
                        "image": image,
                        "edited_image": image.copy(),
                        "colors": {},
                    })
                self.update_image_listbox()
                self.change_states(tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def delete_image(self):
        selected_indices = self.image_listbox.curselection()
        if not selected_indices:
            return

        for index in reversed(selected_indices):
            del self.images[index]

        if len(self.images) == 0:
            self.change_states(tk.DISABLED)
            self.original_preview.config(image="")
            self.edited_preview.config(image="")
            self.colors_listbox.delete(0, tk.END)

        self.update_image_listbox()
        self.update_previews()
        self.update_colors_listbox()

    def clear_all_images(self):
        self.images.clear()

        self.change_states(tk.DISABLED)
        self.original_preview.config(image="")
        self.edited_preview.config(image="")
        self.colors_listbox.delete(0, tk.END)

        self.update_image_listbox()
        self.update_previews()
        self.update_colors_listbox()

    def on_image_select(self, event):
        selected_indices = self.image_listbox.curselection()
        if len(selected_indices) == 1:
            self.selected_image_index = selected_indices[0]
            self.update_previews()
            self.update_colors_listbox()

    def update_image_listbox(self):
        self.image_listbox.delete(0, tk.END)
        for i, img_data in enumerate(self.images):
            name = filename(img_data["path"])
            self.image_listbox.insert(tk.END, name)

    def update_previews(self, event=None):
        if "edit_all_colors" in self.open_toplevels:
            self.open_toplevels["edit_all_colors_update"]()
            
        if self.selected_image_index is not None and len(self.images) != 0:
            img_data = self.images[self.selected_image_index]
            
            # If the path has changed (after save), reload the image
            if img_data["path"] != img_data.get("previous_path"):
                img_data["previous_path"] = img_data["path"]
                # Reload the image based on the updated path
                updated_image = Image.open(img_data["path"]).convert("RGBA")
                img_data["image"] = updated_image
                img_data["edited_image"] = updated_image.copy()

            original_width, original_height = img_data["image"].size

            # Calculate 4 times the original dimensions
            new_width = original_width * self.resize_factor.get()  # Use .get() to retrieve value from IntVar
            new_height = original_height * self.resize_factor.get()  # Use .get() to retrieve value from IntVar

            # Update Original Image Preview
            original_resized = img_data["image"].resize((new_width, new_height), Image.Resampling.NEAREST)
            original_preview = ImageTk.PhotoImage(original_resized)
            self.original_preview.image = original_preview
            self.original_preview.config(image=original_preview)

            # Update Edited Image Preview
            edited_resized = img_data["edited_image"].resize((new_width, new_height), Image.Resampling.NEAREST)
            edited_preview = ImageTk.PhotoImage(edited_resized)
            self.edited_preview.image = edited_preview
            self.edited_preview.config(image=edited_preview)
        else:
            self.original_preview.config(image="")
            self.edited_preview.config(image="")

    def update_colors_listbox(self):
        if "edit_all_colors" in self.open_toplevels:
            self.open_toplevels["edit_all_colors_update"]()
            
        self.colors_listbox.delete(0, tk.END)
        if self.selected_image_index is not None and len(self.images) != 0:
            img_data = self.images[self.selected_image_index]
            unique_colors = img_data["image"].getcolors(maxcolors=99999)
            if unique_colors:
                for count, color in unique_colors:
                    # Check if the alpha value is not 0
                    if color[3] != 0:
                        original_color = color
                        edited_color = img_data["colors"].get(color, color)
                        self.colors_listbox.insert(tk.END, f"{original_color} - {edited_color}")
    
    def reset_changes(self):
        selected_indices = self.image_listbox.curselection()
        if not selected_indices:
            return

        for index in selected_indices:
            img_data = self.images[index]
            img_data["edited_image"] = img_data["image"].copy()  # Reset edited image to original image
            img_data["colors"].clear()  # Clear any color modifications

        self.update_previews()  # Refresh the image previews
        self.update_colors_listbox()  # Refresh the colors list
        self.custom_colors.clear()
        if len(self.images) == 1:
            messagebox.showinfo("Reset Successful", f"Changes have been reset for {self.num_to_words(len(self.images))} image.")
        else:
            messagebox.showinfo("Reset Successful", f"Changes have been reset for {self.num_to_words(len(self.images))} images.")

    def reset_all_changes(self):
        if not self.images:
            return
        
        for img_data in self.images:
            img_data["edited_image"] = img_data["image"].copy()  # Reset edited image to original
            img_data["colors"].clear()  # Clear any color modifications

        # Update the UI to reflect the changes
        self.update_previews()
        self.update_colors_listbox()
        self.custom_colors.clear()

        messagebox.showinfo("Success", "All changes have been reset.")

    def edit_color(self, event=None):
        selected_index = self.colors_listbox.curselection()
        if not selected_index:
            return

        color_line = self.colors_listbox.get(selected_index[0])

        try:
            original_color_str = color_line.split(" - ")[1]
            original_color = tuple(map(int, original_color_str.strip("()").split(",")))

            if len(original_color) == 3:
                original_color = original_color + (255,)
            elif len(original_color) != 4:
                raise ValueError("Invalid color format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse color: {e}")
            return

        if "edit_color" in self.open_toplevels:
            self.open_toplevels["edit_color"].focus()
            return

        toplevel = Toplevel(self.root)
        self.open_toplevels["edit_color"] = toplevel
        toplevel.title("Edit Color")
        toplevel.geometry("200x200")
        toplevel.resizable(False, False)

        def on_close():
            del self.open_toplevels["edit_color"]
            toplevel.destroy()

        toplevel.protocol("WM_DELETE_WINDOW", on_close)

        red_var = tk.IntVar(value=original_color[0])
        green_var = tk.IntVar(value=original_color[1])
        blue_var = tk.IntVar(value=original_color[2])
        alpha_var = tk.IntVar(value=original_color[3])

        tk.Label(toplevel, text="Red:").grid(row=1, column=0, sticky="e", pady=5)
        tk.Spinbox(toplevel, from_=0, to=255, textvariable=red_var, width=5).grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(toplevel, text="Green:").grid(row=2, column=0, sticky="e", pady=5)
        tk.Spinbox(toplevel, from_=0, to=255, textvariable=green_var, width=5).grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(toplevel, text="Blue:").grid(row=3, column=0, sticky="e", pady=5)
        tk.Spinbox(toplevel, from_=0, to=255, textvariable=blue_var, width=5).grid(row=3, column=1, sticky="w", pady=5)

        tk.Label(toplevel, text="Alpha:").grid(row=4, column=0, sticky="e", pady=5)
        tk.Spinbox(toplevel, from_=0, to=255, textvariable=alpha_var, width=5).grid(row=4, column=1, sticky="w", pady=5)

        def apply_color_changes():
            new_color = (red_var.get(), green_var.get(), blue_var.get(), alpha_var.get())

            if self.selected_image_index is not None and len(self.images) != 0:
                img_data = self.images[self.selected_image_index]

                # Retrieve the true original color from custom_colors if new_color already exists
                true_original_color = next(
                    (key for key, value in self.custom_colors.items() if value == new_color),
                    original_color
                )

                if true_original_color != new_color:
                    # Update the global custom_colors mapping
                    self.custom_colors[true_original_color] = new_color

                    # Update the mapping for the original color in the specific image
                    img_data["colors"][true_original_color] = new_color

                    # Reapply all custom colors for the specific image
                    original_image = img_data["image"].copy()
                    pixels = original_image.load()

                    # Apply custom color mappings to the original image
                    for y in range(original_image.height):
                        for x in range(original_image.width):
                            current_pixel = pixels[x, y]
                            if current_pixel in self.custom_colors:
                                pixels[x, y] = self.custom_colors[current_pixel]

                    img_data["edited_image"] = original_image
                    self.update_previews()
                    self.update_colors_listbox()
                    on_close()

        tk.Button(toplevel, text="Apply", command=apply_color_changes).grid(row=5, column=0, columnspan=2, pady=10)

    def edit_all_colors(self, event=None):
        if len(self.images) == 0:
            return
        if "edit_all_colors" in self.open_toplevels:
            self.open_toplevels["edit_all_colors"].focus()
            return
        # Create the Toplevel window to edit all colors
        toplevel = Toplevel(self.root)
        toplevel.title("Edit All Colors")
        toplevel.geometry("400x400")
        toplevel.resizable(False, False)

        def on_close():
            del self.open_toplevels["edit_all_colors"]
            del self.open_toplevels["edit_all_colors_update"]
            toplevel.destroy()
        
        toplevel.protocol("WM_DELETE_WINDOW", on_close)

        # Listbox to display colors
        all_colors_listbox = tk.Listbox(toplevel, selectmode=tk.SINGLE, width=40)
        all_colors_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        # Function to get all unique colors from all images
        def get_all_unique_colors():
            all_colors = set()
            for img_data in self.images:
                unique_colors = img_data["image"].getcolors(maxcolors=99999)
                if unique_colors:
                    for count, color in unique_colors:
                        if color[3] != 0:  # Exclude fully transparent colors
                            all_colors.add(color)
            return sorted(all_colors, key=lambda c: (c[0], c[1], c[2], c[3]))

        # Function to update the listbox dynamically
        def update_all_colors_listbox():
            all_colors_listbox.delete(0, tk.END)
            for color in get_all_unique_colors():
                edited_color = color
                if color in self.custom_colors:
                    edited_color = self.custom_colors[color]
                all_colors_listbox.insert(tk.END, f"{color} - {edited_color}")

        # Populate the listbox initially
        update_all_colors_listbox()
        self.open_toplevels["edit_all_colors"] = toplevel
        self.open_toplevels["edit_all_colors_update"] = update_all_colors_listbox

        # Edit selected color
        def edit_color_from_all_colors(event=None):
            selected_index = all_colors_listbox.curselection()
            if not selected_index:
                return

            color_str = all_colors_listbox.get(selected_index[0]).split(" - ")[1]
            original_color = tuple(map(int, color_str.strip("()").split(",")))

            # Open color edit window
            self.edit_color_for_all(original_color, update_all_colors_listbox)

        edit_button = tk.Button(toplevel, text="Edit Selected Color", command=edit_color_from_all_colors)
        edit_button.pack(pady=5)
        all_colors_listbox.bind("<Double-1>", edit_color_from_all_colors)

    def edit_color_for_all(self, original_color, update_all_colors_listbox):
        if "edit_color_for_all" in self.open_toplevels:
            self.open_toplevels["edit_color_for_all"].focus()
            return

        toplevel = Toplevel(self.root)
        self.open_toplevels["edit_color_for_all"] = toplevel
        toplevel.title("Edit Color")
        toplevel.geometry("200x200")
        toplevel.resizable(False, False)

        def on_close():
            del self.open_toplevels["edit_color_for_all"]
            toplevel.destroy()

        toplevel.protocol("WM_DELETE_WINDOW", on_close)

        red_var = tk.IntVar(value=original_color[0])
        green_var = tk.IntVar(value=original_color[1])
        blue_var = tk.IntVar(value=original_color[2])
        alpha_var = tk.IntVar(value=original_color[3])

        tk.Label(toplevel, text="Red:").grid(row=1, column=0, sticky="e", pady=5)
        tk.Spinbox(toplevel, from_=0, to=255, textvariable=red_var, width=5).grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(toplevel, text="Green:").grid(row=2, column=0, sticky="e", pady=5)
        tk.Spinbox(toplevel, from_=0, to=255, textvariable=green_var, width=5).grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(toplevel, text="Blue:").grid(row=3, column=0, sticky="e", pady=5)
        tk.Spinbox(toplevel, from_=0, to=255, textvariable=blue_var, width=5).grid(row=3, column=1, sticky="w", pady=5)

        tk.Label(toplevel, text="Alpha:").grid(row=4, column=0, sticky="e", pady=5)
        tk.Spinbox(toplevel, from_=0, to=255, textvariable=alpha_var, width=5).grid(row=4, column=1, sticky="w", pady=5)

        def apply_color_changes():
            new_color = (red_var.get(), green_var.get(), blue_var.get(), alpha_var.get())

            if original_color != new_color:
                # Update the custom_colors dictionary
                self.custom_colors[original_color] = new_color

                for img_data in self.images:
                    original_image = img_data["image"].copy()
                    pixels = original_image.load()

                    # Apply custom color mappings to the original image
                    for y in range(original_image.height):
                        for x in range(original_image.width):
                            current_pixel = pixels[x, y]
                            if current_pixel in self.custom_colors:
                                pixels[x, y] = self.custom_colors[current_pixel]

                    img_data["edited_image"] = original_image

            self.update_previews()
            self.update_colors_listbox()
            update_all_colors_listbox()
            on_close()

        tk.Button(toplevel, text="Apply", command=apply_color_changes).grid(row=5, column=0, columnspan=2, pady=10)

    def save_image(self):
        if self.selected_image_index is not None and len(self.images) != 0:
            img_data = self.images[self.selected_image_index]
            img_path = img_data["path"]
            img_data["edited_image"].save(img_path)
            img_data["colors"] = {}  # Reset color changes after save

            # Reload the saved image
            saved_image = Image.open(img_path).convert("RGBA")
            img_data["image"] = saved_image
            img_data["edited_image"] = saved_image.copy()

            self.custom_colors.clear()

            self.update_image_listbox()
            self.update_colors_listbox()
            self.update_previews()
            messagebox.showinfo("Success", f"{img_path} saved successfully.")

    def save_image_as(self):
        if self.selected_image_index is not None and len(self.images) != 0:
            img_data = self.images[self.selected_image_index]
            
            # Ask the user for a new file path using a file dialog
            new_img_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")])
            
            if new_img_path:  # User canceled the dialog
                img_data["edited_image"].save(new_img_path)
            
                # Update the image path and reload the image
                img_data["path"] = new_img_path
                saved_image = Image.open(new_img_path).convert("RGBA")
                img_data["image"] = saved_image
                img_data["edited_image"] = saved_image.copy()

                # Clear any custom color modifications
                self.custom_colors.clear()

                # Update UI components like listboxes and previews
                self.update_image_listbox()
                self.update_colors_listbox()
                self.update_previews()

                messagebox.showinfo("Success", f"Image saved as {filename(new_img_path)}.")
    
    def save_all_images(self):
        for img_data in self.images:
            img_data["edited_image"].save(img_data["path"])

            # Reload each saved image
            saved_image = Image.open(img_data["path"]).convert("RGBA")
            img_data["image"] = saved_image
            img_data["edited_image"] = saved_image.copy()

        for img_data in self.images:
            img_data["colors"] = {}
        
        self.custom_colors.clear()

        self.update_image_listbox()
        self.update_colors_listbox()
        self.update_previews()

        if len(self.images) == 1:
            messagebox.showinfo("Success", f"One image has been saved.")
        else:
            messagebox.showinfo("Success", f"{self.num_to_words(len(self.images)).capitalize()} images have been saved.")
    
    def on_original_preview_click(self, event):
        if self.selected_image_index is not None and len(self.images) != 0:
            img_data = self.images[self.selected_image_index]
            original_image = img_data["image"]
            
            # Get the dimensions of the displayed image and the original image
            displayed_width = self.original_preview.winfo_width()
            displayed_height = self.original_preview.winfo_height()
            original_width, original_height = original_image.size
            
            # Calculate the scaling factor
            scale_x = original_width / displayed_width
            scale_y = original_height / displayed_height
            
            # Get the pixel coordinates on the original image
            original_x = int(event.x * scale_x)
            original_y = int(event.y * scale_y)
            
            # Ensure the coordinates are within bounds
            if 0 <= original_x < original_width and 0 <= original_y < original_height:
                pixel_color = original_image.getpixel((original_x, original_y))
                if pixel_color[3] == 0:
                    return
                messagebox.showinfo("Pixel Color", f"Color: {pixel_color}")
    
    def on_edited_preview_click(self, event):
        if self.selected_image_index is not None and len(self.images) != 0:
            img_data = self.images[self.selected_image_index]
            edited_image = img_data["edited_image"]
            
            # Get the dimensions of the displayed image and the edited image
            displayed_width = self.edited_preview.winfo_width()
            displayed_height = self.edited_preview.winfo_height()
            edited_width, edited_height = edited_image.size
            
            # Calculate the scaling factor
            scale_x = edited_width / displayed_width
            scale_y = edited_height / displayed_height
            
            # Get the pixel coordinates on the edited image
            edited_x = int(event.x * scale_x)
            edited_y = int(event.y * scale_y)
            
            # Ensure the coordinates are within bounds
            if 0 <= edited_x < edited_width and 0 <= edited_y < edited_height:
                pixel_color = edited_image.getpixel((edited_x, edited_y))
                if pixel_color[3] == 0:
                    return
                messagebox.showinfo("Pixel Color", f"Color: {pixel_color}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
