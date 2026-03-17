import os
import asyncio
import csv
import base64
from dotenv import load_dotenv
from groq import Groq
from playwright.async_api import async_playwright

# Load .env file
load_dotenv()

# --- AI INTEGRATION (GROQ) ---
API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def analyze_screenshot_with_vision(image_path):
    try:
        base64_image = encode_image(image_path)
        
        prompt = "Look at this screenshot of a webinar page taken after a form was submitted. Is there a video player or embedded iframe (like youtube/vidyard/vimeo) cleanly visible on the page? Does the page look fully loaded without visual overlapping or obvious UI errors? Reply starting with 'PASS:' and a short sentence if it looks good, or 'FAIL:' and a 1-sentence reason if it doesn't."
        
        # Using Llama 3.2 Vision Preview on Groq
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

async def analyze_test_report(csv_path):
    """Generates an AI summary of the test execution based on the CSV report."""
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
            
        prompt = f"You are an expert SDET and QA Lead analyzing automated test results.\n\nHere is the CSV output of an automated test run that checked webinar forms and validated the presence of a video using AI Vision.\n\n{csv_content}\n\nWrite a 3-sentence professional summary of the test execution. In the summary, highlight the success rate and note any failures that need engineering attention. Do not use markdown formatting, just clear, professional plain text."
        
        # Using Llama 3.3 70B for the text analysis
        chat_completion = await asyncio.to_thread(
            client.chat.completions.create,
            messages=[
                {"role": "system", "content": "You are a professional SDET Lead."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary Error: {str(e)}"

# --- PLAYWRIGHT AUTOMATION ---
async def fill_form(page, url, sitecore_id, status):
    print(f"\nNavigating to {url}...")
    result_status = "UNKNOWN"
    reason = ""
    clean_id = sitecore_id.replace("{", "").replace("}", "").strip()
    screenshot_path = f"screenshot_{clean_id}.png"

    try:
        await page.goto(url, timeout=60000)
        
        # Form filling Phase
        print("Filling out email to reveal the rest of the form...")
        first_name_val = "bwong"
        email_address = f"{first_name_val}+{clean_id}+{status.strip()}@enuat.com"
        
        email_locator = page.locator('[data-sc-field-name="email"]')
        await email_locator.wait_for(state='visible', timeout=30000)
        await email_locator.fill(email_address)
        await email_locator.press("Tab")

        print("Waiting for hidden fields to appear...")
        first_name_locator = page.locator('[data-sc-field-name="firstName"]')
        await first_name_locator.wait_for(state='visible', timeout=15000)

        print("Filling out the rest of the form fields...")
        await first_name_locator.fill(first_name_val)
        await page.locator('[data-sc-field-name="lastName"]').fill("Doe")
        await page.locator('[data-sc-field-name="phone"]').fill("0417406590")
        await page.locator('[data-sc-field-name="company"]').fill("Extreme Company")
        await page.locator('[data-sc-field-name="title"]').fill("Quality Assurance Engineer")

        await page.locator('[data-sc-field-name="industry"]').select_option("Technology")
        await page.locator('[data-sc-field-name="country"]').select_option("Germany")

        # Handle cookie banner
        try:
            cookie_btn = page.locator('#onetrust-accept-btn-handler')
            if await cookie_btn.count() > 0:
                await cookie_btn.click(timeout=3000)
        except Exception:
            pass

        # Check the consent checkbox
        await page.locator('[data-sc-field-name="Prv_Consent_to_Unsubscribe1"]').evaluate("el => el.click()")

        print("Form filled out successfully. Submitting...")
        await page.locator('input[type="submit"][value="Submit"]').click(force=True)

        # Wait a moment for the post-submission page to load fully
        await page.wait_for_timeout(5000)
        
        # --- VALIDATION PHASE ---
        print("Taking screenshot for Llama Vision Validation...")
        await page.screenshot(path=screenshot_path, full_page=True)

        print("Sending screenshot to Groq (Llama 3.2 Vision) for perceptual validation...")
        ai_verdict = await analyze_screenshot_with_vision(screenshot_path)
        print(f"🤖 Groq Verdict: {ai_verdict}")
        
        if "PASS" in ai_verdict.upper():
            result_status = "PASS"
            reason = f"Vision Confirmed: {ai_verdict}"
        else:
            result_status = "FAIL"
            reason = f"Vision Rejected: {ai_verdict}"

    except Exception as e:
        print(f"❌ FAIL (Error): {e} on {url}\n")
        result_status = "FAIL"
        reason = f"Error: {e}"

    return {"url": url, "sitecore_id": sitecore_id, "test_status": result_status, "reason": reason}

def read_test_data(csv_file="form_data.csv"):
    data = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Please create it first.")
    return data

async def main():
    test_data = read_test_data("form_data.csv")
    
    if not test_data:
        print("No test data found. Exiting.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        results = []
        for row in test_data:
            url = row.get('url')
            sitecore_id = row.get('sitecore_id')
            status = row.get('status')
            
            if url and sitecore_id and status:
                res = await fill_form(page, url, sitecore_id, status)
                results.append(res)
            else:
                print(f"Skipping row due to missing values: {row}")

        await browser.close()
        
        print("\n========================================")
        print("        TEST EXECUTION SUMMARY          ")
        print("========================================")
        passed_count = sum(1 for r in results if r['test_status'] == 'PASS')
        failed_count = len(results) - passed_count
        print(f"Total Forms Processed:     {len(results)}")
        print(f"Passed (Vision Confirmed): {passed_count}")
        print(f"Failed / Warnings:         {failed_count}")
        
        report_file = "ai_test_report.csv"
        try:
            with open(report_file, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["url", "sitecore_id", "test_status", "reason"])
                writer.writeheader()
                writer.writerows(results)
            print(f"\nDetailed test report saved to {report_file}")
        except PermissionError:
            print(f"\n❌ ERROR: Could not save {report_file} because it is open in another program (like Excel). Please close it and run the script again.")
            return

        # Generate Final AI Report Summary
        print("\nGenerating AI Executive Summary on Groq...")
        ai_summary = await analyze_test_report(report_file)
        print("\n🤖 GROQ AI EXECUTIVE SUMMARY:")
        print(ai_summary)
        print("========================================")

if __name__ == "__main__":
    asyncio.run(main())


