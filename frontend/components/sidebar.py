import streamlit as st
from datetime import datetime
import json
import os
import shutil
from config import OUTPUT_DIR
import time

def create_sidebar():
    with st.sidebar:
        st.header("ℹ️ Project Information")
        st.info("""
**AI-Powered Video Generation Platform**    
Using Manim library to create educational animations from natural language prompts.
    
**Supported Subjects:**
• Mathematics
• Computer Science  
• Physics
• General concepts
""")
        
        st.header("📊 Session Statistics")
        completed_scenes = len([s for s in st.session_state.generated_scenes if s['status'] == 'completed'])
        error_scenes = len([s for s in st.session_state.generated_scenes if s['status'] == 'error'])

        st.metric("Total Scenes", len(st.session_state.generated_scenes))
        st.metric("Completed Scenes", completed_scenes)
        st.metric("Failed Scenes", error_scenes)
        st.metric("Total Prompts" , len(st.session_state.generation_history))

        # Export options
        st.header("💾 Export Options")
        if st.session_state.final_video_path and os.path.exists(st.session_state.final_video_path):
            with open(st.session_state.final_video_path, "rb") as f:
                st.download_button(
                    label="📥 Download Final Video",
                    data=f.read(),
                    file_name="generative_manim_video.mp4",
                    mime="video/mp4"
                )

        if st.session_state.generated_scenes:
            # Export scene data as JSON
            scene_data = {
                "scenes": st.session_state.generated_scenes,
                "export_time": datetime.now().isoformat(),
                "total_scenes": len(st.session_state.generated_scenes)
            }

            scene_json = json.dumps(scene_data, indent=2)
            st.download_button(
                label="📄 Export Scene Data",
                data=scene_json,
                file_name=f"scene_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        # Clear all data
        st.header("🗑️ Reset")
        if st.button("Clear All Data", type="secondary"):
            # Clean up video files
            shutil.rmtree(OUTPUT_DIR)

            # Reset session state
            st.session_state.current_status = "ready"
            st.session_state.processing_scene_id = None
            st.session_state.generated_scenes = []
            st.session_state.generation_history = []
            st.session_state.final_video_path = None
            st.session_state.selection_order = []

            st.success("✅ All data cleared!")
            time.sleep(1)
            st.rerun()