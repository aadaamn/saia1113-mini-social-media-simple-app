# -------------------------------
#   __________  ____   ____  
#  |___  / __ \|  _ \ / __ \ 
#     / / |  | | |_) | |  | |
#    / /| |  | |  _ <| |  | |
#   / /_| |__| | |_) | |__| |
#  /_____\____/|____/ \____/ 
# 
# -------------------------------
                           
import bcrypt
from datetime import datetime
import customtkinter as ctk

# Colors Declaration
BG = "#FAFBF8"
BG_CARD = "#FFFFFF"
BG_SECONDARY = "#F0F4EC"
OLIVE = "#5C6B3D"
OLIVE_DARK = "#4A5632"
OLIVE_LIGHT = "#7A8B5A"
OLIVE_PALE = "#E8EDE0"
TEXT_PRIMARY = "#1F2A1F"
TEXT_SECONDARY = "#5A6B5A"
TEXT_MUTED = "#8A9B8A"
BORDER = "#D4DEC8"
RED = "#C44D4D"
RED_LIGHT = "#E85D5D"
GREEN = "#4A7C4E"

# ---------------------------
# Data Structures Declaration
# ---------------------------
# Users dictionary: stores user accounts with hashed passwords
# Structure: {user_id: {id, username, password (hashed), created}}
USERS_DATA = {}

# Posts dictionary: stores all posts with their content and interactions
# Structure: {post_id: {id, author, content, created, likes (list), comments (list)}}
POSTS_DATA = {}

# --------------------------
# Sample Data Initialization
# --------------------------
def initialize_sample_data():
    global USERS_DATA, POSTS_DATA
    
    # Pre-existing users with hashed passwords
    USERS_DATA = {
        "1": {
            "id": "1",
            "username": "aadaamn",
            "password": "$2b$12$wbP/z1FNnyN2m4pQhDye8ejAqHkErQc99tROOyI8ut1.f4fDXPJOK",
            "created": "2025-12-20T20:18:46.456896"
        },
        "2": {
            "id": "2",
            "username": "enderomeda",
            "password": "$2b$12$oHcUfg6i7MgChzkbJ7WAwuPtIBsJsPnlnFbvrwU7Igk0EhyCIoy8C",
            "created": "2025-12-20T20:30:50.112727"
        },
        "3": {
            "id": "3",
            "username": "areppo",
            "password": "$2b$12$zCAk5fkfqB.tiwugNEckeuncQ6SJPkpDvpoqu8P4HGg2Vk80tB5B6",
            "created": "2026-01-01T22:42:01.632204"
        }
    }
    
    # Pre-existing posts with engagement data
    POSTS_DATA = {
        "1": {
            "id": "1",
            "author": "1",
            "content": "I am FEELING GREAT today!",
            "created": "2025-12-20T20:28:15.823042",
            "likes": ["1"],
            "comments": [
                {"author": "1", "text": "yo", "created": "2025-12-20T20:28:41.000147"},
                {"author": "3", "text": "stylo", "created": "2026-01-01T22:47:33.281025"}
            ]
        },
        "2": {
            "id": "2",
            "author": "3",
            "content": "Happy New Year gang!!",
            "created": "2026-01-01T22:47:24.053107",
            "likes": [],
            "comments": []
        },
        "3": {
            "id": "3",
            "author": "3",
            "content": "DANISH THE BEST!",
            "created": "2026-01-01T22:51:16.256627",
            "likes": ["3"],
            "comments": []
        }
    }

# --------------------------
# User Functions Declaration
# --------------------------
# Function for registering a new user into the app
def register(username, password):
    # Validate username length
    if len(username) < 3:
        return False, "Username too short (min 3)"
    
    # Validate password length
    if len(password) < 6:
        return False, "Password too short (min 6)"
    
    # Check if username already exists (case-insensitive)
    for u in USERS_DATA.values():
        if u["username"].lower() == username.lower():
            return False, "Username taken"
    
    # Generate unique user ID
    # Find highest existing user number to avoid ID conflicts
    max_num = 0
    for uid in USERS_DATA.keys():
        try:
            num = int(uid)
            if num > max_num:
                max_num = num
        except ValueError:
            pass
    user_id = str(max_num + 1)
    
    # Hash password using bcrypt for security
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    # Store new user in dictionary
    USERS_DATA[user_id] = {
        "id": user_id,
        "username": username.lower(),
        "password": hashed,
        "created": datetime.now().isoformat()
    }
    
    return True, "Account created!"

