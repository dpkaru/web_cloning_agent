'''import streamlit as st
import agent

st.set_page_config(layout="wide", page_title="Website Cloning Agent")
st.title("🤖 AI Website Cloning Agent")

if "ready" not in st.session_state:
    st.session_state.ready = False

url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("Clone website") and url:
    with st.status("Working...", expanded=True) as status:
        st.write("🔍 Analyzing website...")
        spec = agent.analyze(url)
        with st.expander("Detected design spec"):
            st.json(spec)
        st.write("🛠️ Generating Next.js frontend...")
        ok = agent.generate(spec, log=st.write)
        if "dev" not in st.session_state:
            st.write("🚀 Starting preview server...")
            st.session_state.dev = agent.start_preview()
        st.session_state.ready = True
        status.update(label="Done!", state="complete")

if st.session_state.ready:
    left, right = st.columns([3, 1])
    with right:
        view = st.radio("Preview", ["Desktop", "Mobile"])
        st.subheader("✏️ Modify")
        instruction = st.text_input("e.g. Make the navbar sticky")
        if st.button("Apply") and instruction:
            with st.spinner("Modifying..."):
                agent.modify(instruction, log=st.write)
            st.rerun()
    with left:
        width = 390 if view == "Mobile" else 1200
        st.markdown(
            f'<iframe src="http://localhost:3001" width="{width}" height="800" '
            f'style="border:1px solid #ccc;border-radius:8px"></iframe>',
            unsafe_allow_html=True)'''

import streamlit as st
import agent

st.set_page_config(layout="wide", page_title="Website Cloning Agent")
st.title("🤖 AI Website Cloning Agent")

if "ready" not in st.session_state:
    st.session_state.ready = False

url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("Clone website") and url:
    with st.status("Working...", expanded=True) as status:
        st.write("🔍 Analyzing website...")
        spec = agent.analyze(url)
        with st.expander("Detected design spec"):
            st.json(spec)
        st.write("🛠️ Generating Next.js frontend...")
        ok = agent.generate(spec, log=st.write)
        if "dev" not in st.session_state:
            st.write("🚀 Starting preview server...")
            st.session_state.dev = agent.start_preview()
        st.session_state.ready = True
        status.update(label="Done!", state="complete")

if st.session_state.ready:
    # Use a clean layout split with explicit gap spacing
    left, right = st.columns([3, 1], gap="large")
    
    with right:
        st.write("**Preview Mode**")
        view = st.radio("Preview", ["Desktop", "Mobile"], label_visibility="collapsed")
        st.subheader("✏️ Modify")
        instruction = st.text_input("Modification instruction", placeholder="e.g. Make the navbar sticky", label_visibility="collapsed")
        if st.button("Apply", use_container_width=True) and instruction:
            with st.spinner("Modifying..."):
                agent.modify(instruction, log=st.write)
            st.rerun()
            
    with left:
        # Dynamically set width string: 100% forces it to fit cleanly within the column on desktop
        width_style = "390px" if view == "Mobile" else "100%"
        
        # Wrapped iframe in a responsive block to enforce proper margins and bounds
        st.markdown(
            f'<div style="width: 100%; display: flex; justify-content: flex-start;">'
            f'  <iframe src="http://localhost:3001" width="{width_style}" height="800" '
            f'  style="border:1px solid #ccc; border-radius:8px; width: {width_style}; max-width: 100%;"></iframe>'
            f'</div>',
            unsafe_allow_html=True
        )
