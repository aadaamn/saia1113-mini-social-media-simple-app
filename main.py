"""
Mini Social Media Feed Simulator
================================
A simple social media app with login, posts, likes, and comments.

Data Structures Used:
- Dictionary: Store users and posts
- List: Store comments and feed
- Set: Track unique likes
- Tuple: Session info
"""

import os
import json
import shutil
import uuid
import bcrypt
from datetime import datetime
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog

# =============================================================================
# SETUP
# =============================================================================

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
POSTS_FILE = os.path.join(DATA_DIR, "posts.json")

# Create folders
os.makedirs(IMAGES_DIR, exist_ok=True)

# Colors (White + Olive Green theme)
BG = "#FFFFFF"
BG2 = "#F5F7F2"
OLIVE = "#6B7B3C"
OLIVE_LIGHT = "#8FA055"
TEXT = "#2C3E2D"
TEXT_LIGHT = "#888888"
BORDER = "#E0E5DC"
RED = "#D64545"
GREEN = "#4A7C4E"

# =============================================================================
# DATA FUNCTIONS
# =============================================================================

def load_data(filepath):
    """Load JSON data from file."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_data(filepath, data):
    """Save data to JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

# =============================================================================
# USER FUNCTIONS
# =============================================================================

def register(username, password):
    """Register new user. Returns (success, message)."""
    if len(username) < 3:
        return False, "Username too short (min 3)"
    if len(password) < 6:
        return False, "Password too short (min 6)"
    
    users = load_data(USERS_FILE)
    
    # Check if exists
    for u in users.values():
        if u["username"].lower() == username.lower():
            return False, "Username taken"
    
    # Create user
    user_id = f"U{len(users)+1:03d}"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    users[user_id] = {
        "id": user_id,
        "username": username.lower(),
        "password": hashed,
        "created": datetime.now().isoformat()
    }
    
    save_data(USERS_FILE, users)
    return True, "Registered!"

def login(username, password):
    """Login user. Returns (success, user_data or None)."""
    users = load_data(USERS_FILE)
    
    for user in users.values():
        if user["username"].lower() == username.lower():
            if bcrypt.checkpw(password.encode(), user["password"].encode()):
                return True, {"id": user["id"], "username": user["username"]}
    
    return False, None

def get_username(user_id):
    """Get username by ID."""
    users = load_data(USERS_FILE)
    return users.get(user_id, {}).get("username", "Unknown")

# =============================================================================
# POST FUNCTIONS
# =============================================================================

def create_post(user_id, content, image_path=""):
    """Create a new post."""
    if not content or len(content) > 500:
        return False
    
    posts = load_data(POSTS_FILE)
    post_id = f"P{len(posts)+1:03d}"
    
    # Save image if provided
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
        "likes": [],      # List used as Set (unique users)
        "comments": []    # List of comment dicts
    }
    
    save_data(POSTS_FILE, posts)
    return True

def get_posts():
    """Get all posts as list, sorted by newest first."""
    posts = list(load_data(POSTS_FILE).values())
    return sorted(posts, key=lambda p: p["created"], reverse=True)

def get_user_posts(user_id):
    """Get posts by a specific user."""
    return [p for p in get_posts() if p["author"] == user_id]

def toggle_like(user_id, post_id):
    """Toggle like on a post."""
    posts = load_data(POSTS_FILE)
    if post_id in posts:
        likes = set(posts[post_id]["likes"])  # Convert to Set
        if user_id in likes:
            likes.remove(user_id)
        else:
            likes.add(user_id)
        posts[post_id]["likes"] = list(likes)  # Back to List
        save_data(POSTS_FILE, posts)

def add_comment(user_id, post_id, text):
    """Add comment to a post."""
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
    """Delete a post (only if owner)."""
    posts = load_data(POSTS_FILE)
    if post_id in posts and posts[post_id]["author"] == user_id:
        del posts[post_id]
        save_data(POSTS_FILE, posts)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def time_ago(iso_time):
    """Convert timestamp to '5m ago' format."""
    try:
        dt = datetime.fromisoformat(iso_time)
        secs = (datetime.now() - dt).total_seconds()
        if secs < 60: return "now"
        if secs < 3600: return f"{int(secs/60)}m"
        if secs < 86400: return f"{int(secs/3600)}h"
        return f"{int(secs/86400)}d"
    except:
        return ""

def load_image(path, max_size=(350, 250)):
    """Load image for display."""
    try:
        if path and os.path.exists(path):
            img = Image.open(path)
            img.thumbnail(max_size)
            return ctk.CTkImage(img, img, size=(img.width, img.height))
    except:
        pass
    return None

