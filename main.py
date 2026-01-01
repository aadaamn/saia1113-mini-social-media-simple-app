import os
import json
import shutil
import uuid
import bcrypt
from datetime import datetime
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
POSTS_FILE = os.path.join(DATA_DIR, "posts.json")

# Create folders
os.makedirs(IMAGES_DIR, exist_ok=True)

# Colors (White + Olive Green theme - Enhanced)
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
SHADOW = "#00000008"


# Data Functions
def load_data(filepath):
    # Load JSON data from file
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_data(filepath, data):
    # Save data to JSON file
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


# User Functions
def register(username, password):
    # Register new user. Returns (success, message)
    if len(username) < 3:
        return False, "Username too short (min 3)"
    if len(password) < 6:
        return False, "Password too short (min 6)"
    
    users = load_data(USERS_FILE)
    
    for u in users.values():
        if u["username"].lower() == username.lower():
            return False, "Username taken"
    
    # Find highest existing user number to avoid ID conflicts
    max_num = 0
    for uid in users.keys():
        try:
            num = int(uid[1:])  # Extract number from "U001" -> 1
            if num > max_num:
                max_num = num
        except ValueError:
            pass
    user_id = f"U{max_num + 1:03d}"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    users[user_id] = {
        "id": user_id,
        "username": username.lower(),
        "password": hashed,
        "created": datetime.now().isoformat()
    }
    
    save_data(USERS_FILE, users)
    return True, "Account created!"

def login(username, password):
    # Login user. Returns (success, user_data or None)
    users = load_data(USERS_FILE)
    
    for user in users.values():
        if user["username"].lower() == username.lower():
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                return True, {"id": user["id"], "username": user["username"]}
    
    return False, None

def get_username(user_id):
    # Get username by ID
    users = load_data(USERS_FILE)
    return users.get(user_id, {}).get("username", "Unknown")


# Post Functions
def create_post(user_id, content, image_path=""):
    # Create a new post
    if not content or len(content) > 500:
        return False
    
    posts = load_data(POSTS_FILE)
    
    # Find highest existing post number to avoid ID conflicts
    max_num = 0
    for pid in posts.keys():
        try:
            num = int(pid[1:])  # Extract number from "P001" -> 1
            if num > max_num:
                max_num = num
        except ValueError:
            pass
    post_id = f"P{max_num + 1:03d}"
    
    saved_image = ""
    if image_path and os.path.exists(image_path):
        ext = os.path.splitext(image_path)[1]
        new_name = f"{uuid.uuid4()}{ext}"
        saved_image = os.path.join(IMAGES_DIR, new_name)
        shutil.copy2(image_path, saved_image)
    
    posts[post_id] = {
        "id": post_id,
        "author": user_id,
        "content": content,
        "image": saved_image,
        "created": datetime.now().isoformat(),
        "likes": [],      
        "comments": []    
    }
    
    save_data(POSTS_FILE, posts)
    return True

def get_posts(sort_by="recent"):
    # Get all posts sorted by criteria. sort_by: "recent" (newest first) or "popular" (most engagement)
    posts = list(load_data(POSTS_FILE).values())
    
    if sort_by == "popular":
        # Sort by engagement: likes + comments count
        return sorted(posts, key=lambda p: len(p["likes"]) + len(p["comments"]), reverse=True)
    else:
        # Default: sort by recent
        return sorted(posts, key=lambda p: p["created"], reverse=True)

def get_user_posts(user_id):
    # Get posts by a specific user
    return [p for p in get_posts() if p["author"] == user_id]

def toggle_like(user_id, post_id):
    # Toggle like on a post
    posts = load_data(POSTS_FILE)
    if post_id in posts:
        likes = set(posts[post_id]["likes"])  
        if user_id in likes:
            likes.remove(user_id)
        else:
            likes.add(user_id)
        posts[post_id]["likes"] = list(likes) 
        save_data(POSTS_FILE, posts)

