"""
Main Streamlit Application - Unified ATS-Optimized Application Assistant.
"""
import streamlit as st
import os
from datetime import datetime, timedelta
from pathlib import Path

# Import modules
from src.utils.database import Database
from src.parsers.jd_parser import JobDescriptionParser
from src.engines.unified_cv_generator import UnifiedCVGenerator
from src.engines.cover_letter_gen import CoverLetterGenerator
from src.checkers.ats_compatibility import ATSCompatibilityChecker
from src.checkers.keyword_matcher import KeywordMatcher
from src.checkers.ats_detector import ATSSystemDetector
from src.trackers.application_tracker import ApplicationTracker
from src.trackers.analytics import ApplicationAnalytics
from src.ui.checklists import ChecklistSystem
from src.assistants.application_form import ApplicationFormAssistant
from src.utils.docx_handler import read_docx_from_bytes, extract_docx_text, read_docx
from src.utils.pdf_handler import extract_pdf_text

# Page config
st.set_page_config(
    page_title="Resume Critic - ATS Optimizer",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = ApplicationTracker()
if 'analytics' not in st.session_state:
    st.session_state.analytics = ApplicationAnalytics(st.session_state.tracker)
if 'checklist' not in st.session_state:
    st.session_state.checklist = ChecklistSystem()

# Sidebar navigation
st.sidebar.title("📄 Resume Critic")
st.sidebar.markdown("**ATS-Optimized Application Assistant**")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "➕ New Application", "📊 Applications", "📋 Checklists", "⚙️ Settings"]
)

# Dashboard Page
if page == "🏠 Dashboard":
    st.title("📊 Dashboard")
    
    # Get statistics
    stats = st.session_state.analytics.get_success_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applications", stats.get('total_applications', 0))
    
    with col2:
        st.metric("This Week", stats.get('this_week', 0))
    
    with col3:
        st.metric("Response Rate", f"{stats.get('response_rate', 0)}%")
    
    with col4:
        st.metric("Interview Rate", f"{stats.get('interview_rate', 0)}%")
    
    # Status breakdown
    st.subheader("Status Breakdown")
    status_breakdown = stats.get('status_breakdown', {})
    if status_breakdown:
        cols = st.columns(len(status_breakdown))
        for i, (status, count) in enumerate(status_breakdown.items()):
            with cols[i]:
                st.metric(status, count)
    else:
        st.info("No applications yet. Start by creating a new application!")
    
    # Recent applications
    st.subheader("Recent Applications")
    recent_apps = st.session_state.tracker.get_applications(limit=5)
    if recent_apps:
        for app in recent_apps:
            with st.expander(f"{app['company_name']} - {app['job_title']} ({app['status']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Date Applied:** {app['date_applied']}")
                    st.write(f"**Status:** {app['status']}")
                with col2:
                    if app.get('interview_date'):
                        st.write(f"**Interview:** {app['interview_date']}")
                    if app.get('followup_date'):
                        st.write(f"**Follow-up:** {app['followup_date']}")
                if app.get('notes'):
                    st.write(f"**Notes:** {app['notes']}")
    else:
        st.info("No applications yet. Click 'New Application' to get started!")

