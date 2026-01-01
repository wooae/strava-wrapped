# Strava Wrapped 🎁✨

A fun project to generate Instagram-style "Wrapped" summaries from your Strava activity data for the year. It creates visual summaries highlighting your top sports, total distances, elevations, times, and weekly activity patterns.

## Features

- Generates summary graphics for Run and Ride activities (more coming)
- Calculates average and peak weekly distances for each activity type
- Displays total stats including distance, elevation, and time
- Highlights your longest and most popular activities


## Prerequisites

- Python 3.8+
- Strava API access

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/wooae/strava-wrapped.git
   cd strava-wrapped
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```


## Usage

1. **Run the script:**
   ```bash
   python strava_wrapped.py
   ```

2. **OAuth Authorization (single time):**
   - The script will prompt you to authorize the app
    ```
    Open this URL in your browser and authorize the app:

    https://www.strava.com/oauth/authorize?client_id=191048&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,activity:read_all
    ```
   - Open the provided URL in your browser
   - Authorize the app and copy the authorization code from the URL
     - http://localhost/exchange_token?state=&code=AUTHORIZATION_CODE_HERE&scope=read,activity:read_all
     - Do not be alarmed to see an Unable to connect error - we are not actually running a server on localhost. Strava already generated the authorization code in the URL, which is all we need to continue.
   - Paste the code back into the terminal
   - This step will create a local file `strava_tokens.json`, which will contain your access token that you will use to access the Strava API. You only need to do the OAuth Authorization once, then the script will automatically refresh the tokens (Strava access tokens expire every 6 hours) for you in `strava_tokens.json` so that you can run the script again in the future.

3. **Wait for processing:**
   - The script will fetch your activities for the specified year
   - Generate summary images for Run and Ride activities (or other top sports)

4. **View results:**
   - Check the generated image files: `Run_wrapped.png`, `Ride_wrapped.png`, etc.

## Output Files

- `{sport}_wrapped.png`: Detailed summary for each sport (e.g., Run, Ride)
- `strava_summary_{year}.png`: Overview of top sports
- `strava_activities_{year}.csv`: Raw activity data

## Customization

- Modify `YEAR` in `strava_wrapped.py` to analyze different years
- Adjust colors, fonts, and layout in `constants.py`
- Add more sports by updating the logic in `main()`

## Notes

- The script calculates weekly distances only for full weeks (Monday-Sunday) within the year, excluding partial weeks at the beginning and end
- Activities are grouped by sport type, and summaries are generated for the top sports with the most activities

## License

This project is for personal use. Please respect Strava's API terms of service.