def add_comment(user_id, post_id, text):
    # Add comment to a post
    if not text:
        return
    posts = load_data(POSTS_FILE)
    if post_id in posts:
        posts[post_id]["comments"].append({
            "author": user_id,
            "text": text,
            "created": datetime.now().isoformat()
        })
        save_data(POSTS_FILE, posts)

def delete_post(user_id, post_id):
    # Delete a post (only if owner)
    posts = load_data(POSTS_FILE)
    if post_id in posts and posts[post_id]["author"] == user_id:
        # Delete associated image if exists
        if posts[post_id].get("image") and os.path.exists(posts[post_id]["image"]):
            try:
                os.remove(posts[post_id]["image"])
            except Exception:
                pass
        del posts[post_id]
        save_data(POSTS_FILE, posts)

# Utility Functions
def time_ago(iso_time):
    # Convert timestamp to readable format
    try:
        dt = datetime.fromisoformat(iso_time)
        secs = (datetime.now() - dt).total_seconds()
        if secs < 60:
            return "Just now"
        if secs < 3600:
            mins = int(secs / 60)
            return f"{mins}m ago"
        if secs < 86400:
            hours = int(secs / 3600)
            return f"{hours}h ago"
        days = int(secs / 86400)
        return f"{days}d ago"
    except Exception:
        return ""

def load_image(path, max_size=(350, 250)):
    # Load and resize image for display
    try:
        if not path:
            return None
        
        # Try the original path first
        if os.path.exists(path):
            img = Image.open(path)
            img.thumbnail(max_size)
            return ctk.CTkImage(img, img, size=(img.width, img.height))
        
        # If path doesn't exist, try to find the image by filename in our images folder
        filename = os.path.basename(path)
        local_path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(local_path):
            img = Image.open(local_path)
            img.thumbnail(max_size)
            return ctk.CTkImage(img, img, size=(img.width, img.height))
    except Exception:
        pass
    return None

# Main Application

class ZoboApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ZOBO - Social Feed")
        self.geometry("900x700")
        self.minsize(800, 600)
        ctk.set_appearance_mode("light")
        self.configure(fg_color=BG)
        
        # Current user session (tuple: id, username)
        self.user = None
        # Current sort mode
        self.sort_mode = "recent"
        
        self.show_login()
    

    def clear(self):
        # Remove all widgets
        for w in self.winfo_children():
            w.destroy()
    
    # Login / Register Screen
    
    def show_login(self):
        self.clear()
        self.user = None
        
        # Main container with gradient-like background
        main = ctk.CTkFrame(self, fg_color=BG)
        main.pack(fill="both", expand=True)
        
        # Left decorative panel
        left_panel = ctk.CTkFrame(main, fg_color=OLIVE, width=350, corner_radius=0)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)
        
        # Decorative content on left
        deco_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        deco_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(deco_frame, text="ZOBO", font=("Segoe UI", 42, "bold"),
                     text_color="#FFFFFF").pack()
        ctk.CTkLabel(deco_frame, text="Share moments.\nConnect with friends.",
                     font=("Segoe UI", 14), text_color="#E8E8E8",
                     justify="center").pack(pady=(10, 0))
        
        # Decorative circles
        ctk.CTkLabel(left_panel, text="●", font=("", 80), text_color="#7A8B6A").place(x=20, y=50)
        ctk.CTkLabel(left_panel, text="●", font=("", 120), text_color="#6B7C5A").place(x=220, y=480)
        
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
        
        # Username
        ctk.CTkLabel(inner, text="Username", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        login_user = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                   fg_color=BG_SECONDARY, border_color=BORDER,
                                   border_width=1, placeholder_text="Enter username")
        login_user.pack(pady=(5, 15))
        
        # Password
        ctk.CTkLabel(inner, text="Password", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        login_pass = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                   fg_color=BG_SECONDARY, border_color=BORDER,
                                   border_width=1, placeholder_text="Enter password", show="●")
        login_pass.pack(pady=(5, 10))
        
        # Error message
        login_msg = ctk.CTkLabel(inner, text="", text_color=RED, font=("Segoe UI", 11))
        login_msg.pack()
        
        def do_login():
            ok, data = login(login_user.get(), login_pass.get())
            if ok:
                self.user = (data["id"], data["username"])
                self.show_feed()
            else:
                login_msg.configure(text="Invalid username or password")
        
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
        
        ctk.CTkLabel(left_panel, text="●", font=("", 80), text_color="#7A8B6A").place(x=20, y=50)
        ctk.CTkLabel(left_panel, text="●", font=("", 120), text_color="#6B7C5A").place(x=220, y=480)
        
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
        
        # Username
        ctk.CTkLabel(inner, text="Username", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        reg_user = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                 fg_color=BG_SECONDARY, border_color=BORDER,
                                 border_width=1, placeholder_text="Choose a username")
        reg_user.pack(pady=(5, 15))
        
        # Password
        ctk.CTkLabel(inner, text="Password", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        reg_pass = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                 fg_color=BG_SECONDARY, border_color=BORDER,
                                 border_width=1, placeholder_text="Create password", show="●")
        reg_pass.pack(pady=(5, 15))
        
        # Confirm password
        ctk.CTkLabel(inner, text="Confirm Password", font=("Segoe UI", 12, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w")
        reg_pass2 = ctk.CTkEntry(inner, width=280, height=45, corner_radius=10,
                                  fg_color=BG_SECONDARY, border_color=BORDER,
                                  border_width=1, placeholder_text="Confirm password", show="●")
        reg_pass2.pack(pady=(5, 10))
        
        reg_msg = ctk.CTkLabel(inner, text="", font=("Segoe UI", 11))
        reg_msg.pack()
        
        def do_register():
            if reg_pass.get() != reg_pass2.get():
                reg_msg.configure(text="Passwords don't match", text_color=RED)
                return
            ok, msg = register(reg_user.get(), reg_pass.get())
            reg_msg.configure(text=msg, text_color=GREEN if ok else RED)
            if ok:
                self.after(1000, self.show_login)
        
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
    
    # ========================================================================
    # Feed Screen
    # ========================================================================
    
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
        
        ctk.CTkButton(nav_inner, text="🏠  Feed", width=170, height=42, corner_radius=10,
                      fg_color=OLIVE_PALE, text_color=OLIVE_DARK, hover_color=OLIVE_PALE,
                      font=("Segoe UI", 13), anchor="w",
                      command=self.show_feed).pack(pady=3)
        ctk.CTkButton(nav_inner, text="✏️  New Post", width=170, height=42, corner_radius=10,
                      fg_color="transparent", text_color=TEXT_PRIMARY, hover_color=BG_SECONDARY,
                      font=("Segoe UI", 13), anchor="w",
                      command=self.show_create).pack(pady=3)
        ctk.CTkButton(nav_inner, text="👤  Profile", width=170, height=42, corner_radius=10,
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
        
        recent_btn = ctk.CTkButton(sort_frame, text="📅  Recent", width=170, height=38, corner_radius=8,
                      fg_color=OLIVE if self.sort_mode == "recent" else "transparent",
                      text_color="#FFFFFF" if self.sort_mode == "recent" else TEXT_PRIMARY,
                      hover_color=OLIVE_LIGHT if self.sort_mode == "recent" else BG_SECONDARY,
                      font=("Segoe UI", 12), anchor="w",
                      command=lambda: set_sort("recent"))
        recent_btn.pack(pady=2)
        
        popular_btn = ctk.CTkButton(sort_frame, text="🔥  Popular", width=170, height=38, corner_radius=8,
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
        
        sort_label = "🔥 Popular Posts" if self.sort_mode == "popular" else "📅 Recent Posts"
        ctk.CTkLabel(feed_header, text=sort_label, font=("Segoe UI", 18, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        
        # Scrollable feed
        feed = ctk.CTkScrollableFrame(feed_container, fg_color="transparent", corner_radius=0)
        feed.pack(fill="both", expand=True)
        
        posts = get_posts(self.sort_mode)
        
        if not posts:
            empty_frame = ctk.CTkFrame(feed, fg_color=BG_CARD, corner_radius=16)
            empty_frame.pack(fill="x", pady=20, padx=5)
            ctk.CTkLabel(empty_frame, text="🌱", font=("", 40)).pack(pady=(30, 10))
            ctk.CTkLabel(empty_frame, text="No posts yet",
                         font=("Segoe UI", 16, "bold"), text_color=TEXT_PRIMARY).pack()
            ctk.CTkLabel(empty_frame, text="Be the first to share something!",
                         font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=(5, 30))
        
        for post in posts:
            self._create_post_card(feed, post)
    
    def _create_post_card(self, parent, post):
        # Create a styled post card
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=16)
        card.pack(fill="x", pady=8, padx=5)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=20, pady=18)
        
        # Header - Author and time
        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x")
        
        author = get_username(post["author"])
        
        # Avatar circle
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
        
        # Engagement stats in header
        engagement = len(post["likes"]) + len(post["comments"])
        if engagement > 0:
            ctk.CTkLabel(header, text=f"🔥 {engagement}", font=("Segoe UI", 11),
                         text_color=TEXT_MUTED).pack(side="right")
        
        # Content
        ctk.CTkLabel(inner, text=post["content"], font=("Segoe UI", 13),
                     text_color=TEXT_PRIMARY, wraplength=480, justify="left", anchor="w"
                     ).pack(fill="x", pady=(15, 10))
        
        # Image
        if post.get("image"):
            img = load_image(post["image"], (400, 280))
            if img:
                img_frame = ctk.CTkFrame(inner, fg_color=BG_SECONDARY, corner_radius=12)
                img_frame.pack(fill="x", pady=10)
                lbl = ctk.CTkLabel(img_frame, image=img, text="")
                lbl.image = img
                lbl.pack(padx=10, pady=10)
        
        # Divider
        divider = ctk.CTkFrame(inner, fg_color=BORDER, height=1)
        divider.pack(fill="x", pady=(10, 12))
        
        # Actions
        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack(fill="x")
        
        likes = set(post["likes"])
        is_liked = self.user[0] in likes
        
        def do_like():
            toggle_like(self.user[0], post["id"])
            self.show_feed()
        
        like_btn = ctk.CTkButton(actions, 
                      text=f"{'❤️' if is_liked else '🤍'}  {len(likes)}",
                      width=70, height=32, corner_radius=8,
                      fg_color=OLIVE_PALE if is_liked else BG_SECONDARY,
                      text_color=OLIVE_DARK if is_liked else TEXT_SECONDARY,
                      hover_color=OLIVE_PALE, font=("Segoe UI", 12),
                      command=do_like)
        like_btn.pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(actions, text=f"💬 {len(post['comments'])}",
                     font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(side="left", padx=8)
        
        # Comment input
        comment_entry = ctk.CTkEntry(actions, width=180, height=32, corner_radius=8,
                                      fg_color=BG_SECONDARY, border_width=0,
                                      placeholder_text="Write a comment...",
                                      font=("Segoe UI", 11))
        comment_entry.pack(side="left", padx=8)
        
        def do_comment():
            text = comment_entry.get().strip()
            if text:
                add_comment(self.user[0], post["id"], text)
            self.show_feed()
        
        ctk.CTkButton(actions, text="Post", width=60, height=32, corner_radius=8,
                      fg_color=OLIVE, hover_color=OLIVE_DARK, font=("Segoe UI", 11),
                      command=do_comment).pack(side="left")
        
        # Show recent comments
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
        selected_image = {"path": ""} 
        
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
        
        # Text area
        text_box = ctk.CTkTextbox(form, height=180, corner_radius=12,
                                   fg_color=BG_SECONDARY, border_width=0,
                                   font=("Segoe UI", 13))
        text_box.pack(fill="x", pady=10)
        
        # Character count
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
        
        # Image section
        img_section = ctk.CTkFrame(form, fg_color=BG_SECONDARY, corner_radius=12)
        img_section.pack(fill="x", pady=15)
        
        img_inner = ctk.CTkFrame(img_section, fg_color="transparent")
        img_inner.pack(padx=20, pady=15)
        
        img_label = ctk.CTkLabel(img_inner, text="📷 No image selected",
                                  font=("Segoe UI", 12), text_color=TEXT_MUTED)
        img_label.pack(side="left")
        
        preview_frame = ctk.CTkFrame(form, fg_color="transparent")
        preview_frame.pack(fill="x")
        preview_label = ctk.CTkLabel(preview_frame, text="")
        preview_label.pack()
        
        def select_image():
            path = filedialog.askopenfilename(
                filetypes=[("Images", "*.jpg *.jpeg *.png *.gif *.webp")])
            if path:
                selected_image["path"] = path
                img_label.configure(text=f"📷 {os.path.basename(path)}", text_color=OLIVE)
                preview = load_image(path, (250, 180))
                if preview:
                    preview_label.configure(image=preview)
                    preview_label.image = preview
        
        def remove_image():
            selected_image["path"] = ""
            img_label.configure(text="📷 No image selected", text_color=TEXT_MUTED)
            preview_label.configure(image=None)
            preview_label.image = None
        
        ctk.CTkButton(img_inner, text="Add Image", width=100, height=32, corner_radius=8,
                      fg_color=OLIVE, hover_color=OLIVE_DARK, font=("Segoe UI", 11),
                      command=select_image).pack(side="left", padx=(15, 5))
        ctk.CTkButton(img_inner, text="Remove", width=80, height=32, corner_radius=8,
                      fg_color=RED, hover_color=RED_LIGHT, font=("Segoe UI", 11),
                      command=remove_image).pack(side="left", padx=5)
        
        # Message
        msg_label = ctk.CTkLabel(form, text="", font=("Segoe UI", 12))
        msg_label.pack(pady=10)
        
        # Post button
        def do_post():
            content_text = text_box.get("1.0", "end-1c").strip()
            if not content_text:
                msg_label.configure(text="Please write something!", text_color=RED)
                return
            if len(content_text) > 500:
                msg_label.configure(text="Post is too long!", text_color=RED)
                return
            
            create_post(self.user[0], content_text, selected_image["path"])
            msg_label.configure(text="Posted successfully! 🎉", text_color=GREEN)
            self.after(800, self.show_feed)
        
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
        
        # Avatar
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
        ctk.CTkLabel(info, text="ZOBO Member", font=("Segoe UI", 13),
                     text_color=TEXT_MUTED).pack(anchor="w")
        
        # Stats
        my_posts = get_user_posts(self.user[0])
        total_likes = sum(len(p["likes"]) for p in my_posts)
        total_comments = sum(len(p["comments"]) for p in my_posts)
        
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
        
        # Posts section
        posts_header = ctk.CTkFrame(content, fg_color="transparent")
        posts_header.pack(fill="x", pady=(10, 15))
        
        ctk.CTkLabel(posts_header, text="My Posts", font=("Segoe UI", 16, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        
        # Scrollable posts
        posts_frame = ctk.CTkScrollableFrame(content, fg_color="transparent", corner_radius=0)
        posts_frame.pack(fill="both", expand=True)
        
        if not my_posts:
            empty = ctk.CTkFrame(posts_frame, fg_color=BG_CARD, corner_radius=12)
            empty.pack(fill="x", pady=10)
            ctk.CTkLabel(empty, text="You haven't posted anything yet.",
                         font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=30)
        
        for post in my_posts:
            item = ctk.CTkFrame(posts_frame, fg_color=BG_CARD, corner_radius=12)
            item.pack(fill="x", pady=5)
            
            item_inner = ctk.CTkFrame(item, fg_color="transparent")
            item_inner.pack(fill="x", padx=18, pady=14)
            
            # Content preview
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
                delete_post(self.user[0], pid)
                self.show_profile()
            
            ctk.CTkButton(item_inner, text="🗑️", width=35, height=32, corner_radius=8,
                          fg_color=RED, hover_color=RED_LIGHT, font=("Segoe UI", 12),
                          command=do_delete).pack(side="right")



# Run Application
if __name__ == "__main__":
    print("Starting ZOBO...")
    app = ZoboApp()
    app.mainloop()
