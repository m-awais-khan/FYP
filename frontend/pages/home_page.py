import streamlit as st
from frontend.utils import apply_custom_css
from frontend.components.home_page_cols import create_home_page_cols

# Initialize session state
def initialize_session_state():
    if 'current_status' not in st.session_state:
        st.session_state.current_status = "ready"
    if 'processing_scene_id' not in st.session_state:
        st.session_state.processing_scene_id = None
    if 'generated_scenes' not in st.session_state:
        st.session_state.generated_scenes = []
    if 'generation_history' not in st.session_state:
        st.session_state.generation_history = []
        
def run():
    initialize_session_state()

    # Streamlit page configuration
    st.set_page_config(
        page_title="Manimatic",
        page_icon="🎬",
        layout="wide"
    )
    
    # Header Section with Custom CSS
    apply_custom_css()
    st.markdown('<h1 class="main-header">🎬 Manimatic</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create Educational Animations with Manim using Natural Language</p>', unsafe_allow_html=True)

    # Main Layout
    create_home_page_cols()