import streamlit as st
import requests
import json
from datetime import datetime
import re
import os

# Add these imports for file handling
from io import StringIO
from PyPDF2 import PdfReader
import docx

# Page configuration
st.set_page_config(
    page_title="Legal AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .function-header {
        font-size: 1.8rem;
        color: #2c5aa0;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e6f3ff;
        padding-bottom: 0.5rem;
    }
    .result-box {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    # Try to get API key from environment variable if not already set
    st.session_state.api_key = os.environ.get("OPENROUTER_API_KEY", "")

def make_api_request(prompt, system_prompt="You are a helpful legal AI assistant."):
    """Make request to OpenRouter API"""
    if not st.session_state.api_key:
        st.error("Please enter your OpenRouter API key in the sidebar.")
        return None
    
    headers = {
        "Authorization": f"Bearer {st.session_state.api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Sidebar for API configuration
with st.sidebar:
    st.markdown("### 🔐 API Configuration")
    # Only show the API key input if not set in environment variable
    if os.environ.get("OPENROUTER_API_KEY", "") == "":
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get your API key from https://openrouter.ai"
        )
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
    else:
        st.success("API key loaded from environment variable.", icon="🔒")

    st.markdown("---")
    st.markdown("### 📋 Functions Available")
    st.markdown("""
    1. **Contract Analysis** - Review and analyze contracts
    2. **Legal Document Drafting** - Create legal documents
    3. **Case Law Research** - Research relevant cases
    4. **Legal Memo Generator** - Generate legal memorandums
    5. **Compliance Checker** - Check regulatory compliance
    """)
    
    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    st.markdown("""
    This tool provides AI-generated legal assistance for informational purposes only. 
    Always consult with qualified legal professionals for actual legal advice.
    """)

# Main header
st.markdown('<h1 class="main-header">⚖️ Legal AI Assistant</h1>', unsafe_allow_html=True)

# Function selection
function_choice = st.selectbox(
    "Select Legal AI Function:",
    [
        "Contract Analysis & Review",
        "Legal Document Drafting",
        "Case Law Research Assistant",
        "Legal Memorandum Generator",
        "Regulatory Compliance Checker"
    ],
    index=0
)

# Function 1: Contract Analysis & Review
if function_choice == "Contract Analysis & Review":
    st.markdown('<h2 class="function-header">📄 Contract Analysis & Review</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File uploader for PDF/DOCX
        uploaded_file = st.file_uploader(
            "Upload contract file (PDF or DOCX):",
            type=["pdf", "docx"]
        )

        contract_text = ""
        if uploaded_file is not None:
            file_type = uploaded_file.name.split(".")[-1].lower()
            if file_type == "pdf":
                try:
                    pdf_reader = PdfReader(uploaded_file)
                    contract_text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
                except Exception as e:
                    st.error(f"Could not read PDF: {e}")
            elif file_type == "docx":
                try:
                    doc = docx.Document(uploaded_file)
                    contract_text = "\n".join([para.text for para in doc.paragraphs])
                except Exception as e:
                    st.error(f"Could not read DOCX: {e}")
        else:
            contract_text = st.text_area(
                "Paste your contract text here:",
                height=300,
                placeholder="Enter the contract text you want to analyze..."
            )
        
        analysis_type = st.selectbox(
            "Analysis Type:",
            ["General Review", "Risk Assessment", "Key Terms Extraction", "Compliance Check"]
        )
    
    with col2:
        st.markdown("**Analysis Focus:**")
        focus_areas = st.multiselect(
            "Select areas to focus on:",
            ["Liability Clauses", "Payment Terms", "Termination Conditions", 
             "Intellectual Property", "Confidentiality", "Force Majeure"]
        )
        
        contract_type = st.selectbox(
            "Contract Type:",
            ["Employment", "Service Agreement", "NDA", "Purchase Agreement", "Lease", "Other"]
        )
    
    if st.button("🔍 Analyze Contract", type="primary"):
        if contract_text and contract_text.strip():
            system_prompt = f"""You are an expert legal contract analyst. Analyze the provided contract with focus on {analysis_type.lower()}. 
            Pay special attention to: {', '.join(focus_areas) if focus_areas else 'all standard contract provisions'}.
            This appears to be a {contract_type.lower()} contract.
            
            Provide a structured analysis including:
            1. Executive Summary
            2. Key Terms and Conditions
            3. Potential Risks and Red Flags
            4. Recommendations
            5. Missing Clauses (if any)
            
            Format your response clearly with headings and bullet points."""
            
            with st.spinner("Analyzing contract..."):
                result = make_api_request(contract_text, system_prompt)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### Analysis Results")
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please provide contract text or upload a contract file to analyze.")

# Function 2: Legal Document Drafting
elif function_choice == "Legal Document Drafting":
    st.markdown('<h2 class="function-header">📝 Legal Document Drafting</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        document_type = st.selectbox(
            "Document Type:",
            ["Non-Disclosure Agreement (NDA)", "Employment Contract", "Service Agreement", 
             "Terms of Service", "Privacy Policy", "Demand Letter", "Cease and Desist"]
        )
        
        document_details = st.text_area(
            "Provide specific details and requirements:",
            height=200,
            placeholder="Describe the specific terms, parties involved, and any special requirements..."
        )
    
    with col2:
        st.markdown("**Document Parameters:**")
        
        if document_type in ["Employment Contract", "Service Agreement"]:
            duration = st.text_input("Contract Duration:", placeholder="e.g., 2 years")
            compensation = st.text_input("Compensation Details:", placeholder="e.g., $50,000 annually")
        
        jurisdiction = st.text_input("Jurisdiction:", placeholder="e.g., California, USA")
        
        parties = st.text_area(
            "Parties Involved:",
            height=100,
            placeholder="List the parties (names, addresses, roles)"
        )
    
    if st.button("📋 Generate Document", type="primary"):
        if document_details.strip():
            system_prompt = f"""You are an expert legal document drafter. Create a comprehensive {document_type} based on the provided requirements.
            
            Include standard legal provisions appropriate for this document type, considering the jurisdiction: {jurisdiction if jurisdiction else 'general'}.
            
            Structure the document professionally with:
            1. Title and parties identification
            2. Recitals/Background
            3. Main terms and conditions
            4. Standard legal clauses
            5. Signature blocks
            
            Make it legally sound but clearly written. Include appropriate legal disclaimers."""
            
            full_prompt = f"""Document Type: {document_type}
            Details: {document_details}
            Parties: {parties if parties else 'Not specified'}
            Jurisdiction: {jurisdiction if jurisdiction else 'Not specified'}
            Additional Info: Duration: {duration if 'duration' in locals() else 'N/A'}, Compensation: {compensation if 'compensation' in locals() else 'N/A'}"""
            
            with st.spinner("Drafting document..."):
                result = make_api_request(full_prompt, system_prompt)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### Generated Document")
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add download button
                    st.download_button(
                        label="📥 Download Document",
                        data=result,
                        file_name=f"{document_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("Please provide document details and requirements.")

# Function 3: Case Law Research Assistant
elif function_choice == "Case Law Research Assistant":
    st.markdown('<h2 class="function-header">🔍 Case Law Research Assistant</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        legal_issue = st.text_area(
            "Describe the legal issue or question:",
            height=150,
            placeholder="e.g., Employment discrimination based on age in California..."
        )
        
        case_context = st.text_area(
            "Additional context or specific circumstances:",
            height=150,
            placeholder="Provide any relevant facts, similar situations, or specific requirements..."
        )
    
    with col2:
        st.markdown("**Research Parameters:**")
        
        jurisdiction_filter = st.multiselect(
            "Jurisdiction Focus:",
            ["Federal", "Kuala Lumpur", "Selangor", "Putrajaya", "Sabah", "Sarawak", "Other State"]
        )
        
        case_type = st.selectbox(
            "Case Type:",
            ["All Types", "Civil", "Criminal", "Constitutional", "Employment", "Contract", "Tort"]
        )
        
        time_period = st.selectbox(
            "Time Period:",
            ["Recent (last 5 years)", "Last 10 years", "Landmark cases", "All time periods"]
        )
    
    if st.button("🔎 Research Cases", type="primary"):
        if legal_issue.strip():
            system_prompt = f"""You are an expert Malaysia legal researcher. Research and provide information about relevant case law for the given legal issue.
            
            Focus on: {', '.join(jurisdiction_filter) if jurisdiction_filter else 'all jurisdictions'}
            Case type: {case_type}
            Time period: {time_period}
            
            Provide a comprehensive research summary including:
            1. Most relevant landmark/precedent cases
            2. Key legal principles established
            3. Recent developments or trends
            4. Distinguishing factors and exceptions
            5. Practical applications and implications
            
            Cite cases properly and explain their relevance to the issue."""
            
            research_query = f"""Legal Issue: {legal_issue}
            Context: {case_context if case_context else 'Not provided'}
            Research Parameters: Jurisdiction: {jurisdiction_filter}, Type: {case_type}, Period: {time_period}"""
            
            with st.spinner("Researching case law..."):
                result = make_api_request(research_query, system_prompt)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### Case Law Research Results")
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please describe the legal issue you want to research.")

# Function 4: Legal Memorandum Generator
elif function_choice == "Legal Memorandum Generator":
    st.markdown('<h2 class="function-header">📋 Legal Memorandum Generator</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        memo_to = st.text_input("To:", placeholder="e.g., Senior Partner, Client Name")
        memo_from = st.text_input("From:", placeholder="e.g., Associate Attorney")
        memo_subject = st.text_input("Subject:", placeholder="Legal issue or case matter")
        
        facts = st.text_area(
            "Statement of Facts:",
            height=150,
            placeholder="Provide the relevant facts of the case or situation..."
        )
        
        legal_question = st.text_area(
            "Legal Question(s):",
            height=100,
            placeholder="What specific legal questions need to be addressed?"
        )
    
    with col2:
        st.markdown("**Memo Parameters:**")
        
        memo_type = st.selectbox(
            "Memorandum Type:",
            ["Legal Research Memo", "Case Analysis", "Litigation Strategy", "Compliance Memo", "Opinion Letter"]
        )
        
        priority = st.selectbox("Priority Level:", ["Standard", "Urgent", "Confidential"])
        
        analysis_depth = st.selectbox(
            "Analysis Depth:",
            ["Brief Summary", "Standard Analysis", "Comprehensive Review"]
        )
        
        include_recommendations = st.checkbox("Include Recommendations", value=True)
    
    if st.button("📄 Generate Memorandum", type="primary"):
        if all([memo_subject, facts, legal_question]):
            system_prompt = f"""You are an expert legal writer creating a professional legal memorandum. 
            
            Create a {memo_type.lower()} with {analysis_depth.lower()} level of detail.
            Priority: {priority}
            Include recommendations: {include_recommendations}
            
            Structure the memorandum professionally:
            1. Header (To, From, Date, Subject)
            2. Executive Summary
            3. Statement of Facts
            4. Legal Analysis
            5. Conclusion
            {'6. Recommendations' if include_recommendations else ''}
            
            Use proper legal writing style with clear headings and logical flow."""
            
            memo_content = f"""MEMORANDUM DETAILS:
            To: {memo_to}
            From: {memo_from}
            Subject: {memo_subject}
            Type: {memo_type}
            
            Facts: {facts}
            Legal Questions: {legal_question}"""
            
            with st.spinner("Generating memorandum..."):
                result = make_api_request(memo_content, system_prompt)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### Generated Legal Memorandum")
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add download button
                    st.download_button(
                        label="📥 Download Memorandum",
                        data=result,
                        file_name=f"Legal_Memo_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )
        else:
            st.warning("Please fill in all required fields (Subject, Facts, and Legal Questions).")

# Function 5: Regulatory Compliance Checker
elif function_choice == "Regulatory Compliance Checker":
    st.markdown('<h2 class="function-header">✅ Regulatory Compliance Checker</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        industry = st.selectbox(
            "Industry/Sector:",
            ["Healthcare (HIPAA)", "Finance (SOX, GDPR)", "Technology (GDPR, CCPA)", 
             "Education (FERPA)", "Government Contracting", "Food & Drug (FDA)", "Other"]
        )
        
        business_description = st.text_area(
            "Business/Activity Description:",
            height=150,
            placeholder="Describe your business activities, data handling, or specific practices to check..."
        )
        
        specific_concerns = st.text_area(
            "Specific Compliance Concerns:",
            height=150,
            placeholder="Any particular regulations or compliance areas you're concerned about?"
        )
    
    with col2:
        st.markdown("**Compliance Parameters:**")
        
        business_size = st.selectbox(
            "Business Size:",
            ["Startup/Small", "Medium Enterprise", "Large Corporation", "Non-Profit"]
        )
        
        geographic_scope = st.multiselect(
            "Geographic Operations:",
            ["United States", "European Union", "California", "Canada", "International"]
        )
        
        compliance_areas = st.multiselect(
            "Focus Areas:",
            ["Data Privacy", "Financial Reporting", "Employment Law", "Environmental", 
             "Safety Standards", "Licensing", "Tax Compliance"]
        )
    
    if st.button("🔍 Check Compliance", type="primary"):
        if business_description.strip():
            system_prompt = f"""You are an expert regulatory compliance consultant. Analyze the provided business description for compliance requirements in the {industry} sector.
            
            Consider:
            - Business size: {business_size}
            - Geographic scope: {', '.join(geographic_scope) if geographic_scope else 'Not specified'}
            - Focus areas: {', '.join(compliance_areas) if compliance_areas else 'General compliance'}
            
            Provide a comprehensive compliance analysis including:
            1. Applicable Regulations and Laws
            2. Current Compliance Status Assessment
            3. Required Actions and Documentation
            4. Risk Areas and Potential Violations
            5. Implementation Timeline and Priorities
            6. Ongoing Compliance Requirements
            
            Be specific about regulatory requirements and practical steps."""
            
            compliance_query = f"""Industry: {industry}
            Business Description: {business_description}
            Specific Concerns: {specific_concerns if specific_concerns else 'General compliance review'}
            Business Context: Size: {business_size}, Geographic: {geographic_scope}, Focus: {compliance_areas}"""
            
            with st.spinner("Analyzing compliance requirements..."):
                result = make_api_request(compliance_query, system_prompt)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown("### Compliance Analysis Results")
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Warning box
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.markdown("**⚠️ Important Notice:** This analysis is for informational purposes only. "
                              "Consult with qualified legal and compliance professionals for specific advice "
                              "and to ensure full regulatory compliance.")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("Please provide a business description to analyze compliance requirements.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>⚖️ Legal AI Assistant | Develop by AICE DagangNet</p>
    <p><small>This tool provides AI-generated legal assistance for informational purposes only. 
    Always consult with qualified legal professionals for actual legal advice.</small></p>
</div>
""", unsafe_allow_html=True)