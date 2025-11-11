"""
Main Streamlit application for Structured Reasoning System.
"""
import streamlit as st
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.api_client import APIClient

# Page configuration
st.set_page_config(
    page_title="Structured Reasoning System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "current_scenario" not in st.session_state:
    st.session_state.current_scenario = None


def show_login_page():
    """Display login/registration page."""
    st.title("🧠 Structured Reasoning System")
    st.markdown("---")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if email and password:
                    try:
                        client = APIClient()
                        result = asyncio.run(client.login(email, password))
                        st.session_state.access_token = result["access_token"]

                        # Get user info
                        client = APIClient(token=st.session_state.access_token)
                        user = asyncio.run(client.get_current_user())
                        st.session_state.user = user

                        st.success("Logged in successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")
                else:
                    st.error("Please enter email and password")

    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            email = st.text_input("Email")
            password = st.text_input("Password (min 8 characters)", type="password")
            password_confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")

            if submit:
                if email and password and password_confirm:
                    if password != password_confirm:
                        st.error("Passwords do not match")
                    elif len(password) < 8:
                        st.error("Password must be at least 8 characters")
                    else:
                        try:
                            client = APIClient()
                            asyncio.run(client.register(email, password))
                            st.success("Registration successful! Please login.")
                        except Exception as e:
                            st.error(f"Registration failed: {str(e)}")
                else:
                    st.error("Please fill in all fields")


def show_main_app():
    """Display main application with navigation."""
    st.title("🧠 Structured Reasoning System")

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")

        if st.session_state.user:
            st.write(f"**User:** {st.session_state.user['email']}")

        st.markdown("---")

        page = st.radio(
            "Select Phase",
            [
                "📝 Scenario Input",
                "🎯 Phase 1: Assumptions",
                "❓ Phase 2: Deep Questions",
                "🔀 Phase 3: Counterfactuals",
                "📊 Phase 5: Strategic Outcomes",
                "📋 My Scenarios"
            ]
        )

        st.markdown("---")

        if st.button("Logout"):
            st.session_state.access_token = None
            st.session_state.user = None
            st.session_state.current_scenario = None
            st.rerun()

    # Display selected page
    if page == "📝 Scenario Input":
        show_scenario_input()
    elif page == "🎯 Phase 1: Assumptions":
        show_phase_1()
    elif page == "❓ Phase 2: Deep Questions":
        show_phase_2()
    elif page == "🔀 Phase 3: Counterfactuals":
        show_phase_3()
    elif page == "📊 Phase 5: Strategic Outcomes":
        show_phase_5()
    elif page == "📋 My Scenarios":
        show_my_scenarios()


def show_scenario_input():
    """Scenario input page."""
    st.header("📝 Scenario Input")
    st.markdown("Enter a complex scenario for structured analysis.")

    with st.form("scenario_form"):
        title = st.text_input("Scenario Title", placeholder="e.g., Geopolitical Crisis Analysis")
        description = st.text_area(
            "Scenario Description",
            placeholder="Provide a detailed description of the scenario you want to analyze...",
            height=300
        )

        submit = st.form_submit_button("Create Scenario")

        if submit:
            if title and description:
                try:
                    client = APIClient(token=st.session_state.access_token)
                    scenario = asyncio.run(client.create_scenario(title, description))
                    st.session_state.current_scenario = scenario
                    st.success(f"Scenario '{title}' created successfully!")
                    st.info("Proceed to Phase 1: Assumptions to begin analysis")
                except Exception as e:
                    st.error(f"Failed to create scenario: {str(e)}")
            else:
                st.error("Please provide both title and description")


def show_phase_1():
    """Phase 1: Surface Analysis page."""
    st.header("🎯 Phase 1: Surface Premise Analysis")

    if not st.session_state.current_scenario:
        st.warning("Please create or select a scenario first")
        return

    scenario = st.session_state.current_scenario
    st.subheader(f"Scenario: {scenario['title']}")
    st.markdown(f"*{scenario['description'][:200]}...*")

    st.markdown("---")

    if st.button("Generate Assumptions", type="primary"):
        with st.spinner("Analyzing scenario and extracting assumptions..."):
            try:
                client = APIClient(token=st.session_state.access_token)
                analysis = asyncio.run(client.create_surface_analysis(scenario['id']))
                st.session_state.surface_analysis = analysis
                st.success("Assumptions extracted successfully!")
            except Exception as e:
                st.error(f"Failed to generate analysis: {str(e)}")

    # Display assumptions if they exist
    if "surface_analysis" in st.session_state:
        analysis = st.session_state.surface_analysis
        st.subheader("Extracted Assumptions")

        for assumption in analysis.get("assumptions", []):
            with st.expander(f"**{assumption['category'].title()}**: {assumption['text'][:80]}..."):
                st.markdown(f"**Full Text:** {assumption['text']}")
                st.markdown(f"**Category:** {assumption['category']}")
                st.markdown(f"**Confidence:** {assumption['confidence']:.2f}")

        if analysis.get("baseline_narrative"):
            st.subheader("Baseline Narrative")
            st.markdown(analysis["baseline_narrative"])

        st.info("Proceed to Phase 2 to challenge these assumptions")


def show_phase_2():
    """Phase 2: Deep Questions page."""
    st.header("❓ Phase 2: Deep Questioning")

    if not st.session_state.current_scenario:
        st.warning("Please create a scenario and complete Phase 1 first")
        return

    scenario = st.session_state.current_scenario

    if st.button("Generate Probing Questions", type="primary"):
        with st.spinner("Generating interrogative questions..."):
            try:
                client = APIClient(token=st.session_state.access_token)
                questions = asyncio.run(client.generate_deep_questions(scenario['id']))
                st.session_state.deep_questions = questions
                st.success(f"Generated {len(questions)} probing questions!")
            except Exception as e:
                st.error(f"Failed to generate questions: {str(e)}")

    # Display questions if they exist
    if "deep_questions" in st.session_state:
        questions = st.session_state.deep_questions

        # Group by dimension
        dimensions = {}
        for q in questions:
            dim = q['dimension']
            if dim not in dimensions:
                dimensions[dim] = []
            dimensions[dim].append(q)

        for dim, dim_questions in dimensions.items():
            st.subheader(f"{dim.title()} Questions")
            for q in dim_questions:
                st.markdown(f"**Q:** {q['question_text']}")
                st.markdown("---")

        st.info("Proceed to Phase 3 to generate counterfactual scenarios")


def show_phase_3():
    """Phase 3: Counterfactuals page."""
    st.header("🔀 Phase 3: Counterfactual Generation")

    if not st.session_state.current_scenario:
        st.warning("Please create a scenario and complete previous phases first")
        return

    scenario = st.session_state.current_scenario

    if st.button("Generate Counterfactuals", type="primary"):
        with st.spinner("Generating counterfactual scenarios across six strategic axes..."):
            try:
                client = APIClient(token=st.session_state.access_token)
                counterfactuals = asyncio.run(client.generate_counterfactuals(scenario['id']))
                st.session_state.counterfactuals = counterfactuals
                st.success(f"Generated {len(counterfactuals)} counterfactual scenarios!")
            except Exception as e:
                st.error(f"Failed to generate counterfactuals: {str(e)}")

    # Display counterfactuals if they exist
    if "counterfactuals" in st.session_state:
        counterfactuals = st.session_state.counterfactuals

        # Group by axis
        axes = {}
        for cf in counterfactuals:
            axis = cf['axis']
            if axis not in axes:
                axes[axis] = []
            axes[axis].append(cf)

        for axis, axis_cfs in axes.items():
            st.subheader(f"Axis: {axis.replace('_', ' ').title()}")
            for cf in axis_cfs:
                with st.expander(f"Breach: {cf['breach_condition'][:80]}..."):
                    st.markdown(f"**Breach Condition:** {cf['breach_condition']}")
                    st.markdown(f"**Severity:** {cf.get('severity_rating', 'N/A')}/10")
                    st.markdown(f"**Probability:** {cf.get('probability_rating', 'N/A')}")
                    st.markdown("**Consequences:**")
                    for cons in cf.get('consequences', []):
                        st.markdown(f"- {cons}")

        st.info("Proceed to Phase 5 to project strategic outcomes")


def show_phase_5():
    """Phase 5: Strategic Outcomes page."""
    st.header("📊 Phase 5: Strategic Outcomes")

    if not st.session_state.current_scenario:
        st.warning("Please create a scenario and complete previous phases first")
        return

    if "counterfactuals" not in st.session_state:
        st.warning("Please generate counterfactuals in Phase 3 first")
        return

    st.markdown("Select a counterfactual to project its strategic outcome trajectory")

    counterfactuals = st.session_state.counterfactuals
    cf_options = {f"{cf['axis']}: {cf['breach_condition'][:50]}...": cf for cf in counterfactuals}

    selected = st.selectbox("Select Counterfactual", list(cf_options.keys()))

    if selected:
        cf = cf_options[selected]

        if st.button("Generate Strategic Outcome", type="primary"):
            with st.spinner("Projecting strategic outcome trajectory..."):
                try:
                    client = APIClient(token=st.session_state.access_token)
                    outcome = asyncio.run(client.generate_strategic_outcome(cf['id']))
                    st.session_state.current_outcome = outcome
                    st.success("Strategic outcome generated!")
                except Exception as e:
                    st.error(f"Failed to generate outcome: {str(e)}")

        # Display outcome if exists
        if "current_outcome" in st.session_state:
            outcome = st.session_state.current_outcome

            st.subheader("Trajectory Timeline")
            trajectory = outcome.get("trajectory", {})
            for timepoint, data in trajectory.items():
                st.markdown(f"**{timepoint}**")
                st.markdown(data.get("status", ""))
                if "events" in data:
                    for event in data["events"]:
                        st.markdown(f"- {event}")
                st.markdown("---")

            if outcome.get("decision_points"):
                st.subheader("Critical Decision Points")
                for dp in outcome["decision_points"]:
                    st.markdown(f"**{dp.get('time')}**: {dp.get('description')}")

            if outcome.get("confidence_intervals"):
                st.subheader("Confidence Intervals")
                st.bar_chart(outcome["confidence_intervals"])


def show_my_scenarios():
    """My Scenarios page."""
    st.header("📋 My Scenarios")

    try:
        client = APIClient(token=st.session_state.access_token)
        scenarios = asyncio.run(client.list_scenarios())

        if scenarios:
            for scenario in scenarios:
                with st.expander(f"**{scenario['title']}**"):
                    st.markdown(f"**Created:** {scenario['created_at']}")
                    st.markdown(f"**Description:** {scenario['description'][:200]}...")
                    if st.button(f"Load", key=f"load_{scenario['id']}"):
                        st.session_state.current_scenario = scenario
                        st.success("Scenario loaded!")
                        st.rerun()
        else:
            st.info("No scenarios yet. Create one to get started!")

    except Exception as e:
        st.error(f"Failed to load scenarios: {str(e)}")


# Main app logic
if st.session_state.access_token:
    show_main_app()
else:
    show_login_page()