# =============================================================================
# MAIN APP
# =============================================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Mini Social Media Feed")
        self.geometry("850x650")
        ctk.set_appearance_mode("light")
        self.configure(fg_color=BG)
        
        # Current user (tuple: id, username)
        self.user = None
        
        # Show login screen
        self.show_login()
    
    def clear(self):
        """Remove all widgets."""
        for w in self.winfo_children():
            w.destroy()
    
    # -------------------------------------------------------------------------
    # LOGIN SCREEN
    # -------------------------------------------------------------------------
    
    def show_login(self):
        self.clear()
        self.user = None
        
        # Center frame
        frame = ctk.CTkFrame(self, fg_color=BG)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        ctk.CTkLabel(frame, text="🌿", font=("", 50)).pack()
        ctk.CTkLabel(frame, text="Mini Social Media Feed", 
                     font=("", 26, "bold"), text_color=OLIVE).pack(pady=(0,5))
        ctk.CTkLabel(frame, text="Connect with friends", 
                     text_color=TEXT_LIGHT).pack(pady=(0,25))
        
        # Tabs
        tabs = ctk.CTkTabview(frame, width=320, height=300, 
                              fg_color=BG2, segmented_button_selected_color=OLIVE)
        tabs.pack()
        tabs.add("Login")
        tabs.add("Register")
        
        # --- Login Tab ---
        login_tab = tabs.tab("Login")
        
        login_user = ctk.CTkEntry(login_tab, width=260, height=40,
                                   placeholder_text="Username", fg_color=BG)
        login_user.pack(pady=(25,10))
        
        login_pass = ctk.CTkEntry(login_tab, width=260, height=40,
                                   placeholder_text="Password", show="•", fg_color=BG)
        login_pass.pack(pady=10)
        
        login_msg = ctk.CTkLabel(login_tab, text="", text_color=RED)
        login_msg.pack()
        
        def do_login():
            ok, data = login(login_user.get(), login_pass.get())
            if ok:
                self.user = (data["id"], data["username"])
                self.show_feed()
            else:
                login_msg.configure(text="Invalid username or password")
        
        ctk.CTkButton(login_tab, text="Login", width=260, height=40,
                      fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=do_login).pack(pady=15)
        
        # --- Register Tab ---
        reg_tab = tabs.tab("Register")
        
        reg_user = ctk.CTkEntry(reg_tab, width=260, height=38,
                                 placeholder_text="Username", fg_color=BG)
        reg_user.pack(pady=(20,8))
        
        reg_pass = ctk.CTkEntry(reg_tab, width=260, height=38,
                                 placeholder_text="Password", show="•", fg_color=BG)
        reg_pass.pack(pady=8)
        
        reg_pass2 = ctk.CTkEntry(reg_tab, width=260, height=38,
                                  placeholder_text="Confirm Password", show="•", fg_color=BG)
        reg_pass2.pack(pady=8)
        
        reg_msg = ctk.CTkLabel(reg_tab, text="", text_color=RED)
        reg_msg.pack()
        
        def do_register():
            if reg_pass.get() != reg_pass2.get():
                reg_msg.configure(text="Passwords don't match", text_color=RED)
                return
            ok, msg = register(reg_user.get(), reg_pass.get())
            reg_msg.configure(text=msg, text_color=GREEN if ok else RED)
            if ok:
                tabs.set("Login")
        
        ctk.CTkButton(reg_tab, text="Register", width=260, height=40,
                      fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=do_register).pack(pady=10)
    
    # -------------------------------------------------------------------------
    # FEED SCREEN
    # -------------------------------------------------------------------------
    
    def show_feed(self):
        self.clear()
        
        # Header
        header = ctk.CTkFrame(self, fg_color=BG, height=50)
        header.pack(fill="x", padx=20, pady=(15,10))
        
        ctk.CTkLabel(header, text="🌿 Mini Social Feed", 
                     font=("", 22, "bold"), text_color=OLIVE).pack(side="left")
        
        ctk.CTkLabel(header, text=f"@{self.user[1]}", 
                     text_color=TEXT_LIGHT).pack(side="right", padx=10)
        
        # Feed area
        feed = ctk.CTkScrollableFrame(self, fg_color=BG2, corner_radius=10)
        feed.pack(fill="both", expand=True, padx=20, pady=10)
        
        posts = get_posts()
        
        if not posts:
            ctk.CTkLabel(feed, text="No posts yet. Create the first one! ✨",
                         text_color=TEXT_LIGHT, font=("", 14)).pack(pady=50)
        
        for post in posts:
            self.create_post_card(feed, post)
        
        # Navigation bar
        nav = ctk.CTkFrame(self, fg_color=BG, height=50)
        nav.pack(fill="x", padx=20, pady=(10,15))
        
        ctk.CTkButton(nav, text="🏠 Feed", fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=self.show_feed).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="✏️ New Post", fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=self.show_create).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="👤 Profile", fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=self.show_profile).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="🚪 Logout", fg_color=RED, hover_color="#B33",
                      command=self.show_login).pack(side="right", padx=5)
    
    def create_post_card(self, parent, post):
        """Create a post card widget."""
        card = ctk.CTkFrame(parent, fg_color=BG, corner_radius=10)
        card.pack(fill="x", padx=8, pady=6)
        
        # Author and time
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10,5))
        
        author = get_username(post["author"])
        ctk.CTkLabel(top, text=f"@{author}", font=("", 13, "bold"),
                     text_color=OLIVE).pack(side="left")
        ctk.CTkLabel(top, text=time_ago(post["created"]),
                     text_color=TEXT_LIGHT, font=("", 11)).pack(side="right")
        
        # Content
        ctk.CTkLabel(card, text=post["content"], text_color=TEXT,
                     wraplength=450, justify="left", anchor="w"
                     ).pack(fill="x", padx=12, pady=5)
        
        # Image
        if post.get("image"):
            img = load_image(post["image"])
            if img:
                lbl = ctk.CTkLabel(card, image=img, text="")
                lbl.image = img  # Keep reference
                lbl.pack(padx=12, pady=5)
        
        # Actions
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(5,8))
        
        # Like button
        likes = set(post["likes"])
        is_liked = self.user[0] in likes
        
        def do_like():
            toggle_like(self.user[0], post["id"])
            self.show_feed()
        
        ctk.CTkButton(actions, text=f"{'❤️' if is_liked else '🤍'} {len(likes)}", 
                      width=60, height=28, fg_color=BG2, text_color=TEXT,
                      hover_color=BORDER, command=do_like).pack(side="left", padx=(0,5))
        
        # Comment count
        ctk.CTkLabel(actions, text=f"💬 {len(post['comments'])}",
                     text_color=TEXT_LIGHT).pack(side="left", padx=5)
        
        # Comment input
        comment_entry = ctk.CTkEntry(actions, width=150, height=28,
                                      placeholder_text="Comment...", fg_color=BG)
        comment_entry.pack(side="left", padx=5)
        
        def do_comment():
            add_comment(self.user[0], post["id"], comment_entry.get())
            self.show_feed()
        
        ctk.CTkButton(actions, text="Post", width=50, height=28,
                      fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=do_comment).pack(side="left")
        
        # Show last 2 comments
        for c in post["comments"][-2:]:
            c_author = get_username(c["author"])
            ctk.CTkLabel(card, text=f"💬 {c_author}: {c['text']}", 
                         text_color=TEXT_LIGHT, font=("", 11),
                         wraplength=400, anchor="w"
                         ).pack(fill="x", padx=15, pady=1)
    
    # -------------------------------------------------------------------------
    # CREATE POST SCREEN
    # -------------------------------------------------------------------------
    
    def show_create(self):
        self.clear()
        selected_image = {"path": ""}  # Use dict to store in closure
        
        # Header
        header = ctk.CTkFrame(self, fg_color=BG)
        header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(header, text="← Back", width=80, fg_color=BG2,
                      text_color=TEXT, hover_color=BORDER,
                      command=self.show_feed).pack(side="left")
        ctk.CTkLabel(header, text="Create Post", font=("", 20, "bold"),
                     text_color=OLIVE).pack(side="left", padx=20)
        
        # Form
        form = ctk.CTkFrame(self, fg_color=BG2, corner_radius=10)
        form.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(form, text="What's on your mind?", 
                     text_color=TEXT_LIGHT).pack(anchor="w", padx=15, pady=(15,5))
        
        text_box = ctk.CTkTextbox(form, height=150, fg_color=BG)
        text_box.pack(fill="x", padx=15, pady=5)
        
        # Character count
        count_label = ctk.CTkLabel(form, text="0/500", text_color=TEXT_LIGHT)
        count_label.pack(anchor="e", padx=15)
        
        def update_count(e=None):
            n = len(text_box.get("1.0", "end-1c"))
            count_label.configure(text=f"{n}/500", text_color=RED if n > 500 else TEXT_LIGHT)
        text_box.bind("<KeyRelease>", update_count)
        
        # Image section
        img_frame = ctk.CTkFrame(form, fg_color="transparent")
        img_frame.pack(fill="x", padx=15, pady=10)
        
        img_label = ctk.CTkLabel(img_frame, text="No image selected", text_color=TEXT_LIGHT)
        img_label.pack(side="left")
        
        preview_label = ctk.CTkLabel(form, text="")
        preview_label.pack(pady=5)
        
        def select_image():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.gif")])
            if path:
                selected_image["path"] = path
                img_label.configure(text=f"📷 {os.path.basename(path)}", text_color=OLIVE)
                # Show preview
                preview = load_image(path, (200, 150))
                if preview:
                    preview_label.configure(image=preview)
                    preview_label.image = preview
        
        def remove_image():
            selected_image["path"] = ""
            img_label.configure(text="No image selected", text_color=TEXT_LIGHT)
            preview_label.configure(image=None)
        
        ctk.CTkButton(img_frame, text="📷 Add Image", fg_color=OLIVE,
                      hover_color=OLIVE_LIGHT, command=select_image).pack(side="left", padx=10)
        ctk.CTkButton(img_frame, text="✕ Remove", fg_color=RED,
                      hover_color="#B33", command=remove_image).pack(side="left")
        
        # Message
        msg_label = ctk.CTkLabel(form, text="", text_color=TEXT_LIGHT)
        msg_label.pack(pady=5)
        
        # Post button
        def do_post():
            content = text_box.get("1.0", "end-1c").strip()
            if not content:
                msg_label.configure(text="Write something!", text_color=RED)
                return
            if len(content) > 500:
                msg_label.configure(text="Too long!", text_color=RED)
                return
            
            create_post(self.user[0], content, selected_image["path"])
            msg_label.configure(text="Posted! 🎉", text_color=GREEN)
            self.after(800, self.show_feed)
        
        ctk.CTkButton(form, text="📤 Share Post", width=200, height=45,
                      font=("", 15, "bold"), fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=do_post).pack(pady=20)
    
    # -------------------------------------------------------------------------
    # PROFILE SCREEN
    # -------------------------------------------------------------------------
    
    def show_profile(self):
        self.clear()
        
        # Header
        header = ctk.CTkFrame(self, fg_color=BG)
        header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(header, text=f"👤 @{self.user[1]}", font=("", 20, "bold"),
                     text_color=OLIVE).pack(side="left")
        
        # Stats
        my_posts = get_user_posts(self.user[0])
        total_likes = sum(len(p["likes"]) for p in my_posts)
        total_comments = sum(len(p["comments"]) for p in my_posts)
        
        stats = ctk.CTkFrame(self, fg_color=BG2, corner_radius=10)
        stats.pack(fill="x", padx=20, pady=10)
        
        for i, (label, value) in enumerate([
            ("📝 Posts", len(my_posts)),
            ("❤️ Likes", total_likes),
            ("💬 Comments", total_comments)
        ]):
            box = ctk.CTkFrame(stats, fg_color=BG, corner_radius=8)
            box.grid(row=0, column=i, padx=10, pady=12, sticky="nsew")
            stats.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(box, text=str(value), font=("", 24, "bold"),
                         text_color=OLIVE).pack(pady=(10,0))
            ctk.CTkLabel(box, text=label, text_color=TEXT_LIGHT).pack(pady=(0,10))
        
        # My posts
        ctk.CTkLabel(self, text="My Posts", font=("", 16, "bold"),
                     text_color=TEXT).pack(anchor="w", padx=20, pady=(10,5))
        
        posts_frame = ctk.CTkScrollableFrame(self, fg_color=BG2, corner_radius=10)
        posts_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        if not my_posts:
            ctk.CTkLabel(posts_frame, text="No posts yet!", 
                         text_color=TEXT_LIGHT).pack(pady=30)
        
        for post in my_posts:
            item = ctk.CTkFrame(posts_frame, fg_color=BG, corner_radius=8)
            item.pack(fill="x", padx=8, pady=4)
            
            # Content preview
            content = post["content"][:60] + ("..." if len(post["content"]) > 60 else "")
            ctk.CTkLabel(item, text=content, text_color=TEXT,
                         wraplength=350, anchor="w").pack(side="left", padx=10, pady=8)
            
            # Delete button
            def do_delete(pid=post["id"]):
                delete_post(self.user[0], pid)
                self.show_profile()
            
            ctk.CTkButton(item, text="🗑️", width=35, fg_color=RED,
                          hover_color="#B33", command=do_delete).pack(side="right", padx=10, pady=8)
            
            # Stats
            ctk.CTkLabel(item, text=f"❤️{len(post['likes'])} 💬{len(post['comments'])}",
                         text_color=TEXT_LIGHT, font=("", 11)).pack(side="right", padx=5)
        
        # Navigation
        nav = ctk.CTkFrame(self, fg_color=BG)
        nav.pack(fill="x", padx=20, pady=(10,15))
        
        ctk.CTkButton(nav, text="🏠 Feed", fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=self.show_feed).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="✏️ New Post", fg_color=OLIVE, hover_color=OLIVE_LIGHT,
                      command=self.show_create).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="🚪 Logout", fg_color=RED, hover_color="#B33",
                      command=self.show_login).pack(side="right", padx=5)


# =============================================================================
# RUN APP
# =============================================================================

if __name__ == "__main__":
    print("Starting Mini Social Media Feed...")
    app = App()
    app.mainloop()
