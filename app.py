import streamlit as st
import pandas as pd
from utils.web_scraper import WebScraper
from utils.seo_analyzer import SEOAnalyzer
from agents.seo_agent import SEOAgent
import time
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()




# Page configuration
st.set_page_config(
    page_title="SEO Agentic AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .seo-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .good-score { background-color: #C8E6C9; color: #2E7D32; }
    .medium-score { background-color: #FFF3CD; color: #856404; }
    .poor-score { background-color: #F8D7DA; color: #721C24; }
    .recommendation-card {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        border-left: 4px solid;
    }
    .high-priority { border-left-color: #DC3545; background-color: #F8D7DA; }
    .medium-priority { border-left-color: #FFC107; background-color: #FFF3CD; }
    .low-priority { border-left-color: #28A745; background-color: #D4EDDA; }
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'seo_agent' not in st.session_state:
    st.session_state.seo_agent = SEOAgent()
if 'page_data' not in st.session_state:
    st.session_state.page_data = None
if 'seo_analysis' not in st.session_state:
    st.session_state.seo_analysis = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

def analyze_website(url):
    """Perform SEO analysis on a website"""
    with st.spinner("Analyzing website..."):
        # Initialize components
        scraper = WebScraper()
        analyzer = SEOAnalyzer()
        
        # Fetch website data
        page_data, error = scraper.fetch_url(url)
        
        if error:
            st.error(f"Error: {error}")
            return None, None, None
        
        # Perform SEO analysis
        seo_analysis = analyzer.analyze_page(page_data)
        
        # Get AI recommendations
        agent = st.session_state.seo_agent
        recommendations = agent.analyze_and_advise(page_data, seo_analysis)
        
        return page_data, seo_analysis, recommendations

def display_seo_score(score):
    """Display SEO score with appropriate styling"""
    if score >= 70:
        css_class = "good-score"
    elif score >= 40:
        css_class = "medium-score"
    else:
        css_class = "poor-score"
    
    st.markdown(f"""
    <div class="seo-score {css_class}">
        SEO Score: {score}/100
    </div>
    """, unsafe_allow_html=True)

def display_recommendations(recommendations):
    """Display SEO recommendations"""
    if not recommendations:
        return
    
    st.subheader("AI Recommendations")
    
    # Display summary
    if 'summary' in recommendations:
        with st.expander("Analysis Summary", expanded=True):
            st.write(recommendations['summary'])
    
    # Display recommendations by priority
    if 'recommendations' in recommendations and recommendations['recommendations']:
        st.subheader("Action Items")
        
        # Create tabs for different priorities
        tab1, tab2, tab3 = st.tabs(["🔴 High Priority", "🟡 Medium Priority", "🟢 Low Priority"])
        
        high_priority = [r for r in recommendations['recommendations'] if r.get('priority', '').lower() == 'high']
        medium_priority = [r for r in recommendations['recommendations'] if r.get('priority', '').lower() == 'medium']
        low_priority = [r for r in recommendations['recommendations'] if r.get('priority', '').lower() == 'low']
        
        with tab1:
            for i, rec in enumerate(high_priority):
                with st.container():
                    st.markdown(f"""
                    <div class="recommendation-card high-priority">
                        <h4>{i+1}. {rec.get('title', 'Recommendation')}</h4>
                        <p>{rec.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            for i, rec in enumerate(medium_priority):
                with st.container():
                    st.markdown(f"""
                    <div class="recommendation-card medium-priority">
                        <h4>{i+1}. {rec.get('title', 'Recommendation')}</h4>
                        <p>{rec.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab3:
            for i, rec in enumerate(low_priority):
                with st.container():
                    st.markdown(f"""
                    <div class="recommendation-card low-priority">
                        <h4>{i+1}. {rec.get('title', 'Recommendation')}</h4>
                        <p>{rec.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Display quick wins
    if 'quick_wins' in recommendations and recommendations['quick_wins']:
        with st.expander("⚡ Quick Wins"):
            for win in recommendations['quick_wins']:
                st.markdown(f"- {win}")

def display_analysis_details(seo_analysis):
    """Display detailed SEO analysis"""
    st.subheader("Detailed Analysis")
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Word Count", seo_analysis['content_analysis']['word_count'])
    
    with col2:
        title_status = "✅" if seo_analysis['title_analysis']['optimal'] else "⚠️"
        st.metric("Title Length", f"{seo_analysis['title_analysis']['length']} chars", 
                 delta=None, delta_color="normal", help=title_status)
    
    with col3:
        desc_status = "✅" if seo_analysis['meta_description_analysis']['optimal'] else "⚠️"
        st.metric("Description Length", f"{seo_analysis['meta_description_analysis']['length']} chars",
                 delta=None, delta_color="normal", help=desc_status)
    
    with col4:
        st.metric("Images with Alt Text", 
                 f"{seo_analysis['image_analysis']['alt_percentage']}%")
    
    # Detailed sections
    with st.expander("🔤 Title Analysis"):
        st.write(f"**Current Title:** {seo_analysis['title_analysis']['current']}")
        st.write(f"**Length:** {seo_analysis['title_analysis']['length']} characters")
        if seo_analysis['title_analysis']['issues']:
            st.warning("**Issues:**")
            for issue in seo_analysis['title_analysis']['issues']:
                st.write(f"- {issue}")
        else:
            st.success("✅ No issues found")
    
    with st.expander("📝 Meta Description Analysis"):
        st.write(f"**Current Description:** {seo_analysis['meta_description_analysis']['current']}")
        st.write(f"**Length:** {seo_analysis['meta_description_analysis']['length']} characters")
        if seo_analysis['meta_description_analysis']['issues']:
            st.warning("**Issues:**")
            for issue in seo_analysis['meta_description_analysis']['issues']:
                st.write(f"- {issue}")
        else:
            st.success("✅ No issues found")
    
    with st.expander("📄 Content Analysis"):
        st.write(f"**Word Count:** {seo_analysis['content_analysis']['word_count']}")
        st.write(f"**Average Sentence Length:** {seo_analysis['content_analysis']['avg_sentence_length']} words")
        
        if seo_analysis['content_analysis']['keyword_density']:
            st.write("**Keyword Density:**")
            for keyword, density in seo_analysis['content_analysis']['keyword_density'].items():
                st.write(f"- {keyword}: {density}%")
        
        if seo_analysis['content_analysis']['issues']:
            st.warning("**Issues:**")
            for issue in seo_analysis['content_analysis']['issues']:
                st.write(f"- {issue}")
    
    with st.expander("🏷️ Header Structure"):
        for level in range(1, 7):
            count = seo_analysis['header_analysis']['structure'].get(f'h{level}', 0)
            st.write(f"**H{level}:** {count}")
        
        if seo_analysis['header_analysis']['issues']:
            st.warning("**Issues:**")
            for issue in seo_analysis['header_analysis']['issues']:
                st.write(f"- {issue}")

def chat_interface():
    """Chat interface for discussing SEO improvements"""
    st.subheader("Discuss Improvements with SEO Agent")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about SEO improvements..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get context for the agent
        context = {
            'url': st.session_state.page_data.get('url', '') if st.session_state.page_data else '',
            'score': st.session_state.seo_analysis.get('score', 0) if st.session_state.seo_analysis else 0,
            'main_issues': []
        }
        
        # Extract main issues from analysis
        if st.session_state.seo_analysis:
            for category, data in st.session_state.seo_analysis.items():
                if isinstance(data, dict) and 'issues' in data and data['issues']:
                    context['main_issues'].extend(data['issues'][:2])
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.seo_agent.chat(prompt, context)
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")

def main():
    # Header
    st.markdown('<h1 class="main-header">SEO Agentic AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered SEO analysis and improvement recommendations</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # URL input
        url = st.text_input("🌐 Website URL", 
                           placeholder="https://example.com",
                           help="Enter the full URL of the website to analyze")
        
        # Model selection
        try:
            # Get available models
            agent = st.session_state.seo_agent
            available_models = agent.get_available_models()
            
            if available_models:
                default_model = available_models[0]
                model = st.selectbox(
                    "Ollama Model",
                    available_models,
                    index=available_models.index(default_model) if default_model in available_models else 0,
                    help="Select the Ollama model to use for analysis"
                )
            else:
                st.warning("No Ollama models found. Please run: `ollama pull llama3.1:8b`")
                model = DEFAULT_MODEL
        except Exception as e:
            st.error(f"Error loading models: {e}")
            model = DEFAULT_MODEL

        if model != st.session_state.seo_agent.model:
            st.session_state.seo_agent = SEOAgent(model)

        
        # Analysis button
        analyze_btn = st.button("Analyze Website", type="primary", use_container_width=True)
        
        if analyze_btn and url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Perform analysis
            page_data, seo_analysis, recommendations = analyze_website(url)
            
            if page_data:
                st.session_state.page_data = page_data
                st.session_state.seo_analysis = seo_analysis
                st.session_state.recommendations = recommendations
                st.session_state.analysis_complete = True
                st.session_state.chat_history = []  # Clear chat history
                st.session_state.seo_agent.clear_history()  # Clear agent history
                
                st.success("✅ Analysis complete!")
                st.rerun()
        
        st.divider()
        
        # Additional options
        st.header("📊 Export")
        
        if st.session_state.analysis_complete:
            if st.button("📥 Export Report", use_container_width=True):
                # Create report data
                report = {
                    'url': st.session_state.page_data.get('url', ''),
                    'timestamp': datetime.now().isoformat(),
                    'seo_score': st.session_state.seo_analysis.get('score', 0),
                    'analysis': st.session_state.seo_analysis,
                    'recommendations': st.session_state.recommendations
                }
                
                # Convert to JSON for download
                import json
                report_json = json.dumps(report, indent=2)
                
                st.download_button(
                    label="Download JSON Report",
                    data=report_json,
                    file_name=f"seo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        st.divider()
        
        # Clear button
        if st.button("🗑️ Clear Analysis", use_container_width=True):
            for key in ['page_data', 'seo_analysis', 'recommendations', 'chat_history', 'analysis_complete']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.seo_agent.clear_history()
            st.rerun()
    
    # Main content area
    if st.session_state.analysis_complete and st.session_state.seo_analysis:
        # Display SEO score
        display_seo_score(st.session_state.seo_analysis['score'])
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📈 Recommendations", "🔍 Analysis Details", "💬 Chat with Agent"])
        
        with tab1:
            if st.session_state.recommendations:
                display_recommendations(st.session_state.recommendations)
            else:
                st.info("No recommendations generated yet.")
        
        with tab2:
            display_analysis_details(st.session_state.seo_analysis)
        
        with tab3:
            chat_interface()
    
    else:
        # Welcome/instructions
        st.info("👈 Enter a website URL in the sidebar and click 'Analyze Website' to begin.")
        
        # Features overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 🔍 Comprehensive Analysis
            - Title & meta description optimization
            - Content quality assessment
            - Header structure analysis
            - Image SEO evaluation
            """)
        
        with col2:
            st.markdown("""
            ### 🤖 AI-Powered Insights
            - Ollama-powered recommendations
            - Priority-based suggestions
            - Quick win identification
            - Long-term strategies
            """)
        
        with col3:
            st.markdown("""
            ### 💬 Interactive Chat
            - Discuss improvements
            - Ask specific questions
            - Get implementation guidance
            - Continuous learning
            """)
        
        # Example URLs
        st.divider()
        st.subheader("Try with these example URLs:")
        
        examples = st.columns(4)
        example_urls = [
            ("Example Blog", "https://blog.example.com"),
            ("E-commerce Site", "https://shop.example.com"),
            ("Business Website", "https://business.example.com"),
            ("Portfolio Site", "https://portfolio.example.com")
        ]
        
        for i, (name, url) in enumerate(example_urls):
            with examples[i]:
                if st.button(name, use_container_width=True):
                    st.session_state.page_data = None
                    st.session_state.seo_analysis = None
                    st.session_state.recommendations = None
                    st.session_state.analysis_complete = False
                    st.rerun()

if __name__ == "__main__":
    main()