# Function for log in (authenticating user login)
def login(username, password):
    for user in USERS_DATA.values():
        if user["username"].lower() == username.lower():
            # Verify password using bcrypt
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                return True, {"id": user["id"], "username": user["username"]}
    
    return False, None

# Function for getting username by user ID
def get_username(user_id):
    return USERS_DATA.get(user_id, {}).get("username", "Unknown")


# ---------------
# POST FUNCTIONS
# ---------------
# Function for creating a new post
def create_post(user_id, content):

    # Validate content
    if not content or len(content) > 500:
        return False
    
    # Generate unique post ID
    max_num = 0
    for pid in POSTS_DATA.keys():
        try:
            num = int(pid)
            if num > max_num:
                max_num = num
        except ValueError:
            pass
    post_id = str(max_num + 1)
    
    # Create post entry in dictionary
    POSTS_DATA[post_id] = {
        "id": post_id,
        "author": user_id,
        "content": content,
        "created": datetime.now().isoformat(),
        "likes": [],      
        "comments": []    
    }
    
    return True

# Function for getting all posts sorted by recent or popular
def get_posts(sort_by="recent"):
    posts = list(POSTS_DATA.values())
    
    if sort_by == "popular":
        # Sort by engagement: likes + comments count
        return sorted(posts, key=lambda p: len(p["likes"]) + len(p["comments"]), reverse=True)
    else:
        # Sort by creation time (newest first)
        return sorted(posts, key=lambda p: p["created"], reverse=True)

# Function for getting all posts by a specific user
def get_user_posts(user_id):
    return [p for p in get_posts() if p["author"] == user_id]

# Function for toggling like status on a post
def toggle_like(user_id, post_id):

    if post_id in POSTS_DATA:
        # Use set for efficient operations
        likes = set(POSTS_DATA[post_id]["likes"]) 
        if user_id in likes:
            likes.remove(user_id)
        else:
            likes.add(user_id)
         # Convert back to list
        POSTS_DATA[post_id]["likes"] = list(likes) 

# Function for adding a comment to a post
def add_comment(user_id, post_id, text):
    if not text:
        return
    
    if post_id in POSTS_DATA:
        POSTS_DATA[post_id]["comments"].append({
            "author": user_id,
            "text": text,
            "created": datetime.now().isoformat()
        })

# Function for deleting a post
def delete_post(user_id, post_id):
    if post_id in POSTS_DATA and POSTS_DATA[post_id]["author"] == user_id:
        del POSTS_DATA[post_id]


# -------------------
# Other Functions Declaration
# -------------------
# Function for converting ISO timestamp to human-readable relative time 
def time_ago(iso_time):
    try:
        dt = datetime.fromisoformat(iso_time)
        secs = (datetime.now() - dt).total_seconds()
        
        if secs < 60:
            return "Just now"
        elif secs < 3600:
            mins = int(secs / 60)
            return f"{mins}m ago"
        elif secs < 86400:
            hours = int(secs / 3600)
            return f"{hours}h ago"
        else:
            days = int(secs / 86400)
            return f"{days}d ago"
    except Exception:
        return ""

# Function for validating text input against length constraints
def validate_input(text, min_len=1, max_len=500):

    if not text or len(text.strip()) < min_len:
        return False, f"Input must be at least {min_len} characters"
    if len(text) > max_len:
        return False, f"Input must not exceed {max_len} characters"
    return True, None


# ------------------------------------------
# Main Application Class using CustomTkinter
# ------------------------------------------

