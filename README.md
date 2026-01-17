# ZOBO Mini Social Media Feed

A simple social media app built with Python.

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

## Features

- Register and login
- Create text posts
- Like and comment on posts
- View your profile
- Sort posts by recent or popular

## Code Structure

The code is organized into simple sections:

1. **Setup** - Colors and theme configuration
2. **Data Storage** - In-memory dictionaries for users and posts
3. **User Functions** - Register, login, get username
4. **Post Functions** - Create, delete, like, comment
5. **Utility Functions** - Time formatting, input validation
6. **Main App** - The GUI with 4 screens:
   - Login screen
   - Register screen
   - Feed screen
   - Create post screen
   - Profile screen

## Data Structures Used

| Data Structure | Usage |
|----------------|-------|
| Dictionary | Store users (USERS_DATA) and posts (POSTS_DATA) |
| List | Store comments, likes, feed items |
| Set | Track unique likes (in toggle_like function) |
| Tuple | Store session (user_id, username) |

## User-Defined Functions

| Function | Purpose |
|----------|---------|
| `initialize_sample_data()` | Load initial sample data |
| `register()` | Create new user account |
| `login()` | Authenticate user |
| `get_username()` | Get username by user ID |
| `create_post()` | Create a new post |
| `get_posts()` | Get all posts sorted by criteria |
| `get_user_posts()` | Get posts by specific user |
| `toggle_like()` | Like or unlike a post |
| `add_comment()` | Add comment to a post |
| `delete_post()` | Delete a post |
| `time_ago()` | Convert timestamp to readable format |
| `validate_input()` | Validate text input length |

## Files

```
Project/
├── main.py           # Main application code
├── requirements.txt  # Python dependencies
└── README.md         # Documentation
```
