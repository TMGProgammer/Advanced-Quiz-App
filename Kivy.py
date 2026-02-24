from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import requests
import json
import os
from datetime import date

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

def send_score_online(username, score):
    try:
        requests.post(
            f"{SERVER_URL}/submit",
            json={
                "username": username,
                "score": score
            },
            timeout=3
        )
    except:
        pass

# Load sounds
click_sound = SoundLoader.load('click.wav')
correct_sound = SoundLoader.load('correct.wav')
wrong_sound = SoundLoader.load('wrong.wav')
result_sound = SoundLoader.load('result.wav')

def play_click():
    if click_sound:
        click_sound.play()

def play_correct():
    if correct_sound:
        correct_sound.play()

def play_wrong():
    if wrong_sound:
        wrong_sound.play()

def play_result():
    if result_sound:
        result_sound.play()

# Global variables
user_xp = user_data.get("xp", 0)
username = user_data.get("username", "Player")
user_level = calculate_level(user_xp)

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

class UsernameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        self.title_label = Label(text="Create Username", font_size=28)
        self.layout.add_widget(self.title_label)
        
        self.input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.input_layout.add_widget(Label(text="Username:", size_hint=(None, 1), width=100))
        self.username_input = TextInput(multiline=False, font_size=18)
        self.input_layout.add_widget(self.username_input)
        self.layout.add_widget(self.input_layout)
        
        self.save_btn = Button(text="SAVE", font_size=20, background_color=(0.35, 0.8, 0.02, 1), size_hint_y=None, height=60)
        self.save_btn.bind(on_press=self.save_username)
        self.layout.add_widget(self.save_btn)
        
        self.add_widget(self.layout)
    
    def save_username(self, instance):
        name = self.username_input.text.strip()
        if name:
            global username
            username = name
            save_user_data({"username": username, "xp": user_xp, "level": calculate_level(user_xp), "last_play_date": user_data.get("last_play_date", "")})
            self.manager.current = 'lobby'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.level_label = Label(text=f"LEVEL {calculate_level(user_xp)}", font_size=24, color=(0.35, 0.8, 0.02, 1))
        self.layout.add_widget(self.level_label)
        
        self.xp_bar = ProgressBar(max=XP_TO_LEVEL, value=user_xp % XP_TO_LEVEL, size_hint_y=None, height=30)
        self.layout.add_widget(self.xp_bar)
        
        self.xp_text = Label(text=f"{user_xp % XP_TO_LEVEL}/{XP_TO_LEVEL} XP", font_size=14)
        self.layout.add_widget(self.xp_text)
        
        self.total_xp_label = Label(text=f"Total XP: {user_xp}", font_size=14)
        self.layout.add_widget(self.total_xp_label)
        
        self.title_label = Label(text="🟢 QUIZ LOBBY", font_size=32, color=(0.35, 0.8, 0.02, 1))
        self.layout.add_widget(self.title_label)
        
        self.start_btn = Button(text="START QUIZ", font_size=18, background_color=(0.35, 0.8, 0.02, 1), size_hint_y=None, height=50)
        self.start_btn.bind(on_press=self.go_to_levels)
        self.layout.add_widget(self.start_btn)
        
        rank = self.get_my_rank(fetch_leaderboard(), username)
        rank_text = f"🌍 Global Rank: #{rank}" if rank else "🌍 Global Rank: —"
        self.rank_label = Label(text=rank_text, font_size=14)
        self.layout.add_widget(self.rank_label)
        
        badge = self.get_badge(user_xp)
        self.badge_label = Label(text=f"Badge: {badge}", font_size=14, color=(1, 0.6, 0, 1))
        self.layout.add_widget(self.badge_label)
        
        self.leaderboard_btn = Button(text="LEADERBOARD", font_size=14, size_hint_y=None, height=40)
        self.leaderboard_btn.bind(on_press=self.go_to_leaderboard)
        self.layout.add_widget(self.leaderboard_btn)
        
        self.add_widget(self.layout)
        self.update_ui()
    
    def on_enter(self):
        if username == "Player":
            self.manager.current = 'username'
    
    def update_ui(self):
        global user_xp, user_level
        user_level = calculate_level(user_xp)
        self.level_label.text = f"LEVEL {user_level}"
        self.xp_bar.value = user_xp % XP_TO_LEVEL
        self.xp_text.text = f"{user_xp % XP_TO_LEVEL}/{XP_TO_LEVEL} XP"
        self.total_xp_label.text = f"Total XP: {user_xp}"
        rank = self.get_my_rank(fetch_leaderboard(), username)
        self.rank_label.text = f"🌍 Global Rank: #{rank}" if rank else "🌍 Global Rank: —"
        self.badge_label.text = f"Badge: {self.get_badge(user_xp)}"
    
    def go_to_levels(self, instance):
        play_click()
        self.manager.current = 'level'
    
    def go_to_leaderboard(self, instance):
        self.manager.current = 'leaderboard'
    
    def get_my_rank(self, board, username):
        for i, u in enumerate(board):
            if u["username"] == username:
                return i + 1
        return None
    
    def get_badge(self, xp):
        if xp >= 1000: return "👑 LEGEND"
        if xp >= 500: return "🔥 PRO"
        if xp >= 200: return "⭐ RISING"
        return "🌱 BEGINNER"

class LevelScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.title_label = Label(text="🎯 SELECT LEVEL", font_size=28)
        self.layout.add_widget(self.title_label)
        
        self.level1_btn = Button(text="LEVEL 1", font_size=16, background_color=(0.35, 0.8, 0.02, 1), size_hint_y=None, height=50)
        self.level1_btn.bind(on_press=lambda x: self.start_level(1))
        self.layout.add_widget(self.level1_btn)
        
        self.level2_btn = Button(text="LEVEL 2", font_size=16, background_color=(0.35, 0.8, 0.02, 1), size_hint_y=None, height=50)
        self.level2_btn.bind(on_press=lambda x: self.start_level(2))
        self.layout.add_widget(self.level2_btn)
        
        self.back_btn = Button(text="⬅ BACK", font_size=14, size_hint_y=None, height=40)
        self.back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_btn)
        
        self.add_widget(self.layout)
        self.update_buttons()
    
    def update_buttons(self):
        global user_level
        if user_level < 2:
            self.level2_btn.disabled = True
            self.level2_btn.text = "🔒 LEVEL 2"
        else:
            self.level2_btn.disabled = False
            self.level2_btn.text = "LEVEL 2"
    
    def start_level(self, lvl):
        play_click()
        today = str(date.today())
        if user_data.get("last_play_date") == today:
            popup = Popup(title='Daily Limit', content=Label(text='❌ You already played today.\nCome back tomorrow!'), size_hint=(0.8, 0.4))
            popup.open()
            return
        
        quiz_screen = self.manager.get_screen('quiz')
        if lvl == 1:
            quiz_screen.questions = QUESTIONS_LVL1
        elif lvl == 2:
            quiz_screen.questions = QUESTIONS_LVL2
        quiz_screen.start_quiz()
        self.manager.current = 'quiz'
    
    def go_back(self, instance):
        play_click()
        self.manager.current = 'lobby'

class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.timer_label = Label(text="⏱ 10s", font_size=16, color=(1, 0, 0, 1))
        self.layout.add_widget(self.timer_label)
        
        self.question_label = Label(text="", font_size=18, size_hint_y=None, height=100, text_size=(400, None))
        self.layout.add_widget(self.question_label)
        
        self.options_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, height=200)
        self.option_buttons = []
        for i in range(4):
            btn = Button(text="", font_size=14, background_color=(0.87, 0.87, 0.87, 1), size_hint_y=None, height=40)
            btn.bind(on_press=self.check_answer)
            self.options_layout.add_widget(btn)
            self.option_buttons.append(btn)
        self.layout.add_widget(self.options_layout)
        
        self.add_widget(self.layout)
        self.questions = []
        self.q_index = 0
        self.score = 0
        self.time_left = 10
        self.timer_event = None
    
    def start_quiz(self):
        self.q_index = 0
        self.score = 0
        self.time_left = 10
        self.load_question()
    
    def load_question(self):
        self.time_left = 10
        self.timer_label.text = f"⏱ {self.time_left}s"
        q = self.questions[self.q_index]
        self.question_label.text = f"Q{self.q_index+1}. {q['question']}"
        options = q["options"]
        for i in range(4):
            self.option_buttons[i].text = options[i]
            self.option_buttons[i].background_color = (0.87, 0.87, 0.87, 1)
            self.option_buttons[i].disabled = False
        self.start_timer()
    
    def start_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
    
    def update_timer(self, dt):
        self.time_left -= 1
        self.timer_label.text = f"⏱ {self.time_left}s"
        if self.time_left <= 0:
            self.timer_event.cancel()
            play_wrong()
            self.next_question()
    
    def check_answer(self, instance):
        if self.timer_event:
            self.timer_event.cancel()
        selected = instance.text
        correct = self.questions[self.q_index]["answer"]
        for btn in self.option_buttons:
            btn.disabled = True
        if selected == correct:
            play_correct()
            self.score += 1
            instance.background_color = (0.35, 0.8, 0.02, 1)
        else:
            play_wrong()
            instance.background_color = (1, 0.42, 0.42, 1)
            for btn in self.option_buttons:
                if btn.text == correct:
                    btn.background_color = (0.35, 0.8, 0.02, 1)
        Clock.schedule_once(lambda dt: self.next_question(), 0.8)
    
    def next_question(self):
        self.q_index += 1
        if self.q_index < 5:
            self.load_question()
        else:
            self.manager.current = 'result'