# New Application Page
elif page == "➕ New Application":
    st.title("🎯 New Application")
    
    # Step 1: Job Description Input
    st.header("Step 1: Job Description")
    
    jd_input_method = st.radio(
        "How would you like to input the job description?",
        ["Paste Text", "Upload File"]
    )
    
    jd_text = ""
    
    if jd_input_method == "Paste Text":
        jd_text = st.text_area(
            "Paste the job description here",
            height=300,
            placeholder="Paste the full job description..."
        )
    else:  # Upload File
        uploaded_file = st.file_uploader("Upload JD file", type=['txt', 'docx'])
        if uploaded_file:
            if uploaded_file.type == 'text/plain':
                jd_text = str(uploaded_file.read(), 'utf-8')
            elif uploaded_file.name.endswith('.docx'):
                doc = read_docx_from_bytes(uploaded_file.read())
                jd_text = extract_docx_text(doc)
            st.success("File uploaded successfully!")
    
    # Company details
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name *")
        job_location = st.text_input("Location")
    
    with col2:
        job_title = st.text_input("Job Title *")
        salary_range = st.text_input("Salary Range (if mentioned)")
    
    jd_url = st.text_input("Job Posting URL (optional)")
    
    # Analyze button
    if st.button("🔍 Analyze Job Description", type="primary"):
        if jd_text and company_name and job_title:
            with st.spinner("Analyzing job description..."):
                # Parse JD
                parser = JobDescriptionParser(jd_text)
                analysis = parser.extract_all()
                
                # Store in session state
                st.session_state['jd_analysis'] = analysis
                st.session_state['jd_parser'] = parser
                st.session_state['company_name'] = company_name
                st.session_state['job_title'] = job_title
                st.session_state['job_location'] = job_location
                st.session_state['salary_range'] = salary_range
                st.session_state['jd_url'] = jd_url
                st.session_state['jd_text'] = jd_text
                
                st.success("✅ Analysis complete!")
                st.session_state['step'] = 2
        else:
            st.error("Please fill in all required fields (marked with *)")
    
    # Step 2: JD Analysis Results
    if 'step' in st.session_state and st.session_state['step'] >= 2:
        st.header("Step 2: Analysis Results")
        
        if 'jd_analysis' in st.session_state:
            analysis = st.session_state['jd_analysis']
            
            st.subheader("📋 Extracted Information")
            
            # Job title
            st.write(f"**Detected Job Title:** {analysis['job_title']}")
            
            # Keywords
            with st.expander("🔑 Technical Skills"):
                st.write(", ".join(analysis.get('technical_skills', [])))
            
            with st.expander("📝 Required vs Preferred"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Required:**")
                    for item in analysis.get('required_skills', [])[:10]:
                        st.write(f"• {item}")
                with col2:
                    st.write("**Preferred:**")
                    for item in analysis.get('preferred_skills', [])[:10]:
                        st.write(f"• {item}")
            
            with st.expander("💬 Verbatim Phrases"):
                for phrase in analysis.get('verbatim_phrases', [])[:5]:
                    st.write(f"• {phrase}")
            
            # Company values
            if analysis.get('company_values'):
                with st.expander("🎯 Company Values"):
                    st.write(", ".join(analysis['company_values']))
            
            # ATS Detection
            if st.session_state.get('jd_url'):
                ats_detector = ATSSystemDetector()
                detected_ats = ats_detector.detect_ats(application_url=st.session_state['jd_url'])
                if detected_ats:
                    st.info(f"**ATS System Detected:** {detected_ats.upper()}")
                    tips = ats_detector.get_optimization_tips(detected_ats)
                    st.write(f"**Focus:** {tips['focus']}")
                    st.write("**Tips:**")
                    for tip in tips['tips']:
                        st.write(f"• {tip}")
            
            st.session_state['step'] = 3
    
    # Step 3: CV Generation
    if 'step' in st.session_state and st.session_state['step'] >= 3:
        st.header("Step 3: Generate Tailored CV")
        
        # Upload base CV
        base_cv = st.file_uploader(
            "Upload your base CV",
            type=['docx', 'pdf'],
            key='base_cv'
        )
        
        if base_cv:
            # Save temporarily
            temp_dir = Path('data/output/cvs')
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_cv_path = temp_dir / f"temp_{base_cv.name}"
            
            with open(temp_cv_path, 'wb') as f:
                f.write(base_cv.getbuffer())
            
            st.session_state['base_cv_path'] = str(temp_cv_path)
            
            # Generation mode
            generation_mode = st.radio(
                "Generation Mode",
                ["Rule-Based (ATS Optimized)", "CrewAI (AI-Powered)", "Both (Combined)"],
                help="Rule-Based: Fast, keyword-focused. CrewAI: Intelligent rewriting. Both: Best of both worlds."
            )
            
            mode_map = {
                "Rule-Based (ATS Optimized)": "rule-based",
                "CrewAI (AI-Powered)": "crewai",
                "Both (Combined)": "both"
            }
            
            # Tailoring options
            st.subheader("Tailoring Options")
            col1, col2 = st.columns(2)
            with col1:
                match_title = st.checkbox("Match job title", value=True)
                inject_keywords = st.checkbox("Inject verbatim keywords", value=True)
                add_values = st.checkbox("Add values alignment section", value=True)
            
            with col2:
                mirror_structure = st.checkbox("Mirror JD structure", value=True)
                optimize_density = st.checkbox("Optimize keyword density", value=True)
            
            # Additional info
            st.subheader("Additional Information")
            location_avail = st.text_input(
                "Location Availability",
                placeholder="e.g., Hybrid, London, 3 days/week"
            )
            right_to_work = st.text_input(
                "Right to Work",
                placeholder="e.g., UK Citizen"
            )
            
            # Generate button
            if st.button("📝 Generate Tailored CV", type="primary"):
                with st.spinner("Generating your tailored CV..."):
                    try:
                        # Create output filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        company = st.session_state['company_name'].replace(" ", "_")
                        job = st.session_state['job_title'].replace(" ", "_")
                        output_filename = f"{company}_{job}_{timestamp}.docx"
                        output_path = temp_dir / output_filename
                        
                        # Generate CV
                        generator = UnifiedCVGenerator()
                        result = generator.generate_cv(
                            str(temp_cv_path),
                            st.session_state['jd_text'],
                            mode=mode_map[generation_mode],
                            output_path=str(output_path),
                            output_format='docx',
                            location_availability=location_avail,
                            right_to_work=right_to_work
                        )
                        
                        # Run ATS check
                        checker = ATSCompatibilityChecker(str(output_path))
                        ats_report = checker.generate_report()
                        
                        # Calculate keyword match
                        cv_text = extract_docx_text(read_docx(str(output_path)))
                        keyword_matcher = KeywordMatcher(
                            cv_text,
                            {
                                'required_skills': st.session_state['jd_analysis'].get('required_skills', []),
                                'technical_skills': st.session_state['jd_analysis'].get('technical_skills', [])
                            }
                        )
                        keyword_match = keyword_matcher.calculate_match_percentage()
                        
                        # Store results
                        st.session_state['cv_output_path'] = str(output_path)
                        st.session_state['ats_report'] = ats_report
                        st.session_state['keyword_match'] = keyword_match
                        st.session_state['step'] = 4
                        
                        st.success("✅ CV Generated Successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating CV: {str(e)}")
                        st.exception(e)
    
    # Step 4: CV Review & ATS Check
    if 'step' in st.session_state and st.session_state['step'] >= 4:
        st.header("Step 4: CV Review & ATS Check")
        
        if 'ats_report' in st.session_state:
            ats_report = st.session_state['ats_report']
            keyword_match = st.session_state['keyword_match']
            
            # ATS Score
            score = ats_report['score']
            score_color = "green" if score >= 80 else "orange" if score >= 60 else "red"
            st.markdown(f"**ATS Compatibility Score:** :{score_color}[{score}/100]")
            st.write(f"**Grade:** {ats_report['grade']}")
            
            # Keyword match
            st.write(f"**Keyword Match:** {keyword_match['match_percentage']}% ({keyword_match['matched_keywords']}/{keyword_match['total_keywords']})")
            
            # Issues
            if ats_report['issues']:
                with st.expander("⚠️ Issues Found"):
                    for issue in ats_report['issues']:
                        st.write(f"[{issue['severity']}] {issue['issue']}")
            
            # Recommendations
            if ats_report['recommendations']:
                with st.expander("💡 Recommendations"):
                    for rec in ats_report['recommendations']:
                        st.write(f"• {rec}")
            
            # Missing keywords
            if keyword_match['missing_keywords']:
                with st.expander("🔑 Missing Keywords"):
                    for kw in keyword_match['missing_keywords_list'][:10]:
                        st.write(f"• {kw}")
            
            # Download button
            if 'cv_output_path' in st.session_state:
                with open(st.session_state['cv_output_path'], 'rb') as f:
                    st.download_button(
                        "⬇️ Download Tailored CV",
                        f.read(),
                        file_name=os.path.basename(st.session_state['cv_output_path']),
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    )
            
            st.session_state['step'] = 5
    
    # Step 5: Cover Letter Generation
    if 'step' in st.session_state and st.session_state['step'] >= 5:
        st.header("Step 5: Generate Cover Letter")
        
        company_detail = st.text_area(
            "What specific detail about the company excites you?",
            placeholder="e.g., Their recent AI product launch and mission to democratize data analytics...",
            height=100
        )
        
        achievement = st.text_area(
            "Select a relevant achievement from your CV to highlight",
            placeholder="e.g., Led data governance project, resulting in 3050% ROI...",
            height=100
        )
        
        role_aspect = st.text_area(
            "What specific aspect from the JD interests you?",
            placeholder="e.g., The opportunity to lead data transformation...",
            height=100
        )
        
        if st.button("✉️ Generate Cover Letter", type="primary"):
            with st.spinner("Generating cover letter..."):
                try:
                    # Get CV data (simplified)
                    cv_data = {'personal_info': {}}
                    
                    cl_gen = CoverLetterGenerator(
                        st.session_state['jd_analysis'],
                        cv_data,
                        company_detail
                    )
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cl_output_path = Path('data/output/cover_letters') / f"cover_letter_{timestamp}.docx"
                    cl_output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    result = cl_gen.generate_docx(
                        str(cl_output_path),
                        st.session_state['company_name'],
                        st.session_state['job_title'],
                        company_detail=company_detail,
                        achievement=achievement,
                        role_aspect=role_aspect
                    )
                    
                    st.session_state['cover_letter_path'] = str(cl_output_path)
                    st.session_state['cover_letter_result'] = result
                    st.session_state['step'] = 6
                    
                    st.success("✅ Cover Letter Generated!")
                    st.write(f"**Word Count:** {result['word_count']} {'✅ Under 400 words' if result['under_400_words'] else '⚠️ Over 400 words'}")
                    
                    # Download button
                    with open(cl_output_path, 'rb') as f:
                        st.download_button(
                            "⬇️ Download Cover Letter",
                            f.read(),
                            file_name=os.path.basename(cl_output_path),
                            mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                        )
                
                except Exception as e:
                    st.error(f"Error generating cover letter: {str(e)}")
    
    # Step 6: Final Checklist & Submit
    if 'step' in st.session_state and st.session_state['step'] >= 6:
        st.header("Step 6: Final Checklist")
        
        checklist = st.session_state.checklist
        final_items = checklist.get_final_submission_checklist()
        
        st.subheader("Final Submission Checklist")
        completion = {}
        
        for item in final_items:
            key = item['id']
            completion[key] = st.checkbox(item['task'], key=key)
            if completion[key]:
                checklist.mark_complete('final_submission', key)
            else:
                checklist.mark_incomplete('final_submission', key)
        
        completion_pct = checklist.get_completion_percentage('final_submission')
        st.progress(completion_pct / 100)
        st.write(f"**Completion:** {completion_pct:.0f}%")
        
        if st.button("✅ Mark Application as Submitted", type="primary"):
            # Save to database
            app_id = st.session_state.tracker.add_application(
                st.session_state['company_name'],
                st.session_state['job_title'],
                status='Applied',
                cv_version_path=st.session_state.get('cv_output_path'),
                cover_letter_included='cover_letter_path' in st.session_state,
                notes=f"Generated using {generation_mode if 'generation_mode' in locals() else 'rule-based'} mode"
            )
            
            # Add JD to database
            if 'jd_parser' in st.session_state:
                jd_id = st.session_state.tracker.db.add_job_description(
                    app_id,
                    st.session_state['jd_text'],
                    jd_url=st.session_state.get('jd_url'),
                    job_location=st.session_state.get('job_location'),
                    salary_range=st.session_state.get('salary_range')
                )
                
                # Add keywords
                analysis = st.session_state['jd_analysis']
                keywords = []
                for category, items in [
                    ('required_skills', analysis.get('required_skills', [])),
                    ('preferred_skills', analysis.get('preferred_skills', [])),
                    ('technical_skills', analysis.get('technical_skills', []))
                ]:
                    for item in items:
                        keywords.append({
                            'category': category,
                            'keyword': item,
                            'frequency': 1,
                            'priority': 'HIGH' if category == 'required_skills' else 'MEDIUM'
                        })
                
                st.session_state.tracker.db.add_keywords(jd_id, keywords)
            
            st.success("✅ Application saved to tracker!")
            st.balloons()
            
            # Reset for new application
            for key in ['step', 'jd_analysis', 'cv_output_path', 'cover_letter_path']:
                if key in st.session_state:
                    del st.session_state[key]

# Applications Page
elif page == "📊 Applications":
    st.title("📊 Application Tracker")
    
    # Status filter
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Applied", "Screening", "Interview", "Offer", "Rejected"]
    )
    
    # Get applications
    if status_filter == "All":
        apps = st.session_state.tracker.get_applications()
    else:
        apps = st.session_state.tracker.get_applications(status=status_filter)
    
    # Display applications
    if apps:
        for app in apps:
            with st.expander(f"{app['company_name']} - {app['job_title']} ({app['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Date Applied:** {app['date_applied']}")
                    st.write(f"**Status:** {app['status']}")
                    
                    # Status update
                    new_status = st.selectbox(
                        "Update Status",
                        ["Applied", "Screening", "Interview", "Offer", "Rejected"],
                        index=["Applied", "Screening", "Interview", "Offer", "Rejected"].index(app['status']) if app['status'] in ["Applied", "Screening", "Interview", "Offer", "Rejected"] else 0,
                        key=f"status_{app['id']}"
                    )
                    if new_status != app['status']:
                        if st.button(f"Update Status", key=f"update_{app['id']}"):
                            st.session_state.tracker.update_status(app['id'], new_status)
                            st.rerun()
                
                with col2:
                    if app.get('interview_date'):
                        st.write(f"**Interview:** {app['interview_date']}")
                    if app.get('followup_date'):
                        st.write(f"**Follow-up:** {app['followup_date']}")
                
                if app.get('notes'):
                    st.write(f"**Notes:** {app['notes']}")
                
                if app.get('cv_version_path'):
                    st.write(f"**CV:** {app['cv_version_path']}")
    else:
        st.info("No applications found")

