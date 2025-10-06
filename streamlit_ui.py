import json
import streamlit as st
from OpenAI_Medical_Expert import get_differential_diagnoses, get_followup_response
import plotly.express as px

# function to display the analysis results
def display_analysis(data):
    # display each differential diagnosis
    for i,d in enumerate(data["differentials"], start=1):
        st.markdown(f"""
        ### {i}. {d["diagnosis"]}\n
        **Probability:** {d["probability_percent"]}%\n
        **Rationale:** {d["rationale"]}
        """)

    st.markdown("---")
    st.markdown(f"**⚠️ Red Flags:** {data['red_flags']}")
    st.caption(data["disclaimer"])

# CSS styling
st.markdown("""
    <style>
    h1 {
        text-align: center;
        color: #1ee61e !important;
    }
    """, unsafe_allow_html=True)

# title and page config
st.set_page_config(page_title="Medical Assistant", page_icon="🧬", layout="centered")

st.title("🧬 Medical Assistant - Differential Diagnoses")

st.caption("For educational purposes only. Not a substitute for professional medical advice.")

# initialize session state for conversation history
for key in ["user_history", "chat_history", "current_analysis"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ["user_history", "chat_history"] else None


user_symptoms = st.text_area("Please enter the patient's symptoms along with any relevant context. Press CTRL+ENTER to submit", placeholder="e.g., fever, cough, shortness of breath")

# default empty context
context = {"age": None, "sex": None, "duration": None, "onset": None, "fever": None, "pregnancy": None, "comorbidities": None, "medications": None, "allergies": None, "smoking": None, "travel": None, "noticed": None}

# expandable form for additional context
with st.expander("Additional Clinical Context (Optional)"):
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120)
        sex = st.selectbox("Sex", ["", "Male", "Female", "Other", "Prefer not to say"])
        duration = st.text_input("Symptom duration")
        onset = st.selectbox("Onset", ["", "Sudden", "Gradual"])
    with col2:
        fever = st.selectbox("Fever", ["", "Yes", "No", "Unknown"])
        pregnancy = st.selectbox("Pregnancy status", ["", "Pregnant", "Not pregnant", "Unknown"])
        comorbid = st.text_input("Previous illnesses or comorbidities")
        meds = st.text_input("Current medications")
    with col3:
        allergies = st.text_input("Allergies")
        smoking = st.selectbox("Smoking status", ["", "Never", "Former", "Current"])
        travel = st.text_input("Recent travel or exposure")
        noticed = st.text_input("When did you notice symptoms")

# update context with provided values, keeping None for empty inputs
context.update({
    "age": age if age != 0 else None,
    "sex": sex if sex else None,
    "duration": duration if duration else None,
    "onset": onset if onset else None,
    "fever": fever if fever else None,
    "pregnancy": pregnancy if pregnancy else None,
    "comorbidities": comorbid if comorbid else None,
    "medications": meds if meds else None,
    "allergies": allergies if allergies else None,
    "smoking": smoking if smoking else None,
    "travel": travel if travel else None,
    "noticed": noticed if noticed else None
})

# button to submit and get differential diagnoses
if user_symptoms and st.button("Get Differential Diagnoses"):
    with st.spinner("⏳ Analyzing symptoms..."):
        response = get_differential_diagnoses(user_symptoms, context=context)
        if response:
            data = json.loads(response)
            st.session_state.current_analysis = data

            # resetting chat history
            st.session_state.chat_history = []
            
            session_record = {
                "symptoms": user_symptoms,
                "context": context,
                "response": data
            }
            st.session_state.user_history.append(session_record)

# Display analysis if it exists
if st.session_state.current_analysis:
    data = st.session_state.current_analysis
    
    try:
        # Plot bar chart
        fig = px.bar(
            x=[d["diagnosis"] for d in data["differentials"]],
            y=[d["probability_percent"] for d in data["differentials"]],
            labels={"x": "Diagnosis", "y": "Probability (%)"},
            range_y=[0, 100],
            title="Differential Diagnoses Probability Distribution"
        )
        
        fig.update_layout(
            xaxis={
                'tickangle': 0,
                'tickmode': 'array',
                'ticktext': [d["diagnosis"].replace(" ", "<br>", 2) for d in data["differentials"]],
                'tickvals': list(range(len(data["differentials"]))),
                'tickfont': {'size': 10},
                'showticklabels': True
            },
            margin=dict(b=70),
            bargap=0.3,
        )
        
        st.markdown("##### ✅ Here's your analysis:")
        st.plotly_chart(fig, use_container_width=True)
        display_analysis(data)

        # Follow-up section
        st.markdown("---")
        st.markdown("**Any further questions regarding the analysis?**")
        
        # Display chat history
        for chat in st.session_state.chat_history:
            # st.markdown("---")
            st.markdown(f"##### You: {chat['q']}")
            st.markdown(f"##### {chat['a']}")

        st.markdown("---")

        # Display the suggested clarifying questions after the first analysis
        if "clarifying_questions" in data and data["clarifying_questions"] and len(st.session_state.chat_history) == 0:
            st.markdown("**Suggested questions:**")
            for i, q in enumerate(data["clarifying_questions"]):
                if st.button(q, key=f"suggested_q_{i}"):
                    followup_response = get_followup_response(q, history=st.session_state.user_history, chat_context=st.session_state.chat_history)
                    st.session_state.chat_history.append({"q": q, "a": followup_response})
                    st.rerun()      
        
        # Follow-up input
        followup_query = st.text_input("💬 Ask a follow-up question", key="chat_input")
        if followup_query and st.button("Generate Response", key="followup_button"):
            with st.spinner("Thinking..."):
                followup_response = get_followup_response(followup_query, history = st.session_state.user_history, chat_context = st.session_state.chat_history)
                st.session_state.chat_history.append({"q": followup_query, "a": followup_response})
                st.rerun()
    except Exception as e:
        st.markdown("**⚠️ Error displaying results. Make sure you are entering the symptoms correctly.**")

                            

            