class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.title_label = Label(text="🎉 QUIZ COMPLETE", font_size=28)
        self.layout.add_widget(self.title_label)
        
        self.score_label = Label(text="", font_size=18)
        self.layout.add_widget(self.score_label)
        
        self.gain_xp_label = Label(text="", font_size=18)
        self.layout.add_widget(self.gain_xp_label)
        
        self.total_xp_label = Label(text="", font_size=18)
        self.layout.add_widget(self.total_xp_label)
        
        self.level_label = Label(text="", font_size=18)
        self.layout.add_widget(self.level_label)
        
        self.back_btn = Button(text="BACK TO LOBBY", font_size=16, background_color=(0.35, 0.8, 0.02, 1), size_hint_y=None, height=50)
        self.back_btn.bind(on_press=self.back_to_lobby)
        self.layout.add_widget(self.back_btn)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        global user_xp
        quiz_screen = self.manager.get_screen('quiz')
        score = quiz_screen.score
        gained_xp = min(score * 10, 100)
        user_xp += gained_xp
        save_user_data({"username": username, "xp": user_xp, "level": calculate_level(user_xp), "last_play_date": str(date.today())})
        current_level = calculate_level(user_xp)
        
        self.score_label.text = f"Score: {score}/5"
        self.gain_xp_label.text = f"XP Gained: +{gained_xp}"
        self.total_xp_label.text = f"Total XP: {user_xp}"
        self.level_label.text = f"Level: {current_level}"
        
        send_score_online(username, score)
        play_result()
        self.manager.get_screen('lobby').update_ui()
        self.manager.get_screen('level').update_buttons()
    
    def back_to_lobby(self, instance):
        play_click()
        self.manager.current = 'lobby'

class LeaderboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.title_label = Label(text="🏆 LEADERBOARD", font_size=24)
        self.layout.add_widget(self.title_label)
        
        self.scroll = ScrollView()
        self.leaderboard_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.leaderboard_layout.bind(minimum_height=self.leaderboard_layout.setter('height'))
        self.scroll.add_widget(self.leaderboard_layout)
        self.layout.add_widget(self.scroll)
        
        self.refresh_btn = Button(text="🔄 Refresh", font_size=14, size_hint_y=None, height=40)
        self.refresh_btn.bind(on_press=self.load_leaderboard)
        self.layout.add_widget(self.refresh_btn)
        
        self.back_btn = Button(text="BACK", font_size=14, size_hint_y=None, height=40)
        self.back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_btn)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.load_leaderboard()
    
    def load_leaderboard(self, instance=None):
        for child in self.leaderboard_layout.children[:]:
            self.leaderboard_layout.remove_widget(child)
        
        loading_label = Label(text="Loading leaderboard...", font_size=16)
        self.leaderboard_layout.add_widget(loading_label)
        
        # Schedule the actual loading after a short delay to show loading
        Clock.schedule_once(lambda dt: self._do_load_leaderboard(loading_label), 0.1)
    
    def _do_load_leaderboard(self, loading_label):
        self.leaderboard_layout.remove_widget(loading_label)
        
        board = fetch_leaderboard()
        if not board:
            error_label = Label(text="⚠️ No internet / server offline", font_size=16, color=(1, 0, 0, 1))
            self.leaderboard_layout.add_widget(error_label)
            return
        
        for i, user in enumerate(board):
            medal = ""
            if i == 0: medal = "🥇 "
            elif i == 1: medal = "🥈 "
            elif i == 2: medal = "🥉 "
            color = (0.35, 0.8, 0.02, 1) if user["username"] == username else (0, 0, 0, 1)
            label = Label(text=f"{medal}{i+1}. {user['username']} — {user['xp']} XP", font_size=16, color=color, size_hint_y=None, height=30)
            self.leaderboard_layout.add_widget(label)
    
    def go_back(self, instance):
        self.manager.current = 'lobby'

class QuizApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(UsernameScreen(name='username'))
        sm.add_widget(LobbyScreen(name='lobby'))
        sm.add_widget(LevelScreen(name='level'))
        sm.add_widget(QuizScreen(name='quiz'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(LeaderboardScreen(name='leaderboard'))
        return sm

if __name__ == '__main__':
    QuizApp().run()
