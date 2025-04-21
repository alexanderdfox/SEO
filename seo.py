import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

# --- Config ---
openai.api_key = "your-openai-key"  # Set in UI for security

# --- Functions ---
def get_google_autocomplete_suggestions(query):
	try:
		response = requests.get(f"https://suggestqueries.google.com/complete/search?client=firefox&q={query}")
		suggestions = response.json()[1]
		return suggestions
	except Exception as e:
		return [f"Error fetching suggestions: {e}"]

def generate_blog_post(topic, keywords):
	prompt = f"""
	Write a blog post about "{topic}" using the following keywords: {', '.join(keywords)}.
	Include a catchy intro, SEO-friendly subheadings, and a conclusion.
	"""
	response = openai.ChatCompletion.create(
		model="gpt-4",
		messages=[{"role": "user", "content": prompt}]
	)
	return response['choices'][0]['message']['content']

def optimize_html_page(html, title, description, keywords):
	soup = BeautifulSoup(html, "html.parser")

	if not soup.head:
		head_tag = soup.new_tag("head")
		soup.html.insert(0, head_tag)

	# Title
	if soup.title:
		soup.title.string = title
	else:
		new_title = soup.new_tag("title")
		new_title.string = title
		soup.head.append(new_title)

	meta_desc = soup.new_tag("meta", attrs={"name": "description", "content": description})
	meta_keywords = soup.new_tag("meta", attrs={"name": "keywords", "content": ', '.join(keywords)})

	soup.head.append(meta_desc)
	soup.head.append(meta_keywords)

	return str(soup)

def check_robots_txt(url):
	try:
		robots_url = f"{url.rstrip('/')}/robots.txt"
		r = requests.get(robots_url)
		return "✅ robots.txt found" if r.status_code == 200 else "⚠️ No robots.txt found"
	except:
		return "❌ Error checking robots.txt"

# --- UI ---
st.set_page_config(page_title="SEO Automation Dashboard", layout="wide")
st.title("🔧 SEO Automation Dashboard")

# --- Sidebar ---
with st.sidebar:
	st.header("🔑 API Keys")
	openai.api_key = st.text_input("OpenAI API Key", type="password")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
	"🔍 Keyword Tool", "✍️ Blog Generator", "⚙️ Optimizer", "🧪 SEO Audit", "📤 Export"
])

with tab1:
	st.subheader("🔍 Google Keyword Suggestions")
	query = st.text_input("Search Query", "ai guitar pedal")
	if st.button("Get Suggestions"):
		suggestions = get_google_autocomplete_suggestions(query)
		st.write(suggestions)

with tab2:
	st.subheader("✍️ Generate AI Blog Post")
	topic = st.text_input("Blog Topic", "AI-powered guitar pedals")
	kw_input = st.text_area("Keywords (comma-separated)", "ai guitar, smart pedals, audio effects")
	if st.button("Generate Blog"):
		keywords = [kw.strip() for kw in kw_input.split(",")]
		blog = generate_blog_post(topic, keywords)
		st.session_state["blog"] = blog
		st.markdown(blog)

with tab3:
	st.subheader("⚙️ Optimize HTML Page")
	title = st.text_input("Page Title", "AI Guitar Effects")
	desc = st.text_input("Meta Description", "Explore the best AI-powered pedals for musicians.")
	html_input = st.text_area("Paste Raw HTML", "<html><head></head><body><h1>Sample</h1></body></html>", height=250)
	if st.button("Optimize HTML"):
		keywords = [kw.strip() for kw in kw_input.split(",")]
		optimized_html = optimize_html_page(html_input, title, desc, keywords)
		st.text_area("Optimized HTML", optimized_html, height=250)

with tab4:
	st.subheader("🧪 Quick SEO Health Check")
	domain = st.text_input("Website URL", "https://example.com")
	if st.button("Run Check"):
		result = check_robots_txt(domain)
		st.write(result)

with tab5:
	st.subheader("📤 Export")
	if "blog" in st.session_state:
		st.download_button("Download Blog Post", st.session_state["blog"], file_name="blog_post.txt")
	else:
		st.write("No blog post generated yet.")
