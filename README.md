# Kilometerregistratie PWA

Een mobile-first Progressive Web App (PWA) voor kilometerregistratie van Nederlandse zakelijke lease auto's, gebouwd met Python Reflex.

## Features

- 🚗 **Nederlandse Lease Auto's**: Speciaal ontworpen voor zakelijke rijders en lease auto's
- 📱 **Mobile-First Design**: Geoptimaliseerd voor mobiele apparaten
- 🔐 **Gebruikersauthenticatie**: Eenvoudige username/password authenticatie via omgevingsvariabelen
- 💾 **SQLite Database**: Lichtgewicht database voor kilometerregistratie en voertuiggegevens
- 🔔 **Webhook Notificaties**: Stuur notificaties naar Home Assistant of andere webhook endpoints
- 🌍 **Nederlands & Engels**: Nederlandse interface met Engelse fallback
- 📊 **Kilometerregistratie**: Registreer start/eindlocatie, kilometerstand, doel, en kosten
- 🚙 **Voertuigbeheer**: Beheer meerdere lease auto's met kenteken, merk, en model
- 💰 **Kostenregistratie**: Brandstof, parkeren, en tolkosten
- 📈 **Maandoverzicht**: Automatische berekening van zakelijke kilometers en vergoedingen
- ⚡ **PWA Features**: Installeerbare app met offline mogelijkheden
- 🐳 **Docker Support**: Eenvoudige deployment met Docker Compose

## Quick Start

### 1. Clone en Setup

```bash
git clone <repository-url>
cd kilometerregistratie-pwa
```

### 2. Maak Environment File

```bash
cp .env.example .env
```

Bewerk `.env` met je inloggegevens:
```bash
AUTH_USERNAME=jouw_gebruikersnaam
AUTH_PASSWORD=jouw_veilige_wachtwoord
```

### 3. Start met Docker Compose

```bash
docker-compose up -d
```

De app is beschikbaar op `http://localhost:3000`

### 4. Installeer als PWA

1. Open de app in je mobiele browser
2. Tap "Toevoegen aan startscherm" (iOS) of "App installeren" (Android)
3. De app wordt geïnstalleerd als een native-achtige applicatie

## Nederlandse Belasting & Lease Compliance

### Zakelijke Kilometers
- **Zakelijk**: Volledig aftrekbaar voor belasting, vergoeding €0,23/km (2024)
- **Privé**: Niet aftrekbaar
- **Woon-werk**: Beperkt aftrekbaar afhankelijk van situatie

### Registratieplicht
De app helpt bij het voldoen aan Nederlandse registratieplichten voor:
- Zakelijke lease auto's
- Belastingaangifte (IB/VPB)
- Lease maatschappij rapportage
- BTW verantwoording

## Configuratie

### Authenticatie

Stel je inloggegevens in via het `.env` bestand:
- `AUTH_USERNAME`: Je gebruikersnaam (standaard: admin)
- `AUTH_PASSWORD`: Je wachtwoord (standaard: password123)

### Webhook Integratie

#### Home Assistant Integratie

1. Ga naar Instellingen in de app
2. Schakel webhooks in
3. Stel webhook URL in: `http://jouw-ha-instance:8123/api/webhook/kilometerregistratie`
4. Maak in Home Assistant een automatisering die reageert op webhook calls

#### Webhook Payload

De app stuurt JSON payloads zoals:
```json
{
  "type": "mileage_entry",
  "date": "2025-05-25",
  "distance_km": 45,
  "trip_type": "zakelijk",
  "start_location": "Amsterdam",
  "end_location": "Utrecht", 
  "purpose": "Klantbezoek",
  "reimbursement": 10.35,
  "license_plate": "12-ABC-3",
  "timestamp": "2025-05-25T10:30:00"
}
```

### Kilometervergoeding

Standaard ingesteld op €0,23 per kilometer (Nederlandse norm 2024). Aanpasbaar via instellingen.

## Development

### Lokale Development

1. Installeer Python 3.11+
2. Installeer dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start de development server:
   ```bash
   reflex run
   ```

### Database Schema

De app gebruikt SQLite met drie hoofdtabellen:

#### `trips` tabel
- `id`: Primary key
- `date`: Rit datum
- `start_location`: Startlocatie
- `end_location`:# Hour Registration PWA

A mobile-first Progressive Web App (PWA) for hour registration and time tracking, built with Python Reflex.

## Features

