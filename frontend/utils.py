import streamlit as st

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