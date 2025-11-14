import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import mysql.connector
from prettytable import PrettyTable
import sys
from datetime import datetime

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Alumni Network Database System")
        self.root.geometry("400x350")
        self.root.configure(bg="#2c3e50")

        tk.Label(root, text="Alumni Network Login", bg="#2c3e50", fg="white",
                 font=("Arial", 16, "bold")).pack(pady=20)

        # --- Role Selection Dropdown ---
        tk.Label(root, text="Select Role:", bg="#2c3e50", fg="white").pack(pady=5)
        self.role_var = tk.StringVar()
        role_dropdown = ttk.Combobox(root, textvariable=self.role_var, state="readonly")
        role_dropdown['values'] = ["Admin", "Student", "Alumni"]
        role_dropdown.pack()

        # --- Username & Password Inputs ---
        tk.Label(root, text="Username:", bg="#2c3e50", fg="white").pack(pady=5)
        self.username = tk.Entry(root)
        self.username.pack()

        tk.Label(root, text="Password:", bg="#2c3e50", fg="white").pack(pady=5)
        self.password = tk.Entry(root, show="*")
        self.password.pack()

        tk.Button(root, text="Login", command=self.check_login,
                  bg="#27ae60", fg="white").pack(pady=20)

    def check_login(self):
        role = self.role_var.get()
        user = self.username.get()
        pw = self.password.get()

        if not role or not user or not pw:
            messagebox.showerror("Error", "Please fill all fields.")
            return

        valid = {"Admin": "admin", "Student": "student", "Alumni": "alumni"}
        if user != valid.get(role):
            messagebox.showerror("Login Error", f"Username does not match selected role: {role}")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user=user,
                password=pw,
                database="AlumniDB"
            )
            conn.close()

            messagebox.showinfo("Success", f"Login successful as {role}!")
            self.root.withdraw()
            main_window = tk.Toplevel(self.root)
            app = AlumniDBGUI(main_window, user, pw, role)  # ✅ Pass role
        except mysql.connector.Error as err:
            messagebox.showerror("Login Failed", f"Database connection error:\n{err}")


