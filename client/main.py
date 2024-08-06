import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkcalendar import Calendar
from tkinter import ttk
from PIL import ImageTk, Image
import threading
import socket
import sys
import time
import os

SERVER_HOST = "192.168.1.26"
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"
PATH = "PATH"
DOWNLOAD_FOLDER = "uploads"

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_widget_scaling(1.0)  # Set UI scaling to 100% by default

# separate id and name function
def sep_id_and_info(id_info):
    get_id = id_info[:4]
    get_name = id_info[7:]
    return get_id, get_name

# get file extension function
def get_file_extension(file_info):
    parts = file_info.split(' - ')
    filename = parts[2]
    extension = filename.split('.')[-1]
    return extension

# take signal from server function
def take_signal(signal):
    # create a socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # send signal to the server
    client_socket.sendall(signal.encode())

    # receive data from the server
    data = client_socket.recv(1024).decode()
    
    # close the connection
    client_socket.close()
    
    return data

# handle signal to server function
def handle_client(client_socket):
    try:
        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)
        
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)
        with open(filepath, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    break
                f.write(bytes_read)
        print(f"File {filename} received successfully")
    finally:
        client_socket.close()

# read from server message to dictionary function
def import_data_from_server(key_from_server, value_from_server):
    key_and_value = ["", ""]
    index = 0
    for i in key_from_server:
        if (i == ':') or (i == '|'):
            if i == '|':
                value_from_server[key_and_value[0]] = key_and_value[1]
                key_and_value = ["", ""]
            index = 1 - index
        else:
            key_and_value[index] += i

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
             
        # initialize user login data
        self.users_login = {} # {"account": "password"}
        self.current_user = None
        
        # message from server user and password
        message_from_server_uap = take_signal("user")
       
        # import user login data
        import_data_from_server(message_from_server_uap, self.users_login)
        
        # initialize all server files data
        self.all_server_files = {} # {"id": "acc_name_file_and_upload_date"}
        
        # message from server all server files
        message_from_server_asf = take_signal("asf")
          
        # import all server files data
        import_data_from_server(message_from_server_asf, self.all_server_files)
        
        # initialize starred files data
        self.starred_files = {} # {"id": "acc_name_file_and_upload_date"}
        
        # initialize deleted files data
        self.deleted_files = {} # {"id": "acc_name_file_and_upload_date"}
        
        # configure window
        self.title("Box Storage")
        self.geometry(f"{1175}x{660}")
        self.iconbitmap(PATH + "mmt_project/client/image/icon_logo.ico") 
        
        # import image
        image_bg = ImageTk.PhotoImage(Image.open(PATH + "mmt_project/client/image/background_frame.jpg"))
        logo_image = Image.open(PATH + "mmt_project/client/image/logo.png")
        logo_image = logo_image.resize((140, 81))
        image_logo = ImageTk.PhotoImage(logo_image)
        
        # create background frame
        self.background_frame = customtkinter.CTkFrame(self, width=1100, height=620)
        self.background_frame.pack(fill="both", expand=True)
        
        # create background label
        self.background_label = customtkinter.CTkLabel(master=self.background_frame, image=image_bg)
        self.background_label.pack(fill="both", expand=True)        
        
        # create login frame
        self.login_frame = customtkinter.CTkFrame(master=self.background_label, width=400, height=300, corner_radius=0, fg_color="Snow")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.login_label = customtkinter.CTkLabel(self.login_frame, text="Login", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.login_label.grid(row=0, column=0, padx=20, pady=(20, 10), columnspan=2)

        self.username_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text="Username")
        self.username_entry.grid(row=1, column=0, padx=20, pady=10, columnspan=2)

        self.password_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
        self.password_entry.grid(row=2, column=0, padx=20, pady=10, columnspan=2)

        self.login_button = customtkinter.CTkButton(self.login_frame, text="Login", command=self.login, fg_color="SlateBlue", hover_color="MediumSlateBlue")
        self.login_button.grid(row=3, column=0, padx=20, pady=10)

        self.register_button = customtkinter.CTkButton(self.login_frame, text="Register", command=self.show_register_frame, fg_color="SlateBlue", hover_color="MediumSlateBlue")
        self.register_button.grid(row=3, column=1, padx=20, pady=10)

        # create register frame
        self.register_frame = customtkinter.CTkFrame(master=self.background_label, width=400, height=300, corner_radius=0, fg_color="Snow")

        self.register_label = customtkinter.CTkLabel(self.register_frame, text="Register", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.register_label.grid(row=0, column=0, padx=20, pady=(20, 10), columnspan=2)

        self.new_username_entry = customtkinter.CTkEntry(self.register_frame, placeholder_text="Username")
        self.new_username_entry.grid(row=1, column=0, padx=20, pady=10, columnspan=2)

        self.new_password_entry = customtkinter.CTkEntry(self.register_frame, placeholder_text="Password", show="*")
        self.new_password_entry.grid(row=2, column=0, padx=20, pady=10, columnspan=2)

        self.confirm_password_entry = customtkinter.CTkEntry(self.register_frame, placeholder_text="Confirm Password", show="*")
        self.confirm_password_entry.grid(row=3, column=0, padx=20, pady=10, columnspan=2)

        self.create_account_button = customtkinter.CTkButton(self.register_frame, text="Create Account", command=self.register, fg_color="SlateBlue", hover_color="MediumSlateBlue")
        self.create_account_button.grid(row=4, column=0, padx=20, pady=10)

        self.back_to_login_button = customtkinter.CTkButton(self.register_frame, text="Back to Login", command=self.show_login_frame, fg_color="SlateBlue", hover_color="MediumSlateBlue")
        self.back_to_login_button.grid(row=4, column=1, padx=20, pady=10)
        

        # create main frame for file manager
        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        
        # configure grid layout (4x4)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure((2, 3), weight=0)
        self.main_frame.grid_rowconfigure((0, 1, 2), weight=1)
        
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self.main_frame, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="File Manager", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Upload", command=self.upload_file)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="My Storage", command=self.open_my_storage)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Recycle Bin", command=self.open_trash_bin)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        self.language_button = customtkinter.CTkButton(self.sidebar_frame, text="English", command=self.change_language_event)
        self.language_button.grid(row=4, column=0, padx=20, pady=(10, 0))
        
        self.logo_button = customtkinter.CTkButton(self.sidebar_frame, image=image_logo, text="", fg_color="transparent", hover_color=["Gainsboro", "#2B2B2B"], command=self.show_setting_window)
        self.logo_button.grid(row=5, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
    
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.set("100%")
        self.scaling_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="Enter URL of File")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")

        self.main_button_1 = customtkinter.CTkButton(master=self.main_frame, text="Search", border_width=2, command=self.upload_file_by_path)
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self.main_frame, width=250)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.textbox.insert("0.0", "Process Activity Log :\n\n" + "Log-Message \"Application started\"\n" + "Log-Message \"User logged in\"\n" + "Log-Message \"Data user updated\"\n\n" + "This screen will show the activities you perform in this application. That processes will be shown below...\n\n")

        # create clock and calendar by tabview
        self.tabview = customtkinter.CTkTabview(self.main_frame, width=0)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Time by hours")
        self.tabview.add("Time by dates")
        self.tabview.tab("Time by hours").grid_columnconfigure(0, weight=1)  
        self.tabview.tab("Time by dates").grid_columnconfigure(0, weight=1)

        # create labels to notify time by hours and time by dates
        self.label_tab_1 = customtkinter.CTkButton(self.tabview.tab("Time by hours"), text="Hours : Minutes", command=self.show_calendar)
        self.label_tab_1.grid(row=2, column=0, padx=20, pady=(20, 20))
        self.label_tab_2 = customtkinter.CTkButton(self.tabview.tab("Time by dates"), text="Dates - Months", command=self.show_calendar)
        self.label_tab_2.grid(row=2, column=0, padx=20, pady=(20, 20))
        
        # create real-time digital clock
        self.clock_label = customtkinter.CTkLabel(self.tabview.tab("Time by hours"), text="", font=("Arial", 55))
        self.clock_label.grid(row=3, column=0, padx=20, pady=20)
        self.update_clock()
        
        # create real-time digital calendar
        self.date_label = customtkinter.CTkLabel(self.tabview.tab("Time by dates"), text="", font=("Arial", 55))
        self.date_label.grid(row=3, column=0, padx=20, pady=20)
        self.update_date_month()

        # create notification frame
        self.radiobutton_frame = customtkinter.CTkFrame(self.main_frame)
        self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radiobutton_frame.grid_columnconfigure(0, weight=1)  

        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Notification", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_radio_group.grid(row=0, column=0, pady=(10, 0), padx=20, sticky="n")
        
        self.radio = customtkinter.CTkLabel(master=self.radiobutton_frame, text="All processes successfully")
        self.radio.grid(row=1, column=0, pady=5, padx=20, sticky="n")

        self.radio_var = tkinter.IntVar(value=0)

        # create buttons, slider and progressbar frame
        self.slider_progressbar_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        
        # create buttons of all server file and starred file
        self.open_asf = customtkinter.CTkButton(self.slider_progressbar_frame, text="All Server File", command=self.open_all_server_file)
        self.open_asf.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.open_sf = customtkinter.CTkButton(self.slider_progressbar_frame, text="Starred File", command=self.open_starred_file)
        self.open_sf.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")          
        
        # create progressbars and sliders
        self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_1 = customtkinter.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
        self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_2 = customtkinter.CTkSlider(self.slider_progressbar_frame, orientation="vertical")
        self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        self.progressbar_3 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, orientation="vertical")
        self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

        self.slider_1.configure(command=self.progressbar_2.set)
        self.slider_2.configure(command=self.progressbar_3.set)

        # create help frame with FAQ
        self.help_frame = customtkinter.CTkScrollableFrame(self.main_frame, label_text="Help - FAQ")
        self.help_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.help_frame.grid_columnconfigure(0, weight=1)

        self.faq_questions = [
            "How to upload a file?",
            "How to download a file?",
            "How to delete a file?",
            "How to search by file URL?",
            "How to change scaling?",
            "How to change language?",
            "How to restore a file?",
            "How to change appearance mode?",
            "How to starred a file?",
            "How to unstarred a file?",
            "How to delete a file?",
            "How to change hours to dates?",
            "How to open the calendar?",
            "How to find our product code?",
            "How to change password?",
            "How to log out?"
        ]

        self.faq_answers = {
            "How to upload a file?": "To upload a file, click on the 'Upload' button in the sidebar and select the file you want to upload.",
            "How to download a file?": "To download a file, click on the 'Download' button in 'All Server File', 'Starred File' or 'My Storage' after select the file you want to download.",
            "How to remove a file?": "To remove a file, select the file and click on the 'Remove' button in 'My Storage'. The file will be moved to the recycle bin.",
            "How to search by file URL?": "To search by file URL, enter the URL in the search box and click the 'Search' button.",
            "How to change scaling?": "To change the UI scaling, select the desired scaling from the 'UI Scaling' dropdown in the sidebar.",
            "How to change language?": "To change the language, click on the 'Language' button in the sidebar. This will toggle between English and Vietnamese.",            
            "How to restore a file?": "To restore a file from the recycle bin, click on the 'Recycle Bin' button in the sidebar, select file, and click 'Restore'.",
            "How to change appearance mode?": "To change the appearance mode, select the desired mode from the 'Appearance Mode' dropdown in the sidebar.",
            "How to starred a file?": "To starred a file, click on the 'All Server File' button. This will mark file as starred.",
            "How to unstarred a file?": "To unstarred a file, click on the 'Starred File' button in the sidebar, select file, and click 'Unstarred'.",
            "How to delete a file?": "To delete a file, click on the 'Delete' button in the recycle bin, select file, and click 'Delete'.",
            "How to change hours to dates?": "To change hours to dates, click on the 'Time by dates' tab in the main frame.",
            "How to open the calendar?": "To open the calendar, click on the 'Hours - Minutes' or 'Dates - Months' label in the 'Time by dates' tab.",
            "How to find our product code?": "To find our product code, click on the 'Box', then click to our qr code to see our product.",
            "How to change password?": "To change password, click on the 'Box', then click on the 'Change Password' button.",
            "How to log out?": "To log out, click on the 'Box', then click on the 'Log Out' button."
        }

        for question in self.faq_questions:
            button = customtkinter.CTkButton(self.help_frame, text=question, command=lambda q=question: self.show_answer(q))
            button.pack(pady=5, padx=10)

        # create contact us frame
        self.contact_us_frame = customtkinter.CTkFrame(self.main_frame)
        self.contact_us_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.contact_label = customtkinter.CTkLabel(master=self.contact_us_frame, text="Contact Us", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.contact_label.grid(row=0, column=0, pady=10, padx=20, sticky="n")

        self.name_label = customtkinter.CTkLabel(master=self.contact_us_frame, text="Team : Your Team")
        self.name_label.grid(row=1, column=0, pady=5, padx=20, sticky="n")

        self.email_label = customtkinter.CTkLabel(master=self.contact_us_frame, text="Email : example@gmail.com")
        self.email_label.grid(row=2, column=0, pady=5, padx=20, sticky="n")

        self.phone_label = customtkinter.CTkLabel(master=self.contact_us_frame, text="Phone : +123456789")
        self.phone_label.grid(row=3, column=0, pady=5, padx=20, sticky="n")

        self.address_label = customtkinter.CTkLabel(master=self.contact_us_frame, text="Address : 227 Nguyen Van Cu\nWard 4, District 5\nHo Chi Minh City, Viet Nam")
        self.address_label.grid(row=4, column=0, pady=5, padx=20, sticky="n")
        
    # create a function to show login frame
    def show_login_frame(self):
        self.register_frame.place_forget()
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

    # create a function to show register frame
    def show_register_frame(self):
        self.login_frame.place_forget()
        self.register_frame.place(relx=0.5, rely=0.5, anchor="center")

    # create a function to open folder manager
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.users_login and self.users_login[username] == password:
            self.current_user = username
            self.login_frame.place_forget()
            self.background_frame.pack_forget()
            self.main_frame.grid(row=0, column=0, sticky="nsew")
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.notice_sign = customtkinter.CTkLabel(master=self.radiobutton_frame, text=f"Welcome, {username}")
            self.notice_sign.grid(row=2, column=0, pady=5, padx=20, sticky="n")
            self.after(2000, self.show_notification)
            
            # message from server starred files
            message_from_server_sf = take_signal(self.current_user + "|sf")
                        
            # import starred files data
            if message_from_server_sf != "none":
                import_data_from_server(message_from_server_sf, self.starred_files)
            
            # message from server deleted files
            message_from_server_df = take_signal(self.current_user + "|rb")
            
            # import deleted files data
            if message_from_server_df != "none":
                import_data_from_server(message_from_server_df, self.deleted_files)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # create a function to register
    def register(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if username in self.users_login:
            messagebox.showerror("Registration Failed", "Username already exists.")
        elif password != confirm_password:
            messagebox.showerror("Registration Failed", "Passwords do not match.")
        else:
            self.users_login[username] = password
            messagebox.showinfo("Registration Successful", "Account created successfully.")
            take_signal(username + '|' + password + "|uu")
            self.show_login_frame()

    # create a function to log activities
    def log_activity(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.textbox.insert(tkinter.END, f"{timestamp} - {message}\n")
        self.textbox.yview(tkinter.END)  

    # change appearance mode event
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        self.log_activity(f"Changed appearance mode to {new_appearance_mode}.")

    # change scaling event
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
        self.log_activity(f"Changed scaling to {new_scaling}.")

    # update clock vietnam
    def update_clock(self):
        vietnam_hours = time.strftime('%H:%M')
        self.clock_label.configure(text=vietnam_hours)
        self.after(1000, self.update_clock)

    # update date month
    def update_date_month(self):
        vietnam_dates = time.strftime('%d-%m')
        self.date_label.configure(text=vietnam_dates)
        self.after(86400000, self.update_date_month)
        
    # show callendar
    def show_calendar(self):
        self.log_activity("Opened Calendar.")
        calendar_window = customtkinter.CTkToplevel(self)
        calendar_window.title("Calendar")
        calendar_window.geometry(f"{550}x{400}")
        calendar_window.attributes('-topmost', True)
        calendar_window.resizable(False, False)
        
        calendar_window_frame = customtkinter.CTkFrame(calendar_window)
        calendar_window_frame.pack(fill="both", padx=10, pady=10, expand=True)
        
        calendar_window_style = ttk.Style(calendar_window)
        calendar_window_style.theme_use("default")
 
        cal = Calendar(calendar_window_frame, selectmode='day', locale='en_US', disabledforeground='red',
                    cursor="hand2", background=customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                    selectbackground=customtkinter.ThemeManager.theme["CTkButton"]["fg_color"][1])
        cal.pack(fill="both", expand=True, padx=10, pady=10)       
        
    # create a function to show answer
    def show_answer(self, question):
        answer = self.faq_answers.get(question, "Answer not found.")
        tkinter.messagebox.showinfo("Answer", answer)
        self.log_activity(f"FAQ: {question}")

    # change language event
    def change_language_event(self):
        current_text = self.language_button.cget("text")
        if current_text == "English":
            self.logo_label.configure(text="Quản lý Tệp")
            self.language_button.configure(text="Tiếng Việt")
            self.sidebar_button_1.configure(text="Tải lên")
            self.sidebar_button_2.configure(text="Tệp cá nhân")
            self.sidebar_button_3.configure(text="Thùng rác")
            self.appearance_mode_label.configure(text="Chế độ giao diện:")
            self.scaling_label.configure(text="Tỷ lệ giao diện:")
            self.label_tab_1.configure(text="Giờ : Phút")
            self.label_tab_2.configure(text="Ngày - Tháng")
            self.help_frame.configure(label_text="Trợ giúp - Câu hỏi thường gặp")
            self.open_asf.configure(text="Tất cả tệp trên máy chủ")
            self.open_sf.configure(text="Tệp được đánh dấu")
            self.label_radio_group.configure(text="Thông báo")
            self.contact_label.configure(text="Liên hệ với chúng tôi")
            self.entry.configure(placeholder_text="Nhập URL của tệp")
            self.main_button_1.configure(text="Tìm kiếm")
            self.log_activity("Đã chuyển sang tiếng Việt.")
        else:
            self.logo_label.configure(text="File Manager")
            self.language_button.configure(text="English")
            self.sidebar_button_1.configure(text="Upload")
            self.sidebar_button_2.configure(text="My Storage")
            self.sidebar_button_3.configure(text="Recycle Bin")
            self.appearance_mode_label.configure(text="Appearance Mode:")
            self.scaling_label.configure(text="UI Scaling:")
            self.label_tab_1.configure(text="Hours : Minutes")
            self.label_tab_2.configure(text="Dates - Months")
            self.help_frame.configure(label_text="Help - FAQ")
            self.open_asf.configure(text="All Server File")
            self.open_sf.configure(text="Starred File")
            self.label_radio_group.configure(text="Notification")
            self.contact_label.configure(text="Contact Us")
            self.entry.configure(placeholder_text="Enter URL of File")
            self.main_button_1.configure(text="Search")
            self.log_activity("Switched to English.")
            
    # upload file to server function
    def upload_to_server(self, file_path):
        if not file_path:
            raise ValueError("File path must not be null or empty")
        
        filesize = os.path.getsize(file_path)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
        except ConnectionRefusedError:
            self.log_activity(f"Connection to server refused. Make sure the server is running.")
            return
                
        try:
            client_socket.send(f"{file_path}{SEPARATOR}{filesize}".encode())
        except ConnectionResetError:
            self.log_activity("Connection to server was reset. Make sure the server is running.")
            return
        
        with open(file_path, "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                try:
                    client_socket.sendall(bytes_read)
                except ConnectionResetError:
                    self.log_activity("Connection to server was reset. Make sure the server is running.")
                    return
                
        client_socket.close()
        self.log_activity(f"File {file_path} uploaded successfully.")

    # upload file functions
    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.upload_to_server(file_path)
        else:
            self.log_activity("No file selected to upload.")
                
    # upload file by path
    def upload_file_by_path(self):
        file_path = self.entry.get()
        if os.path.isfile(file_path):
            self.upload_to_server(file_path)
        else:
            self.log_activity("Invalid file path.")

    # open my storage function
    def open_my_storage(self):
        self.log_activity("Opened My Storage.")
        my_storage_window = customtkinter.CTkToplevel(self)
        my_storage_window.title("My Storage")
        my_storage_window.geometry(f"{420}x{300}")
        my_storage_window.attributes('-topmost', True)
        my_storage_window.resizable(False, False)
        
        # configure grid layout (3x2)
        my_storage_window.grid_columnconfigure(1, weight=1)
        my_storage_window.grid_columnconfigure((0, 2, 3), weight=0)
        my_storage_window.grid_rowconfigure((0, 1), weight=1)
        my_storage_window.grid_rowconfigure(2, weight=0)

        # create scrollable frame
        my_storage_window.scrollable_frame = customtkinter.CTkScrollableFrame(my_storage_window, label_text="My Storage", height=650)
        my_storage_window.scrollable_frame.grid(row=1, column=0, columnspan=4, padx=(20, 20), pady=(20, 10), sticky="nsew")
        my_storage_window.scrollable_frame.grid_columnconfigure(0, weight=1)
        my_storage_window.scrollable_frame_checkboxes = []
        self.all_server_files = dict(sorted(self.all_server_files.items()))
        count_line = 0
        for id_ms, afd_ms in (self.all_server_files).items():
            a_ms = afd_ms.split(' - ')[0]
            if a_ms == self.current_user:
                checkbox = customtkinter.CTkCheckBox(master=my_storage_window.scrollable_frame, text=f"{id_ms} - {afd_ms}", width=100)
                checkbox.grid(row=count_line, column=0, padx=10, pady=(0, 20))
                my_storage_window.scrollable_frame_checkboxes.append(checkbox)
                count_line += 1

        # create additional buttons in the top-right corner
        my_storage_window.button_1 = customtkinter.CTkButton(my_storage_window, text="Remove", width=180, command=lambda: self.remove_file(my_storage_window.scrollable_frame_checkboxes, my_storage_window))
        my_storage_window.button_1.grid(row=2, column=1, padx=(10, 10), pady=(20, 10), sticky="ne")

        my_storage_window.button_2 = customtkinter.CTkButton(my_storage_window, text="Download", width=180, command=lambda: self.download_file(my_storage_window.scrollable_frame_checkboxes, my_storage_window))
        my_storage_window.button_2.grid(row=2, column=2, padx=(10, 20), pady=(20, 10), sticky="ne")
    
    # open trash bin function
    def open_trash_bin(self):
        self.log_activity("Opened Recycle Bin.")
        trash_bin_window = customtkinter.CTkToplevel(self)
        trash_bin_window.title("Recycle Bin")
        trash_bin_window.geometry(f"{420}x{300}")
        trash_bin_window.attributes('-topmost', True)
        trash_bin_window.resizable(False, False)
        
        # configure grid layout (3x2)
        trash_bin_window.grid_columnconfigure(1, weight=1)
        trash_bin_window.grid_columnconfigure((0, 2, 3), weight=0)
        trash_bin_window.grid_rowconfigure((0, 1), weight=1)
        trash_bin_window.grid_rowconfigure(2, weight=0)

        # create scrollable frame
        trash_bin_window.scrollable_frame = customtkinter.CTkScrollableFrame(trash_bin_window, label_text="Recycle Bin", height=650)
        trash_bin_window.scrollable_frame.grid(row=1, column=0, columnspan=4, padx=(20, 20), pady=(20, 10), sticky="nsew")
        trash_bin_window.scrollable_frame.grid_columnconfigure(0, weight=1)
        trash_bin_window.scrollable_frame_checkboxes = []
        self.deleted_files = dict(sorted(self.deleted_files.items()))
        count_line = 0
        for id_rb, afd_rb in (self.deleted_files).items():
            checkbox = customtkinter.CTkCheckBox(master=trash_bin_window.scrollable_frame, text=f"{id_rb} - {afd_rb}", width=100)
            checkbox.grid(row=count_line, column=0, padx=10, pady=(0, 20))
            trash_bin_window.scrollable_frame_checkboxes.append(checkbox)
            count_line += 1

        # create additional buttons in the top-right corner
        trash_bin_window.button_1 = customtkinter.CTkButton(trash_bin_window, text="Restore", width=180, command=lambda: self.restore_file(trash_bin_window.scrollable_frame_checkboxes, trash_bin_window))
        trash_bin_window.button_1.grid(row=2, column=1, padx=(10, 10), pady=(20, 10), sticky="ne")

        trash_bin_window.button_2 = customtkinter.CTkButton(trash_bin_window, text="Delete", width=180, command=lambda: self.delete_file(trash_bin_window.scrollable_frame_checkboxes, trash_bin_window))
        trash_bin_window.button_2.grid(row=2, column=2, padx=(10, 20), pady=(20, 10), sticky="ne")  

    # open all server file function
    def open_all_server_file(self):
        self.log_activity("Opened All Server File.")
        all_server_file_window = customtkinter.CTkToplevel(self)
        all_server_file_window.title("All Server File")
        all_server_file_window.geometry(f"{420}x{300}")
        all_server_file_window.attributes('-topmost', True)
        all_server_file_window.resizable(False, False)
        
        # configure grid layout (3x2)
        all_server_file_window.grid_columnconfigure(1, weight=1)
        all_server_file_window.grid_columnconfigure((0, 2, 3), weight=0)
        all_server_file_window.grid_rowconfigure((0, 1), weight=1)
        all_server_file_window.grid_rowconfigure(2, weight=0)

        # create scrollable frame
        all_server_file_window.scrollable_frame = customtkinter.CTkScrollableFrame(all_server_file_window, label_text="All Server File", height=650)
        all_server_file_window.scrollable_frame.grid(row=1, column=0, columnspan=4, padx=(20, 20), pady=(20, 10), sticky="nsew")
        all_server_file_window.scrollable_frame.grid_columnconfigure(0, weight=1)
        all_server_file_window.scrollable_frame_checkboxes = []
        self.all_server_files = dict(sorted(self.all_server_files.items()))
        count_line = 0
        for id_asf, afd_asf in (self.all_server_files).items():
            checkbox = customtkinter.CTkCheckBox(master=all_server_file_window.scrollable_frame, text=f"{id_asf} - {afd_asf}", width=100)
            checkbox.grid(row=count_line, column=0, padx=10, pady=(0, 20))
            all_server_file_window.scrollable_frame_checkboxes.append(checkbox)
            count_line += 1

        # create additional buttons in the top-right corner
        all_server_file_window.button_1 = customtkinter.CTkButton(all_server_file_window, text="Download", width=180, command=lambda: self.download_file(all_server_file_window.scrollable_frame_checkboxes, all_server_file_window))
        all_server_file_window.button_1.grid(row=2, column=1, padx=(10, 10), pady=(20, 10), sticky="ne")

        all_server_file_window.button_2 = customtkinter.CTkButton(all_server_file_window, text="Starred", width=180, command=lambda: self.starred_file(all_server_file_window.scrollable_frame_checkboxes, all_server_file_window))
        all_server_file_window.button_2.grid(row=2, column=2, padx=(10, 20), pady=(20, 10), sticky="ne")        
        
    # open starred file function
    def open_starred_file(self):
        self.log_activity("Opened Starred File.")
        starred_window = customtkinter.CTkToplevel(self)
        starred_window.title("Starred File")
        starred_window.geometry(f"{420}x{300}")
        starred_window.attributes('-topmost', True)
        starred_window.resizable(False, False)
        
        # configure grid layout (3x2)
        starred_window.grid_columnconfigure(1, weight=1)
        starred_window.grid_columnconfigure((0, 2, 3), weight=0)
        starred_window.grid_rowconfigure((0, 1), weight=1)
        starred_window.grid_rowconfigure(2, weight=0)

        # create scrollable frame
        starred_window.scrollable_frame = customtkinter.CTkScrollableFrame(starred_window, label_text="Starred File", height=650)
        starred_window.scrollable_frame.grid(row=1, column=0, columnspan=4, padx=(20, 20), pady=(20, 10), sticky="nsew")
        starred_window.scrollable_frame.grid_columnconfigure(0, weight=1)
        starred_window.scrollable_frame_checkboxes = []
        self.starred_files = dict(sorted(self.starred_files.items()))
        count_line = 0
        for id_sf, afd_sf in (self.starred_files).items():
            checkbox = customtkinter.CTkCheckBox(master=starred_window.scrollable_frame, text=f"{id_sf} - {afd_sf}", width=100)
            checkbox.grid(row=count_line, column=0, padx=10, pady=(0, 20))
            starred_window.scrollable_frame_checkboxes.append(checkbox)
            count_line += 1

        # create additional buttons in the top-right corner
        starred_window.button_1 = customtkinter.CTkButton(starred_window, text="Download", width=180, command=lambda: self.download_file(starred_window.scrollable_frame_checkboxes, starred_window))
        starred_window.button_1.grid(row=2, column=1, padx=(10, 10), pady=(20, 10), sticky="ne")

        starred_window.button_2 = customtkinter.CTkButton(starred_window, text="Unstarred", width=180, command=lambda: self.unstarred_file(starred_window.scrollable_frame_checkboxes, starred_window))
        starred_window.button_2.grid(row=2, column=2, padx=(10, 20), pady=(20, 10), sticky="ne")  
        
    # remove file function
    def remove_file(self, checkboxes, window):
        checked_items = [cb.cget("text") for cb in checkboxes if cb.get()]
        if checked_items:
            self.log_activity(f"Remove all the following file into the recycle bin: \n{'\n'.join(checked_items)}")
            for item in checked_items:
                id_item, info_item = sep_id_and_info(item)
                self.deleted_files[id_item] = info_item
                del self.all_server_files[id_item]
                if id_item in self.starred_files:
                    del self.starred_files[id_item]
                # do on server
                take_signal(id_item + '|' + info_item + "|rm")
            tkinter.messagebox.showinfo("Remove File", "All ticked file have been removed successfully.")
            window.destroy()
        else:
            tkinter.messagebox.showwarning("Remove File", "Please select file to remove.")
            
    # download from server
    def download_from_server(self, file_path, filesize):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
        except ConnectionRefusedError:
            self.log_activity(f"Connection to server refused. Make sure the server is running.")
            return
        
        try:
            client_socket.send(f"{file_path}{SEPARATOR}{filesize}".encode())
        except ConnectionResetError:
            self.log_activity("Connection to server was reset. Make sure the server is running.")
            return
        
        with open(file_path, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    break
                f.write(bytes_read)
                
        client_socket.close()
        self.log_activity(f"File {file_path} downloaded successfully.")
        
    # download file function
    def download_file(self, checkboxes, window):
        checked_items = [cb.cget("text") for cb in checkboxes if cb.get()]
        if checked_items:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(("0.0.0.0", SERVER_PORT))
            server_socket.listen(1)
            
            # download file from server
            for item in checked_items:
                # send signal to server
                take_signal(item.split(" - ")[2])
                client_socket, address = server_socket.accept()
                    
                # receive file
                client_handler = threading.Thread(target=handle_client, args=(client_socket,))
                client_handler.start()         
                   
                # close client socket
                client_socket.close()    
                
                self.log_activity(f"File {item} downloaded successfully.")
                
            server_socket.close()        
            tkinter.messagebox.showinfo("Download File", "All ticked file have been downloaded successfully.")
            window.destroy()
        else:
            tkinter.messagebox.showwarning("Download File", "Please select file to download.")
        
    # restore file function
    def restore_file(self, checkboxes, window):
        checked_items = [cb.cget("text") for cb in checkboxes if cb.get()]
        if checked_items:
            self.log_activity(f"Restored all the following file into the server file: \n{'\n'.join(checked_items)}")
            for item in checked_items:
                id_item, info_item = sep_id_and_info(item)
                self.all_server_files[id_item] = info_item
                del self.deleted_files[id_item]
            # do on server
            take_signal(id_item + '|' + info_item + "|rs")
            tkinter.messagebox.showinfo("Restore File", "All ticked file have been restored successfully.")
            window.destroy()
        else:
            tkinter.messagebox.showwarning("Restore File", "Please select file to restore.")
        
    # delete file function
    def delete_file(self, checkboxes, window):
        checked_items = [cb.cget("text") for cb in checkboxes if cb.get()]
        if checked_items:
            tkinter.messagebox.showwarning("Delete File", "File have been deleted can't be restored. So be sure before deleting the file.")
            self.log_activity(f"All the following file have been deleted from the recycle bin: \n{'\n'.join(checked_items)}")
            for item in checked_items:
                id_item, info_item = sep_id_and_info(item)
                del self.deleted_files[id_item]
                # do on server
                take_signal(id_item + '|' + info_item + "|df")
            tkinter.messagebox.showinfo("Delete File", "All ticked file have been deleted successfully.")
            window.destroy()
        else:
            tkinter.messagebox.showwarning("Delete File", "Please select file to delete.")
        
    # starred file function
    def starred_file(self, checkboxes, window):
        checked_items = [cb.cget("text") for cb in checkboxes if cb.get()]
        if checked_items:
            self.log_activity(f"All the following file have been starred: \n{'\n'.join(checked_items)}")
            for item in checked_items:
                id_item, info_item = sep_id_and_info(item)
                if id_item not in self.starred_files:
                    self.starred_files[id_item] = info_item
                    # do on server
                    take_signal(self.current_user + '|' + item + "|sf")
            tkinter.messagebox.showinfo("Starred File", "All ticked file have been starred successfully.")
            window.destroy()
        else:
            tkinter.messagebox.showwarning("Starred File", "Please select file to star.")
        
    # unstarred file function
    def unstarred_file(self, checkboxes, window):
        checked_items = [cb.cget("text") for cb in checkboxes if cb.get()]
        if checked_items:
            self.log_activity(f"All the following file have been unstarred from the starred file: \n{'\n'.join(checked_items)}")
            for item in checked_items:
                id_item, info_item = sep_id_and_info(item)
                del self.starred_files[id_item]
                # do on server
                take_signal(self.current_user + '|' + item + "|uf")
            tkinter.messagebox.showinfo("Unstarred File", "All ticked file have been unstarred successfully.")
            window.destroy()
        else:
            tkinter.messagebox.showwarning("Unstarred File", "Please select file to unstar.")
        
    # show notification function
    def show_notification(self):
        self.update_data_sign = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Data information updated")
        self.update_data_sign.grid(row=3, column=0, pady=5, padx=20, sticky="n")
        self.after(2000, self.show_next_update)

    # show next update function
    def show_next_update(self):
        self.next_update = customtkinter.CTkLabel(master=self.radiobutton_frame, text="Server is available now")
        self.next_update.grid(row=4, column=0, pady=5, padx=20, sticky="n")
        
    # show setting window function
    def show_setting_window(self):
        self.log_activity("Opened Setting.")
        setting_window = customtkinter.CTkToplevel(self)
        setting_window.title("Setting")
        setting_window.geometry(f"{338}x{150}")
        setting_window.attributes('-topmost', True)
        setting_window.resizable(False, False)
        
        setting_window.button_1 = customtkinter.CTkButton(setting_window, text="Our QR", width=300, command=lambda: self.our_qr(setting_window))
        setting_window.button_1.grid(row=1, column=0, padx=(20, 20), pady=(10, 10), sticky="n")
        
        setting_window.button_2 = customtkinter.CTkButton(setting_window, text="Change Password", width=300, command=lambda: self.change_password(setting_window))
        setting_window.button_2.grid(row=2, column=0, padx=(20, 20), pady=(10, 10), sticky="n")
        
        setting_window.button_3 = customtkinter.CTkButton(setting_window, text="Log Out", width=300, command=self.log_out)
        setting_window.button_3.grid(row=3, column=0, padx=(20, 20), pady=(10, 10), sticky="n")

    # connect to github function
    def our_qr(self, setting_window):
        setting_window.destroy()
        self.log_activity("Opened Our QR.")
        our_qr_window = customtkinter.CTkToplevel(self)
        our_qr_window.title("QR")
        our_qr_window.geometry(f"{205}x{205}")
        our_qr_window.attributes('-topmost', True)
        our_qr_window.resizable(False, False)
                
        qr_image = Image.open(PATH + "mmt_project/client/image/qr_code.png")
        qr_image = qr_image.resize((250, 250))
        qr_code = ImageTk.PhotoImage(qr_image)
        
        label_qr = customtkinter.CTkLabel(our_qr_window, image=qr_code, text="")
        label_qr.pack(expand=True)
        
    # change password function
    def change_password(self, setting_window):
        setting_window.destroy()
        self.log_activity("Opened Change Password.")
        new_password = customtkinter.CTkInputDialog(text="Enter new password:", title="Change Password")
        self.users_login[self.current_user] = new_password.get_input()
        # do on server
        take_signal(self.current_user + '|' + new_password.get_input() + "|cp")
        tkinter.messagebox.showinfo("Change Password", "Password changed successfully.")
               
    # create a function to log out
    def log_out(self):
        python = sys.executable
        os.execl(python, python, * sys.argv)
        
if __name__ == "__main__":
    app = App()
    app.mainloop()
