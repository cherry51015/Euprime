"""
Lead Generation Web Agent - Streamlit App
==========================================
Deployed demo for EuPrime Application
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Lead Generation Agent | 3D In-Vitro Models",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main background - gradient */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metric cards - add spacing between them */
    [data-testid="stMetricLabel"] {
        color: #1f1f1f !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #0066cc !important;
        font-weight: 700 !important;
        font-size: 28px !important;
    }
    
    
    [data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 5px;
    }
    
    
    h1 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    h2 {
        color: white !important;
        font-size: 28px !important;
        margin-top: 30px !important;
        margin-bottom: 20px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    h3 {
        color: white !important;
        font-size: 20px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #2d3748;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    
    [data-testid="column"] {
        padding: 0 10px;
    }
    
    /* Expander styling */
    [data-testid="stExpander"] {
        background-color: white;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
            /* FIX: Expander content text color on white background */
[data-testid="stExpander"] * {
    color: #1f1f1f !important;
}

[data-testid="stExpander"] summary {
    color: #1f1f1f !important;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)



class LeadScorer:
    """Calculate propensity-to-buy scores."""
    
    @staticmethod
    def score_role(title: str) -> int:
        title_lower = title.lower()
        if any(word in title_lower for word in ['director', 'head', 'vp', 'chief']):
            return 30
        elif 'senior' in title_lower or 'principal' in title_lower:
            return 20
        elif 'manager' in title_lower or 'lead' in title_lower:
            return 15
        return 10
    
    @staticmethod
    def score_funding(funding: str) -> int:
        funding_lower = funding.lower()
        if 'series b' in funding_lower or 'series c' in funding_lower:
            return 20
        elif 'ipo' in funding_lower or 'public' in funding_lower:
            return 15
        elif 'series a' in funding_lower:
            return 10
        return 5
    
    @staticmethod
    def score_technographic(title: str) -> int:
        keywords = ['toxicology', 'safety', 'dmpk', 'hepatic', 'liver', 'vitro']
        title_lower = title.lower()
        return 15 if any(k in title_lower for k in keywords) else 5
    
    @staticmethod
    def score_location(location: str, hq: str) -> int:
        hubs = ['boston', 'cambridge', 'san francisco', 'bay area', 'basel', 'oxford']
        combined = f"{location} {hq}".lower()
        return 10 if any(hub in combined for hub in hubs) else 0
    
    @staticmethod
    def score_scientific(has_publication: bool) -> int:
        return 40 if has_publication else 0
    
    @classmethod
    def calculate_total_score(cls, lead: dict) -> int:
        score = 0
        score += cls.score_role(lead['title'])
        score += cls.score_funding(lead['funding_stage'])
        score += cls.score_technographic(lead['title'])
        score += cls.score_location(lead['location'], lead['company_hq'])
        score += cls.score_scientific(lead['recent_publication'])
        return min(100, max(0, score))


def generate_sample_leads(num_leads: int = 50) -> pd.DataFrame:
    """Generating sample lead data for demonstration."""
    
    titles = [
        'Director of Toxicology', 'Head of Preclinical Safety', 'VP Safety Assessment',
        'Director of Drug Safety', 'Principal Scientist Toxicology', 'Senior Director DMPK',
        'Head of In Vitro Pharmacology', 'Director of Translational Medicine',
        'Associate Director Safety Assessment', 'Manager Preclinical Development'
    ]
    
    companies = [
        {'name': 'Moderna Therapeutics', 'hq': 'Cambridge, MA', 'funding': 'Series C', 'hub': True},
        {'name': 'Genentech', 'hq': 'South San Francisco, CA', 'funding': 'Acquired (Roche)', 'hub': True},
        {'name': 'Vertex Pharmaceuticals', 'hq': 'Boston, MA', 'funding': 'Public (IPO)', 'hub': True},
        {'name': 'BioMarin Pharmaceutical', 'hq': 'San Rafael, CA', 'funding': 'Public', 'hub': True},
        {'name': 'Alnylam Pharmaceuticals', 'hq': 'Cambridge, MA', 'funding': 'Series B', 'hub': True},
        {'name': 'Regeneron', 'hq': 'Tarrytown, NY', 'funding': 'Public', 'hub': False},
        {'name': 'Sage Therapeutics', 'hq': 'Cambridge, MA', 'funding': 'Series C', 'hub': True},
        {'name': 'Denali Therapeutics', 'hq': 'South San Francisco, CA', 'funding': 'Series B', 'hub': True},
    ]
    
    locations = [
        'Cambridge, MA', 'Remote - Colorado', 'Boston, MA', 'South San Francisco, CA',
        'San Diego, CA', 'Remote - Texas', 'New York, NY', 'Basel, Switzerland',
        'Remote - North Carolina', 'San Rafael, CA'
    ]
    
    first_names = ['Sarah', 'Michael', 'Jennifer', 'David', 'Emily', 'Robert', 'Lisa', 
                   'James', 'Maria', 'John', 'Amanda', 'Christopher', 'Patricia', 'Daniel']
    last_names = ['Chen', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson', 
                  'Moore', 'Taylor', 'Anderson', 'Martinez', 'Garcia', 'Rodriguez', 'Hernandez']
    
    leads = []
    
    for i in range(num_leads):
        company = companies[i % len(companies)]
        title = titles[i % len(titles)]
        location = locations[i % len(locations)]
        first_name = first_names[i % len(first_names)]
        last_name = last_names[i % len(last_names)]
        
        has_publication = np.random.random() > 0.7
        
        lead = {
            'name': f'{first_name} {last_name}',
            'title': title,
            'company': company['name'],
            'location': location,
            'company_hq': company['hq'],
            'funding_stage': company['funding'],
            'email': f"{first_name.lower()}.{last_name.lower()}@{company['name'].lower().replace(' ', '')}.com",
            'linkedin_url': f"linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{i}",
            'recent_publication': has_publication,
            'phone': f"+1 (555) {np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}"
        }
        
        lead['score'] = LeadScorer.calculate_total_score(lead)
        leads.append(lead)
    
    df = pd.DataFrame(leads)
    df = df.sort_values('score', ascending=False).reset_index(drop=True)
    df['rank'] = df.index + 1
    
    return df


def display_score_breakdown(lead):
    """Displaying detailed score breakdown."""
    st.markdown("### Score Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        role_score = LeadScorer.score_role(lead['title'])
        st.metric("Role Fit", f"{role_score}/30", help="Based on seniority level")
        
        funding_score = LeadScorer.score_funding(lead['funding_stage'])
        st.metric("Company Funding", f"{funding_score}/20", help="Based on funding stage")
        
        tech_score = LeadScorer.score_technographic(lead['title'])
        st.metric("Technical Relevance", f"{tech_score}/15", help="Title keywords match")
    
    with col2:
        loc_score = LeadScorer.score_location(lead['location'], lead['company_hq'])
        st.metric("Location Hub", f"{loc_score}/10", help="Biotech hub location")
        
        sci_score = LeadScorer.score_scientific(lead['recent_publication'])
        st.metric("Scientific Activity", f"{sci_score}/40", help="Recent publications")
        
        total = lead['score']
        st.metric("**TOTAL SCORE**", f"**{total}/100**", help="Overall propensity to buy")


def main():
    # Header
    st.title("🔬 Lead Generation Agent")
    st.markdown("### 3D In-Vitro Models - Qualified Prospects for Biotech/Pharma")
    st.markdown("**Demo for EuPrime Application**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.markdown("### Search Criteria")
        num_leads = st.slider("Number of Leads", 10, 100, 50)
        min_score = st.slider("Minimum Score", 0, 100, 0, 5)
        
        st.markdown("### Filters")
        show_publications = st.checkbox("Only Recent Publications", False)
        show_hubs = st.checkbox("Only Biotech Hubs", False)
        
        st.markdown("---")
        
        if st.button("🔄 Generate New Leads", type="primary"):
            st.session_state.leads = generate_sample_leads(num_leads)
            st.rerun()
        
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        This tool identifies and scores qualified leads for 3D in-vitro model technologies.
        
        **Scoring Algorithm:**
        - Role Fit: 30 pts
        - Funding: 20 pts
        - Tech Fit: 15 pts
        - Location: 10 pts
        - Publications: 40 pts
        """)
    
    # Initialize or get leads
    if 'leads' not in st.session_state:
        with st.spinner("Generating leads..."):
            st.session_state.leads = generate_sample_leads(num_leads)
            time.sleep(0.5)
    
    df = st.session_state.leads.copy()
    
    # Apply filters
    if show_publications:
        df = df[df['recent_publication'] == True]
    
    if show_hubs:
        hubs = ['Cambridge', 'Boston', 'San Francisco', 'Basel', 'Oxford']
        df = df[df['company_hq'].str.contains('|'.join(hubs), case=False, na=False)]
    
    df = df[df['score'] >= min_score]
    
    # Summary Statistics
    st.markdown("## 📊 Summary Statistics")
    
    # Add some spacing before metrics
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", len(df))
    with col2:
        high_priority = len(df[df['score'] >= 80])
        st.metric("High Priority (80+)", high_priority)
    with col3:
        avg_score = df['score'].mean() if len(df) > 0 else 0
        st.metric("Average Score", f"{avg_score:.1f}")
    with col4:
        with_pubs = len(df[df['recent_publication'] == True])
        st.metric("With Publications", with_pubs)
    
    # Add spacing after metrics
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Score Distribution
    st.markdown("## 📈 Score Distribution")
    st.markdown("<br>", unsafe_allow_html=True)
    
    score_bins = pd.cut(df['score'], bins=[0, 40, 60, 80, 100], labels=['<40', '40-59', '60-79', '80+'])
    score_counts = score_bins.value_counts().sort_index()
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    colors = ['🔴', '🟡', '🟢', '🟢']
    
    for i, (category, count) in enumerate(score_counts.items()):
        with cols[i]:
            st.metric(f"{colors[i]} {category}", count)
    
    # Add spacing after score distribution
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Top Leads Table
    st.markdown("## 🏆 Top Qualified Leads")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Search box
    search = st.text_input("🔍 Search by name, title, or company", "")
    
    if search:
        mask = (
            df['name'].str.contains(search, case=False, na=False) |
            df['title'].str.contains(search, case=False, na=False) |
            df['company'].str.contains(search, case=False, na=False)
        )
        df = df[mask]
    
    # Display table
    if len(df) > 0:
        # Format for display
        display_df = df[['rank', 'score', 'name', 'title', 'company', 'location', 'company_hq', 'email']].copy()
        
        
        def color_score(val):
            if val >= 80:
                return 'background-color: #d4edda; color: #155724'
            elif val >= 60:
                return 'background-color: #fff3cd; color: #856404'
            elif val >= 40:
                return 'background-color: #f8d7da; color: #721c24'
            return 'background-color: #f5f5f5'
        
        styled_df = display_df.style.applymap(color_score, subset=['score'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=400
        )
        
        # Export options
        st.markdown("### 💾 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"qualified_leads_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        
        with col2:
            # Google Sheets format
            sheets_format = df[['rank', 'score', 'name', 'title', 'company', 'email']].to_csv(index=False)
            st.download_button(
                label="📊 Google Sheets Format",
                data=sheets_format,
                file_name=f"leads_for_sheets_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        st.markdown("---")
        
        # Detailed Lead Cards
        st.markdown("## 🎯 Lead Details (Top 10)")
        
        for idx, lead in df.head(10).iterrows():
            with st.expander(f"#{lead['rank']} - {lead['name']} ({lead['score']}/100) - {lead['company']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Title:** {lead['title']}")
                    st.markdown(f"**Company:** {lead['company']}")
                    st.markdown(f"**Location:** {lead['location']}")
                    st.markdown(f"**HQ:** {lead['company_hq']}")
                    st.markdown(f"**Funding:** {lead['funding_stage']}")
                    st.markdown(f"**Email:** {lead['email']}")
                    st.markdown(f"**LinkedIn:** {lead['linkedin_url']}")
                    
                    if lead['recent_publication']:
                        st.success("✅ Recent Publication")
                    else:
                        st.info("ℹ️ No recent publications")
                
                with col2:
                    display_score_breakdown(lead)
    else:
        st.warning("No leads found matching your criteria.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: white;'>
        <p><b>Lead Generation Web Agent</b> | Built for EuPrime Application</p>
        <p>Contact: <a href='mailto:akash@euprime.org' style='color: white;'>akash@euprime.org</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":

    main()
