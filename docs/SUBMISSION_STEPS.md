# Publish and submit: simple Windows/browser walkthrough

**Deadline:** Friday, 30 October 2026, **11:59 PM Rwanda time**, according to the official NISR **2026** hackathon page. Registration closed October 20, so this process assumes your two-student team already registered.

**Your final NISR form needs only two project URLs:** (1) public GitHub source repository and (2) deployed web application. Your team name, leader contact and chosen track are separate fields. A standalone video or PowerPoint upload field is not shown in the submitted 2026 form.

## Step 1 — Extract the project ZIP on Windows

**Application:** Windows File Explorer. **Effect:** creates local files; does not upload or publish.

1. Download `CropBalance_Rwanda_2026_Submission.zip` from this chat.
2. Right-click the ZIP → **Extract All…** → **Extract**.
3. Open the extracted folder. You should see **`app.py`**, **`requirements.txt`**, **`README.md`**, **`DECLARATION.md`**, and the **`src`**, **`data`**, **`docs`**, and **`scripts`** folders.
4. Open `README.md` and `DECLARATION.md` in any text editor and fill in the real team name, members and truthful declaration. Do not edit any data figure unless you have checked the source.

## Step 2 — Create a PUBLIC GitHub repository

**Application:** Chrome/Edge browser → https://github.com/new. **Effect:** creates a public repository that others can see.

1. Sign in or create a free GitHub account.
2. Repository name: `cropbalance-rwanda-2026` (or another available name).
3. Description (optional): `NISR 2026 Big Data Hackathon — Rwanda agricultural utilization and production forecast`.
4. Choose **Public** — the NISR rules require a public GitHub link.
5. Leave **Add a README file** unchecked for this upload method; leave `.gitignore` / license as **None**.
6. Click **Create repository**.

If you already created the repository and it is private, go to **Settings → General → Danger Zone → Change repository visibility → Make public**. Do not do this if the repository contains secrets or unrelated private files; instead, create a new clean repository.

## Step 3 — Upload the PROJECT FILES (not the ZIP)

**Application:** GitHub repository page + Windows File Explorer. **Effect:** publishes the contents of your project.

1. On the empty repository page, select **uploading an existing file** (or **Add file → Upload files** if not empty).
2. In Windows File Explorer, open the **extracted project folder** (not the ZIP).
3. Drag the **contents of the extracted folder**, including `app.py`, `requirements.txt`, `README.md` and the `data`, `docs`, `src`, `scripts` folders, into the GitHub upload area. Do **not** upload the ZIP alone.
4. If your browser does not accept folders, drag the folders one by one, or use GitHub Desktop/Cursor. Ensure that the website preserves the correct folder structure.
5. Scroll down to the Commit section; enter a message such as `Initial NISR 2026 hackathon prototype` and click **Commit changes**.
6. Confirm the repository main page shows **`app.py` and `requirements.txt` at the TOP LEVEL**. If they are inside an extra `CropBalance_Rwanda_2026` folder, the deployment entrypoint is not at root and you will need to use that nested path when deploying.

**Your first submission URL:** copy the repository URL from the browser address bar, like `https://github.com/your-account/cropbalance-rwanda-2026`. Do not use this example as your actual link.

## Step 4 — Put the app online (Streamlit Community Cloud)

**Application:** Chrome/Edge browser → https://share.streamlit.io. **Effect:** publicly deploys the Streamlit app from GitHub.

1. Open https://share.streamlit.io and sign in with **GitHub**; authorize the necessary access.
2. Click **Create app** → **Yup, I have an app**.
3. Select **your GitHub repository**, the **`main`** branch, and **`app.py`** as the entrypoint/main file path.
4. Advanced settings: keep/default **Python 3.12** (or pick a supported Python version); this project does not need secrets or passwords.
5. Click **Deploy**. Streamlit will read `requirements.txt`, install libraries, and launch the app.
6. Confirm you see the CropBalance Rwanda dashboard with four tabs and 15 commodities. Try changing a sidebar slider.
7. Copy the live address ending in **`.streamlit.app`**. Streamlit may assign a different address from your preferred name.
8. Check the live link in a private/incognito tab, **without signing in**, and on a mobile device if convenient. If a log-in screen appears, ensure your repository and app sharing are public.

**Your second submission URL:** the actual `https://something.streamlit.app/` that is working in your browser.

Official deployment guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Step 5 — Double-check project completeness

At https://github.com/your-account/cropbalance-rwanda-2026, make sure `README.md`, `DECLARATION.md`, `docs/METHODOLOGY.md`, `docs/DATA_SOURCES.md`, `app.py`, `requirements.txt`, and the source dataset are included.

- Open the README and replace the app URL placeholder with your real Streamlit link. This GitHub change will update the public README.
- Review and complete the AI-assistance/originality statement accurately with your teammate.
- Test the app's **National outlook**, **Commodity explorer**, **Forecast checks**, and **Data & method** tabs.
- Keep your real team ID/student card eligibility documents available if NISR asks.

## Step 6 — Complete the official NISR 2026 submission form

**Application:** NISR website in Chrome/Edge. **Effect:** submits your project officially.

Open the 2026 competition page: https://statistics.gov.rw/about/hackathon/2026-hackathon-competition and click the **Submit Hackathon Entry** link. In the submission form:

| Form field | Enter/select |
|---|---|
| TEAM NAME / TEAM NAME (Alphabetical P–Z) | Choose the **exact registered team** from the appropriate dropdown; only one name should be selected |
| Team Leader's Email | Registered team leader's real email |
| Team Leader's phone contact | Registered leader's reachable +250 number |
| Topic chosen for the project | **TRACK 1: Agricultural Productivity** |
| GitHub Repository URL | Your actual public `https://github.com/...` repository URL |
| GitHub Link Title (if shown) | `CropBalance Rwanda — GitHub Repository` |
| Deployed Web/App URL | Your actual public `https://....streamlit.app` URL |
| App Link Title (if shown) | `CropBalance Rwanda — Live Dashboard` |

Click **Submit** and save a screenshot of any submission confirmation. Do **not** substitute a PDF, ZIP file, YouTube video or PPTX link for either URL field.

## If something breaks

- **GitHub link says 404:** repository may still be private or URL copied incorrectly.
- **Streamlit says file not found:** make sure `app.py` is at the repository root, or correct the selected entrypoint path.
- **ModuleNotFoundError:** ensure `requirements.txt` is committed in the repository and its install completed; check the Streamlit app logs.
- **The app shows a traceback:** copy the entire error and which tab it came from. Do not submit until it is resolved.
- **Your team name is missing from NISR's dropdown:** NISR lists `prosper.ayinebyona@statistics.gov.rw` (and `competition@statistics.gov.rw`) and telephone **0786 872 057**. Registration deadline was 20 October 2026; do not create an unregistered fake team name.

## Critical 2026 rule reminders

The official 2026 rules require **two enrolled undergraduate/master's students**, at least one Rwandan, public GitHub, deployed app, documentation, truthful originality and AI-use disclosure, and agreement to NISR's intellectual-property assignment. Review those terms before clicking Submit.
