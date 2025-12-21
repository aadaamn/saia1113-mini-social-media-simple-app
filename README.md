# Mini Social Media Feed

A simple social media app built with Python.

## How to Run

```bash
pip install customtkinter pillow bcrypt
python main.py
```

## Features

- Register and login
- Create posts with images
- Like and comment on posts
- View your profile

## Code Structure

The code is organized into simple sections:

1. **Setup** - Paths and colors
2. **Data Functions** - Load/save JSON files
3. **User Functions** - Register, login, get username
4. **Post Functions** - Create, delete, like, comment
5. **Helper Functions** - Time formatting, image loading
6. **Main App** - The GUI with 4 screens:
   - Login screen
   - Feed screen
   - Create post screen
   - Profile screen

## Data Structures Used

Dictionary: Store users and posts in JSON |
List: Store comments, feed items |
Set: Track unique likes |
Tuple: Store session (user_id, username) |

## Files

```
Project/
├── main.py         
├── requirements.txt 
└── data/
    ├── users.json  
    ├── posts.json   
    └── images/      
```
