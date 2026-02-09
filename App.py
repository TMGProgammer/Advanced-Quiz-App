from datetime import date
from gettext import install
import tkinter as tk
from tkinter import ttk
import winsound
import requests
import json, os
from tkinter import messagebox

XP_TO_LEVEL = 100
XP_PER_CORRECT = 10

def calculate_level(xp):
    return (xp // XP_TO_LEVEL) + 1

USER_FILE = "user_xp.json"
def load_user_data():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {
        "username": "Player",
        "xp": 0,
        "level": 1,
        "last_play_date": ""
    }
def save_user_data(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_data = load_user_data()
if "level" not in user_data:
    user_data["level"] = calculate_level(user_data["xp"])
    save_user_data(user_data)

SERVER_URL = "https://quiz-leaderboard-server-xz1c.onrender.com"

def fetch_leaderboard():
    try:
        r = requests.get(f"{SERVER_URL}/leaderboard", timeout=3)
        return r.json()
    except:
        return []


def send_score_online():
    try:
        requests.post(
            f"{SERVER_URL}/submit",
            json={
                "username": username,
                "xp": user_xp
            },
            timeout=3
        )
    except:
        pass


def play_click():
    winsound.PlaySound("click.wav", winsound.SND_ASYNC)

def play_correct():
    winsound.PlaySound("correct.wav", winsound.SND_ASYNC)

def play_wrong():
    winsound.PlaySound("wrong.wav", winsound.SND_ASYNC)

def play_result():
    try:
        winsound.PlaySound("result.wav", winsound.SND_ASYNC)
    except:
        pass



# ================= APP SETUP =================
root = tk.Tk()
root.title("Quiz App")
root.geometry("480x560")
root.config(bg="#f6f7fb")

XP_FILE = "user_xp.json"
board = fetch_leaderboard()

# ================= LOAD XP =================
if os.path.exists(XP_FILE):
    with open(XP_FILE, "r") as f:
        data = json.load(f)
        user_xp = data.get("xp", 0)
        username = data.get("username", "")
else:
    user_xp = 0
    username = ""

user_level = calculate_level(user_xp)




# ================= SAVE XP =================
def save_user():
    with open(XP_FILE, "w") as f:
        json.dump({"username": username, "xp": user_xp}, f)

def save_xp():
    data = {
        "xp": user_xp,
        "username": username
    }
    with open(XP_FILE, "w") as f:
        json.dump(data, f)
        
def get_level():
    return user_xp // XP_TO_LEVEL + 1

def get_xp_in_level():
    return user_xp % XP_TO_LEVEL

# ================= DATA =================
QUESTIONS_LVL1 = [
        {"question": "What is the capital of France?", "options": ["Paris", "Rome", "Madrid", "Berlin"], "answer": "Paris"},
        {"question": "What is 5 + 7?", "options": ["10", "11", "12", "13"], "answer": "12"},
        {"question": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Mars"},
        {"question": "What is the largest mammal?", "options": ["Elephant", "Blue Whale", "Giraffe", "Hippopotamus"], "answer": "Blue Whale"},
        {"question": "Who wrote 'Romeo and Juliet'?", "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"], "answer": "William Shakespeare"}
    ]
QUESTIONS_LVL2 = [
        {"question": "What is the chemical symbol for Gold?", "options": ["Au", "Ag", "Gd", "Go"], "answer": "Au"},
        {"question": "Who developed the theory of relativity?", "options": ["Isaac Newton", "Albert Einstein", "Nikola Tesla", "Galileo Galilei"], "answer": "Albert Einstein"},
        {"question": "What is the square root of 144?", "options": ["10", "11", "12", "13"], "answer": "12"},
        {"question": "Which gas is most abundant in the Earth's atmosphere?", "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Argon"], "answer": "Nitrogen"},
        {"question": "Who painted the Mona Lisa?", "options": ["Vincent Van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Claude Monet"], "answer": "Leonardo da Vinci"}
    ]

# ================= STATE =================
current_level = 1
q_index = 0
score = 0
time_left = 10
timer_id = None

# ================= SCREENS =================
lobby_frame = tk.Frame(root, bg="#f6f7fb")
level_frame = tk.Frame(root, bg="#f6f7fb")
quiz_frame = tk.Frame(root, bg="#f6f7fb")
result_frame = tk.Frame(root, bg="#f6f7fb")
leaderboard_frame = tk.Frame(root, bg="#f6f7fb")

# ================= FUNCTIONS =================
def hide_all():
    for f in (lobby_frame, level_frame, quiz_frame, result_frame, leaderboard_frame):
        f.pack_forget()

def ask_username():
    popup = tk.Toplevel(root)
    popup.title("Create Username")
    popup.geometry("300x200")
    popup.grab_set()

    tk.Label(popup, text="Enter your username",
             font=("Arial", 14, "bold")).pack(pady=20)

    entry = tk.Entry(popup, font=("Arial", 12))
    entry.pack(pady=10)

    def save_name():
        nonlocal popup
        name = entry.get().strip()
        if name:
            global username
            username = name
            save_user()
            popup.destroy()
            show_lobby()

    tk.Button(popup, text="SAVE",
              bg="#58cc02", fg="white",
              font=("Arial", 12, "bold"),
              command=save_name).pack(pady=20)

def show_lobby():
     if username == "":
         ask_username()
         return
     hide_all()
     update_xp_ui()
     update_level_buttons()
     lobby_frame.pack(fill="both", expand=True)

def update_level_buttons():
    global user_level

    user_level = calculate_level(user_xp)

    if user_level < 2:
        level2_btn.config(
            state="disabled",
            text="🔒 LEVEL 2"
        )
    else:
        level2_btn.config(
            state="normal",
            text="LEVEL 2"
        )



def show_leaderboard():
    hide_all()
    leaderboard_frame.pack(fill="both", expand=True)

    for w in leaderboard_box.winfo_children():
        w.destroy()

    loading = tk.Label(
        leaderboard_box,
        text="Loading leaderboard...",
        font=("Arial", 14),
        bg="#f5f5f5"
    )
    loading.pack()

    leaderboard_frame.after(100, load_leaderboard_ui)

def load_leaderboard_ui():
    for w in leaderboard_box.winfo_children():
        w.destroy()

    board = fetch_leaderboard()

    if not board:
        tk.Label(
            leaderboard_box,
            text="⚠️ No internet / server offline",
            font=("Arial", 14),
            fg="red",
            bg="#f5f5f5"
        ).pack()
        return

    render_leaderboard(board)

def render_leaderboard(board):
    for i, user in enumerate(board):
        medal = ""
        if i == 0: medal = "🥇 "
        elif i == 1: medal = "🥈 "
        elif i == 2: medal = "🥉 "

        color = "#58cc02" if user["username"] == username else "#000000"

        tk.Label(
            leaderboard_box,
            text=f"{medal}{i+1}. {user['username']} — {user['xp']} XP",
            font=("Arial", 14, "bold"),
            fg=color,
            bg="#f5f5f5"
        ).pack(anchor="w", pady=4)


def open_leaderboard():
    hide_all()
    update_leaderboard_ui()
    leaderboard_frame.pack(fill="both", expand=True)

def update_xp_ui():
    current_level = calculate_level(user_xp)
    xp_in_level = user_xp % XP_TO_LEVEL
    
    xp_bar["maximum"] = XP_TO_LEVEL
    xp_bar["value"] = xp_in_level
    xp_text.config(text=f"{xp_in_level}/{XP_TO_LEVEL} XP")
    level_label.config(text=f"LEVEL {current_level}")


def show_levels():
    hide_all()
    level_frame.pack(expand=True)

def start_level(lvl):
    global questions

    # Check if already played today
    today = str(date.today())
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            data = json.load(f)
            last_date = data.get("last_play_date", "")
            
            if last_date == today:
                messagebox.showinfo(
                    "Daily Limit",
                    "❌ You already played today.\nCome back tomorrow!"
                )
                return

    if lvl == 1:
        questions = QUESTIONS_LVL1
    elif lvl == 2:
        questions = QUESTIONS_LVL2
    else:
        return

    start_quiz()

def start_quiz():
    global q_index, score, time_left

    q_index = 0
    score = 0
    time_left = 10

    hide_all()
    quiz_frame.pack(fill="both", expand=True)
    load_question()


def load_question():
    global time_left, timer_id
    time_left = 10
    timer_label.config(text=f"⏱ {time_left}s")

    q = questions[q_index]
    question_label.config(text=f"Q{q_index+1}. {q['question']}")

    options = q["options"]
    for i in range(4):
        option_buttons[i].config(
            text=options[i],
            bg="#dddddd",  # Reset to default color
            state="normal",  # Enable button
            command=lambda opt=options[i]: check_answer(opt)
        )

    start_timer()

def start_timer():
    global time_left, timer_id
    if time_left > 0:
        timer_label.config(text=f"⏱ {time_left}s")
        time_left -= 1
        timer_id = root.after(1000, start_timer)
    else:
        play_wrong()
        next_question()

def check_answer(selected):
    global score, user_xp
    root.after_cancel(timer_id)

    correct = questions[q_index]["answer"]
    
    # Disable all buttons
    for btn in option_buttons:
        btn.config(state="disabled")
    
    if selected == correct:
        play_correct()
        score += 1
        user_xp += XP_PER_CORRECT
        update_level_buttons()
        save_user()
        
        # Highlight correct button in green
        for btn in option_buttons:
            if btn.cget("text") == correct:
                btn.config(bg="#58cc02")  # Green
    else:
        play_wrong()
        
        # Highlight wrong button in red and correct in green
        for btn in option_buttons:
            if btn.cget("text") == selected:
                btn.config(bg="#ff6b6b")  # Red
            elif btn.cget("text") == correct:
                btn.config(bg="#58cc02")  # Green

    # Delay before next question (let sound finish)
    root.after(800, next_question)

def next_question():
    global q_index
    q_index += 1
    if q_index < 5:
        load_question()
    else:
        show_result()

def show_result():
    global user_xp

    hide_all()
    result_frame.pack(fill="both", expand=True)

    gained_xp = score * 10
    gained_xp = min(gained_xp, 100)  # Cap at 100 XP per quiz
    user_xp += gained_xp

    save_xp()  # existing function

    current_level = calculate_level(user_xp)

    score_label.config(text=f"Score: {score}/{len(questions)}")
    gain_xp_label.config(text=f"XP Gained: +{gained_xp}")
    total_xp_label.config(text=f"Total XP: {user_xp}")
    result_level_label.config(text=f"Level: {current_level}")

    update_level_buttons()
    update_xp_ui()
    send_score_online()
    play_result()

def back_to_lobby_from_result():
    # Save today's date when returning from quiz
    today = str(date.today())
    if os.path.exists(XP_FILE):
        with open(XP_FILE, "r") as f:
            data = json.load(f)
        data["last_play_date"] = today
        with open(XP_FILE, "w") as f:
            json.dump(data, f, indent=4)
    
    play_click()
    show_lobby()



def update_leaderboard_ui():
    leaderboard_box.delete("1.0", tk.END)
    board = fetch_leaderboard()
    for i, user in enumerate(board[:10], start=1):
        leaderboard_box.insert(
            tk.END,
            f"{i}. {user['username']} — XP {user['xp']}\n"
        )

def send_score_online():
    # Send only the SCORE (0-5), let server calculate XP
    try:
        requests.post(
            f"{SERVER_URL}/submit",
            json={
                "username": username,
                "score": score  # Send score, not XP
            },
            timeout=3
        )
    except:
        pass

def get_my_rank(board, username):
    for i, u in enumerate(board):
        if u["username"] == username:
            return i + 1
    return None

def get_badge(xp):
    if xp >= 1000: return "👑 LEGEND"
    if xp >= 500: return "🔥 PRO"
    if xp >= 200: return "⭐ RISING"
    return "🌱 BEGINNER"



# ================= LOBBY =================
level_label = tk.Label(lobby_frame, font=("Arial", 20, "bold"),
                       fg="#58cc02", bg="#f6f7fb")
level_label.pack(pady=10)

leaderboard_box = tk.Text(
    leaderboard_frame,
    width=30,
    height=12,
    font=("Arial", 14),
    bg="#f6f7fb",
    bd=0
)
leaderboard_box.pack(pady=20)

tk.Button(
    leaderboard_frame,
    text="🔄 Refresh",
    font=("Arial", 12, "bold"),
    command=show_leaderboard
).pack(pady=10)


tk.Button(
    leaderboard_frame,
    text="BACK",
    command=lambda: show_lobby()
).pack(pady=10)

tk.Button(
    lobby_frame,
    text="LEADERBOARD",
    command=open_leaderboard
).pack(pady=10)


result_title = tk.Label(
    result_frame,
    text="🎉 QUIZ COMPLETE",
    font=("Arial", 22, "bold"),
    bg="#f5f5f5"
)
result_title.pack(pady=20)

score_label = tk.Label(result_frame, font=("Arial", 16), bg="#f5f5f5")
score_label.pack(pady=5)

gain_xp_label = tk.Label(result_frame, font=("Arial", 16), bg="#f5f5f5")
gain_xp_label.pack(pady=5)

total_xp_label = tk.Label(result_frame, font=("Arial", 16), bg="#f5f5f5")
total_xp_label.pack(pady=5)

result_level_label = tk.Label(result_frame, font=("Arial", 16, "bold"), bg="#f5f5f5")
result_level_label.pack(pady=10)


xp_bar = ttk.Progressbar(
    lobby_frame,
    orient="horizontal",
    length=300,
    mode="determinate",
    maximum=XP_TO_LEVEL
)
xp_bar.pack(pady=10)

xp_text = tk.Label(lobby_frame, font=("Arial", 12),
                   bg="#f6f7fb")
xp_text.pack()

tk.Label(lobby_frame, text="🟢 QUIZ LOBBY",
         font=("Arial", 26, "bold"),
         fg="#58cc02", bg="#f6f7fb").pack(pady=30)

tk.Button(
    lobby_frame,
    text="START QUIZ",
    font=("Arial", 16, "bold"),
    bg="#58cc02",
    fg="white",
    width=16,
    relief="flat",
    command=lambda: (play_click(), show_levels())
).pack(pady=30)

rank = get_my_rank(fetch_leaderboard(), username)
rank_text = f"🌍 Global Rank: #{rank}" if rank else "🌍 Global Rank: —"
tk.Label(lobby_frame, text=rank_text, font=("Arial", 12, "bold")).pack()

tk.Label(
    lobby_frame,
    text=f"Badge: {get_badge(user_xp)}",
    font=("Arial", 12, "bold"),
    fg="#ff9800"
).pack(pady=4)



# ================= LEVEL SELECT =================
tk.Label(level_frame, text="🎯 SELECT LEVEL",
         font=("Arial", 24, "bold"),
         bg="#f6f7fb").pack(pady=30)

level1_btn = tk.Button(level_frame, text="LEVEL 1",
          font=("Arial", 14, "bold"),
          width=18, bg="#58cc02",
          fg="white", relief="flat",
          command=lambda lvl=1: (play_click(), start_level(lvl)))
level1_btn.pack(pady=8)

level2_btn = tk.Button(
    level_frame,
    text="LEVEL 2",
    font=("Arial", 14, "bold"),
    width=18,
    bg="#58cc02",
    fg="white",
    relief="flat",
    command=lambda: (play_click(), start_level(2))
)
level2_btn.pack(pady=8)


tk.Button(
    level_frame,
    text="⬅ BACK",
    command=lambda: (play_click(), show_lobby()),
    relief="flat"
).pack(pady=20)

# ================= QUIZ =================
timer_label = tk.Label(quiz_frame, font=("Arial", 14, "bold"),
                       fg="red", bg="#f6f7fb")
timer_label.pack(pady=10)

question_label = tk.Label(quiz_frame, font=("Arial", 16, "bold"),
                          wraplength=420,
                          bg="#f6f7fb")
question_label.pack(pady=20)

option_buttons = []
for _ in range(4):
    btn = tk.Button(quiz_frame, font=("Arial", 12),
                    width=30, bg="#dddddd",
                    relief="flat")
    btn.pack(pady=6)
    option_buttons.append(btn)

# ================= RESULT =================
result_label = tk.Label(result_frame, font=("Arial", 22, "bold"),
                        bg="#f6f7fb")
result_label.pack(pady=60)

tk.Button(result_frame, text="BACK TO LOBBY",
          font=("Arial", 14),
          bg="#58cc02", fg="white",
          width=18, relief="flat",
          command=back_to_lobby_from_result).pack(pady=20)

# ================= START =================
show_lobby()
root.mainloop()
