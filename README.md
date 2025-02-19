# AI Resume Analyzer

## Overview

AI Resume Analyzer is a web application that analyzes resumes and provides insights, skill recommendations, and course
suggestions to improve job prospects. The application is built using `Streamlit, PyResparser`, and `MySQL` for data
storage.

## Features

- Resume Parsing: Extracts candidate details (name, email, skills, etc.) from uploaded PDF resumes.
- Skill Recommendations: Suggests additional skills based on current expertise.
- Course Recommendations: Provides relevant courses for upskilling.
- Resume Scoring: Analyzes resumes based on key sections like objectives, achievements, and projects.
- Admin Dashboard: Allows administrators to view user data and generate analytics.

## Installation

### Prerequisites

Ensure you have Python 3.x installed and set up a MySQL database before proceeding.

### Step 1: Install Required Libraries

Run the following command to install dependencies:

```bash
pip install -r requirements.txt
pip install nltk
pip install spacy==2.3.5
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz
pip install pyresparser
```

### Step 2: Set Up Project Structure

Create a directory (e.g., resume) and inside it, create the following structure:

```bash
resume/
│── Logo/                     # Store logo images
│── Uploaded_Resumes/          # Store uploaded resumes
│── App.py                     # Main application file
│── Courses.py                 # Contains course recommendations
```

### Step 3: Start MySQL Database

1. Launch your MySQL server.
2. The application will create a database named cv and a table user_data automatically.

## Usage

### Running the Application

Execute the following command:

```bash
streamlit run App.py
```

This will launch the AI Resume Analyzer web application in your default browser.

### User Mode

1. Upload your resume (PDF format).
2. Get analyzed insights, skills recommendations, and career-related courses.
3. View your resume score and suggestions for improvement.

### Admin Mode

1. Log in as an admin with predefined credentials.
2. View user data, download reports, and generate analytics.

## Course Recommendations

The `Courses.py` file provides categorized online course recommendations, including:

- Data Science Courses
- Web Development Courses
- Android Development Courses
- iOS Development Courses
- UI/UX Design Courses

## Technologies Used

- Python (Streamlit, Pandas, NLTK, PyResparser)
- Database: MySQL (pymysql)
- Visualization: Plotly
