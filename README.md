# AI Resume Critic 📝

A Streamlit-based application that uses AI to critique resumes and provide actionable feedback.

## Features

-   **PDF & TXT Support**: Upload your resume in PDF or plain text format.
-   **Job Role Context**: Specify the job role you are applying for to get tailored feedback.
-   **AI Analysis**: Uses OpenRouter (Meta Llama 3) to provide:
    -   Profile Summary
    -   Top 3 Strengths
    -   Top 3 Areas for Improvement
    -   Actionable Advice
    -   Skills Assessment

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd resume-critic
    ```

2.  **Install dependencies**:
    This project uses `uv` for dependency management, but you can also use pip.
    ```bash
    pip install -r requirements.txt
    # OR with uv
    uv sync
    ```

3.  **Environment Variables**:
    Create a `.env` file in the root directory and add your OpenRouter API key:
    ```env
    OPENROUTER_API_KEY=your_api_key_here
    ```

4.  **Run the application**:
    ```bash
    streamlit run main.py
    ```

## Usage

1.  Enter the **Job Role** you are targeting.
2.  Upload your resume (PDF or TXT).
3.  Click **Analyze Resume**.
4.  Review the AI-generated insights!

## Tech Stack

-   **Python**
-   **Streamlit**
-   **OpenAI API (via OpenRouter)**
-   **PyPDF2**
