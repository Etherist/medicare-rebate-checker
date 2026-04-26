"""
Streamlit Web Application for Medicare Rebate Eligibility Checker.
Provides an interactive web interface for checking rebates.
"""
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import streamlit as st
import pandas as pd

from agents.mbs_fetcher import MBSDataFetcher
from agents.validator import EligibilityValidator
from agents.calculator import RebateCalculator
from agents.reporter import ReportGenerator


# Page configuration
st.set_page_config(
    page_title="Medicare Rebate Checker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize agents
@st.cache_resource
def get_agents():
    """Initialize and cache agent instances."""
    return {
        'fetcher': MBSDataFetcher(),
        'validator': EligibilityValidator(),
        'calculator': RebateCalculator(),
        'reporter': ReportGenerator()
    }

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Medicare Rebate Eligibility Checker</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">AI-Powered Agent System for Australian Healthcare</p>', unsafe_allow_html=True)
    
    # Sidebar for navigation and info
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This tool uses **4 autonomous agents** to:
        1. 📦 Fetch MBS item data
        2. ✅ Validate eligibility
        3. 💰 Calculate rebates
        4. 📄 Generate reports
        """)
        
        st.header("📋 MBS Items Available")
        agents = get_agents()
        fetcher = agents['fetcher']
        
        # Get category counts
        all_items = fetcher.get_all_items()
        if all_items:
            df = pd.DataFrame(all_items)
            if 'category' in df.columns:
                category_counts = df['category'].value_counts()
                st.bar_chart(category_counts)
        
        st.header("🔗 Quick Links")
        st.markdown("""
        - [FastAPI Docs](/docs)
        - [GitHub Repository](https://github.com)
        - [MBS Online](https://www.mbsonline.gov.au)
        """)
    
    # Main content area - Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Check Rebate", "📊 Browse MBS Items", "📈 Statistics"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Check Rebate Eligibility</h2>', unsafe_allow_html=True)
        
        # Input form
        with st.form("rebate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                mbs_item = st.text_input(
                    "MBS Item Number",
                    value="13200",
                    help="Enter the MBS item number (e.g., 13200, 23)"
                )
                age = st.number_input(
                    "Patient Age",
                    min_value=0,
                    max_value=150,
                    value=35,
                    help="Patient age in years"
                )
                has_medicare = st.checkbox(
                    "Has Valid Medicare Card",
                    value=True,
                    help="Patient possesses a valid Medicare card"
                )
            
            with col2:
                concession = st.checkbox(
                    "Concession Status",
                    value=False,
                    help="Patient holds a concession card (e.g., pensioner)"
                )
                hospital = st.checkbox(
                    "Hospital Patient",
                    value=False,
                    help="Patient is currently admitted to hospital"
                )
                output_format = st.selectbox(
                    "Report Format",
                    options=["markdown", "json"],
                    index=0
                )
            
            submitted = st.form_submit_button("🔍 Check Rebate", type="primary", use_container_width=True)
        
        if submitted:
            with st.spinner("Processing..."):
                try:
                    agents = get_agents()
                    fetcher = agents['fetcher']
                    validator = agents['validator']
                    calculator = agents['calculator']
                    reporter = agents['reporter']
                    
                    # Fetch item details
                    mbs_details = fetcher.get_item_details(mbs_item)
                    if not mbs_details:
                        st.error(f"MBS item '{mbs_item}' not found. Please check the item number.")
                    else:
                        # Validate eligibility
                        is_eligible, reason = validator.validate_eligibility(
                            mbs_item=mbs_item,
                            age=age,
                            has_medicare_card=has_medicare,
                            concession_status=concession,
                            hospital_status=hospital
                        )
                        
                        # Calculate rebate
                        if is_eligible:
                            rebate_amount = calculator.calculate_rebate(
                                schedule_fee=mbs_details['schedule_fee'],
                                medicare_benefit_percentage=mbs_details.get('medicare_benefit_percentage', 85.0)
                            )
                        else:
                            rebate_amount = 0.0
                            
                        gap_fee = calculator.calculate_gap_fee(
                            schedule_fee=mbs_details['schedule_fee'],
                            rebate_amount=rebate_amount
                        )
                        
                        # Display results
                        col_left, col_right = st.columns(2)
                        
                        with col_left:
                            st.markdown('<div class="info-box">', unsafe_allow_html=True)
                            st.markdown(f"**MBS Item:** {mbs_item}")
                            st.markdown(f"**Description:** {mbs_details['description']}")
                            st.markdown(f"**Schedule Fee:** ${mbs_details['schedule_fee']:.2f}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col_right:
                            if is_eligible:
                                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                                st.markdown("✅ **Eligible for Rebate**")
                            else:
                                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                                st.markdown("❌ **Not Eligible**")
                            
                            st.markdown(f"**Reason:** {reason}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Financial summary
                        st.markdown("### 💰 Financial Summary")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Schedule Fee", f"${mbs_details['schedule_fee']:.2f}")
                        with col2:
                            st.metric("Rebate Amount", f"${rebate_amount:.2f}")
                        with col3:
                            st.metric("Gap Fee", f"${gap_fee:.2f}")
                        
                        # Generate and offer report download
                        report_data = {
                            'mbs_item': mbs_item,
                            'description': mbs_details['description'],
                            'schedule_fee': mbs_details['schedule_fee'],
                            'rebate_amount': rebate_amount,
                            'gap_fee': gap_fee,
                            'eligible': is_eligible,
                            'reason': reason,
                            'patient_age': age,
                            'has_medicare_card': has_medicare,
                            'concession_status': concession,
                            'hospital_status': hospital,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"rebate_{mbs_item}_{timestamp}.{output_format}"
                        report_path = reporter.generate_report(
                            report_data,
                            format=output_format,
                            output_path=f"reports/{filename}"
                        )
                        
                        with open(report_path, 'r') as f:
                            report_content = f.read()
                        
                        st.download_button(
                            label=f"📥 Download {output_format.upper()} Report",
                            data=report_content,
                            file_name=filename,
                            mime="text/plain" if output_format == 'markdown' else "application/json"
                        )
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    with tab2:
        st.markdown('<h2 class="sub-header">Browse MBS Items</h2>', unsafe_allow_html=True)
        
        agents = get_agents()
        fetcher = agents['fetcher']
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        with col1:
            search_term = st.text_input("Search items", placeholder="Search by description...")
        with col2:
            all_items = fetcher.get_all_items()
            if all_items:
                df = pd.DataFrame(all_items)
                categories = ['All'] + sorted(df['category'].unique().tolist())
                selected_category = st.selectbox("Filter by category", categories)
        
        # Get filtered items
        if search_term:
            items = fetcher.search_items_by_description(search_term)
        elif selected_category and selected_category != 'All':
            items = fetcher.get_items_by_category(selected_category)
        else:
            items = all_items
        
        # Display items in a table
        if items:
            df = pd.DataFrame(items)
            display_columns = ['item_number', 'description', 'schedule_fee', 'category']
            available_columns = [col for col in display_columns if col in df.columns]
            st.dataframe(
                df[available_columns],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No MBS items found matching your criteria.")
    
    with tab3:
        st.markdown('<h2 class="sub-header">System Statistics</h2>', unsafe_allow_html=True)
        
        agents = get_agents()
        fetcher = agents['fetcher']
        
        all_items = fetcher.get_all_items()
        if all_items:
            df = pd.DataFrame(all_items)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total MBS Items", len(df))
            with col2:
                if 'category' in df.columns:
                    st.metric("Categories", df['category'].nunique())
            with col3:
                if 'schedule_fee' in df.columns:
                    avg_fee = df['schedule_fee'].mean()
                    st.metric("Avg Schedule Fee", f"${avg_fee:.2f}")
            
            # Category distribution chart
            if 'category' in df.columns:
                st.markdown("### Category Distribution")
                cat_counts = df['category'].value_counts()
                st.bar_chart(cat_counts)
            
            # Fee distribution
            if 'schedule_fee' in df.columns:
                st.markdown("### Schedule Fee Distribution")
                st.histogram(df['schedule_fee'], bins=20)
        else:
            st.info("No data available for statistics.")


if __name__ == '__main__':
    main()