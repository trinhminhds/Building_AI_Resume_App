# SET UP:

# 1. INSTALL BELOW LIBRARIES

# pip install -r requirements.txt

# pip install nltk

# pip install spacy==3.8.3

# python -m spacy download en_core_web_sm

# pip install pyresparser

# Open `pyresparser/utils.py` in your code editor.
# Locate the line (around line 347) that calls matcher.add().
# Replace:
# matcher.add('NAME', None, *pattern)
# with:
# matcher.add('NAME', pattern)

# 2. CREAT A FOLDER AND NAME IT (e.g. resume)
# 2.1 create two more folders inside this folder (Logo and Uploaded_Resumes)
# 2.2 create two python files (App.py and Courses.py)

# 3. START YOUR SQL DATABASE


# 4. CONTINUE WITH THE FOLLOWING CODE...

import streamlit as st
import pandas as pd
import base64
import random
import time
import datetime

# libraries to parse the resume pdf files
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io

from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos

# for uploading youtube videos
from pytube import YouTube

# to create visualisations at the admin session
import plotly.express as px
import nltk

nltk.download('stopwords')

from pyresparser import ResumeParser


# import os

# os.environ["PAFY_BACKEND"] = "internal"

# Function to fetch the data from the database
def fetch_yt_video(link):
    try:
        video = YouTube(link)
        return video.title
    except KeyError:
        return "Title not found"
    except Exception as e:
        return f"Error: {str(e)}"