# =============================================
#  Main GUI Class
# =============================================
class AlumniDBGUI:
    def __init__(self, root, user="root", pw="root", role="Admin"):
        self.root = root
        self.db_user = user
        self.db_pass = pw
        self.current_role = role  
        self.root.title(f"Alumni Network Database System — Logged in as {self.current_role}")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")

        self.connection = None
        self.connect_to_db()

        # Only set up the GUI after successful DB connection
        if self.connection:
            self.setup_gui()
            self.apply_role_restrictions()  

    def connect_to_db(self):
        """Connect to MySQL database using credentials from login"""
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user=self.db_user,
                password=self.db_pass,
                database="AlumniDB"
            )
            print("Successfully connected to database!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error connecting to database: {err}")
            self.root.destroy()

    def execute_query(self, query, params=None, fetch=True):
        """Execute SQL queries safely with global permission handling."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())

            # For SELECT queries
            if fetch:
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return results, columns

            # For INSERT/UPDATE/DELETE queries
            else:
                self.connection.commit()
                return True

        except mysql.connector.Error as err:
            err_msg = str(err).lower()

            # ✅ Handle permission errors globally
            if "command denied" in err_msg or "execute command denied" in err_msg:
                messagebox.showerror(
                    "Permission Denied",
                    "❌ You do not have the required privileges to perform this action."
                )
                # Explicitly return a safe failure code
                return "permission_denied"

            # ✅ Other MySQL errors
            messagebox.showerror("Database Error", f"Error executing query:\n{err}")
            return None

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    
    def get_departments(self):
        """Get all departments for dropdowns"""
        query = "SELECT dept_id, name FROM Department"
        res = self.execute_query(query)
        if not res:
            return []
        results, _ = res
        return results if results else []
    
    def get_alumni_list(self):
        q = "SELECT alumni_id, name FROM Alumni ORDER BY alumni_id"
        out = self.execute_query(q)
        if not out:
            return []
        results, _ = out
        return results
    
    def get_student_list(self):
        q = "SELECT student_id, name FROM Student ORDER BY student_id"
        out = self.execute_query(q)
        if not out:
            return []
        results, _ = out
        return results
    
    def get_events_list(self):
        q = "SELECT event_id, name FROM Event ORDER BY event_id"
        out = self.execute_query(q)
        if not out:
            return []
        results, _ = out
        return results
    
    def validate_int(self, value, field_name):
        """Validate integer input"""
        try:
            return int(value)
        except ValueError:
            messagebox.showerror("Input Error", f"{field_name} must be a valid number!")
            return None

    def validate_date(self, datestr, field_name):
        """Validate YYYY-MM-DD date"""
        try:
            dt = datetime.strptime(datestr, "%Y-%m-%d").date()
            return dt
        except ValueError:
            messagebox.showerror("Input Error", f"{field_name} must be in YYYY-MM-DD format!")
            return None
    
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        title_label = tk.Label(main_frame, text="Alumni Network Database System", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left sidebar for navigation
        self.setup_sidebar(main_frame)
        
        # Right side for content
        self.setup_content_area(main_frame)
        
    def apply_role_restrictions(self):
        """Restrict actions based on user role."""
        if self.current_role.lower() == "admin":
            return  # Admin has full access

        elif self.current_role.lower() == "student":
            # View-only: disable all insert/update/delete buttons
            for btn in self.root.winfo_children():
                try:
                    if isinstance(btn, tk.Button) and "View" not in btn.cget("text"):
                        btn.config(state="disabled")
                except:
                    pass

            messagebox.showinfo("Access Mode", "Student Mode: View-only access enabled.")

        elif self.current_role.lower() == "alumni":
            # Alumni: only Mentorship management full access
            allowed_sections = ["🤝 Mentorship Management", "📚 Education Management", "🎓 Alumni Management"]

            for child in self.root.winfo_children():
                if isinstance(child, tk.Button):
                    text = child.cget("text")
                    # Disable if button text not in allowed list
                    if not any(keyword in text for keyword in allowed_sections):
                        child.config(state="disabled")

            messagebox.showinfo("Access Mode", "Alumni Mode: Mentorship full access; other sections read-only.")

    def setup_sidebar(self, parent):
        sidebar = ttk.Frame(parent, padding="10", relief='raised', borderwidth=2)
        sidebar.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        # Navigation buttons
        nav_buttons = [
            ("🎓 Alumni Management", self.show_alumni_management),
            ("👨‍🎓 Student Management", self.show_student_management),
            ("🏫 Department Management", self.show_department_management),
            ("📚 Education Management", self.show_education_management),
            ("🤝 Mentorship Management", self.show_mentorship_management),
            ("👥 Committee Management", self.show_committee_management),
            ("🎪 Event Management", self.show_event_management),
            ("📋 Participation Management", self.show_participation_management)
        ]
        
        for i, (text, command) in enumerate(nav_buttons):
            btn = tk.Button(sidebar, text=text, command=command, 
                           font=('Arial', 11), bg='#34495e', fg='white',
                           relief='flat', width=20, height=2)
            btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#3498db'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='#34495e'))
        
        # Exit button
        exit_btn = tk.Button(sidebar, text="🚪 Exit", command=self.root.quit,
                            font=('Arial', 11, 'bold'), bg='#e74c3c', fg='white',
                            relief='flat', width=20, height=2)
        exit_btn.grid(row=len(nav_buttons), column=0, pady=20, sticky=(tk.W, tk.E))
        exit_btn.bind("<Enter>", lambda e: exit_btn.configure(bg='#c0392b'))
        exit_btn.bind("<Leave>", lambda e: exit_btn.configure(bg='#e74c3c'))
    
    def setup_content_area(self, parent):
        self.content_frame = ttk.Frame(parent, padding="10", relief='sunken', borderwidth=2)
        self.content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(1, weight=1)
        
        # Title for content area
        self.content_title = tk.Label(self.content_frame, text="Welcome to Alumni Database System", 
                                     font=('Arial', 16, 'bold'), fg='#2c3e50')
        self.content_title.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Text area for results
        self.result_text = scrolledtext.ScrolledText(self.content_frame, width=80, height=25, font=('Consolas', 10))
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input frame (will be populated based on selection)
        self.input_frame = ttk.Frame(self.content_frame)
        self.input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        self.input_frame.columnconfigure(1, weight=1)
    
    def clear_input_frame(self):
        """Clear the input frame"""
        for widget in self.input_frame.winfo_children():
            widget.destroy()
    
    def show_results(self, results, columns=None):
        """Display results in the text area"""
        self.result_text.delete(1.0, tk.END)
        
        if not results:
            self.result_text.insert(tk.END, "No results found.")
            return
        
        # Create a table using PrettyTable
        table = PrettyTable()
        if columns:
            table.field_names = columns
        else:
            table.field_names = [f"Column {i+1}" for i in range(len(results[0]))]
        
        for row in results:
            table.add_row(row)
        
        self.result_text.insert(tk.END, str(table))
    
    def safe_execute(self, query, params, success_message):
        """Universal wrapper for write operations with permission safety."""
        result = self.execute_query(query, params, fetch=False)
        if not result or result == "permission_denied":
            return  # stop if no permission or failed query
        messagebox.showinfo("Success", success_message)


    # -----------------------
    # Alumni Management
    # -----------------------
    def show_alumni_management(self):
        self.content_title.config(text="🎓 Alumni Management")
        self.clear_input_frame()
        
        buttons = [
            ("Add Alumni", self.add_alumni_gui),
            ("View All Alumni", self.view_alumni),
            ("Search Alumni", self.search_alumni_gui),
            ("Update Company", self.update_company_gui),
            ("Delete Alumni", self.delete_alumni_gui),
            ("Count by Company", self.count_alumni_company),
            ("Filter by Department", self.filter_alumni_dept_gui),
            ("Update Contact Details", self.update_contact_details_gui),

        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(self.input_frame, text=text, command=command,
                          bg='#3498db', fg='white', font=('Arial', 10))
            btn.grid(row=i//4, column=i%4, padx=10, pady=8, sticky="nsew")
        for col in range(4):
            self.input_frame.grid_columnconfigure(col, weight=1, uniform="equal")
    
    def add_alumni_gui(self):
        self.clear_input_frame()
        
        # Get available departments
        departments = self.get_departments()
        if not departments:
            messagebox.showerror("Error", "No departments found! Please add departments first.")
            return
        
        # Create input fields
        tk.Label(self.input_frame, text="Alumni ID:*").grid(row=0, column=0, sticky=tk.W)
        alumni_id = tk.Entry(self.input_frame)
        alumni_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Name:*").grid(row=1, column=0, sticky=tk.W)
        name = tk.Entry(self.input_frame)
        name.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Email:*").grid(row=2, column=0, sticky=tk.W)
        email = tk.Entry(self.input_frame)
        email.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Phone:").grid(row=3, column=0, sticky=tk.W)
        phone = tk.Entry(self.input_frame)
        phone.grid(row=3, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Graduation Year:*").grid(row=4, column=0, sticky=tk.W)
        grad_year = tk.Entry(self.input_frame)
        grad_year.grid(row=4, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Company:").grid(row=5, column=0, sticky=tk.W)
        company = tk.Entry(self.input_frame)
        company.grid(row=5, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Department:*").grid(row=6, column=0, sticky=tk.W)
        dept_var = tk.StringVar()
        dept_combo = ttk.Combobox(self.input_frame, textvariable=dept_var, state="readonly")
        dept_combo['values'] = [f"{dept[0]} - {dept[1]}" for dept in departments]
        dept_combo.grid(row=6, column=1, sticky=(tk.W, tk.E))
        
        # Show available departments
        dept_info = tk.Label(self.input_frame, text=f"Available Departments: {', '.join([f'{dept[0]}' for dept in departments])}", 
                            fg='gray', font=('Arial', 8))
        dept_info.grid(row=7, column=0, columnspan=2, sticky=tk.W)
        
        def submit():
            # Validate required fields
            if not all([alumni_id.get(), name.get(), email.get(), grad_year.get(), dept_var.get()]):
                messagebox.showerror("Input Error", "Please fill all required fields (*)!")
                return
            
            # Validate numeric fields
            alumni_id_val = self.validate_int(alumni_id.get(), "Alumni ID")
            grad_year_val = self.validate_int(grad_year.get(), "Graduation Year")
            if alumni_id_val is None or grad_year_val is None:
                return
            
            # Extract department ID from combo box
            try:
                dept_id_val = int(dept_var.get().split(' - ')[0])
            except (ValueError, IndexError):
                messagebox.showerror("Input Error", "Please select a valid department!")
                return
            
            # Set default values for optional fields
            phone_val = phone.get() if phone.get() else None
            company_val = company.get() if company.get() else 'Not Provided'
            
            query = """INSERT INTO Alumni (alumni_id, name, email, phone_number, 
                     graduation_year, company, dept_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            params = (alumni_id_val, name.get(), email.get(), phone_val, 
                     grad_year_val, company_val, dept_id_val)
            
            self.safe_execute(query, params, "Alumni added successfully!")
            self.view_alumni()
        
        submit_btn = tk.Button(self.input_frame, text="Add Alumni", command=submit, bg='#27ae60', fg='white', font=('Arial', 10, 'bold'))
        submit_btn.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Required fields note
        note_label = tk.Label(self.input_frame, text="* Required fields", fg='red', font=('Arial', 8))
        note_label.grid(row=9, column=0, columnspan=2, sticky=tk.W)
    
    def view_alumni(self):
        query = """SELECT A.alumni_id, A.name, A.email, A.phone_number, 
                          A.graduation_year, A.company, D.name as department
                   FROM Alumni A LEFT JOIN Department D ON A.dept_id=D.dept_id
                   ORDER BY A.alumni_id"""
        results, columns = self.execute_query(query)
        self.show_results(results, columns)
    
    def search_alumni_gui(self):
        self.clear_input_frame()
        
        tk.Label(self.input_frame, text="Search Name:").grid(row=0, column=0, sticky=tk.W)
        search_term = tk.Entry(self.input_frame)
        search_term.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        def search():
            if not search_term.get():
                messagebox.showwarning("Input Error", "Please enter a search term!")
                return
                
            query = "SELECT * FROM Alumni WHERE name LIKE %s ORDER BY name"
            results, columns = self.execute_query(query, (f"%{search_term.get()}%",))
            self.show_results(results, columns)
        
        search_btn = tk.Button(self.input_frame, text="Search", command=search, bg='#3498db', fg='white')
        search_btn.grid(row=1, column=0, columnspan=2, pady=5)
    
    def update_company_gui(self):
        self.clear_input_frame()
        
        tk.Label(self.input_frame, text="Alumni ID:*").grid(row=0, column=0, sticky=tk.W)
        alumni_id = tk.Entry(self.input_frame)
        alumni_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="New Company:*").grid(row=1, column=0, sticky=tk.W)
        company = tk.Entry(self.input_frame)
        company.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        def update():
            if not all([alumni_id.get(), company.get()]):
                messagebox.showerror("Input Error", "Please fill all required fields!")
                return
                
            alumni_id_val = self.validate_int(alumni_id.get(), "Alumni ID")
            if alumni_id_val is None:
                return
                
            query = "UPDATE Alumni SET company=%s WHERE alumni_id=%s"
            self.safe_execute(query, (company.get(), alumni_id_val),"Company updated successfully!")
            self.view_alumni()
        
        update_btn = tk.Button(self.input_frame, text="Update Company", command=update, bg='#f39c12', fg='white')
        update_btn.grid(row=2, column=0, columnspan=2, pady=5)
    
    def delete_alumni_gui(self):
        self.clear_input_frame()
        
        tk.Label(self.input_frame, text="Alumni ID:*").grid(row=0, column=0, sticky=tk.W)
        alumni_id = tk.Entry(self.input_frame)
        alumni_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        def delete():
            if not alumni_id.get():
                messagebox.showerror("Input Error", "Please enter Alumni ID!")
                return
                
            alumni_id_val = self.validate_int(alumni_id.get(), "Alumni ID")
            if alumni_id_val is None:
                return
                
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this alumni?\nThis will also delete related education and mentorship records!"):
                query = "DELETE FROM Alumni WHERE alumni_id=%s"
                self.safe_execute(query, (alumni_id_val,), "Alumni deleted successfully!")
                self.view_alumni()
        
        delete_btn = tk.Button(self.input_frame, text="Delete Alumni", command=delete, bg='#e74c3c', fg='white')
        delete_btn.grid(row=1, column=0, columnspan=2, pady=5)
    
    def count_alumni_company(self):
        query = "SELECT company, COUNT(*) as count FROM Alumni GROUP BY company ORDER BY count DESC"
        results, columns = self.execute_query(query)
        self.show_results(results, columns)
    
    def filter_alumni_dept_gui(self):
        self.clear_input_frame()
        
        departments = self.get_departments()
        if not departments:
            messagebox.showerror("Error", "No departments found!")
            return
        
        tk.Label(self.input_frame, text="Select Department:*").grid(row=0, column=0, sticky=tk.W)
        dept_var = tk.StringVar()
        dept_combo = ttk.Combobox(self.input_frame, textvariable=dept_var, state="readonly")
        dept_combo['values'] = [dept[1] for dept in departments]  # Only department names
        dept_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        def filter_dept():
            if not dept_var.get():
                messagebox.showwarning("Input Error", "Please select a department!")
                return
                
            query = """SELECT A.alumni_id, A.name, A.company, A.graduation_year 
                       FROM Alumni A JOIN Department D ON A.dept_id=D.dept_id
                       WHERE D.name=%s ORDER BY A.name"""
            results, columns = self.execute_query(query, (dept_var.get(),))
            self.show_results(results, columns)
        
        filter_btn = tk.Button(self.input_frame, text="Filter Alumni", command=filter_dept, bg='#9b59b6', fg='white')
        filter_btn.grid(row=1, column=0, columnspan=2, pady=5)
    
    def update_contact_details_gui(self):
        self.clear_input_frame()
        self.content_title.config(text="Update Alumni Contact Details")

        tk.Label(self.input_frame, text="Alumni ID:*").grid(row=0, column=0, sticky=tk.W)
        alumni_id_entry = tk.Entry(self.input_frame)
        alumni_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="New Email (optional):").grid(row=1, column=0, sticky=tk.W)
        email_entry = tk.Entry(self.input_frame)
        email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="New Phone (optional):").grid(row=2, column=0, sticky=tk.W)
        phone_entry = tk.Entry(self.input_frame)
        phone_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        def update():
            if not alumni_id_entry.get():
                messagebox.showerror("Input Error", "Please enter Alumni ID!")
                return

            alumni_id_val = self.validate_int(alumni_id_entry.get(), "Alumni ID")
            if alumni_id_val is None:
                return

            new_email = email_entry.get().strip()
            new_phone = phone_entry.get().strip()

            if not new_email and not new_phone:
                messagebox.showerror("Input Error", "Enter at least one field (email or phone) to update.")
                return

            query = "CALL update_alumni_contact(%s, %s, %s)"
            params = (alumni_id_val, new_email if new_email else '', new_phone if new_phone else '')

            self.safe_execute(query, params, "Contact details updated successfully!")
            self.view_alumni()

        tk.Button(self.input_frame, text="Update Contact Details", command=update,
                bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).grid(
            row=3, column=0, columnspan=2, pady=10)

    # -----------------------
    # Student Management 
    # -----------------------
    def show_student_management(self):
        self.content_title.config(text="👨‍🎓 Student Management")
        self.clear_input_frame()
        
        buttons = [
            ("Add Student", self.add_student_gui),
            ("View All Students", self.view_students),
            ("Update Student", self.update_student_gui),
            ("Delete Student", self.delete_student_gui)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(self.input_frame, text=text, command=command,
                          bg='#3498db', fg='white', font=('Arial', 10))
            btn.grid(row=i//4, column=i%4, padx=10, pady=8, sticky=tk.W+tk.E)
    
    def add_student_gui(self):
        self.clear_input_frame()
        
        # Get available departments
        departments = self.get_departments()
        if not departments:
            messagebox.showerror("Error", "No departments found! Please add departments first.")
            return
        
        fields = [
            ("Student ID:*", "student_id"),
            ("Name:*", "name"),
            ("Email:*", "email"),
            ("Phone:", "phone"),
            ("Batch Year:*", "batch_year"),
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(self.input_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            entries[key] = tk.Entry(self.input_frame)
            entries[key].grid(row=i, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Department:*").grid(row=len(fields), column=0, sticky=tk.W)
        dept_var = tk.StringVar()
        dept_combo = ttk.Combobox(self.input_frame, textvariable=dept_var, state="readonly")
        dept_combo['values'] = [f"{dept[0]} - {dept[1]}" for dept in departments]
        dept_combo.grid(row=len(fields), column=1, sticky=(tk.W, tk.E))
        
        def submit():
            # Validate required fields
            required_fields = ['student_id', 'name', 'email', 'batch_year']
            if not all([entries[key].get() for key in required_fields]) or not dept_var.get():
                messagebox.showerror("Input Error", "Please fill all required fields (*)!")
                return
            
            # Validate numeric fields
            student_id_val = self.validate_int(entries['student_id'].get(), "Student ID")
            batch_year_val = self.validate_int(entries['batch_year'].get(), "Batch Year")
            if student_id_val is None or batch_year_val is None:
                return
            
            # Extract department ID
            try:
                dept_id_val = int(dept_var.get().split(' - ')[0])
            except (ValueError, IndexError):
                messagebox.showerror("Input Error", "Please select a valid department!")
                return
            
            # Set optional field
            phone_val = entries['phone'].get() if entries['phone'].get() else None            
            query = """INSERT INTO Student (student_id, name, email, phone, batch_year, dept_id) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            params = (student_id_val, entries['name'].get(), entries['email'].get(), 
                     phone_val, batch_year_val, dept_id_val)
            
            self.safe_execute(query, params,"Student added successfully!")
            self.view_students()
        
        submit_btn = tk.Button(self.input_frame, text="Add Student", command=submit, bg='#27ae60', fg='white')
        submit_btn.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
    
    def view_students(self):
        query = """SELECT S.student_id, S.name, S.email, S.phone, 
                          S.batch_year, D.name as department
                   FROM Student S LEFT JOIN Department D ON S.dept_id=D.dept_id
                   ORDER BY S.student_id"""
        results, columns = self.execute_query(query)
        self.show_results(results, columns)
    
    def update_student_gui(self):
        self.clear_input_frame()
        tk.Label(self.input_frame, text="Student ID:*").grid(row=0, column=0, sticky=tk.W)
        student_id_entry = tk.Entry(self.input_frame)
        student_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="New Email:").grid(row=1, column=0, sticky=tk.W)
        email_entry = tk.Entry(self.input_frame)
        email_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="New Phone:").grid(row=2, column=0, sticky=tk.W)
        phone_entry = tk.Entry(self.input_frame)
        phone_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

        def update():
            student_id = student_id_entry.get()
            new_email = email_entry.get().strip()
            new_phone = phone_entry.get().strip()

            if not student_id:
                messagebox.showerror("Input Error", "Please enter Student ID!")
                return

            student_id_val = self.validate_int(student_id, "Student ID")
            if student_id_val is None:
                return

            # Only one field can be updated at a time
            if (not new_email and not new_phone):
                messagebox.showerror("Input Error", "Enter either new email or new phone to update.")
                return
            if (new_email and new_phone):
                messagebox.showerror("Input Error", "Please update only one field at a time (either email or phone).")
                return

            # Determine which field to update
            if new_email:
                query = "UPDATE Student SET email=%s WHERE student_id=%s"
                params = (new_email, student_id_val)
            else:
                query = "UPDATE Student SET phone=%s WHERE student_id=%s"
                params = (new_phone, student_id_val)

            self.safe_execute(query, params, "Student information updated successfully!")
            self.view_students()

        tk.Button(self.input_frame, text="Update Student", command=update, bg='#f39c12', fg='white').grid(row=3, column=0, columnspan=2, pady=10)
    
    def delete_student_gui(self):
        self.clear_input_frame()
        
        tk.Label(self.input_frame, text="Student ID:*").grid(row=0, column=0, sticky=tk.W)
        student_id = tk.Entry(self.input_frame)
        student_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        def delete():
            if not student_id.get():
                messagebox.showerror("Input Error", "Please enter Student ID!")
                return
                
            student_id_val = self.validate_int(student_id.get(), "Student ID")
            if student_id_val is None:
                return
                
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
                query = "DELETE FROM Student WHERE student_id=%s"
                self.safe_execute(query, (student_id_val,), "Student deleted successfully!")
                self.view_students()
        
        delete_btn = tk.Button(self.input_frame, text="Delete Student", command=delete,
                             bg='#e74c3c', fg='white')
        delete_btn.grid(row=1, column=0, columnspan=2, pady=5)
    
    # -----------------------
    # Department Management
    # -----------------------
    def show_department_management(self):
        self.content_title.config(text="🏫 Department Management")
        self.clear_input_frame()
        
        buttons = [
            ("Add Department", self.add_department_gui),
            ("View Departments", self.view_departments),
            ("Update Department", self.update_department_gui),
            ("Delete Department", self.delete_department_gui)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(self.input_frame, text=text, command=command, bg='#3498db', fg='white', font=('Arial', 10))
            btn.grid(row=i//4, column=i%4, padx=10, pady=8, sticky=tk.W+tk.E)
    
    def add_department_gui(self):
        self.clear_input_frame()
        
        tk.Label(self.input_frame, text="Department ID:*").grid(row=0, column=0, sticky=tk.W)
        dept_id = tk.Entry(self.input_frame)
        dept_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Department Name:*").grid(row=1, column=0, sticky=tk.W)
        name = tk.Entry(self.input_frame)
        name.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="HOD Name:*").grid(row=2, column=0, sticky=tk.W)
        hod = tk.Entry(self.input_frame)
        hod.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        def submit():
            if not all([dept_id.get(), name.get(), hod.get()]):
                messagebox.showerror("Input Error", "Please fill all required fields!")
                return
                
            dept_id_val = self.validate_int(dept_id.get(), "Department ID")
            if dept_id_val is None:
                return
                
            query = "INSERT INTO Department VALUES (%s, %s, %s)"
            self.safe_execute(query, (dept_id_val, name.get(), hod.get()), "Department added successfully!")
            self.view_departments()
        
        submit_btn = tk.Button(self.input_frame, text="Add Department", command=submit, bg='#27ae60', fg='white')
        submit_btn.grid(row=3, column=0, columnspan=2, pady=10)
    
    def view_departments(self):
        query = "SELECT * FROM Department ORDER BY dept_id"
        results, columns = self.execute_query(query)
        self.show_results(results, columns)
    
    def update_department_gui(self):
        self.clear_input_frame()
        
        tk.Label(self.input_frame, text="Department ID:*").grid(row=0, column=0, sticky=tk.W)
        dept_id = tk.Entry(self.input_frame)
        dept_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="New HOD Name:*").grid(row=1, column=0, sticky=tk.W)
        hod = tk.Entry(self.input_frame)
        hod.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        def update():
            if not all([dept_id.get(), hod.get()]):
                messagebox.showerror("Input Error", "Please fill all required fields!")
                return
                
            dept_id_val = self.validate_int(dept_id.get(), "Department ID")
            if dept_id_val is None:
                return
                
            query = "UPDATE Department SET hod=%s WHERE dept_id=%s"
            self.safe_execute(query, (hod.get(), dept_id_val), "Department updated successfully!")
            self.view_departments()
        
        update_btn = tk.Button(self.input_frame, text="Update Department", command=update, bg='#f39c12', fg='white')
        update_btn.grid(row=2, column=0, columnspan=2, pady=5)
    
    def delete_department_gui(self):
        self.clear_input_frame()
        
        tk.Label(self.input_frame, text="Department ID:*").grid(row=0, column=0, sticky=tk.W)
        dept_id = tk.Entry(self.input_frame)
        dept_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        def delete():
            if not dept_id.get():
                messagebox.showerror("Input Error", "Please enter Department ID!")
                return
                
            dept_id_val = self.validate_int(dept_id.get(), "Department ID")
            if dept_id_val is None:
                return
                
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this department?\nThis will affect related alumni and students!"):
                query = "DELETE FROM Department WHERE dept_id=%s"
                self.safe_execute(query, (dept_id_val,), "Department deleted successfully!")
                self.view_departments()
        
        delete_btn = tk.Button(self.input_frame, text="Delete Department", command=delete, bg='#e74c3c', fg='white')
        delete_btn.grid(row=1, column=0, columnspan=2, pady=5)
    
    # -----------------------
    # Education Management
    # -----------------------
    def show_education_management(self):
        self.content_title.config(text="📚 Education Management")
        self.clear_input_frame()
        
        buttons = [
            ("Add Education", self.add_education_gui),
            ("View Education", self.view_education), 
            ("Delete Education", self.delete_education_gui),
            ("View Alumni Education", self.view_alumni_education)
        ]
        for i, (text, cmd) in enumerate(buttons):
            btn = tk.Button(self.input_frame, text=text, command=cmd, bg='#3498db', fg='white')
            btn.grid(row=i // 4, column=i % 4, padx=10, pady=8, sticky="nsew")
        
    def add_education_gui(self):
        self.clear_input_frame()
        alumni = self.get_alumni_list()
        if not alumni:
            messagebox.showerror("Error", "No alumni found! Please add alumni first.")
            return

        tk.Label(self.input_frame, text="Education ID:* (Unique per Alumni)").grid(row=0, column=0, sticky=tk.W)
        edu_id = tk.Entry(self.input_frame)
        edu_id.grid(row=0, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="Select Alumni:*").grid(row=1, column=0, sticky=tk.W)
        alumni_var = tk.StringVar()
        alumni_combo = ttk.Combobox(self.input_frame, textvariable=alumni_var, state="readonly")
        alumni_combo['values'] = [f"{a[0]} - {a[1]}" for a in alumni]
        alumni_combo.grid(row=1, column=1, sticky=(tk.W, tk.E))

        fields = [
            ("College Name:*", "college_name"),
            ("Degree:*", "degree"),
            ("Course:*", "course"),
            ("Start Year:*", "start_year"),
            ("End Year:*", "end_year")
        ]

        entries = {}
        for i, (label, key) in enumerate(fields, start=2):
            tk.Label(self.input_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            entries[key] = tk.Entry(self.input_frame)
            entries[key].grid(row=i, column=1, sticky=(tk.W, tk.E))

        def submit():
            if not all([edu_id.get(), alumni_var.get()] + [entries[f].get() for f in entries]):
                messagebox.showerror("Input Error", "Please fill all required fields!")
                return

            edu_val = self.validate_int(edu_id.get(), "Education ID")
            if edu_val is None:
                return

            try:
                alumni_id_val = int(alumni_var.get().split(' - ')[0])
            except Exception:
                messagebox.showerror("Input Error", "Select valid Alumni!")
                return

            query = """INSERT INTO Education (edu_id, alumni_id, college_name, degree, course, start_year, end_year)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            params = (
                edu_val,
                alumni_id_val,
                entries['college_name'].get(),
                entries['degree'].get(),
                entries['course'].get(),
                self.validate_int(entries['start_year'].get(), "Start Year"),
                self.validate_int(entries['end_year'].get(), "End Year")
            )

            self.safe_execute(query, params, "Education record added successfully!")
            self.view_education()

        tk.Button(self.input_frame, text="Add Education", command=submit, bg='#27ae60', fg='white').grid(row=len(fields)+2, column=0, columnspan=2, pady=6)

    def view_education(self):
        """Simple education view (hides repeated alumni names)"""
        q = """
        SELECT 
            A.name AS Alumni_Name, 
            E.edu_id, 
            E.college_name, 
            E.degree, 
            E.course,
            E.start_year, 
            E.end_year
        FROM Education E
        JOIN Alumni A ON E.alumni_id = A.alumni_id
        ORDER BY A.name, E.edu_id;
        """
        
        res = self.execute_query(q)
        if res:
            results, columns = res
            # Hide repeated alumni names during display
            processed = []
            last_name = None
            for row in results:
                name = row[0]
                if name == last_name:
                    name = ''  # make duplicate names blank 
                else:
                    last_name = name
                processed.append((name, *row[1:]))
            results = processed
            self.show_results(results, columns)
        else:
            self.result_text.insert(tk.END, "No education records found.")

    def view_alumni_education(self):
        """View alumni with department, company, and education details (grouped neatly)"""
        query = """
        SELECT
            A.name AS Alumni_Name,
            A.company AS Company,
            E.end_year AS Graduation_Year,  
            E.college_name AS College_Name,
            E.degree AS Degree,
            E.course AS Course
        FROM Alumni A
        INNER JOIN Education E ON A.alumni_id = E.alumni_id
        LEFT JOIN Department D ON A.dept_id = D.dept_id
        ORDER BY A.name, E.edu_id;
        """
        res = self.execute_query(query)
        if res:
            results, columns = res
            # Hide duplicate alumni name and company for viewing
            processed = []
            last_name = None
            for row in results:
                name, company = row[0], row[1]
                if name == last_name:
                    name, company = '', ''  # make repeated entries as blank
                else:
                    last_name = row[0]
                processed.append((name, company, *row[2:]))
            results = processed
            self.show_results(results, columns)
        else:
            self.result_text.insert(tk.END, "No records found.")

    def delete_education_gui(self):
        """Delete a specific education record by both Alumni and Education ID"""
        self.clear_input_frame()

        tk.Label(self.input_frame, text="Select Alumni:*").grid(row=0, column=0, sticky=tk.W)
        alumni = self.get_alumni_list()
        if not alumni:
            messagebox.showerror("Error", "No alumni found! Please add alumni first.")
            return

        alumni_var = tk.StringVar()
        alumni_combo = ttk.Combobox(self.input_frame, textvariable=alumni_var, state="readonly")
        alumni_combo['values'] = [f"{a[0]} - {a[1]}" for a in alumni]
        alumni_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="Education ID:*").grid(row=1, column=0, sticky=tk.W)
        edu_id_entry = tk.Entry(self.input_frame)
        edu_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        def delete_record():
            if not alumni_var.get() or not edu_id_entry.get():
                messagebox.showerror("Input Error", "Please select Alumni and enter Education ID!")
                return

            edu_id_val = self.validate_int(edu_id_entry.get(), "Education ID")
            if edu_id_val is None:
                return

            try:
                alumni_id_val = int(alumni_var.get().split(' - ')[0])
            except Exception:
                messagebox.showerror("Input Error", "Please select a valid Alumni!")
                return

            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this education record?"):
                query = "DELETE FROM Education WHERE edu_id=%s AND alumni_id=%s"
                self.safe_execute(query, (edu_id_val, alumni_id_val), "Education record deleted successfully!")
                self.view_education()

        # Delete button
        del_btn = tk.Button(self.input_frame, text="Delete Education Record", command=delete_record, bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'))
        del_btn.grid(row=2, column=0, columnspan=2, pady=8)

    # -----------------------
    # Mentorship Management
    # -----------------------
    def show_mentorship_management(self):
        self.content_title.config(text="🤝 Mentorship Management")
        self.clear_input_frame()
        buttons = [
            ("Start Mentorship", self.add_mentorship_gui),
            ("View Mentorships", self.view_mentorships),
            ("View Duration (in Days)", self.show_mentorship_duration),
            ("End Mentorship (set end date)", self.end_mentorship_gui),
            ("Delete Mentorship", self.delete_mentorship_gui),
            ("List Students by Alumni", self.list_mentorships_by_alumni_gui) 

        ]
        for i, (t, cmd) in enumerate(buttons):
            btn = tk.Button(self.input_frame, text=t, command=cmd, bg='#3498db', fg='white')
            btn.grid(row=i // 4, column=i % 4, padx=10, pady=8, sticky="nsew")
        for col in range(4):
            self.input_frame.grid_columnconfigure(col, weight=1, uniform="equal")
    
    def add_mentorship_gui(self):
        self.clear_input_frame()
        alumni_list = self.get_alumni_list()
        student_list = self.get_student_list()
        if not alumni_list or not student_list:
            messagebox.showerror("Error", "Need both alumni and students to create mentorships.")
            return
        tk.Label(self.input_frame, text="Mentorship ID:*").grid(row=0, column=0, sticky=tk.W)
        mid = tk.Entry(self.input_frame); mid.grid(row=0, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Alumni:*").grid(row=1, column=0, sticky=tk.W)
        alumni_var = tk.StringVar()
        alumni_combo = ttk.Combobox(self.input_frame, textvariable=alumni_var, state="readonly")
        alumni_combo['values'] = [f"{a[0]} - {a[1]}" for a in alumni_list]
        alumni_combo.grid(row=1, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Student:*").grid(row=2, column=0, sticky=tk.W)
        student_var = tk.StringVar()
        student_combo = ttk.Combobox(self.input_frame, textvariable=student_var, state="readonly")
        student_combo['values'] = [f"{s[0]} - {s[1]}" for s in student_list]
        student_combo.grid(row=2, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Start Date (YYYY-MM-DD):*").grid(row=3, column=0, sticky=tk.W)
        start = tk.Entry(self.input_frame); start.grid(row=3, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="End Date (optional YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W)
        end = tk.Entry(self.input_frame); end.grid(row=4, column=1, sticky=(tk.W, tk.E))
        def submit():
            if not all([mid.get(), alumni_var.get(), student_var.get(), start.get()]):
                messagebox.showerror("Input Error", "Please fill required fields!")
                return
            mid_val = self.validate_int(mid.get(), "Mentorship ID")
            if mid_val is None:
                return
            try:
                alumni_id_val = int(alumni_var.get().split(' - ')[0])
                student_id_val = int(student_var.get().split(' - ')[0])
            except Exception:
                messagebox.showerror("Input Error", "Select valid alumni and student!")
                return
            start_date = self.validate_date(start.get(), "Start Date")
            if start_date is None:
                return
            end_date = None
            if end.get():
                ed = self.validate_date(end.get(), "End Date")
                if ed is None:
                    return
                end_date = ed.isoformat()
            q = """INSERT INTO Mentorship (mid, alumni_id, student_id, start_date, end_date)
                   VALUES (%s, %s, %s, %s, %s)"""
            params = (mid_val, alumni_id_val, student_id_val, start_date.isoformat(), end_date)
            self.safe_execute(q, params, "Mentorship started!")
            self.view_mentorships()
        tk.Button(self.input_frame, text="Start Mentorship", command=submit, bg='#27ae60', fg='white').grid(row=5, column=0, columnspan=2, pady=6)
    
    def view_mentorships(self):
        q = """SELECT M.mid, A.name as alumni_name, S.name as student_name, M.start_date, M.end_date
               FROM Mentorship M
               JOIN Alumni A ON M.alumni_id=A.alumni_id
               JOIN Student S ON M.student_id=S.student_id
               ORDER BY M.mid"""
        res = self.execute_query(q)
        if res:
            results, columns = res
            self.show_results(results, columns)
        else:
            self.result_text.insert(tk.END, "No mentorships found.")
    
    def end_mentorship_gui(self):
        self.clear_input_frame()
        tk.Label(self.input_frame, text="Mentorship ID:*").grid(row=0, column=0, sticky=tk.W)
        mid = tk.Entry(self.input_frame)
        mid.grid(row=0, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="End Date (YYYY-MM-DD):*").grid(row=1, column=0, sticky=tk.W)
        end = tk.Entry(self.input_frame)
        end.grid(row=1, column=1, sticky=(tk.W, tk.E))

        def endment():
            if not all([mid.get(), end.get()]):
                messagebox.showerror("Input Error", "Please fill required fields!")
                return

            mid_val = self.validate_int(mid.get(), "Mentorship ID")
            if mid_val is None:
                return

            ed = self.validate_date(end.get(), "End Date")
            if ed is None:
                return

            q = "UPDATE Mentorship SET end_date=%s WHERE mid=%s"
            result = self.execute_query(q, (ed.isoformat(), mid_val), fetch=False)

            if not result or result == "permission_denied":
                return

            messagebox.showinfo("Success", "Mentorship end date updated successfully!")
            self.view_mentorships()

        tk.Button(
            self.input_frame,
            text="Set End Date",
            command=endment,
            bg='#f39c12',
            fg='white'
        ).grid(row=2, column=0, columnspan=2, pady=6)

    
    def delete_mentorship_gui(self):
        self.clear_input_frame()
        tk.Label(self.input_frame, text="Mentorship ID:*").grid(row=0, column=0, sticky=tk.W)
        mid = tk.Entry(self.input_frame); mid.grid(row=0, column=1, sticky=(tk.W, tk.E))
        def delete():
            if not mid.get():
                messagebox.showerror("Input Error", "Please enter Mentorship ID!")
                return
            mid_val = self.validate_int(mid.get(), "Mentorship ID")
            if mid_val is None:
                return
            if messagebox.askyesno("Confirm Delete", "Delete this mentorship?"):
                self.safe_execute("DELETE FROM Mentorship WHERE mid=%s", (mid_val,), "Mentorship deleted.")
                self.view_mentorships()
        tk.Button(self.input_frame, text="Delete Mentorship", command=delete, bg='#e74c3c', fg='white').grid(row=1, column=0, columnspan=2, pady=6)
    
    def show_mentorship_duration(self):
        """Display mentorship durations in days using the SQL function"""
        q = """SELECT M.mid,
                    A.name AS Alumni,
                    S.name AS Student,
                    M.start_date,
                    M.end_date,
                    mentorship_duration(M.start_date, M.end_date) AS DurationDays
            FROM Mentorship M
            JOIN Alumni A ON M.alumni_id = A.alumni_id
            JOIN Student S ON M.student_id = S.student_id
            ORDER BY M.mid"""
        res = self.execute_query(q)
        if res == "permission_denied":
            return 
        if res:
            results, columns = res
            self.show_results(results, columns)
        else:
            self.result_text.insert(tk.END, "No mentorship duration records found.")

    def list_mentorships_by_alumni_gui(self):
        """Call stored procedure list_mentorships_by_alumni(alumniId) via dropdown"""
        self.clear_input_frame()
        alumni_list = self.get_alumni_list()
        if not alumni_list:
            messagebox.showerror("Error", "No alumni found in the database.")
            return

        # Dropdown is used to choose alumni
        tk.Label(self.input_frame, text="Select Alumni:*").grid(row=0, column=0, sticky=tk.W)
        alumni_var = tk.StringVar()
        alumni_combo = ttk.Combobox(self.input_frame, textvariable=alumni_var, state="readonly")
        alumni_combo['values'] = [f"{a[0]} - {a[1]}" for a in alumni_list]
        alumni_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))

        def show_mentorships():
            if not alumni_var.get():
                messagebox.showerror("Input Error", "Please select an alumni!")
                return

            try:
                alumni_id_val = int(alumni_var.get().split(' - ')[0])
            except Exception:
                messagebox.showerror("Input Error", "Invalid alumni selection.")
                return

            # Use stored procedure --------------------------------------------------------------------------------------------------------------------------------
            try:
                cursor = self.connection.cursor()
                cursor.callproc("list_mentorships_by_alumni", (alumni_id_val,))
                results = []
                columns = []
                for result in cursor.stored_results():
                    results = result.fetchall()
                    columns = [desc[0] for desc in result.description]
                    break 
                cursor.close()

                if not results:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "No mentorships found for this alumni.")
                else:
                    self.show_results(results, columns)

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error executing query: {err}")

        tk.Button(self.input_frame, text="Show Mentorships", command=show_mentorships, bg='#9b59b6', fg='white', font=('Arial', 10, 'bold')).grid(row=1,
                                                                                                                             column=0, columnspan=2, pady=10)

    # -----------------------
    # Committee Management
    # -----------------------
    def show_committee_management(self):
        self.content_title.config(text="👥 Committee Management")
        self.clear_input_frame()
        buttons = [
            ("Add Committee", self.add_committee_gui),
            ("View Committees", self.view_committees),
            ("Update Committee", self.update_committee_gui),
            ("Delete Committee", self.delete_committee_gui)
        ]
        for i, (t, cmd) in enumerate(buttons):
            btn = tk.Button(self.input_frame, text=t, command=cmd, bg='#3498db', fg='white')
            btn.grid(row=i // 4, column=i % 4, padx=10, pady=8, sticky="nsew")
        for col in range(2):
            self.input_frame.grid_columnconfigure(col, weight=1, uniform="equal")
    
    def add_committee_gui(self):
        self.clear_input_frame()
        events = self.get_events_list()
        if not events:
            messagebox.showerror("Error", "No events found! Please add events first.")
            return

        tk.Label(self.input_frame, text="Committee ID:*").grid(row=0, column=0, sticky=tk.W)
        cid = tk.Entry(self.input_frame); cid.grid(row=0, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="Event:*").grid(row=1, column=0, sticky=tk.W)
        event_var = tk.StringVar()
        event_combo = ttk.Combobox(self.input_frame, textvariable=event_var, state="readonly")
        event_combo['values'] = [f"{e[0]} - {e[1]}" for e in events]
        event_combo.grid(row=1, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="Name:*").grid(row=2, column=0, sticky=tk.W)
        name = tk.Entry(self.input_frame); name.grid(row=2, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="Phone:").grid(row=3, column=0, sticky=tk.W)
        phone = tk.Entry(self.input_frame); phone.grid(row=3, column=1, sticky=(tk.W, tk.E))

        tk.Label(self.input_frame, text="Head:*").grid(row=4, column=0, sticky=tk.W)
        head = tk.Entry(self.input_frame); head.grid(row=4, column=1, sticky=(tk.W, tk.E))

        def submit():
            if not all([cid.get(), event_var.get(), name.get(), head.get()]):
                messagebox.showerror("Input Error", "Please fill required fields!")
                return

            cid_val = self.validate_int(cid.get(), "Committee ID")
            if cid_val is None:
                return

            try:
                event_id_val = int(event_var.get().split(' - ')[0])
            except Exception:
                messagebox.showerror("Input Error", "Select a valid event!")
                return

            query = """INSERT INTO Committee (cid, event_id, name, phone, head)
                    VALUES (%s, %s, %s, %s, %s)"""
            params = (cid_val, event_id_val, name.get(), phone.get() if phone.get() else None, head.get())

            self.safe_execute(query, params, "Committee added successfully!")
            self.view_committees()

        tk.Button(self.input_frame, text="Add Committee", command=submit, bg='#27ae60', fg='white').grid(row=5, column=0, columnspan=2, pady=6)

    def view_committees(self):
        q = """SELECT C.cid, C.name, C.phone, C.head, E.name AS event_name
            FROM Committee C
            JOIN Event E ON C.event_id = E.event_id
            ORDER BY E.event_id, C.cid"""
        res = self.execute_query(q)
        if res:
            results, columns = res
            self.show_results(results, columns)
        else:
            self.result_text.insert(tk.END, "No committees found.")

    def update_committee_gui(self):
        self.clear_input_frame()
        self.content_title.config(text="👥 Update Committee Details")
        
        tk.Label(self.input_frame, text="Committee ID:*").grid(row=0, column=0, sticky=tk.W)
        cid = tk.Entry(self.input_frame)
        cid.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="New Head Name:").grid(row=1, column=0, sticky=tk.W)
        head = tk.Entry(self.input_frame)
        head.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="New Phone Number:").grid(row=2, column=0, sticky=tk.W)
        phone = tk.Entry(self.input_frame)
        phone.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        def update():
            if not cid.get():
                messagebox.showerror("Input Error", "Please enter Committee ID!")
                return
            
            cid_val = self.validate_int(cid.get(), "Committee ID")
            if cid_val is None:
                return
            
            # Collect only non-empty fields to update
            fields, params = [], []
            if head.get():
                fields.append("head=%s")
                params.append(head.get())
            if phone.get():
                fields.append("phone=%s")
                params.append(phone.get())
            if not fields:
                messagebox.showwarning("No Update", "Please enter at least one field to update!")
                return
            query = f"UPDATE Committee SET {', '.join(fields)} WHERE cid=%s"
            params.append(cid_val)
            
            self.safe_execute(query, tuple(params), "Committee details updated successfully!")
            self.view_committees()
        
        update_btn = tk.Button(self.input_frame, text="Update Committee", command=update, bg='#f39c12', fg='white', font=('Arial', 10, 'bold'))
        update_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def delete_committee_gui(self):
        self.clear_input_frame()
        tk.Label(self.input_frame, text="Committee ID:*").grid(row=0, column=0, sticky=tk.W)
        cid = tk.Entry(self.input_frame); cid.grid(row=0, column=1, sticky=(tk.W, tk.E))
        def delete():
            if not cid.get():
                messagebox.showerror("Input Error", "Please enter Committee ID!")
                return
            cid_val = self.validate_int(cid.get(), "Committee ID")
            if cid_val is None:
                return
            if messagebox.askyesno("Confirm Delete", "Delete this committee?"):
                self.safe_execute("DELETE FROM Committee WHERE cid=%s", (cid_val,), "Committee deleted!")
                self.view_committees()
        tk.Button(self.input_frame, text="Delete Committee", command=delete, bg='#e74c3c', fg='white').grid(row=1, column=0, columnspan=2, pady=6)
    
    # -----------------------
    # Event Management
    # -----------------------
    def show_event_management(self):
        self.content_title.config(text="🎪 Event Management")
        self.clear_input_frame()
        buttons = [
            ("Add Event", self.add_event_gui),
            ("View Events", self.view_events),
            ("Update Event", self.update_event_gui),
            ("Delete Event", self.delete_event_gui)
        ]
        for i, (t, cmd) in enumerate(buttons):
            btn = tk.Button(self.input_frame, text=t, command=cmd, bg='#3498db', fg='white')
            btn.grid(row=i // 4, column=i % 4, padx=10, pady=8, sticky="nsew")
        for col in range(2):
            self.input_frame.grid_columnconfigure(col, weight=1, uniform="equal")
    
    def add_event_gui(self):
        self.clear_input_frame()
        tk.Label(self.input_frame, text="Event ID:*").grid(row=0, column=0, sticky=tk.W)
        eid = tk.Entry(self.input_frame); eid.grid(row=0, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Name:*").grid(row=1, column=0, sticky=tk.W)
        name = tk.Entry(self.input_frame); name.grid(row=1, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Description:").grid(row=2, column=0, sticky=tk.W)
        desc = tk.Entry(self.input_frame); desc.grid(row=2, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Location:*").grid(row=3, column=0, sticky=tk.W)
        loc = tk.Entry(self.input_frame); loc.grid(row=3, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Date (YYYY-MM-DD):*").grid(row=4, column=0, sticky=tk.W)
        date_ent = tk.Entry(self.input_frame); date_ent.grid(row=4, column=1, sticky=(tk.W, tk.E))
        def submit():
            if not all([eid.get(), name.get(), loc.get(), date_ent.get()]):
                messagebox.showerror("Input Error", "Please fill required fields!")
                return
            eid_val = self.validate_int(eid.get(), "Event ID")
            if eid_val is None:
                return
            d = self.validate_date(date_ent.get(), "Event Date")
            if d is None:
                return
            self.safe_execute("INSERT INTO Event (event_id, name, description, location, date) VALUES (%s,%s,%s,%s,%s)",
                                  (eid_val, name.get(), desc.get() if desc.get() else None, loc.get(), d.isoformat()), "Event added!")
            self.view_events()
        tk.Button(self.input_frame, text="Add Event", command=submit, bg='#27ae60', fg='white').grid(row=5, column=0, columnspan=2, pady=6)
    
    def view_events(self):
        res = self.execute_query("SELECT event_id, name, description, location, date FROM Event ORDER BY event_id")
        if res:
            results, columns = res
            self.show_results(results, columns)
        else:
            self.result_text.insert(tk.END, "No events found.")
    
    def update_event_gui(self):
        self.clear_input_frame()
        self.content_title.config(text="🎪 Update Event Details")
        
        tk.Label(self.input_frame, text="Event ID:*").grid(row=0, column=0, sticky=tk.W)
        event_id = tk.Entry(self.input_frame)
        event_id.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="New Description:").grid(row=1, column=0, sticky=tk.W)
        description = tk.Entry(self.input_frame)
        description.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="New Location:").grid(row=2, column=0, sticky=tk.W)
        location = tk.Entry(self.input_frame)
        location.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="New Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W)
        date = tk.Entry(self.input_frame)
        date.grid(row=3, column=1, sticky=(tk.W, tk.E))
        
        def update():
            if not event_id.get():
                messagebox.showerror("Input Error", "Please enter Event ID!")
                return
            
            event_id_val = self.validate_int(event_id.get(), "Event ID")
            if event_id_val is None:
                return
            # Collect only non-empty fields for update
            fields, params = [], []
            if description.get():
                fields.append("description=%s")
                params.append(description.get())
            if location.get():
                fields.append("location=%s")
                params.append(location.get())
            if date.get():
                fields.append("date=%s")
                params.append(date.get())
            
            if not fields:
                messagebox.showwarning("No Update", "Please enter at least one field to update!")
                return
            
            query = f"UPDATE Event SET {', '.join(fields)} WHERE event_id=%s"
            params.append(event_id_val)
            
            self.safe_execute(query, tuple(params), "Event details updated successfully!")
            self.view_events()  # Refresh list
        
        update_btn = tk.Button(self.input_frame, text="Update Event", command=update,
                            bg='#f39c12', fg='white', font=('Arial', 10, 'bold'))
        update_btn.grid(row=4, column=0, columnspan=2, pady=10)

    def delete_event_gui(self):
        self.clear_input_frame()
        tk.Label(self.input_frame, text="Event ID:*").grid(row=0, column=0, sticky=tk.W)
        eid = tk.Entry(self.input_frame); eid.grid(row=0, column=1, sticky=(tk.W, tk.E))
        def delete():
            if not eid.get():
                messagebox.showerror("Input Error", "Please enter Event ID!")
                return
            eid_val = self.validate_int(eid.get(), "Event ID")
            if eid_val is None:
                return
            if messagebox.askyesno("Confirm Delete", "Delete this event?"):
                self.safe_execute("DELETE FROM Event WHERE event_id=%s", (eid_val,), "Event deleted!")
                self.view_events()
        tk.Button(self.input_frame, text="Delete Event", command=delete, bg='#e74c3c', fg='white').grid(row=1, column=0, columnspan=2, pady=6)
    
    # --------------------------
    # Participation Management
    # --------------------------
    def show_participation_management(self):
        self.content_title.config(text="📋 Participation Management")
        self.clear_input_frame()

        buttons = [
            ("Register Student Participation", self.add_participation_student_gui),
            ("Register Alumni Participation", self.add_participation_alumni_gui),
            ("View Student Participation", self.view_participation_students),
            ("View Alumni Participation", self.view_participation_alumni),
            ("Count Event Participants", self.count_event_participants),
            ("Total Events Attended by Alumni", self.show_total_events_attended_gui),
            ("View Alumni by Event", self.view_alumni_by_event_gui),
            ("Delete Participant", self.delete_participant),
            ("Update RSVP Status", self.update_participation_status_gui)
        ]

        for i, (t, cmd) in enumerate(buttons):
            btn = tk.Button(self.input_frame, text=t, command=cmd,
                            bg='#3498db', fg='white', font=('Arial', 10))
            btn.grid(row=i // 4, column=i % 4, padx=10, pady=8, sticky="nsew")
        for col in range(4):
            self.input_frame.grid_columnconfigure(col, weight=1, uniform="equal")

    def add_participation_student_gui(self):
        self.clear_input_frame()
        events = self.get_events_list()
        students = self.get_student_list()
        if not events or not students:
            messagebox.showerror("Error", "Need events and students to register participation.")
            return
        tk.Label(self.input_frame, text="Participation ID:*").grid(row=0, column=0, sticky=tk.W)
        pid = tk.Entry(self.input_frame); pid.grid(row=0, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Event:*").grid(row=1, column=0, sticky=tk.W)
        event_var = tk.StringVar()
        event_combo = ttk.Combobox(self.input_frame, textvariable=event_var, state="readonly")
        event_combo['values'] = [f"{e[0]} - {e[1]}" for e in events]
        event_combo.grid(row=1, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Student:*").grid(row=2, column=0, sticky=tk.W)
        student_var = tk.StringVar()
        st_combo = ttk.Combobox(self.input_frame, textvariable=student_var, state="readonly")
        st_combo['values'] = [f"{s[0]} - {s[1]}" for s in students]
        st_combo.grid(row=2, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Response Status:").grid(row=3, column=0, sticky=tk.W)
        resp_var = tk.StringVar(value="Registered")
        resp_combo = ttk.Combobox(self.input_frame, textvariable=resp_var, state="readonly")
        resp_combo['values'] = ['Registered', 'Attended', 'Cancelled']
        resp_combo.grid(row=3, column=1, sticky=(tk.W, tk.E))
        def submit():
            if not all([pid.get(), event_var.get(), student_var.get()]):
                messagebox.showerror("Input Error", "Please fill required fields!")
                return
            pid_val = self.validate_int(pid.get(), "Participation ID")
            if pid_val is None:
                return
            try:
                event_id_val = int(event_var.get().split(' - ')[0])
                student_id_val = int(student_var.get().split(' - ')[0])
            except Exception:
                messagebox.showerror("Input Error", "Select valid event and student!")
                return
            q = "INSERT INTO EventParticipationStudent (pid, event_id, student_id, resp_status) VALUES (%s,%s,%s,%s)"
            self.safe_execute(q, (pid_val, event_id_val, student_id_val, resp_var.get()), "Student participation registered!")
            self.view_participation_students()
        tk.Button(self.input_frame, text="Register Student", command=submit, bg='#27ae60', fg='white').grid(row=4, column=0, columnspan=2, pady=6)
    
    def add_participation_alumni_gui(self):
        self.clear_input_frame()
        events = self.get_events_list()
        alumni = self.get_alumni_list()
        if not events or not alumni:
            messagebox.showerror("Error", "Need events and alumni to register participation.")
            return
        tk.Label(self.input_frame, text="Participation ID:*").grid(row=0, column=0, sticky=tk.W)
        pid = tk.Entry(self.input_frame); pid.grid(row=0, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Event:*").grid(row=1, column=0, sticky=tk.W)
        event_var = tk.StringVar()
        event_combo = ttk.Combobox(self.input_frame, textvariable=event_var, state="readonly")
        event_combo['values'] = [f"{e[0]} - {e[1]}" for e in events]
        event_combo.grid(row=1, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Alumni:*").grid(row=2, column=0, sticky=tk.W)
        alumni_var = tk.StringVar()
        al_combo = ttk.Combobox(self.input_frame, textvariable=alumni_var, state="readonly")
        al_combo['values'] = [f"{a[0]} - {a[1]}" for a in alumni]
        al_combo.grid(row=2, column=1, sticky=(tk.W, tk.E))
        tk.Label(self.input_frame, text="Response Status:").grid(row=3, column=0, sticky=tk.W)
        resp_var = tk.StringVar(value="Registered")
        resp_combo = ttk.Combobox(self.input_frame, textvariable=resp_var, state="readonly")
        resp_combo['values'] = ['Registered', 'Attended', 'Cancelled']
        resp_combo.grid(row=3, column=1, sticky=(tk.W, tk.E))
        def submit():
            if not all([pid.get(), event_var.get(), alumni_var.get()]):
                messagebox.showerror("Input Error", "Please fill required fields!")
                return
            pid_val = self.validate_int(pid.get(), "Participation ID")
            if pid_val is None:
                return
            try:
                event_id_val = int(event_var.get().split(' - ')[0])
                alumni_id_val = int(alumni_var.get().split(' - ')[0])
            except Exception:
                messagebox.showerror("Input Error", "Select valid event and alumni!")
                return
            q = "INSERT INTO EventParticipationAlumni (pid, event_id, alumni_id, resp_status) VALUES (%s,%s,%s,%s)"
            self.safe_execute(q, (pid_val, event_id_val, alumni_id_val, resp_var.get()), "Alumni participation registered!")
            self.view_participation_alumni()
        tk.Button(self.input_frame, text="Register Alumni", command=submit, bg='#27ae60', fg='white').grid(row=4, column=0, columnspan=2, pady=6)
    
    def view_participation_students(self):
        q = """SELECT P.pid, E.name as event_name, S.name as student_name, P.resp_status
               FROM EventParticipationStudent P
               JOIN Event E ON P.event_id=E.event_id
               JOIN Student S ON P.student_id=S.student_id
               ORDER BY P.pid"""
        res = self.execute_query(q)
        if res:
            results, columns = res
            self.show_results(results, columns)
        else:
            self.result_text.insert(tk.END, "No student participation records found.")
    
    def view_participation_alumni(self):
        q = """SELECT P.pid, E.name as event_name, A.name as alumni_name, P.resp_status
               FROM EventParticipationAlumni P
               JOIN Event E ON P.event_id=E.event_id
               JOIN Alumni A ON P.alumni_id=A.alumni_id
               ORDER BY P.pid"""
        res = self.execute_query(q)
        if res:
            results, columns = res
            self.show_results(results, columns)
        else:
            self.result_text.insert(tk.END, "No alumni participation records found.")
    
    def count_event_participants(self):
        """Show total number of attendees (students + alumni) per event"""
        query = """
        SELECT e.event_id,
            e.name AS Event_Name,
            (SELECT COUNT(*) FROM EventParticipationStudent eps
                WHERE eps.event_id = e.event_id AND eps.resp_status = 'Attended')
            +
            (SELECT COUNT(*) FROM EventParticipationAlumni epa
                WHERE epa.event_id = e.event_id AND epa.resp_status = 'Attended')
            AS Total_Attendees
        FROM Event e
        ORDER BY e.event_id;
        """
        results, columns = self.execute_query(query)
        self.show_results(results, columns)


    def delete_participant(self):
        """Delete a participant record (student/alumni) by PID"""
        self.clear_input_frame()
        
        tk.Label(self.input_frame, text="Participant Type:* (Student / Alumni)").grid(row=0, column=0, sticky=tk.W)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(self.input_frame, textvariable=type_var, state="readonly")
        type_combo['values'] = ['Student', 'Alumni']
        type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        tk.Label(self.input_frame, text="Participation ID (pid):*").grid(row=1, column=0, sticky=tk.W)
        pid_entry = tk.Entry(self.input_frame)
        pid_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        def delete_record():
            if not type_var.get() or not pid_entry.get():
                messagebox.showerror("Input Error", "Please select participant type and enter PID!")
                return
            
            pid_val = self.validate_int(pid_entry.get(), "Participation ID")
            if pid_val is None:
                return
            
            table = "EventParticipationStudent" if type_var.get() == "Student" else "EventParticipationAlumni"
            query = f"DELETE FROM {table} WHERE pid=%s"
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this {type_var.get()} participant?"):
                if self.safe_execute(query, (pid_val,), f"{type_var.get()} participant deleted successfully!"):
                    if type_var.get() == "Student":
                        self.view_participation_students()
                    else:
                        self.view_participation_alumni()
        
        delete_btn = tk.Button(self.input_frame, text="Delete Participant", command=delete_record,
                            bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'))
        delete_btn.grid(row=2, column=0, columnspan=2, pady=10)

    def show_total_events_attended_gui(self):
        """Show total number of events attended by a selected alumni using SQL function"""
        self.clear_input_frame()
        self.content_title.config(text="🎯 Total Events Attended by Alumni")

        alumni_list = self.get_alumni_list()
        if not alumni_list:
            messagebox.showerror("Error", "No alumni records found.")
            return

        tk.Label(self.input_frame, text="Select Alumni:*").grid(row=0, column=0, sticky=tk.W)
        alumni_var = tk.StringVar()
        alumni_combo = ttk.Combobox(self.input_frame, textvariable=alumni_var, state="readonly")
        alumni_combo['values'] = [f"{a[0]} - {a[1]}" for a in alumni_list]
        alumni_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))

        def show_result():
            if not alumni_var.get():
                messagebox.showerror("Input Error", "Please select an alumni!")
                return
            try:
                alumni_id_val = int(alumni_var.get().split(' - ')[0])
            except Exception:
                messagebox.showerror("Input Error", "Invalid alumni selected!")
                return

            query = """
                SELECT A.name AS Alumni_Name,
                    total_events_attended(A.alumni_id) AS Events_Attended
                FROM Alumni A
                WHERE A.alumni_id = %s
            """
            res = self.execute_query(query, (alumni_id_val,))
            if res == "permission_denied":
                return 
            if res:
                results, columns = res
                self.show_results(results, columns)
            else:
                self.result_text.insert(tk.END, "No attendance data found for this alumni.")

        tk.Button(self.input_frame, text="Show Events Attended", command=show_result,
                bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).grid(row=1, column=0, columnspan=2, pady=10)
    
    def view_alumni_by_event_gui(self):
        """Display alumni who participated in a selected event."""
        self.clear_input_frame()

        tk.Label(self.input_frame, text="Select Event:*").grid(row=0, column=0, sticky=tk.W)

        # Fetch event names from the database
        query = "SELECT name FROM Event ORDER BY name"
        res = self.execute_query(query)
        events = [r[0] for r in res[0]] if res and res[0] else []

        event_var = tk.StringVar()
        event_combo = ttk.Combobox(self.input_frame, textvariable=event_var, state="readonly", width=40)
        event_combo['values'] = events
        event_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        def show_results():
            if not event_var.get():
                messagebox.showwarning("Input Error", "Please select an event!")
                return
            query = """
            SELECT A.alumni_id, A.name, A.email, A.company
            FROM Alumni A
            WHERE A.alumni_id IN (
                SELECT EPA.alumni_id
                FROM EventParticipationAlumni EPA
                WHERE EPA.event_id = (
                    SELECT E.event_id
                    FROM Event E
                    WHERE E.name = %s
                )
            )
            ORDER BY A.name;
            """
            res = self.execute_query(query, (event_var.get(),))
            if res == "permission_denied":
                return 
            if res and res[0]:
                results, columns = res
                self.show_results(results, columns)
            else:
                messagebox.showinfo("Info", f"No alumni found for event '{event_var.get()}'.")

        show_btn = tk.Button(self.input_frame, text="Show Alumni", command=show_results,
                            bg='#9b59b6', fg='white', font=('Arial', 10))
        show_btn.grid(row=1, column=0, columnspan=2, pady=10)

    def update_participation_status_gui(self):
        """Update RSVP status (Registered, Attended, Cancelled) for Student or Alumni"""
        self.clear_input_frame()

        # Choose type (Student / Alumni)
        tk.Label(self.input_frame, text="Participant Type:* (Student / Alumni)").grid(row=0, column=0, sticky=tk.W)
        type_var = tk.StringVar()
        type_combo = ttk.Combobox(self.input_frame, textvariable=type_var, state="readonly")
        type_combo['values'] = ['Student', 'Alumni']
        type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Enter participation ID
        tk.Label(self.input_frame, text="Participation ID (pid):*").grid(row=1, column=0, sticky=tk.W)
        pid_entry = tk.Entry(self.input_frame)
        pid_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        # Choose new status
        tk.Label(self.input_frame, text="New RSVP Status:*").grid(row=2, column=0, sticky=tk.W)
        status_var = tk.StringVar()
        status_combo = ttk.Combobox(self.input_frame, textvariable=status_var, state="readonly")
        status_combo['values'] = ['Registered', 'Attended', 'Cancelled']
        status_combo.grid(row=2, column=1, sticky=(tk.W, tk.E))

        def update_status():
            if not all([type_var.get(), pid_entry.get(), status_var.get()]):
                messagebox.showerror("Input Error", "Please fill all required fields!")
                return

            pid_val = self.validate_int(pid_entry.get(), "Participation ID")
            if pid_val is None:
                return

            table = "EventParticipationStudent" if type_var.get() == "Student" else "EventParticipationAlumni"
            query = f"UPDATE {table} SET resp_status=%s WHERE pid=%s"

            if self.safe_execute(query, (status_var.get(), pid_val), f"{type_var.get()} RSVP status updated successfully!"):
                if type_var.get() == "Student":
                    self.view_participation_students()
                else:
                    self.view_participation_alumni()

        tk.Button(self.input_frame, text="Update RSVP Status", command=update_status,
                bg='#f39c12', fg='white', font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, pady=10)

def main():
    root = tk.Tk()
    app = AlumniDBGUI(root)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()