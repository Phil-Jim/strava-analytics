# Strava Analytics Dashboard

A comprehensive Django web application for analyzing your Strava activities with interactive charts and detailed statistics.

## Features

🏃‍♂️ **Activity Analysis**
- Track runs, rides, swims, walks, and other activities
- Analyze distance, time, speed, and elevation data
- View personal records and achievements

📊 **Interactive Dashboard**
- Real-time charts using Chart.js
- Filter by activity type and time period
- Monthly and weekly trend analysis
- Day-of-week activity patterns

🔄 **Strava Integration**
- Automatic activity synchronization
- Secure OAuth authentication
- Rate-limited API calls
- Refresh token handling

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Strava account
- Strava API application (create at https://www.strava.com/settings/api)

### 2. Installation

```bash
# Install dependencies
pip install --user --break-system-packages django requests pandas python-dotenv

# Create database
python3 manage.py makemigrations
python3 manage.py migrate
```

### 3. Strava API Configuration

1. Go to https://www.strava.com/settings/api
2. Create a new application
3. Note your Client ID and Client Secret
4. Update the `.env` file with your credentials:

```env
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here
STRAVA_ACCESS_TOKEN=your_access_token_here
STRAVA_REFRESH_TOKEN=your_refresh_token_here
```

### 4. Getting Access Tokens

To get your access token and refresh token, you need to complete the OAuth flow:

1. Visit this URL (replace YOUR_CLIENT_ID):
```
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:8000/auth&approval_prompt=force&scope=read,activity:read_all
```

2. Authorize the application and copy the code from the redirect URL

3. Exchange the code for tokens:
```bash
curl -X POST https://www.strava.com/oauth/token \
  -F client_id=YOUR_CLIENT_ID \
  -F client_secret=YOUR_CLIENT_SECRET \
  -F code=YOUR_CODE \
  -F grant_type=authorization_code
```

4. Update your `.env` file with the returned access_token and refresh_token

### 5. Sync Your Activities

```bash
# Sync all activities (this may take a while)
python3 manage.py sync_strava

# Sync only recent activities (last 7 days)
python3 manage.py sync_strava --recent 7

# Limit the number of activities
python3 manage.py sync_strava --limit 100
```

### 6. Start the Server

```bash
python3 manage.py runserver 8000
```

Visit http://localhost:8000 to view your dashboard!

## Usage

### Dashboard Features

- **Stats Cards**: Overview of total activities, distance, time, and average speed
- **Filters**: Filter by time period (week/month/year/all) and activity type
- **Charts**:
  - Activity type distribution (doughnut chart)
  - Monthly trends (line chart)
  - Weekly activity levels (bar chart)
  - Day of week analysis (radar chart)
- **Activities Table**: Recent activities with details

### API Endpoints

The application provides several API endpoints for custom integrations:

- `/api/stats/` - Summary statistics
- `/api/breakdown/` - Activity type breakdown
- `/api/monthly-trends/` - Monthly activity trends
- `/api/weekly-trends/` - Weekly activity trends
- `/api/personal-records/` - Personal records and achievements
- `/api/day-of-week/` - Day of week activity patterns
- `/api/activities/` - Activity list with filtering

### Data Analysis Features

- **Time-based Analysis**: View trends over days, weeks, months, and years
- **Activity Type Filtering**: Focus on specific activities (runs, rides, etc.)
- **Personal Records**: Track your longest distances, fastest speeds, etc.
- **Performance Metrics**: Analyze pace, speed, elevation, heart rate, and power data

## Data Privacy

This application:
- Stores activity data locally in your SQLite database
- Only requests read access to your Strava activities
- Does not share your data with third parties
- Allows you to control what data is synced

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Check your Strava API credentials in `.env`
2. **Rate Limiting**: Strava limits API calls - the sync includes delays to prevent hitting limits
3. **Missing Activities**: Run `python3 manage.py sync_strava` to sync recent activities

### Manual Token Refresh

If your access token expires, the application will attempt to refresh it automatically. If this fails, you may need to re-authorize the application.

## Development

The application is built with:
- **Backend**: Django 5.2, Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **API**: Strava API v3

### Project Structure

```
strava-analytics/
├── activities/           # Main Django app
│   ├── models.py        # Activity and summary models
│   ├── views.py         # API and dashboard views
│   ├── analytics.py     # Data analysis logic
│   ├── strava_service.py # Strava API integration
│   └── templates/       # HTML templates
├── strava_analytics/    # Django project settings
└── manage.py           # Django management script
```

## License

This project is for personal use. Please respect Strava's API terms of service.