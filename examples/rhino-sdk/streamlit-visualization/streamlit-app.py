import textwrap
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import rhino_health as rh
from rhino_health import ApiEnvironment
from rhino_health.lib.metrics.basic import Count, StandardDeviation
from typing import Dict, Any, List

from config import (COLOR_PALETTE, MEASURES, RACE_CODES, REGION_MAPPING, 
                   DATASET_EXPORT_YEAR, BIRTH_YEAR_DIVISOR)
from utils import plot_measure_comparison

# Create cache key function
def get_cache_key(dataset_uid, metric_config):
    """Generate a unique cache key for a metric call"""
    return f"{dataset_uid}_{hash(str(metric_config.__dict__))}"

# Cache any SDK calls to avoid redundant API requests
def get_cached_metric(dataset_uid, metric_config):
    """Get metric from cache or calculate and cache it"""
    cache_key = get_cache_key(dataset_uid, metric_config)
    try:
        if cache_key not in st.session_state.metric_cache:
            result = session.dataset.get_dataset_metric([dataset_uid], metric_config).output
            st.session_state.metric_cache[cache_key] = result
        return st.session_state.metric_cache[cache_key]
    except Exception as e:
        st.error(f"Error fetching metric: {str(e)}")
        return None


# Check if user is authenticated
if not st.session_state.get("authenticated", False):
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        try:
            session = rh.login(
                username=username,
                password=password
            )
            if session is not None:
                st.session_state.authenticated = True
                st.session_state.rhino_session = session
                st.rerun()
        except Exception as e:
            st.error("Unable to log in. Please check your credentials and try again.")
            st.session_state.authenticated = False
