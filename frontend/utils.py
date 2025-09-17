import streamlit as st
import os
import time
from backend.services.stitch_videos import video_stitcher

# Custom CSS for better styling
def apply_custom_css():
    st.markdown("""
    <style>
        .main-header {
            text-align: center !important;
            color: #1f77b4 !important;
            font-size: 2.5rem !important;
            font-weight: bold !important;
            margin-bottom: 1rem !important;
        }
    
        .sub-header {
            text-align: center !important;
            color: #666 !important;
            font-size: 1.2rem !important;
            margin-bottom: 2rem !important;
        }
                
        .status-box {
            padding: 1rem !important;
            border-radius: 32px !important;
            margin: 1rem 0 !important;
        }
                
        .status-generating {
            background-color: #fff3cd !important;
            border: 1px solid #ffeaa7 !important;
            color: #856404 !important;
        }
             
    }
</style>
""", unsafe_allow_html=True)
    
def display_video():
    if st.session_state.final_video_path and os.path.exists(st.session_state.final_video_path):
        st.video(st.session_state.final_video_path)
        st.success("🎬 Final stitched video")
    elif any(scene["status"] == "completed" and scene.get("video_path") for scene in st.session_state.generated_scenes):
        # Show the most recent completed scene
        latest_scene = next(
             (scene for scene in reversed(st.session_state.generated_scenes)
            if scene["status"] == "completed" and scene.get("video_path")),
            None
        )
        if latest_scene and os.path.exists(latest_scene["video_path"]):
            st.video(latest_scene["video_path"])
            st.info(f"🎬 Latest Scene: {latest_scene['prompt'][:50]}{'...' if len(latest_scene['prompt']) > 50 else ''}")
        else:
            st.info("🎬 Your generated videos will appear here.")
    else:   
        st.info("🎬 Your generated video will appear here.")

def scene_manager(show_code=False):
    if not st.session_state.generated_scenes:
        return  # No scenes to manage
    st.subheader("🎞️ Generated Scenes")
    with st.expander("View Generated Scenes", expanded=False):
        for idx, scene in enumerate(st.session_state.generated_scenes):
            with st.container():
                col_select, col_info, col_actions = st.columns([0.1, 0.6, 0.3])
                with col_select:
                    if scene["status"] == "completed":
                        key = f"scene_select_{scene['id']}"
                        checked = st.checkbox(f"Scene {scene['id']}", key=key, label_visibility="collapsed")

                        if checked and scene["id"] not in st.session_state.selection_order:
                            # Add when selected
                            st.session_state.selection_order.append(scene["id"])
                        elif not checked and scene["id"] in st.session_state.selection_order:
                            # Remove when deselected
                            st.session_state.selection_order.remove(scene["id"])

                with col_info:
                    if scene["status"] == "completed":
                        status_icon = "✅"
                    elif scene["status"] == "generating":
                        status_icon = "🔄"
                    elif scene["status"] == "error":
                        status_icon = "❌"
                    else:
                        status_icon = "⏳"
                    st.write(f"{status_icon} **Scene {scene['id']}** ({scene['type']})")
                    with st.expander("Show Details"):
                        st.write(f"_{scene['prompt'][:60]}{'...' if len(scene['prompt']) > 60 else ''}_")
                        st.caption(f"{scene['subject']} • {scene['duration']}s • {scene['timestamp']}")
                        if scene["status"] == "error" and scene.get("error"):
                            st.error(f"Error: {scene['error'][:100]}{'...' if len(scene['error']) > 100 else ''}")

                with col_actions:
                    if scene["status"] == "completed" and scene.get("video_path"):
                        key_preview = f"preview_{scene['id']}"
                                
                        # Initialize state if not exists
                        if key_preview not in st.session_state:
                            st.session_state[key_preview] = False
                        
                        # Toggle state when button pressed
                        if st.button("👁️", key=f"btn_{scene['id']}", help="Preview Scene"):
                            st.session_state[key_preview] = not st.session_state[key_preview]
                        
                        # Show video only if state is True
                        if st.session_state[key_preview]:
                            if os.path.exists(scene["video_path"]):
                                st.video(scene["video_path"])

                    if st.button("🗑️", key=f"delete_{scene['id']}", help="Delete Scene"):
                        # Delete video file if exists
                        if scene.get("video_path") and os.path.exists(scene["video_path"]):
                            try:
                                os.remove(scene["video_path"])
                            except Exception as e:
                                st.error(f"Error deleting video: {e}")
                            # Remove from session state
                            st.session_state.generated_scenes.pop(idx)
                            st.success("Scene deleted.")
                            time.sleep(1)
                            st.rerun()

                # Show code if requested
                if show_code and scene.get("code"):
                    with st.expander("Show Generated Code", expanded=False):
                        st.code(scene["code"], language="python")

    # Video stitching section
    completed_selected = [
        sid for sid in st.session_state.selection_order
        if any(s["id"] == sid and s["status"] == "completed"
               for s in st.session_state.generated_scenes)
    ]


    if not len(completed_selected) > 1:
        return  # Need at least 2 scenes to stitch
    st.subheader("🎥 Stitch Selected Scenes")
    st.info(f"Selected {len(completed_selected)} scenes for stitching.")

    # Stitching options
    col_transition, col_order = st.columns(2)

    with col_transition:
        transition_effect = st.selectbox(
            "Transition Effect",
            options=["Fade", "Cut", "Slide", "Zoom"],
        )

    with col_order:
        st.write("**Scene Order:**")
        for scene_id in completed_selected:
            scene = next((s for s in st.session_state.generated_scenes if s["id"] == scene_id), None)
            if scene:
                st.write(f"• Scene {scene_id}: {scene['type']}")

    # Stitch button
    if st.button("🔗 Stitch Selected Scenes", type="primary", use_container_width=True):
        with st.spinner("Stitching scenes..."):
            try:
                # Get video paths
                video_paths = []
                for scene_id in completed_selected:
                    scene = next((s for s in st.session_state.generated_scenes if s["id"] == scene_id), None)
                    if scene and scene.get("video_path") and os.path.exists(scene["video_path"]):
                        video_paths.append(scene["video_path"])

                if not len(video_paths) > 1:
                    st.error("Need at least 2 valid videos to stitch.")
                    return
                output_path = f"generated_videos/final_video_{int(time.time())}.mp4"
                success, error = video_stitcher(video_paths, output_path, transition_effect.lower())

                if not success:
                    st.error(f"❌ Stitching failed: {error}")
                    return
                
                st.session_state.final_video_path = output_path
                st.success("✅ Videos stitched successfully!")
                time.sleep(1)
                st.rerun()

            except Exception as e:
                st.error(f"Error during stitching: {e}")
