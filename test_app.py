import streamlit as st
import sys
import os

st.write("Testing component import...")

# Add the circle_diagram_component to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'circle_diagram_component'))

try:
    from circle_diagram_component import circle_diagram
    st.write("✅ Component imported successfully!")
    
    st.write("Attempting to render component...")
    result = circle_diagram(key="test")
    
    if result:
        st.write("Component returned data:", result)
    else:
        st.write("Component loaded but no data yet (click the diagram)")
        
except Exception as e:
    st.error(f"❌ Error: {e}")
    import traceback
    st.code(traceback.format_exc())