# Checklists Page
elif page == "📋 Checklists":
    st.title("📋 Application Checklists")
    
    checklist = st.session_state.checklist
    
    tab1, tab2 = st.tabs(["Pre-Application", "Final Submission"])
    
    with tab1:
        st.subheader("Pre-Application Checklist")
        pre_app = checklist.get_pre_application_checklist()
        
        for category in pre_app:
            st.write(f"**{category['category']}**")
            for item in category['items']:
                key = f"pre_{item['id']}"
                checked = st.checkbox(item['task'], key=key)
                if checked:
                    checklist.mark_complete('pre_application', item['id'])
                else:
                    checklist.mark_incomplete('pre_application', item['id'])
        
        completion = checklist.get_completion_percentage('pre_application')
        st.progress(completion / 100)
        st.write(f"**Completion:** {completion:.0f}%")
    
    with tab2:
        st.subheader("Final Submission Checklist")
        final_items = checklist.get_final_submission_checklist()
        
        for item in final_items:
            key = f"final_{item['id']}"
            checked = st.checkbox(item['task'], key=key)
            if checked:
                checklist.mark_complete('final_submission', item['id'])
            else:
                checklist.mark_incomplete('final_submission', item['id'])
        
        completion = checklist.get_completion_percentage('final_submission')
        st.progress(completion / 100)
        st.write(f"**Completion:** {completion:.0f}%")

# Settings Page
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    
    st.subheader("Base CV Template")
    st.info("Upload your master CV that will be used as the base for tailoring")
    
    base_cv_upload = st.file_uploader("Upload Base CV", type=['docx', 'pdf'])
    if base_cv_upload:
        template_dir = Path('data/cv_templates')
        template_dir.mkdir(parents=True, exist_ok=True)
        template_path = template_dir / 'base_cv.docx'
        
        with open(template_path, 'wb') as f:
            f.write(base_cv_upload.getbuffer())
        st.success("Base CV saved!")
    
    st.subheader("Export Data")
    if st.button("Export Applications to Excel"):
        output_path = Path('data/output') / f"applications_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        st.session_state.tracker.export_to_excel(str(output_path))
        st.success(f"Exported to {output_path}")
        
        with open(output_path, 'rb') as f:
            st.download_button(
                "Download Excel Export",
                f.read(),
                file_name=os.path.basename(output_path),
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
