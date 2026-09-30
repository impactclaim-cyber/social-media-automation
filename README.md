# Impact Solution Social Media Automator

A free local automation tool for Impact Solution that:
- creates branded flyers/images locally using Python and Pillow
- generates captions for Instagram/Facebook posts
- saves final images to your Desktop
- sends an update summary to you
- posts to your Meta Business Page when credentials are configured

Important note:
- This project is designed to be free to run locally.
- Meta posting needs your Facebook/Instagram business account permissions and a valid Meta app token.
- Canva use is optional. You can either upload custom Canva designs or create branded flyers locally with this script.

## Features
- Flyer generator with Impact Solution brand colors and style
- Post caption generator
- Desktop file saving
- Meta Business posting (optional)
- Email update notification (optional)
- Dry-run mode for testing without posting

## Tech stack
- Python 3.10+
- Pillow
- requests
- python-dotenv

## Local setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in your values.

```bash
cp .env.example .env
```

5. Run the script in dry-run mode to preview:

```bash
python app.py --dry-run --service "Business Insurance"
```

6. To generate and post for real:

```bash
python app.py --service "Motor Insurance" --post
```

## Required environment values
See `.env.example` for all supported variables.

Minimum values for local generation:
- `COMPANY_NAME=Impact Solution`
- `DESKTOP_PATH=/Users/yourname/Desktop`

Optional for Meta posting:
- `META_PAGE_ID=`
- `META_ACCESS_TOKEN=`
- `META_APP_ID=`
- `META_APP_SECRET=`

Optional for email updates:
- `SMTP_HOST=`
- `SMTP_PORT=`
- `SMTP_USERNAME=`
- `SMTP_PASSWORD=`
- `EMAIL_TO=`

## Usage examples

Generate a flyer only:
```bash
python app.py --service "Home Insurance" --dry-run
```

Generate a flyer and save to Desktop:
```bash
python app.py --service "Family Protection" --save-only
```

Generate, save, and post to Meta:
```bash
python app.py --service "Business Insurance" --post
```

## Generated output
The script saves files to:
- your Desktop by default
- `output/` folder inside the project as a backup

Files created include:
- `Impact_Solution_Business_Insurance.png`
- `caption.txt`
- `summary.txt`

## Notes
- If no Meta credentials are given, the app still generates the flyer and caption locally.
- If no AI provider is configured, the script uses a strong default caption template suited to Insurance & Protection businesses.
- For Canva integration, you can manually export your own design and drop it into the project, or replace the local flyer generation logic with your Canva export flow.

## Disclaimer
This project is intended for lawful business use and transparent posting. You are responsible for making sure your Meta account, content, and ad/post compliance match your business policies.