class ZoboApp(ctk.CTk):
    # Constructor 
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("ZOBO - Mini Social Media App")
        self.geometry("900x700")
        self.minsize(800, 600)
        ctk.set_appearance_mode("light")
        self.configure(fg_color=BG)
        
        # Current user session (tuple: id, username)
        self.user = None
        
        # Current sort mode for posts
        self.sort_mode = "recent"
        
        # Start with login screen
        self.show_login()
    

    def clear(self):
        for w in self.winfo_children():
            w.destroy()
    
 
    # Login/Register Screens
    def show_login(self):
        self.clear()
        self.user = None
        
        # Main container 
        main = ctk.CTkFrame(self, fg_color=BG)
        main.pack(fill="both", expand=True)
        
        # Left panel
        left_panel = ctk.CTkFrame(main, fg_color=OLIVE, width=350, corner_radius=0)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)
        deco_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        deco_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(deco_frame, text="ZOBO", font=("Segoe UI", 42, "bold"),
                     text_color="#FFFFFF").pack()
        ctk.CTkLabel(deco_frame, text="Share moments.\nConnect with friends.",
                     font=("Segoe UI", 14), text_color="#E8E8E8",
                     justify="center").pack(pady=(10, 0))
        
        # Right panel - Login form
        right_panel = ctk.CTkFrame(main, fg_color=BG)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Center form
        form_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_container.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(form_container, text="Welcome Back",
                     font=("Segoe UI", 28, "bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(form_container, text="Sign in to continue to ZOBO",
                     font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(anchor="w", pady=(5, 25))
        
        # Login form card
        card = ctk.CTkFrame(form_container, fg_color=BG_CARD, corner_radius=16)
        card.pack(fill="x", pady=10)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=30, pady=30)
        
        # Username field
        ctk.CTkLabel(inner, text="Username", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        login_user = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                   fg_color=BG_SECONDARY, border_color=BORDER,
                                   border_width=1, placeholder_text="Enter username")
        login_user.pack(pady=(5, 15))
        
        # Password field
        ctk.CTkLabel(inner, text="Password", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        login_pass = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                   fg_color=BG_SECONDARY, border_color=BORDER,
                                   border_width=1, placeholder_text="Enter password", show="●")
        login_pass.pack(pady=(5, 10))
        
        # Error message label
        login_msg = ctk.CTkLabel(inner, text="", text_color=RED, font=("Segoe UI", 11))
        login_msg.pack()
        
        def do_login():
            try:
                username = login_user.get().strip()
                password = login_pass.get()
                
                if not username or not password:
                    login_msg.configure(text="Please enter username and password")
                    return
                
                ok, data = login(username, password)
                if ok:
                    self.user = (data["id"], data["username"])
                    self.show_feed()
                else:
                    login_msg.configure(text="Invalid username or password")
            except Exception as e:
                login_msg.configure(text="An error occurred. Please try again.")
        
        # Login button
        ctk.CTkButton(inner, text="Sign In", width=280, height=45, corner_radius=10,
                      fg_color=OLIVE, hover_color=OLIVE_DARK, font=("Segoe UI", 14, "bold"),
                      command=do_login).pack(pady=(15, 0))
        
        # Register link
        reg_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        reg_frame.pack(pady=20)
        
        ctk.CTkLabel(reg_frame, text="Don't have an account?",
                     text_color=TEXT_MUTED, font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkButton(reg_frame, text="Create Account", fg_color="transparent",
                      text_color=OLIVE, hover_color=OLIVE_PALE, font=("Segoe UI", 12, "bold"),
                      command=self.show_register).pack(side="left", padx=5)
    
    # Function for displaying the registration screen
    def show_register(self):
        self.clear()
        main = ctk.CTkFrame(self, fg_color=BG)
        main.pack(fill="both", expand=True)
        
        # Left decorative panel
        left_panel = ctk.CTkFrame(main, fg_color=OLIVE, width=350, corner_radius=0)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)
        
        deco_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        deco_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(deco_frame, text="ZOBO", font=("Segoe UI", 42, "bold"),
                     text_color="#FFFFFF").pack()
        ctk.CTkLabel(deco_frame, text="Join our community.\nStart sharing today.",
                     font=("Segoe UI", 14), text_color="#E8E8E8",
                     justify="center").pack(pady=(10, 0))
        
        # Right panel
        right_panel = ctk.CTkFrame(main, fg_color=BG)
        right_panel.pack(side="right", fill="both", expand=True)
        
        form_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_container.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(form_container, text="Create Account",
                     font=("Segoe UI", 28, "bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(form_container, text="Fill in your details to get started",
                     font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(anchor="w", pady=(5, 25))
        
        card = ctk.CTkFrame(form_container, fg_color=BG_CARD, corner_radius=16)
        card.pack(fill="x", pady=10)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=30, pady=30)
        
        # Username field
        ctk.CTkLabel(inner, text="Username", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        reg_user = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                 fg_color=BG_SECONDARY, border_color=BORDER,
                                 border_width=1, placeholder_text="Choose a username")
        reg_user.pack(pady=(5, 15))
        
        # Password field
        ctk.CTkLabel(inner, text="Password", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        reg_pass = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                 fg_color=BG_SECONDARY, border_color=BORDER,
                                 border_width=1, placeholder_text="Create password", show="●")
        reg_pass.pack(pady=(5, 15))
        
        # Confirm password field
        ctk.CTkLabel(inner, text="Confirm Password", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        reg_pass2 = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                  fg_color=BG_SECONDARY, border_color=BORDER,
                                  border_width=1, placeholder_text="Confirm password", show="●")
        reg_pass2.pack(pady=(5, 10))
        
        reg_msg = ctk.CTkLabel(inner, text="", font=("Segoe UI", 11))
        reg_msg.pack()
        
        # Function for registering a new user
        def do_register():
            try:
                username = reg_user.get().strip()
                password = reg_pass.get()
                confirm = reg_pass2.get()
                
                # Validate inputs
                if not username or not password or not confirm:
                    reg_msg.configure(text="Please fill in all fields", text_color=RED)
                    return
                
                if password != confirm:
                    reg_msg.configure(text="Passwords don't match", text_color=RED)
                    return
                
                ok, msg = register(username, password)
                reg_msg.configure(text=msg, text_color=GREEN if ok else RED)
                
                if ok:
                    self.after(1000, self.show_login)
            except Exception as e:
                reg_msg.configure(text="An error occurred. Please try again.", text_color=RED)
        
        ctk.CTkButton(inner, text="Create Account", width=280, height=45, corner_radius=10,
                      fg_color=OLIVE, hover_color=OLIVE_DARK, font=("Segoe UI", 14, "bold"),
                      command=do_register).pack(pady=(15, 0))
        
        # Back to login
        back_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        back_frame.pack(pady=20)
        
        ctk.CTkLabel(back_frame, text="Already have an account?",
                     text_color=TEXT_MUTED, font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkButton(back_frame, text="Sign In", fg_color="transparent",
                      text_color=OLIVE, hover_color=OLIVE_PALE, font=("Segoe UI", 12, "bold"),
                      command=self.show_login).pack(side="left", padx=5)
    
    # Home/Feed Screen
    def show_feed(self):
        self.clear()
        
        # Header
        header = ctk.CTkFrame(self, fg_color=BG_CARD, height=70, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=25)
        
        # Brand
        brand = ctk.CTkFrame(header_inner, fg_color="transparent")
        brand.pack(side="left", pady=15)
        
        ctk.CTkLabel(brand, text="ZOBO", font=("Segoe UI", 24, "bold"),
                     text_color=OLIVE).pack(side="left")
        
        # User info & logout
        user_section = ctk.CTkFrame(header_inner, fg_color="transparent")
        user_section.pack(side="right", pady=15)
        
        ctk.CTkLabel(user_section, text=f"@{self.user[1]}", font=("Segoe UI", 13),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=15)
        ctk.CTkButton(user_section, text="Logout", width=80, height=35, corner_radius=8,
                      fg_color=RED, hover_color=RED_LIGHT, font=("Segoe UI", 12),
                      command=self.show_login).pack(side="left")
        
        # Main content area
        content = ctk.CTkFrame(self, fg_color=BG)
        content.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Left sidebar - Navigation
        sidebar = ctk.CTkFrame(content, fg_color=BG_CARD, width=200, corner_radius=16)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)
        
        nav_inner = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_inner.pack(fill="x", padx=15, pady=20)
        
        ctk.CTkLabel(nav_inner, text="Menu", font=("Segoe UI", 11, "bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 10))
        
        # Navigation buttons
        ctk.CTkButton(nav_inner, text="Feed", width=170, height=42, corner_radius=10,
                      fg_color=OLIVE_PALE, text_color=OLIVE_DARK, hover_color=OLIVE_PALE,
                      font=("Segoe UI", 13), anchor="w",
                      command=self.show_feed).pack(pady=3)
        ctk.CTkButton(nav_inner, text="New Post", width=170, height=42, corner_radius=10,
                      fg_color="transparent", text_color=TEXT_PRIMARY, hover_color=BG_SECONDARY,
                      font=("Segoe UI", 13), anchor="w",
                      command=self.show_create).pack(pady=3)
        ctk.CTkButton(nav_inner, text="Profile", width=170, height=42, corner_radius=10,
                      fg_color="transparent", text_color=TEXT_PRIMARY, hover_color=BG_SECONDARY,
                      font=("Segoe UI", 13), anchor="w",
                      command=self.show_profile).pack(pady=3)
        
        # Sort section
        sort_frame = ctk.CTkFrame(nav_inner, fg_color="transparent")
        sort_frame.pack(fill="x", pady=(30, 0))
        
        ctk.CTkLabel(sort_frame, text="Sort Posts", font=("Segoe UI", 11, "bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 10))
        
        def set_sort(mode):
            self.sort_mode = mode
            self.show_feed()
        
        # Sort buttons - Recent
        recent_btn = ctk.CTkButton(sort_frame, text="Recent", width=170, height=38, corner_radius=8,
                      fg_color=OLIVE if self.sort_mode == "recent" else "transparent",
                      text_color="#FFFFFF" if self.sort_mode == "recent" else TEXT_PRIMARY,
                      hover_color=OLIVE_LIGHT if self.sort_mode == "recent" else BG_SECONDARY,
                      font=("Segoe UI", 12), anchor="w",
                      command=lambda: set_sort("recent"))
        recent_btn.pack(pady=2)
        
        # Sort buttons - Popular
        popular_btn = ctk.CTkButton(sort_frame, text="Popular", width=170, height=38, corner_radius=8,
                      fg_color=OLIVE if self.sort_mode == "popular" else "transparent",
                      text_color="#FFFFFF" if self.sort_mode == "popular" else TEXT_PRIMARY,
                      hover_color=OLIVE_LIGHT if self.sort_mode == "popular" else BG_SECONDARY,
                      font=("Segoe UI", 12), anchor="w",
                      command=lambda: set_sort("popular"))
        popular_btn.pack(pady=2)
        
        # Feed area
        feed_container = ctk.CTkFrame(content, fg_color="transparent")
        feed_container.pack(side="left", fill="both", expand=True)
        
        # Feed header
        feed_header = ctk.CTkFrame(feed_container, fg_color="transparent")
        feed_header.pack(fill="x", pady=(0, 15))
        
        sort_label = "Popular Posts" if self.sort_mode == "popular" else "Recent Posts"
        ctk.CTkLabel(feed_header, text=sort_label, font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        
        # Scrollable feed
        feed = ctk.CTkScrollableFrame(feed_container, fg_color="transparent", corner_radius=0)
        feed.pack(fill="both", expand=True)
        
        posts = get_posts(self.sort_mode)
        
        # Show empty state if no posts
        if not posts:
            empty_frame = ctk.CTkFrame(feed, fg_color=BG_CARD, corner_radius=16)
            empty_frame.pack(fill="x", pady=20, padx=5)
            ctk.CTkLabel(empty_frame, text="No posts yet",
                         font=("Segoe UI", 16, "bold"), text_color=TEXT_PRIMARY).pack(pady=(30, 10))
            ctk.CTkLabel(empty_frame, text="Be the first to share something!",
                         font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=(5, 30))
        
        # Display each post
        for post in posts:
            self._create_post_card(feed, post)
    
    # Function for creating a styled post widget
    def _create_post_card(self, parent, post):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=16)
        card.pack(fill="x", pady=8, padx=5)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=20, pady=18)
        
        # Header - Author and time
        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x")
        
        author = get_username(post["author"])
        
        # Avatar circle with first letter of username
        avatar = ctk.CTkFrame(header, fg_color=OLIVE_PALE, width=40, height=40, corner_radius=20)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=author[0].upper(), font=("Segoe UI", 14, "bold"),
                     text_color=OLIVE_DARK).place(relx=0.5, rely=0.5, anchor="center")
        
        # Author info
        author_info = ctk.CTkFrame(header, fg_color="transparent")
        author_info.pack(side="left", padx=12)
        
        ctk.CTkLabel(author_info, text=f"@{author}", font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(author_info, text=time_ago(post["created"]),
                     font=("Segoe UI", 11), text_color=TEXT_MUTED).pack(anchor="w")
        
        # Post content
        ctk.CTkLabel(inner, text=post["content"], font=("Segoe UI", 13),
                     text_color=TEXT_PRIMARY, wraplength=480, justify="left", anchor="w"
                     ).pack(fill="x", pady=(15, 10))
        
        # Divider line
        divider = ctk.CTkFrame(inner, fg_color=BORDER, height=1)
        divider.pack(fill="x", pady=(10, 12))
        
        # Actions row
        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(fill="x")
        
        likes = set(post["likes"])
        is_liked = self.user[0] in likes
        
        # Function for handling like button click
        def do_like():
            toggle_like(self.user[0], post["id"])
            self.show_feed()
        
        # Like button
        like_btn = ctk.CTkButton(actions, 
                      text=f"{'❤️' if is_liked else '🤍'}  {len(likes)}",
                      width=70, height=32, corner_radius=8,
                      fg_color=OLIVE_PALE if is_liked else BG_SECONDARY,
                      text_color=OLIVE_DARK if is_liked else TEXT_SECONDARY,
                      hover_color=OLIVE_PALE, font=("Segoe UI", 12),
                      command=do_like)
        like_btn.pack(side="left", padx=(0, 8))
        
        # Comment count
        ctk.CTkLabel(actions, text=f"💬 {len(post['comments'])}",
                     font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(side="left", padx=8)
        
        # Comment input
        comment_entry = ctk.CTkEntry(actions, width=180, height=32, corner_radius=8,
                                      fg_color=BG_SECONDARY, border_width=0,
                                      placeholder_text="Write a comment...",
                                      font=("Segoe UI", 11))
        comment_entry.pack(side="left", padx=8)
        
        # Function for posting a comment
        def do_comment():
            text = comment_entry.get().strip()
            if text:
                add_comment(self.user[0], post["id"], text)
            self.show_feed()
        
        # Post comment button
        ctk.CTkButton(actions, text="Post", width=60, height=32, corner_radius=8,
                      fg_color=OLIVE, hover_color=OLIVE_DARK, font=("Segoe UI", 11),
                      command=do_comment).pack(side="left")
        
        # Show recent comments (last 2)
        if post["comments"]:
            comments_frame = ctk.CTkFrame(inner, fg_color="transparent")
            comments_frame.pack(fill="x", pady=(12, 0))
            
            for c in post["comments"][-2:]:
                c_author = get_username(c["author"])
                comment_row = ctk.CTkFrame(comments_frame, fg_color=BG_SECONDARY, corner_radius=8)
                comment_row.pack(fill="x", pady=3)
                ctk.CTkLabel(comment_row, text=f"@{c_author}: {c['text']}",
                             font=("Segoe UI", 11), text_color=TEXT_SECONDARY,
                             wraplength=450, anchor="w").pack(padx=12, pady=8, anchor="w")

    # Create Post Screen
    def show_create(self):
        self.clear()
        
        # Header
        header = ctk.CTkFrame(self, fg_color=BG_CARD, height=70, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=25)
        
        ctk.CTkButton(header_inner, text="← Back", width=80, height=35, corner_radius=8,
                    fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY, hover_color=BORDER,
                    font=("Segoe UI", 12), command=self.show_feed).pack(side="left", pady=17)
        
        ctk.CTkLabel(header_inner, text="Create Post", font=("Segoe UI", 20, "bold"),
                    text_color=TEXT_PRIMARY).pack(side="left", padx=20, pady=17)
        
        # Scrollable content area
        scroll_container = ctk.CTkScrollableFrame(self, fg_color=BG)
        scroll_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Form card
        card = ctk.CTkFrame(scroll_container, fg_color=BG_CARD, corner_radius=16)
        card.pack(fill="x", padx=50, pady=(0, 20))
        
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=35)
        
        ctk.CTkLabel(form, text="What's on your mind?", font=("Segoe UI", 16, "bold"),
                    text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(form, text="Share your thoughts with the community",
                    font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(anchor="w", pady=(3, 15))
        
        # Text area for post content
        text_box = ctk.CTkTextbox(form, height=180, corner_radius=12,
                                fg_color=BG_SECONDARY, border_width=0,
                                font=("Segoe UI", 13))
        text_box.pack(fill="x", pady=10)
        
        # Character count display
        count_frame = ctk.CTkFrame(form, fg_color="transparent")
        count_frame.pack(fill="x")
        count_label = ctk.CTkLabel(count_frame, text="0 / 500 characters",
                                    font=("Segoe UI", 11), text_color=TEXT_MUTED)
        count_label.pack(side="right")
        
        def update_count(e=None):
            n = len(text_box.get("1.0", "end-1c"))
            count_label.configure(text=f"{n} / 500 characters",
                                text_color=RED if n > 500 else TEXT_MUTED)
        text_box.bind("<KeyRelease>", update_count)
        
        # Message label for feedback
        msg_label = ctk.CTkLabel(form, text="", font=("Segoe UI", 12))
        msg_label.pack(pady=10)
        
        def do_post():
            try:
                content_text = text_box.get("1.0", "end-1c").strip()
                
                # Validate content
                if not content_text:
                    msg_label.configure(text="Please write something!", text_color=RED)
                    return
                if len(content_text) > 500:
                    msg_label.configure(text="Post is too long! (max 500 characters)", text_color=RED)
                    return
                
                # Create the post
                success = create_post(self.user[0], content_text)
                
                if success:
                    msg_label.configure(text="Posted successfully!", text_color=GREEN)
                    self.after(800, self.show_feed)
                else:
                    msg_label.configure(text="Failed to create post. Please try again.", text_color=RED)
            except Exception as e:
                msg_label.configure(text="An error occurred. Please try again.", text_color=RED)
        
        # Submit button
        ctk.CTkButton(form, text="Share Post", width=200, height=48, corner_radius=12,
                      fg_color=OLIVE, hover_color=OLIVE_DARK, font=("Segoe UI", 15, "bold"),
                      command=do_post).pack(pady=20)

    # Profile Screen
    def show_profile(self):
        self.clear()
        
        # Header
        header = ctk.CTkFrame(self, fg_color=BG_CARD, height=70, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=25)
        
        ctk.CTkButton(header_inner, text="← Back", width=80, height=35, corner_radius=8,
                      fg_color=BG_SECONDARY, text_color=TEXT_PRIMARY, hover_color=BORDER,
                      font=("Segoe UI", 12), command=self.show_feed).pack(side="left", pady=17)
        
        ctk.CTkLabel(header_inner, text="My Profile", font=("Segoe UI", 20, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left", padx=20, pady=17)
        
        # Content
        content = ctk.CTkFrame(self, fg_color=BG)
        content.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Profile header card
        profile_card = ctk.CTkFrame(content, fg_color=BG_CARD, corner_radius=16)
        profile_card.pack(fill="x", pady=(0, 20))
        
        profile_inner = ctk.CTkFrame(profile_card, fg_color="transparent")
        profile_inner.pack(fill="x", padx=30, pady=25)
        
        # Avatar with user initial
        avatar = ctk.CTkFrame(profile_inner, fg_color=OLIVE, width=70, height=70, corner_radius=35)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=self.user[1][0].upper(), font=("Segoe UI", 28, "bold"),
                     text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")
        
        # User info
        info = ctk.CTkFrame(profile_inner, fg_color="transparent")
        info.pack(side="left", padx=20)
        
        ctk.CTkLabel(info, text=f"@{self.user[1]}", font=("Segoe UI", 22, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(info, text="Member", font=("Segoe UI", 13),
                     text_color=TEXT_MUTED).pack(anchor="w")
        
        # Calculate stats
        my_posts = get_user_posts(self.user[0])
        total_likes = sum(len(p["likes"]) for p in my_posts)
        total_comments = sum(len(p["comments"]) for p in my_posts)
        
        # Stats display
        stats_frame = ctk.CTkFrame(profile_inner, fg_color="transparent")
        stats_frame.pack(side="right")
        
        for value, label in [(len(my_posts), "Posts"), (total_likes, "Likes"), (total_comments, "Comments")]:
            stat_box = ctk.CTkFrame(stats_frame, fg_color=BG_SECONDARY, corner_radius=12)
            stat_box.pack(side="left", padx=8)
            stat_inner = ctk.CTkFrame(stat_box, fg_color="transparent")
            stat_inner.pack(padx=20, pady=12)
            ctk.CTkLabel(stat_inner, text=str(value), font=("Segoe UI", 20, "bold"),
                         text_color=OLIVE).pack()
            ctk.CTkLabel(stat_inner, text=label, font=("Segoe UI", 11),
                         text_color=TEXT_MUTED).pack()
        
        # Posts section header
        posts_header = ctk.CTkFrame(content, fg_color="transparent")
        posts_header.pack(fill="x", pady=(10, 15))
        
        ctk.CTkLabel(posts_header, text="My Posts", font=("Segoe UI", 16, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        
        # Scrollable posts list
        posts_frame = ctk.CTkScrollableFrame(content, fg_color="transparent", corner_radius=0)
        posts_frame.pack(fill="both", expand=True)
        
        # Show empty state if no posts
        if not my_posts:
            empty = ctk.CTkFrame(posts_frame, fg_color=BG_CARD, corner_radius=12)
            empty.pack(fill="x", pady=10)
            ctk.CTkLabel(empty, text="You haven't posted anything yet.",
                         font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=30)
        
        # Display user's posts with delete option
        for post in my_posts:
            item = ctk.CTkFrame(posts_frame, fg_color=BG_CARD, corner_radius=12)
            item.pack(fill="x", pady=5)
            
            item_inner = ctk.CTkFrame(item, fg_color="transparent")
            item_inner.pack(fill="x", padx=18, pady=14)
            
            # Content preview (truncated)
            content_text = post["content"][:80] + ("..." if len(post["content"]) > 80 else "")
            ctk.CTkLabel(item_inner, text=content_text, font=("Segoe UI", 12),
                         text_color=TEXT_PRIMARY, wraplength=400, anchor="w"
                         ).pack(side="left", fill="x", expand=True)
            
            # Stats
            stats_text = f"❤️ {len(post['likes'])}  💬 {len(post['comments'])}"
            ctk.CTkLabel(item_inner, text=stats_text, font=("Segoe UI", 11),
                         text_color=TEXT_MUTED).pack(side="left", padx=15)
            
            # Delete button
            def do_delete(pid=post["id"]):
                """Handle post deletion."""
                delete_post(self.user[0], pid)
                self.show_profile()
            
            ctk.CTkButton(item_inner, text="🗑️", width=35, height=32, corner_radius=8,
                          fg_color=RED, hover_color=RED_LIGHT, font=("Segoe UI", 12),
                          command=do_delete).pack(side="right")


# ----------------
# Run Application
# ----------------
if __name__ == "__main__":
    print("Starting ZOBO...")
    print("Initializing data...")
    
    # Initialize sample data for demonstration
    initialize_sample_data()
    
    print("Launching application...")
    
    app = ZoboApp()
    app.mainloop()
