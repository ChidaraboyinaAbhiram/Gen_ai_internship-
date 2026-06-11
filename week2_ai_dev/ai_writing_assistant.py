# ai_writing_assistant.py
# streamlit run ai_writing_assistant.py
import streamlit as st
import json
import os
from datetime import datetime
import utils.groq_client as groq_client
import utils.gemini_client as gemini_client
from utils.prompts import PROMPTS
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
	page_title='AI Writing Assistant',
	page_icon='✍️',
	layout='wide',
	initial_sidebar_state='expanded'
)

# ── Custom CSS styling ────────────────────────────────────────────────────
st.markdown("""
<style>
	/* Make sidebar and main container feel cohesive and premium */
	.main .block-container {
		padding-top: 2rem;
		padding-bottom: 2rem;
	}
	.stButton>button {
		border-radius: 8px;
		transition: all 0.3s ease;
	}
	.stButton>button:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}
	/* Success messages */
	div.stSuccess {
		border-radius: 8px;
		border-left: 5px solid #2ecc71;
	}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────
if 'history' not in st.session_state:
	st.session_state.history = []
if 'last_output' not in st.session_state:
	st.session_state.last_output = ''

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
	st.title('✍️ AI Writing Assistant')
	st.caption('ContentCo Internal Tool')
	st.divider()

	st.subheader('Model Configuration')
	provider = st.selectbox('API Provider', ['Groq', 'Gemini'])

	# Load keys from environment
	env_groq_key = os.getenv('GROQ_API_KEY', '')
	env_gemini_key = os.getenv('GEMINI_API_KEY') or os.getenv('gemini_key', '')

	if provider == 'Groq':
		model = st.selectbox('Model', ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant'], index=0)
		api_key = st.text_input('Groq API Key', type='password', value=env_groq_key, help='Override default Groq API Key')
	else:
		model = st.selectbox('Model', ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.5-flash'], index=0)
		api_key = st.text_input('Gemini API Key', type='password', value=env_gemini_key, help='Override default Gemini API Key')

	st.divider()
	brand = st.text_input('Brand / Company Name', value='ContentCo')
	tone = st.selectbox('Default Tone', ['Professional', 'Casual', 'Formal', 'Friendly', 'Persuasive'])
	temperature = st.slider('Creativity', 0.0, 1.5, 0.7, 0.1, help='0=focused/factual 1.5=creative/varied')
	st.divider()
	st.metric('Content Generated Today', len(st.session_state.history))
	if st.button('🗑️ Clear History'):
		st.session_state.history = []
		st.rerun()
	st.caption(f'Powered by {provider} ({model}) · Brand: {brand} · Tone: {tone}')


# ── Wrapper functions to route requests based on active provider ─────────
def generate(system_prompt, user_prompt, temperature=0.7, max_tokens=1000):
	if provider == 'Groq':
		return groq_client.generate(system_prompt, user_prompt, temperature, max_tokens, model=model, api_key=api_key)
	else:
		return gemini_client.generate(system_prompt, user_prompt, temperature, max_tokens, model=model, api_key=api_key)


def translate_content(text, target_language):
	if provider == 'Groq':
		return groq_client.translate_content(text, target_language, api_key=api_key)
	else:
		system_prompt = f'You are an expert translator. Translate to {target_language}. Return ONLY the translation.'
		return gemini_client.generate(system_prompt, text, temperature=0.1, max_tokens=1000, model=model, api_key=api_key)

# ── Tabs ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(['📝 Blog', '📧 Email', '📱 Social Media', '📣 Ad Copy', '🌐 Translate'])


def save_and_display(content, content_type):
	st.session_state.last_output = content
	st.session_state.history.append({
		'type': content_type,
		'content': content,
		'time': datetime.now().strftime('%H:%M')
	})
	st.success(f'✅ {content_type} generated!')
	st.write(content)
	col1, col2 = st.columns(2)
	col1.download_button('📥 Download .txt', content, f'{content_type.lower()}_{datetime.now().strftime("%H%M")}.txt')
	col2.download_button('📋 Download .md', content, f'{content_type.lower()}_{datetime.now().strftime("%H%M")}.md')


# TAB 1 — Blog Post
with tab1:
	st.subheader('📝 Blog Post Generator')
	c1, c2, c3 = st.columns(3)
	topic = c1.text_input('Topic', placeholder='AI in Indian Agriculture')
	audience = c2.selectbox('Audience', ['General Public', 'Students', 'Professionals', 'Executives'])
	length = c3.select_slider('Length (words)', [300, 500, 800, 1200, 1500], value=800)
	keywords = st.text_input('SEO Keywords', placeholder='AI, farming, technology, India')
	sections = st.slider('Number of Sections', 3, 8, 4)
	if st.button('Generate Blog Post', type='primary', key='blog'):
		if topic:
			with st.spinner('Writing your blog post...'):
				prompt = PROMPTS['blog']['user'].format(
					length=length, topic=topic, audience=audience, tone=tone, keywords=keywords, sections=sections
				)

				result = generate(PROMPTS['blog']['system'], prompt, temperature, length * 2)
				save_and_display(result, 'Blog Post')


# TAB 2 — Email
with tab2:
	st.subheader('📧 Email Generator')
	c1, c2 = st.columns(2)
	purpose = c1.selectbox('Purpose', ['Job Application', 'Partnership Proposal', 'Follow-Up', 'Meeting Request', 'Product Pitch', 'Thank You', 'Complaint'])
	recipient = c2.text_input('Recipient Role', placeholder='CEO, HR Manager, Client...')
	context = st.text_area('Your Context & Key Points', height=100, placeholder='What do you want to communicate?')
	if st.button('Generate Email', type='primary', key='email'):
		if context:
			with st.spinner('Drafting your email...'):
				prompt = PROMPTS['email']['user'].format(purpose=purpose, recipient=recipient, context=context, tone=tone)
				result = generate(PROMPTS['email']['system'], prompt, max_tokens=600, temperature=max(0, temperature - 0.1))
				save_and_display(result, 'Email')


# TAB 3 — Social Media
with tab3:
	st.subheader('📱 Social Media Content')
	c1, c2, c3 = st.columns(3)
	sm_topic = c1.text_input('Topic / Message')
	platform = c2.selectbox('Platform', ['LinkedIn', 'Twitter/X', 'Instagram', 'WhatsApp', 'YouTube'])
	num_posts = c3.number_input('Number of Post Variations', 1, 5, 3)
	use_emoji = st.checkbox('Include Emojis', value=True)
	use_tags = st.checkbox('Include Hashtags', value=True)
	char_map = {'LinkedIn': 3000, 'Twitter/X': 280, 'Instagram': 2200, 'WhatsApp': 500, 'YouTube': 5000}
	if st.button('Generate Posts', type='primary', key='social'):
		if sm_topic:
			with st.spinner(f'Creating {num_posts} {platform} posts...'):
				prompt = f"""Create {num_posts} different {platform} post variations about:
{sm_topic}
Brand: {brand}. Tone: {tone}. Character limit: {char_map[platform]}.
{"Include emojis." if use_emoji else ""}
{"Include 3-5 hashtags." if use_tags else ""}
Separate each variation with ---"""
				result = generate('You are a social media expert.', prompt, temperature=min(1.5, temperature + 0.1), max_tokens=1000)
				save_and_display(result, f'{platform} Posts')


# TAB 4 — Ad Copy
with tab4:
	st.subheader('📣 Ad Copy Generator')
	c1, c2 = st.columns(2)
	product = c1.text_input('Product / Service', placeholder='AI Writing Tool')
	usp = c2.text_input('Unique Selling Point', placeholder='10x faster content creation')
	c3, c4 = st.columns(2)
	ad_audience = c3.text_input('Target Audience', placeholder='Marketing professionals')
	cta = c4.text_input('Call to Action', placeholder='Start Free Trial')
	ad_platform = st.selectbox('Ad Platform', ['Google Ads', 'Facebook/Instagram', 'LinkedIn Ads', 'Banner Ad'])
	if st.button('Generate Ad Copy', type='primary', key='ad'):
		if product:
			with st.spinner('Creating your ad copy...'):
				prompt = PROMPTS['ad']['user'].format(product=product, usp=usp, audience=ad_audience, platform=ad_platform, cta=cta, tone=tone)
				result = generate(PROMPTS['ad']['system'], prompt, temperature, max_tokens=500)
				save_and_display(result, 'Ad Copy')


# TAB 5 — Translate
with tab5:
	st.subheader('🌐 Content Translator')
	use_last = st.checkbox('Translate last generated content', value=True)
	if use_last and st.session_state.last_output:
		to_translate = st.session_state.last_output[:2000]
		st.info('Using last generated content')
	else:
		to_translate = st.text_area('Paste content to translate', height=150)
	target_langs = st.multiselect('Translate to', ['Hindi', 'Telugu', 'Tamil', 'Bengali', 'Marathi', 'Kannada', 'Malayalam', 'Gujarati'], default=['Hindi', 'Telugu'])
	if st.button('Translate All', type='primary', key='trans') and to_translate:
		cols = st.columns(len(target_langs) if target_langs else 1)
		for i, lang in enumerate(target_langs):
			with cols[i]:
				with st.spinner(f'Translating to {lang}...'):
					result = translate_content(to_translate, lang)
					st.subheader(lang)
					st.write(result)
					st.download_button(f'📥 {lang}', result, f'content_{lang.lower()}.txt', key=f'dl_{lang}')


# ── History panel ─────────────────────────────────────────────────────────
if st.session_state.history:
	st.divider()
	with st.expander(f'📚 Session History ({len(st.session_state.history)} items)'):
		for i, item in enumerate(reversed(st.session_state.history)):
			st.caption(f"{item['time']} — {item['type']}")
			st.write(item['content'][:200] + '...')

	st.divider()