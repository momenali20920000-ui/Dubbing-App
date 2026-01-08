import os
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
from kivy.core.window import Window
import requests
import threading
from plyer import filechooser

# 🎨 تصميم عصري (Dark Mode الاحترافي)
Window.clearcolor = (0.05, 0.05, 0.05, 1)

# تسجيل الخط العربي (تأكد من وجود ملف font.ttf بجانب الكود)
try:
    LabelBase.register(name='default', fn_regular='font.ttf')
except:
    pass

class DubbingApp(App):
    def build(self):
        # التنسيق العام
        self.layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        # 1. العنوان الرئيسي
        title = Label(
            text="PRO STUDIO TRANSLATOR", 
            font_size='26sp', 
            color=(0, 0.8, 1, 1), # لون سماوي احترافي
            bold=True,
            size_hint=(1, 0.08)
        )
        self.layout.add_widget(title)
        
        # 2. إدخال السيرفر
        lbl_server = Label(text="Server Link:", color=(0.7, 0.7, 0.7, 1), size_hint=(1, 0.04), halign='left', text_size=(Window.width-50, None))
        self.layout.add_widget(lbl_server)
        
        self.url_input = TextInput(
            hint_text="Paste Server URL here...", 
            multiline=False, 
            size_hint=(1, 0.08),
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[10, 15] # توسيط النص
        )
        self.layout.add_widget(self.url_input)

        # 3. كود التفعيل
        lbl_token = Label(text="Access Token:", color=(0.7, 0.7, 0.7, 1), size_hint=(1, 0.04), halign='left', text_size=(Window.width-50, None))
        self.layout.add_widget(lbl_token)
        
        self.token_input = TextInput(
            text="ADMIN_123", 
            multiline=False, 
            size_hint=(1, 0.08),
            password=True,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[10, 15]
        )
        self.layout.add_widget(self.token_input)
        
        # 4. 📞 معلومات الاتصال (طلبك الأول)
        contact_info = Label(
            text="للحصول على كود التفعيل: 01272666715",
            font_name='font.ttf',
            color=(0, 1, 0.5, 1), # لون أخضر مميز
            font_size='16sp',
            size_hint=(1, 0.05)
        )
        self.layout.add_widget(contact_info)
        
        # 5. زر اختيار الفيديو (تصميم مسطح Flat Design)
        self.btn_select = Button(
            text="Select Video File / اختر الفيديو",
            font_name='font.ttf',
            font_size='18sp',
            size_hint=(1, 0.12),
            background_normal='',
            background_color=(0, 0.4, 0.8, 1), # أزرق غامق
            color=(1, 1, 1, 1)
        )
        self.btn_select.bind(on_press=self.select_file)
        self.layout.add_widget(self.btn_select)
        
        # 6. شاشة اللوج (Log)
        self.status_label = Label(
            text="Ready...", 
            font_name='font.ttf',
            font_size='14sp', 
            size_hint=(1, None),
            height=300,
            valign='top'
        )
        scroll = ScrollView(size_hint=(1, 0.3), do_scroll_x=False)
        scroll.add_widget(self.status_label)
        
        # خلفية بسيطة للوج
        log_bg = BoxLayout(size_hint=(1, 0.35))
        log_bg.add_widget(scroll)
        self.layout.add_widget(log_bg)
        
        # 7. ✒️ التوقيع (طلبك الثاني)
        footer = Label(
            text="Design by Momen Ali",
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            italic=True,
            size_hint=(1, 0.05)
        )
        self.layout.add_widget(footer)
        
        return self.layout

    def select_file(self, instance):
        if not self.url_input.text.strip():
            self.status_label.text = "⚠️ Please enter Server URL first!"
            return

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            
        filechooser.open_file(on_selection=self.start_thread)

    def start_thread(self, selection):
        if selection:
            threading.Thread(target=self.process_video, args=(selection,)).start()

    def process_video(self, selection):
        try:
            video_path = selection[0]
            server_url = self.url_input.text.strip().rstrip('/')
            token = self.token_input.text.strip()
            
            self.update_status(f"Processing: {os.path.basename(video_path)}")
            
            # القص
            self.update_status("✂️ Extracting Audio...")
            audio_path = os.path.join(os.path.dirname(video_path), "temp_audio.mp3")
            
            try:
                import ffmpeg
                (
                    ffmpeg
                    .input(video_path)
                    .output(audio_path, acodec='libmp3lame', q=4, vn=None, loglevel="quiet")
                    .run(overwrite_output=True)
                )
            except Exception as e:
                self.update_status(f"Error (FFmpeg): {e}")
                return

            # الإرسال
            self.update_status("☁️ Uploading & Translating...")
            try:
                with open(audio_path, 'rb') as f:
                    files = {'file': f}
                    data = {'token': token}
                    response = requests.post(f"{server_url}/translate", files=files, data=data, timeout=600)
                    
                if response.status_code == 200:
                    srt_content = response.text
                    self.save_and_merge(video_path, srt_content)
                else:
                    self.update_status(f"Server Error: {response.status_code}")
            except Exception as e:
                self.update_status("Connection Failed. Check URL.")

        except Exception as e:
            self.update_status(f"Error: {e}")

    def save_and_merge(self, video_path, srt_content):
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            self.update_status("📝 Processing Arabic Text...")
            srt_path = os.path.join(os.path.dirname(video_path), "subs.srt")
            
            fixed_lines = []
            for line in srt_content.splitlines():
                if "-->" in line or line.isdigit() or not line.strip():
                    fixed_lines.append(line)
                else:
                    try:
                        reshaped = arabic_reshaper.reshape(line)
                        bidi_text = get_display(reshaped)
                        fixed_lines.append(bidi_text)
                    except:
                        fixed_lines.append(line)
                        
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(fixed_lines))
                
            self.update_status("🎬 Rendering Final Video...")
            output_video = os.path.join(os.path.dirname(video_path), f"Momen_{os.path.basename(video_path)}")
            
            import ffmpeg
            style = "Fontsize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=50"
            (
                ffmpeg
                .input(video_path)
                .output(output_video, vf=f"subtitles={srt_path}:force_style='{style}'", loglevel="quiet")
                .run(overwrite_output=True)
            )
            self.update_status(f"✅ DONE! Saved as:\nMomen_{os.path.basename(video_path)}")
            
            if os.path.exists(audio_path): os.remove(audio_path)
            if os.path.exists(srt_path): os.remove(srt_path)

        except Exception as e:
             self.update_status(f"Merge Error: {e}")

    def update_status(self, text):
        self.status_label.text = text

if __name__ == '__main__':
    DubbingApp().run()