else:
    def initialize_session():
        """Initialize session state and cache"""
        if 'metric_cache' not in st.session_state:
            st.session_state.metric_cache = {}
        return st.session_state.rhino_session

    def get_hospital_data(session: Any, project_name: str) -> tuple:
        """Get available hospitals data"""
        project = session.project.get_project_by_name(project_name)
        available_hospitals = session.project.get_datasets(project.uid)
        available_names = sorted([d.name for d in available_hospitals])
        return project, available_names

    def display_sidebar(available_hospital_names: List[str]) -> tuple:
        """Display and handle sidebar inputs"""
        st.sidebar.subheader("Compare Hospitals", divider=True)
        hospitals = st.sidebar.multiselect('Select hospitals to compare', 
                                         available_hospital_names,
                                         key='hospital_key')
        measures = st.sidebar.multiselect('Select measures to compare', 
                                        list(MEASURES.keys()),
                                        key='measure_key')
        return hospitals, measures

    session = initialize_session()
    project, available_names = get_hospital_data(session, 'streamlit project')
    comparison_hospitals, selected_measures = display_sidebar(available_names)

    # Get dataset UIDs for selected comparison hospitals only
    hospital_datasets = {}
    for hospital_name in comparison_hospitals:
        dataset = session.project.get_dataset_by_name(hospital_name)
        hospital_datasets[hospital_name] = dataset.uid

    # Update number of hospitals based on selected comparisons
    n_hospitals = len(comparison_hospitals)
    st.sidebar.write(f"Number of Hospitals: {n_hospitals}")

    # Initialize dictionary to store counts for each hospital
    hospital_measure_counts = {hospital: {} for hospital in comparison_hospitals}
    hospital_totals = {hospital: {} for hospital in comparison_hospitals}
    
    # Update the metric calculations to use cache
    for measure_name in selected_measures:
        measure_var = MEASURES.get(measure_name)
        data_filters=[{"filter_column":measure_var, "filter_value":1}]
        incidence_config = Count(variable=measure_var, data_filters=data_filters)
        total_config = Count(variable=measure_var)
        
        for hospital_name, dataset_uid in hospital_datasets.items():
            # Get cached incidence count
            count = get_cached_metric(dataset_uid, incidence_config)['count']
            hospital_measure_counts[hospital_name][measure_name] = count

            # Get cached total count
            total = get_cached_metric(dataset_uid, total_config)['count']
            hospital_totals[hospital_name][measure_name] = total

    tab0, tab1, tab2 = st.tabs(["Total Cases", "Incidence Rate", "Demographics"])
    with tab0:
        if n_hospitals == 0 or not selected_measures:
            st.warning("Please select hospitals and measures to compare.")
        else:
            # Prepare data for plotting
            plot_data = {
                hospital: [counts[measure] for measure in selected_measures]
                for hospital, counts in hospital_measure_counts.items()
            }
            fig = plot_measure_comparison(
                plot_data, 
                selected_measures, 
                n_hospitals,
                "Number of Cases"
            )
            st.pyplot(fig)

    with tab1:
        if n_hospitals == 0 or not selected_measures:
            st.warning("Please select hospitals and measures to compare.")
        else:
            # Prepare data for plotting
            plot_data = {}
            for hospital in hospital_measure_counts:
                values = np.array([hospital_measure_counts[hospital][m] for m in selected_measures])
                totals = np.array([hospital_totals[hospital][m] for m in selected_measures])
                rates = np.divide(values, totals, 
                                out=np.zeros_like(values, dtype=float),
                                where=totals!=0)
                plot_data[hospital] = rates
                
            fig = plot_measure_comparison(
                plot_data, 
                selected_measures, 
                n_hospitals,
                "Incidence Rate",
                is_percentage=True
            )
            st.pyplot(fig)
    with tab2:
        if n_hospitals == 0 or not selected_measures:
            st.warning("Please select hospitals and measures to compare.")
        else:
            for measure_name in selected_measures:
                st.subheader(measure_name)
                measure_var = MEASURES.get(measure_name)
                
                # Create columns for each demographic
                age_col, race_col, state_col = st.columns(3)
                
                with age_col:
                    st.write("**Age Distribution**")
                    for hospital_name, dataset_uid in hospital_datasets.items():
                        # Calculate age statistics
                        data_filters=[{"filter_column":measure_var, "filter_value":1}]
                        age_std = StandardDeviation(
                            variable="BENE_BIRTH_DT", 
                            data_filters=data_filters
                        )
                        
                        std_dev = get_cached_metric(dataset_uid, age_std)
                        
                        mean_age = DATASET_EXPORT_YEAR - std_dev['mean'] / BIRTH_YEAR_DIVISOR
                        st.write(f"{hospital_name}: {mean_age:.1f} ± {std_dev['stddev']/BIRTH_YEAR_DIVISOR:.1f} years")

                with race_col:
                    st.write("**Race Distribution**")
                    
                    for hospital_name, dataset_uid in hospital_datasets.items():
                        st.write(f"{hospital_name}:")
                        data_filters=[
                            {"filter_column":measure_var, "filter_value":1}
                        ]
                        race_count = Count(
                            variable="BENE_RACE_CD", 
                            data_filters=data_filters,
                            group_by={"groupings": ["BENE_RACE_CD"]}
                        )
                        race_counts = get_cached_metric(dataset_uid, race_count)
                        for race, count in race_counts.items():
                            st.write(f"- {RACE_CODES.get(race)}: {count['count']}")

                with state_col:
                    st.write("**Regional Distribution**")
                    for hospital_name, dataset_uid in hospital_datasets.items():
                        st.write(f"{hospital_name}:")
                        data_filters=[{"filter_column":measure_var, "filter_value":1}]
                        state_count = Count(
                            variable="SP_STATE_CODE", 
                            data_filters=data_filters,
                            group_by={"groupings": ["SP_STATE_CODE"]}
                        )
                        state_counts = get_cached_metric(dataset_uid, state_count)
                        
                        # Initialize region counts
                        region_counts = {
                            'Northeast': 0,
                            'Midwest': 0,
                            'South': 0,
                            'West': 0,
                            'Other': 0
                        }
                        
                        # Sum counts by region
                        for state, count in state_counts.items():
                            region = REGION_MAPPING.get(state, 'Other')
                            region_counts[region] += count['count']
                        
                        # Display non-zero region counts
                        for region, count in region_counts.items():
                            if count > 0:
                                st.write(f"- {region}: {count}")
                
                st.divider()