- 📱 **Mobile-First Design**: Optimized for mobile devices with responsive design
- 🔐 **Single User Authentication**: Simple username/password authentication using environment variables
- 💾 **SQLite Database**: Lightweight database for storing hour entries and settings
- 🔔 **Webhook Notifications**: Send notifications to Home Assistant or other webhook endpoints
- 🌍 **Multi-Language Support**: Dutch, German, and English locales
- 📊 **Time Tracking**: Track start time, end time, breaks, projects, and descriptions
- 🗂️ **Project Management**: Organize hours by project
- ⚡ **PWA Features**: Installable app with offline capabilities
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd hour-registration-pwa
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
AUTH_USERNAME=your_username
AUTH_PASSWORD=your_secure_password
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

The app will be available at `http://localhost:3000`

### 4. Install as PWA

1. Open the app in your mobile browser
2. Tap "Add to Home Screen" (iOS) or "Install App" (Android)
3. The app will be installed as a native-like application

## Configuration

### Authentication

Set your login credentials in the `.env` file:
- `AUTH_USERNAME`: Your username (default: admin)
- `AUTH_PASSWORD`: Your password (default: password123)

### Webhook Integration

#### Home Assistant Integration

1. Go to Settings in the app
2. Enable webhooks
3. Set webhook URL to: `http://your-ha-instance:8123/api/webhook/hour_registration`
4. In Home Assistant, create an automation that triggers on webhook calls

#### Generic Webhook

The app sends JSON payloads like:
```json
{
  "type": "hour_entry",
  "date": "2025-05-25",
  "hours": 8.5,
  "project": "Project Name",
  "description": "Work description",
  "timestamp": "2025-05-25T10:30:00"
}
```

### Localization

Supported locales:
- `nl_NL`: Dutch (Netherlands) - Default
- `de_DE`: German (Germany)
- `en_US`: English (United States)

The app uses Euro (EUR) as the default currency format.

## File Structure

```
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
├── rxconfig.py         # Reflex configuration
├── manifest.json       # PWA manifest
├── sw.js              # Service worker
├── static/
│   └── css/
│       └── pwa-styles.css  # PWA-specific styles
└── .env               # Environment variables (create from .env.example)
```

## Development

### Local Development

1. Install Python 3.11+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   reflex run
   ```

### Database Schema

The app uses SQLite with two main tables:

#### `hours` table
- `id`: Primary key
- `date`: Entry date
- `start_time`: Start time (HH:MM)
- `end_time`: End time (HH:MM)
- `break_minutes`: Break duration in minutes
- `description`: Work description
- `project`: Project name
- `total_hours`: Calculated total working hours
- `created_at`: Timestamp

#### `app_settings` table
- `webhook_url`: Webhook endpoint URL
- `webhook_enabled`: Boolean flag for webhook notifications
- `locale`: Language/locale setting
- `currency`: Currency format

## Mobile Features

### PWA Capabilities
- **Installable**: Add to home screen on mobile devices
- **Offline Ready**: Basic functionality works offline
- **Responsive**: Adapts to different screen sizes
- **Touch Optimized**: Large touch targets for mobile interaction

### Mobile-Specific Features
- **Safe Area Support**: Handles device notches and rounded corners
- **Viewport Meta Tags**: Prevents zooming on form inputs
- **Touch Feedback**: Visual feedback for touch interactions
- **Mobile Navigation**: Optimized navigation for touch devices

## Docker Deployment

### Environment Variables

The Docker setup uses the following environment variables:
- `AUTH_USERNAME`: Login username
- `AUTH_PASSWORD`: Login password

### Volumes

- `./data:/app/data`: Persistent data storage
- `./hours.db:/app/hours.db`: SQLite database file

### Health Checks

The container includes health checks to ensure the service is running properly.

## Webhook Examples

### Home Assistant Automation

```yaml
alias: "Hour Registration Webhook"
trigger:
  - platform: webhook
    webhook_id: hour_registration
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "Hours Logged"
      message: "{{ trigger.json.hours }}h logged for {{ trigger.json.project }}"
```

### Custom Webhook Handler

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    print(f"Hours logged: {data['hours']} for {data['project']}")
    return "OK"
```

## Troubleshooting

### Common Issues

1. **Database Permission Errors**: Ensure the Docker container has write permissions to the database file
2. **Webhook Not Working**: Check the webhook URL and ensure the endpoint is accessible
3. **PWA Not Installing**: Make sure you're accessing the app via HTTPS (required for PWA features)
4. **Authentication Issues**: Verify the environment variables are set correctly

### Logs

Check Docker logs:
```bash
docker-compose logs -f hour-registration-app
```

## License

This project is open source and available under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.