# Function to get table download link
def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in: dataframe
    out: href string
    """
    csv = df.to_csv(index = False)
    b64 = base64.b64encode(csv.encode()).decode()  # Corrected encoding process
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Function to convert pdf to text
def pdf_reader(file):
    # Open the pdf file
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    # Set parameters for analysis.
    converter = TextConverter(resource_manager, fake_file_handle, laparams = LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    # Read the pdf file
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching = True, check_extractable = True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


# Function show pdf file
def show_pdf(file_path):
    # Open the pdf file
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html = True)


# Function course recommendation
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations🎓**")
    c = 0
    rec_courses = []
    no_of_reco = st.slider('Choose Number of Course Recommendations', 1, 10, 5)
    random.shuffle(course_list)
    # Display the recommended courses
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"{c}. [{c_name}]({c_link})")
        rec_courses.append(c_name)
        if c == no_of_reco:
            break
    return rec_courses


# CONNECT TO DATABASE

# Connect to MySQL server without specifying a database
connection = pymysql.connect(host = 'localhost', user = 'root', password = '23092003')
cursor = connection.cursor()

# Create the database if it does not exist
cursor.execute("CREATE DATABASE IF NOT EXISTS cv")

# Close the initial connection
connection.close()

# Connect to the newly created database
connection = pymysql.connect(host = 'localhost', user = 'root', password = '23092003', db = 'cv')
cursor = connection.cursor()


# Function to insert data into the database
def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills,
                courses):
    BD_table_name = 'user_data'
    insert_sql = "insert into " + BD_table_name + """
    values(0,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    rec_values = (
        name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
        courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


st.set_page_config(page_title = "AI Resume Analyzer", page_icon = '.\Logo\logo2.png')


# Functions to run the app
def run():
    img = Image.open('.\Logo\logo2.png')
    st.image(img)
    st.title("AI Resume Analyzer")
    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options: ", activities)
    link = ['[©Developed by Dr,Briit](https://www.linkedin.com/in/mrbriit/)']
    st.sidebar.markdown(link, unsafe_allow_html = True)

    # Create the BD
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    Name varchar(500) NOT NULL,
                    Email_ID varchar(500) NOT NULL,
                    resume_score varchar(8) NOT NULL,
                    Timestamp varchar(50) NOT NULL,
                    Page_no varchar(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_Level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    PRIMARY KEY (ID));
                    """

    cursor.execute(table_sql)
    if choice == 'User':
        st.markdown(
            '''<h5 style= 'text-align: left; color: #021659; '>Upload your resume, and get smart recommendations</h5>''',
            unsafe_allow_html = True)
        pdf_file = st.file_uploader("Upload your resume", type = ['pdf'])
        if pdf_file is not None:
            with st.spinner('Uploading your resume...'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, 'wb') as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")

                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass

                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = 'Freshers'
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',
                                unsafe_allow_html = True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = 'Intermediate'
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html = True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = 'Experienced'
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                                unsafe_allow_html = True)

                # st.subheader("**Skills Recommendation**")
                ## Skill shows
                keyword = st_tags(label = '### Your Current Skills', text = 'See our skills recommendations below',
                                  value = resume_data['skills'], key = '1')

                # keywords
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask',
                              'streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['java', 'kotlin', 'android studio', 'flutter', 'dart', 'android sdk']
                ios_keyword = ['swift', 'xcode', 'ios sdk', 'objective c', 'ios development', 'ios']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro',
                                'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                                'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                reco_course = []

                # Courses recommendation
                for i in resume_data['skills']:
                    ## Data Science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs. **")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                              'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                              'Streamlit']
                        recommended_keywords = st_tags(label = '### Recommended Skills for you',
                                                       text = 'Recommended skills genarated from System',
                                                       value = recommended_skills, key = '2')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',
                            unsafe_allow_html = True)
                        reco_course = course_recommender(ds_course)
                        break

                    ## Web Development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs. **")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        recommended_keywords = st_tags(label = '### Recommended Skills for you',
                                                       text = 'Recommended skills genarated from System',
                                                       value = recommended_skills, key = '3')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html = True)
                        reco_course = course_recommender(web_course)
                        break

                    ## Android Development recommendation
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android Development Jobs. **")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                              'Kivy', 'GIT', 'SDK', 'SQLite']
                        recommended_keywords = st_tags(label = '### Recommended Skills for you',
                                                       text = 'Recommended skills genarated from System',
                                                       value = recommended_skills, key = '4')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html = True)
                        reco_course = course_recommender(android_course)
                        break

                    ## IOS Development recommendation
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS Development Jobs. **")
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                              'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation',
                                              'Auto-Layout']
                        recommended_keywords = st_tags(label = '### Recommended Skills for you',
                                                       text = 'Recommended skills genarated from System',
                                                       value = recommended_skills, key = '5')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html = True)
                        reco_course = course_recommender(ios_course)
                        break

                    ## UI/UX Development recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI/UX Development'
                        st.success("** Our analysis says you are looking for UI/UX Development Jobs. **")
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                              'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                              'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                              'Solid', 'Grasp', 'User Research']
                        recommended_keywords = st_tags(label = '### Recommended Skills for you',
                                                       text = 'Recommended skills genarated from System',
                                                       value = recommended_skills, key = '6')
                        st.markdown(
                            '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                            unsafe_allow_html = True)
                        reco_course = course_recommender(uiux_course)
                        break

                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date) + '_' + str(cur_time)

                ### Resume writing recommendation
                st.subheader("**Resume Tips & Ideas💡**")
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',
                        unsafe_allow_html = True)
                else:
                    st.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',
                        unsafe_allow_html = True)

                if 'Declaration' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Great! You have added Declaration</h4>''',
                        unsafe_allow_html = True)
                else:
                    st.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',
                        unsafe_allow_html = True)

                if 'Hobbies' or 'Interests' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Good! You have added Hobbies</h4>''',
                        unsafe_allow_html = True)
                else:
                    st.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',
                        unsafe_allow_html = True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Excellent! You have added Achievements</h4>''',
                        unsafe_allow_html = True)
                else:
                    st.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',
                        unsafe_allow_html = True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>[+] Amazing! You have added Projects</h4>''',
                        unsafe_allow_html = True)
                else:
                    st.markdown(
                        '''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',
                        unsafe_allow_html = True)

                # Resume Score
                st.subheader("**Resume Score📝**")
                st.markdown("""<style>.stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }</style>""", unsafe_allow_html = True)

                # Progress bar
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(100):
                    score += 1
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1)
                st.success('**Your Resume Writing Score: ' + str(score) + '**')
                st.warning("**Note: This score is calculated based on the content that you have in your Resume.**")
                st.balloons()

                # Insert data into the database
                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                            str(resume_data['no_of_pages']),
                            reco_field, cand_level, str(resume_data['skills']), str(recommended_skills),
                            str(reco_course))

                ## Resume writing videos
                st.header("**Bonus Videos for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                res_vid_title = fetch_yt_video(resume_vid)
                st.subheader("✅ **" + res_vid_title + "**")
                st.video(resume_vid)

                ## Interview preparation videos
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                int_vid_title = fetch_yt_video(interview_vid)
                st.subheader("✅ **" + int_vid_title + "**")
                st.video(interview_vid)
                connection.commit()

            else:
                st.error("Something went wrong...")

    else:
        ## Admin session
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input('Username')
        ad_password = st.text_input('Password', type = 'password')
        if st.button('Login'):
            if ad_user == 'minhtrinh' and ad_password == 'minh123':
                st.success('Welcome Dr MinhTrinh!')

                # Display the Data
                cursor.execute('''SELECT * FROM user_data''')
                data = cursor.fetchall()
                st.header('**User Data**')
                df = pd.DataFrame(data, columns = ['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                   'Predicted Field', 'User Level', 'Actual Skills',
                                                   'Recommended Skills', 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html = True)

                # Admin Side Data
                query = 'SELECT * FROM user_data'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for Predicted field recommendations
                # Decode binary data to strings
                plot_data['Predicted_Field'] = plot_data['Predicted_Field'].apply(lambda x: x.decode('utf-8'))
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("**Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values = values, names = labels, title = 'Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ## Pie chart for User's 👨‍💻 Experienced Level
                # Decode binary data to strings
                plot_data['User_Level'] = plot_data['User_Level'].apply(lambda x: x.decode('utf-8'))
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values = values, names = labels,
                             title = "Pie-Chart📈 for User's👨‍💻 Experienced Level")
                st.plotly_chart(fig)

            else:
                st.error('Wrong ID & Password Provided')


run()
