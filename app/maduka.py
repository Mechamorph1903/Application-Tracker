#Job Site Scraping Logic
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import requests
import json
from playwright.sync_api import sync_playwright
load_dotenv()
api_key = os.getenv("CLAUDE_KEY")



def scrapeJob(url):
	sehski = { # JSON data of 
		"Status": False,
		"Data": ""
		} 
		

	driver = None

	try:
		with sync_playwright() as p:
			browser = p.chromium.launch(
				headless=True,
				args=["--no-sandbox", "--disable-dev-shm-usage"]
)
			page = browser.new_page()
			page.goto(url, timeout=30000)
			page.wait_for_load_state("networkidle", timeout=15000)
			
			content = page.content()
			browser.close()
		soup = BeautifulSoup(content, "html.parser")
		jusText = soup.get_text()

		keywords = keywords = [
		# role related
		"candidate", "candidates", "hiring", "applicant", "applicants",
		"apply", "application", "opening", "vacancy", "vacancies", "position",
		
		# job details
		"salary", "compensation", "benefits", "bonus", "equity", "pay range",
		"full time", "part time", "contract", "remote", "hybrid", "on site",
		
		# location
		"location", "locations", "relocation", "based in", "office",
		
		# requirements
		"experience", "requirements", "qualifications", "skills", "responsibilities",
		"bachelor", "degree", "years of experience", "preferred", "required",
		
		# company language
		"team", "role", "opportunity", "join us", "we are looking",
		"about the role", "about us", "what you will do", "what we offer"
		]

		if any(word in jusText.lower() for word in keywords):
			print("This got one of the words innit")
			sehski["Status"] =  True
			sehski["Data"] = jusText
		else:
			print("This don't look like a job site big man")
	except Exception as e:
			print(f"Something went wrong with driver creation: {e}")
			sehski["reason"] = str(e)

	return sehski



def getFormData(url):

	job = scrapeJob(url)

	if not job["Status"]:
		print("Not worth the API Call, refer them to manual entry")
		return False

	prompt = f"""
		You are a job posting parser. Your only job is to extract structured data 
		from the raw text of a job posting and return it as valid JSON.

		Here is the text: {job["Data"]}

		EXTRACTION FIELDS:
		- job_name: The full title of the position including any ID codes 
		(e.g. "2026 Summer Intern, Junior Electrician [RBSN19990]")
		- company_name: The hiring company. Hint — they usually appear repeatedly 
		and in phrases like "At [company]..." or "[company] is a..."
		- location: All locations where the position is available
		- role_name: The core role being hired for 
		(e.g. Software Engineer, Team Lead, Medical Intern)
		- work_arrangement: One of — Remote, Hybrid, On-Site, or Not Specified. Must be one of these oprions no other words
		- deadline: Application deadline date if mentioned, otherwise null
		- job_description: The full role description including responsibilities, 
		requirements, qualifications, compensation and benefits

		STATUS FIELDS:
		- status: true if extraction was successful, false if the text provided 
		is not a recognisable job posting or is missing too many fields
		- reason: null on success, brief explanation string on failure

		RULES:
		- Return ONLY valid JSON. No markdown, no code blocks, no explanation text.
		- If a field cannot be found set it to null, do not guess or fabricate.
		- Do not add any fields beyond those specified above.

		Return exactly this structure:
		{{
		"status": true,
		"reason": null,
		"job_name": "...",
		"company_name": "...",
		"location": "...",
		"role_name": "...",
		"work_arrangement": "...",
		"deadline": null,
		"job_description": "..."
		}}

		AGAIN RULES:
		- Return ONLY valid JSON. No markdown, no code blocks, no explanation text.
		- If a field cannot be found set it to null, do not guess or fabricate.
		- Do not add any fields beyond those specified above.
	"""

	api_url = "https://api.anthropic.com/v1/messages"

	headers = {
			"x-api-key": api_key,
			"anthropic-version": "2023-06-01",
			"content-type": "application/json",
		}
	data = {
			"model": "claude-haiku-4-5-20251001",
			"max_tokens": 1024,
			"messages": [{
				"role": "user",
				"content": prompt
			}]
		}
	
	response = requests.post(api_url, headers=headers, json=data)

	if response.ok:
		response_data = response.json()["content"][0]["text"]
		text = response_data.replace("```json", "").replace("```", "").strip()
		job_data = json.loads(text)
		return job_data
