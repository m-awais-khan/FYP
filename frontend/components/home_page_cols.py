import streamlit as st
import uuid
from datetime import datetime
from backend.services.llm_response import get_llm_response
from backend.services.clean_code import code_cleaner
from backend.services.manim_processor import execute_manim_code
import os
import time

class HomePageColumns:
    def __init__(self):
        self.col1, self.col2 = None, None
        self.col_gen, self.col_regen = None, None

    def create_columns(self):
        self.col1, self.col2 = st.columns([1, 1.4])
        self.display_left_column()
        self.display_right_column()

    def display_left_column(self):
        with self.col1:
            st.header("📝 Prompt Input")
            
            # Subject Selection
            self.subject = st.selectbox(
                "Select Subject Area",
                ["Mathematics", "Computer Science", "Physics", "General"]
            )

            # Animation type # Later check, animation type -> play func: input
            self.animation_type = st.selectbox(
                "Animation Type",
                ["Visualization", "Explanation", "Proof", "Algorithm Demo", "Graph Plot"]
            )
        
            # Main prompt input
            self.user_prompt = st.text_area(
                "Describe your animation",
                placeholder="Example: Create an animation showing the Pythagorean theorem with a right triangle, highlighting the squares on each side and demonstrating that a² + b² = c²",
                height=100
            )

            # Additional parameters
            with st.expander("⚙️ Advanced Options"):
                self.duration = st.slider("Animation Duration (seconds)", 3, 15, 8)
                self.quality = st.selectbox("Video Quality", ["480p", "720p", "1080p"])
                self.background_color = st.color_picker("Background Color", "#000000")
                self.text_color = st.color_picker("Text Color", "#FFFFFF")
                self.show_code = st.checkbox("Show Generated Code", value=False)

            # Generate buttons
            self.col_gen, self.col_regen = st.columns(2)
            self.display_generate_button()
            self.display_regenerate_button()

            # Generation history
            if st.session_state.generation_history:
                st.header("📚 Recent Prompts")
                for idx, prompt in enumerate(reversed(st.session_state.generation_history[-5:]), start=1):
                    with st.expander(f"Prompt {len(st.session_state.generation_history) - idx + 1}"):
                        st.text(prompt)
                    
    def display_generate_button(self):
        with self.col_gen:
            if st.button("🎬 Generate Scene", type="primary", use_container_width=True,
                         disabled=(st.session_state.current_status == "generating")):
                if self.user_prompt.strip():
                    # Generate unique scene ID
                    scene_id = str(uuid.uuid4())[:8]

                    # Set generating status
                    st.session_state.current_status = "generating"
                    st.session_state.processing_scene_id = scene_id

                    # Add to scenes list
                    scene_data = {
                        "id": scene_id,
                        "prompt": self.user_prompt,
                        "subject": self.subject,
                        "type": self.animation_type,
                        "duration": self.duration,
                        "quality": self.quality,
                        "background_color": self.background_color,
                        "text_color": self.text_color,
                        "status": "generating",
                        "video_path": None,
                        "code": None,
                        "error": None,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    st.session_state.generated_scenes.append(scene_data)
                    st.session_state.generation_history.append(self.user_prompt)
                    st.rerun()
                else:
                    st.error("Please enter a prompt first!")

    def display_regenerate_button(self):
        with self.col_regen:
            if st.button("🔄 Regenerate Last", use_container_width=True,
                         disabled=(st.session_state.current_status == "generating")):
                if st.session_state.generation_history and st.session_state.generated_scenes:
                    # Get last scene and regenerate
                    last_scene = st.session_state.generated_scenes[-1]
                    last_scene["status"] = "generating"
                    st.session_state.current_status = "generating"
                    st.session_state.processing_scene_id = last_scene["id"]
                    st.rerun()

    def display_right_column(self):
        with self.col2:
            st.header("🎥 Video Preview & Management")

            # Handle generation process
            if st.session_state.current_status == "generating" and st.session_state.processing_scene_id:
                current_scene = next(
                    (scene for scene in st.session_state.generated_scenes 
                     if scene["id"] == st.session_state.processing_scene_id),
                     None
                )

                if current_scene:
                    st.markdown("""
                    <div class="status-box status-generating">
                    <strong>🔄 Generating Animation...</strong><br>
                        Converting your prompt to Manim code and rendering the animation.
                    </div>
                    """, unsafe_allow_html=True)

                # Process tracking
                process_container = st.container()

                with process_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Generate code
                    status_text.text("🤖 Generating Manim code...")
                    progress_bar.progress(10)

                    code = get_llm_response(
                        prompt=current_scene["prompt"],
                        subject=current_scene["subject"],
                        animation_type=current_scene["type"],
                        duration=current_scene["duration"],
                        background_color=current_scene["background_color"],
                        text_color=current_scene["text_color"]
                    )

                    if code:
                        progress_bar.progress(50)
                        status_text.text("Code Formatting...")

                        # Removing unnecessary things from code
                        code = code_cleaner(code)

                        current_scene["code"] = code
                        progress_bar.progress(60)
                        status_text.text("🎬 Rendering animation...")

                        # Execute Manim code
                        video_path, error = execute_manim_code(
                            code=code,
                            scene_id=current_scene["id"],
                            quality=current_scene["quality"]
                        )

                        progress_bar.progress(90)
                        
                        if video_path and os.path.exists(video_path):
                            current_scene["video_path"] = video_path
                            current_scene["status"] = "completed"
                            current_scene["error"] = None
                            progress_bar.progress(100)
                            status_text.text("✅ Animation completed!")

                            st.session_state.current_status = "ready"
                            st.session_state.processing_scene_id = None
                            st.success("✅ Animation generated successfully!")

                            time.sleep(1)  # Brief pause before rerun
                            st.rerun()                            

                        else:
                            current_scene["status"] = "error"
                            current_scene["error"] = error or "Unknown error occurred"

                            st.session_state.current_status = "ready"
                            st.session_state.processing_scene_id = None

                            st.error(f"❌ Rendering failed: {current_scene['error']}")
                            
                    else:
                        current_scene["status"] = "error"
                        current_scene["error"] = "Failed to generate code"
                        st.session_state.current_status = "ready"
                        st.session_state.processing_scene_id = None
                        st.error("❌ Failed to generate Manim code")


def create_home_page_cols():
    home_page = HomePageColumns()
    home_page.create_columns()