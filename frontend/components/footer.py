import streamlit as st

def create_footer():
    st.markdown("---")
    st.markdown("""
<div style="text-align: center; color: #666 !important;">
    <p><strong>Manimatic</strong> | University of Central Punjab | Fall 2025</p>
    <p>Team: Ali Wahaj, Awais Khan, Suleman Naeem | Advisor: Dr. Ahmad Shabbar Kazmi</p>
</div>
""", unsafe_allow_html=True)