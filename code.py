import streamlit as st
from fpdf import FPDF
import base64
import requests

# Replace 'YOUR_CSE_ID' and 'YOUR_API_KEY' with your actual CSE ID and API Key
CSE_ID = '41d4a9e39180b4946'
API_KEY = 'AIzaSyBnFAROY3rNLEaLHiHzrpGzx9tz7gCXurE'

# Function to search courses based on skill level and specific websites
def search_courses(query, sites):
    num_results_per_site = 1  # Number of results to fetch per site

    # List to hold all the results
    all_results = []

    # Perform searches for each site
    for site in sites:
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={CSE_ID}&key={API_KEY}&siteSearch={site}&num={num_results_per_site}"

        # Fetch search results from the site
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            for item in items:
                result = {
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', '')
                }
                all_results.append(result)
        else:
            st.error(f"Error fetching search results for {site}")

    return all_results

# Function to generate PDF
def generate_pdf(course_results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_xy(10, 10)
    pdf.set_font('Arial', '', 12)

    # Write each course info to the PDF
    for course in course_results:
        pdf.set_text_color(0, 0, 255)  # Set text color to blue
        pdf.cell(0, 10, f"Title: {course['title']}", ln=True)
        pdf.set_text_color(0, 0, 0)  # Reset text color to black
        pdf.cell(0, 10, f"Snippet: {course['snippet']}", ln=True)
        pdf.cell(0, 10, f"Link: {course['link']}", ln=True)
        pdf.cell(0, 10, "", ln=True)  # Add an empty line between courses

    return pdf.output(dest="S").encode("latin-1")

# Streamlit UI
def main():
    st.title("Learning Guru")
    st.caption("Creating a comprehensive learning plan from A-Z")

    skill = st.text_input("What skill would you like to learn?")
    current_skill_level = st.selectbox("What is your current skill level in this skill?", ["No skill", "Beginner", "Intermediate", "Advanced"])
    desired_skill_level = st.selectbox("What is the skill level you would like to reach?", ["No skill", "Beginner", "Intermediate", "Advanced", "Mastery"])
    start_date = st.date_input("When would you like to start?")
    end_date = st.date_input("What is the day you would like to finish your goal? (You can approximate the date)")
    weekly_time = st.slider("How much time a week can you dedicate?", 1, 40, 20)
    budget = st.slider("What is your budget to learn this skill?", 0, 500, 250)

    if st.button("Submit"):
        course_results = execute_course_search(current_skill_level, desired_skill_level, skill)  # Get search results
        save_results(course_results)  # Save search results
        display_results(current_skill_level, course_results)  # Display search results

    if st.button("Export Report"):
        course_results = execute_course_search(current_skill_level, desired_skill_level, skill)
        pdf_content = generate_pdf(course_results)
        st.markdown(create_download_link(pdf_content, "course_report"), unsafe_allow_html=True)

def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" style="font-size: 16px; font-weight: bold;" download="{filename}.pdf">Download PDF</a>'

def execute_course_search(user_current_level, user_goal_level, course_topic):
    skill_levels = ['Beginner', 'Intermediate', 'Advanced']
    current_index = skill_levels.index(user_current_level)
    goal_index = skill_levels.index(user_goal_level)

    # Specify websites to search here
    sites = ['youtube.com', 'udemy.com', 'edx.org', 'skillshare.com']

    all_results = []  # Variable to store all search results

    for i in range(current_index, goal_index + 1):
        current_skill_level = skill_levels[i]
        query = f"{current_skill_level} {course_topic} course"
        results = search_courses(query, sites)
        all_results.extend(results)  # Add results to the variable

    return all_results

def save_results(results):
    st.write("Results saved successfully.")

def display_results(skill_level, results):
    st.header(f"{skill_level} Courses")
    if not results:
        st.write("No courses found for this skill level.")
    else:
        for item in results:
            st.subheader(item['title'])
            st.write(item['snippet'])
            st.write("Content Type: Course")
            st.write(f"Link: <span style='color: blue;'>[{item['link']}]({item['link']})</span>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
