import reflex as rx
import sqlite3
import hashlib
import os
import requests
import json
from datetime import datetime, date, timedelta
from typing import List, Optional
import asyncio

# Database setup
def init_db():
    # Use data directory for database
    db_path = os.path.join('/app/data', 'mileage.db')
    os.makedirs('/app/data', exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create mileage trips table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_location TEXT NOT NULL,
            end_location TEXT NOT NULL,
            start_odometer INTEGER,
            end_odometer INTEGER,
            distance_km INTEGER,
            purpose TEXT NOT NULL,
            trip_type TEXT NOT NULL,
            license_plate TEXT,
            client_project TEXT,
            notes TEXT,
            fuel_cost REAL DEFAULT 0,
            parking_cost REAL DEFAULT 0,
            toll_cost REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create vehicles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_plate TEXT UNIQUE NOT NULL,
            brand TEXT,
            model TEXT,
            fuel_type TEXT DEFAULT 'Benzine',
            lease_company TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            id INTEGER PRIMARY KEY,
            webhook_url TEXT,
            webhook_enabled BOOLEAN DEFAULT 0,
            locale TEXT DEFAULT 'nl_NL',
            currency TEXT DEFAULT 'EUR',
            default_vehicle_id INTEGER,
            mileage_rate REAL DEFAULT 0.23
        )
    ''')
    
    # Insert default settings if not exists
    cursor.execute('INSERT OR IGNORE INTO app_settings (id, locale, currency, mileage_rate) VALUES (1, "nl_NL", "EUR", 0.23)')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Dutch localization focused
LOCALES = {
    'nl_NL': {
        'title': 'Kilometerregistratie',
        'login': 'Inloggen',
        'logout': 'Uitloggen',
        'username': 'Gebruikersnaam',
        'password': 'Wachtwoord',
        'date': 'Datum',
        'start_location': 'Vertreklocatie',
        'end_location': 'Bestemmingslocatie',
        'start_odometer': 'Kilometerstand begin',
        'end_odometer': 'Kilometerstand eind',
        'distance_km': 'Afstand (km)',
        'purpose': 'Doel van de rit',
        'trip_type': 'Type rit',
        'license_plate': 'Kenteken',
        'client_project': 'Klant/Project',
        'notes': 'Opmerkingen',
        'fuel_cost': 'Brandstofkosten (€)',
        'parking_cost': 'Parkeerkosten (€)',
        'toll_cost': 'Tol/Vignetten (€)',
        'add_trip': 'Rit Toevoegen',
        'recent_trips': 'Recente Ritten',
        'vehicles': 'Voertuigen',
        'settings': 'Instellingen',
        'webhook_url': 'Webhook URL',
        'webhook_enabled': 'Webhook Ingeschakeld',
        'mileage_rate': 'Kilometervergoeding (€)',
        'save_settings': 'Instellingen Opslaan',
        'delete': 'Verwijderen',
        'edit': 'Bewerken',
        'cancel': 'Annuleren',
        'save': 'Opslaan',
        'today': 'Vandaag',
        'this_week': 'Deze Week',
        'this_month': 'Deze Maand',
        'invalid_login': 'Ongeldige inloggegevens',
        'trip_added': 'Rit toegevoegd',
        'trip_updated': 'Rit bijgewerkt',
        'trip_deleted': 'Rit verwijderd',
        'settings_saved': 'Instellingen opgeslagen',
        'total_km': 'Totaal km',
        'total_cost': 'Totale kosten',
        'reimbursement': 'Vergoeding',
        'business': 'Zakelijk',
        'private': 'Privé',
        'commute': 'Woon-werk',
        'add_vehicle': 'Voertuig Toevoegen',
        'brand': 'Merk',
        'model': 'Model',
        'fuel_type': 'Brandstoftype',
        'lease_company': 'Leasemaatschappij',
        'summary': 'Overzicht',
        'export': 'Exporteren',
        'monthly_overview': 'Maandoverzicht'
    },
    'en_US': {
        'title': 'Mileage Registration',
        'login': 'Login',
        'logout': 'Logout',
        'username': 'Username',
        'password': 'Password',
        'date': 'Date',
        'start_location': 'Start Location',
        'end_location': 'End Location',
        'start_odometer': 'Start Odometer',
        'end_odometer': 'End Odometer',
        'distance_km': 'Distance (km)',
        'purpose': 'Trip Purpose',
        'trip_type': 'Trip Type',
        'license_plate': 'License Plate',
        'client_project': 'Client/Project',
        'notes': 'Notes',
        'fuel_cost': 'Fuel Cost (€)',
        'parking_cost': 'Parking Cost (€)',
        'toll_cost': 'Toll/Vignette (€)',
        'add_trip': 'Add Trip',
        'recent_trips': 'Recent Trips',
        'vehicles': 'Vehicles',
        'settings': 'Settings',
        'webhook_url': 'Webhook URL',
        'webhook_enabled': 'Webhook Enabled',
        'mileage_rate': 'Mileage Rate (€)',
        'save_settings': 'Save Settings',
        'delete': 'Delete',
        'edit': 'Edit',
        'cancel': 'Cancel',
        'save': 'Save',
        'today': 'Today',
        'this_week': 'This Week',
        'this_month': 'This Month',
        'invalid_login': 'Invalid credentials',
        'trip_added': 'Trip added',
        'trip_updated': 'Trip updated',
        'trip_deleted': 'Trip deleted',
        'settings_saved': 'Settings saved',
        'total_km': 'Total km',
        'total_cost': 'Total cost',
        'reimbursement': 'Reimbursement',
        'business': 'Business',
        'private': 'Private',
        'commute': 'Commute',
        'add_vehicle': 'Add Vehicle',
        'brand': 'Brand',
        'model': 'Model',
        'fuel_type': 'Fuel Type',
        'lease_company': 'Lease Company',
        'summary': 'Summary',
        'export': 'Export',
        'monthly_overview': 'Monthly Overview'
    }
}

# Trip types for Dutch tax purposes
TRIP_TYPES = {
    'nl_NL': [
        ('zakelijk', 'Zakelijk'),
        ('prive', 'Privé'),
        ('woon_werk', 'Woon-werk verkeer')
    ],
    'en_US': [
        ('business', 'Business'),
        ('private', 'Private'),
        ('commute', 'Commute')
    ]
}

FUEL_TYPES = ['Benzine', 'Diesel', 'Hybride', 'Elektrisch', 'LPG']

class Trip(rx.Base):
    id: int
    date: str
    start_location: str
    end_location: str
    start_odometer: Optional[int] = None
    end_odometer: Optional[int] = None
    distance_km: int
    purpose: str
    trip_type: str
    license_plate: str
    client_project: str = ""
    notes: str = ""
    fuel_cost: float = 0.0
    parking_cost: float = 0.0
    toll_cost: float = 0.0

class Vehicle(rx.Base):
    id: int
    license_plate: str
    brand: str
    model: str
    fuel_type: str
    lease_company: str = ""
    active: bool = True

class AppSettings(rx.Base):
    webhook_url: str = ""
    webhook_enabled: bool = False
    locale: str = "nl_NL"
    currency: str = "EUR"
    default_vehicle_id: Optional[int] = None
    mileage_rate: float = 0.23  # Dutch standard rate 2024

def get_db_path():
    """Get database path"""
    return os.path.join('/app/data', 'mileage.db')

class State(rx.State):
    # Authentication
    is_authenticated: bool = False
    username: str = ""
    password: str = ""
    login_error: str = ""
    
    # Trip form
    trip_date: str = ""
    start_location: str = ""
    end_location: str = ""
    start_odometer: str = ""
    end_odometer: str = ""
    distance_km: str = ""
    purpose: str = ""
    trip_type: str = "zakelijk"
    selected_vehicle_id: str = ""
    client_project: str = ""
    notes: str = ""
    fuel_cost: str = "0"
    parking_cost: str = "0"
    toll_cost: str = "0"
    
    # Data
    trips: List[Trip] = []
    vehicles: List[Vehicle] = []
    editing_id: Optional[int] = None
    
    # Settings
    settings: AppSettings = AppSettings()
    show_settings: bool = False
    show_vehicles: bool = False
    show_summary: bool = False
    
    # Vehicle form
    vehicle_license_plate: str = ""
    vehicle_brand: str = ""
    vehicle_model: str = ""
    vehicle_fuel_type: str = "Benzine"
    vehicle_lease_company: str = ""
    
    # Messages
    message: str = ""
    message_type: str = ""
    
    # Summary data
    monthly_km: int = 0
    monthly_business_km: int = 0
    monthly_reimbursement: float = 0.0
    
    def get_text(self, key: str) -> str:
        """Get localized text"""
        return LOCALES.get(self.settings.locale, LOCALES['nl_NL']).get(key, key)
    
    def get_trip_types(self):
        """Get trip types for current locale"""
        return TRIP_TYPES.get(self.settings.locale, TRIP_TYPES['nl_NL'])
    
    async def login(self):
        """Authenticate user"""
        expected_username = os.getenv("AUTH_USERNAME", "admin")
        expected_password = os.getenv("AUTH_PASSWORD", "password123")
        
        password_hash = hashlib.sha256(self.password.encode()).hexdigest()
        expected_hash = hashlib.sha256(expected_password.encode()).hexdigest()
        
        if self.username == expected_username and password_hash == expected_hash:
            self.is_authenticated = True
            self.login_error = ""
            await self.load_settings()
            await self.load_vehicles()
            await self.load_trips()
            await self.calculate_monthly_summary()
        else:
            self.login_error = self.get_text("invalid_login")
    
    async def logout(self):
        """Logout user"""
        self.is_authenticated = False
        self.username = ""
        self.password = ""
        self.trips = []
        self.vehicles = []
    
    async def load_settings(self):
        """Load app settings from database"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('SELECT webhook_url, webhook_enabled, locale, currency, default_vehicle_id, mileage_rate FROM app_settings WHERE id = 1')
        row = cursor.fetchone()
        if row:
            self.settings = AppSettings(
                webhook_url=row[0] or "",
                webhook_enabled=bool(row[1]),
                locale=row[2] or "nl_NL",
                currency=row[3] or "EUR",
                default_vehicle_id=row[4],
                mileage_rate=row[5] or 0.23
            )
        conn.close()
    
    async def save_settings(self):
        """Save app settings to database"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE app_settings 
            SET webhook_url = ?, webhook_enabled = ?, locale = ?, currency = ?, 
                default_vehicle_id = ?, mileage_rate = ?
            WHERE id = 1
        ''', (self.settings.webhook_url, self.settings.webhook_enabled, 
              self.settings.locale, self.settings.currency,
              self.settings.default_vehicle_id, self.settings.mileage_rate))
        conn.commit()
        conn.close()
        self.show_message(self.get_text("settings_saved"), "success")
        self.show_settings = False
    
    async def load_vehicles(self):
        """Load vehicles from database"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('SELECT id, license_plate, brand, model, fuel_type, lease_company, active FROM vehicles WHERE active = 1')
        rows = cursor.fetchall()
        conn.close()
        
        self.vehicles = [
            Vehicle(
                id=row[0], license_plate=row[1], brand=row[2], model=row[3],
                fuel_type=row[4], lease_company=row[5], active=bool(row[6])
            ) for row in rows
        ]
        
        # Set default vehicle if available
        if self.vehicles and not self.selected_vehicle_id:
            default_vehicle = None
            if self.settings.default_vehicle_id:
                default_vehicle = next((v for v in self.vehicles if v.id == self.settings.default_vehicle_id), None)
            if not default_vehicle:
                default_vehicle = self.vehicles[0]
            if default_vehicle:
                self.selected_vehicle_id = str(default_vehicle.id)
    
    async def add_vehicle(self):
        """Add new vehicle"""
        if not self.vehicle_license_plate or not self.vehicle_brand:
            return
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicles (license_plate, brand, model, fuel_type, lease_company)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.vehicle_license_plate.upper(), self.vehicle_brand, self.vehicle_model,
              self.vehicle_fuel_type, self.vehicle_lease_company))
        conn.commit()
        conn.close()
        
        self.clear_vehicle_form()
        await self.load_vehicles()
        self.show_message("Voertuig toegevoegd", "success")
    
    def clear_vehicle_form(self):
        """Clear vehicle form"""
        self.vehicle_license_plate = ""
        self.vehicle_brand = ""
        self.vehicle_model = ""
        self.vehicle_fuel_type = "Benzine"
        self.vehicle_lease_company = ""
    
    def calculate_distance(self):
        """Calculate distance from odometer readings"""
        try:
            start = int(self.start_odometer) if self.start_odometer else 0
            end = int(self.end_odometer) if self.end_odometer else 0
            if end > start:
                self.distance_km = str(end - start)
        except ValueError:
            pass
    
    async def add_trip(self):
        """Add new trip"""
        if not self.trip_date or not self.start_location or not self.end_location:
            return
        
        # Get vehicle license plate
        vehicle = next((v for v in self.vehicles if str(v.id) == self.selected_vehicle_id), None)
        license_plate = vehicle.license_plate if vehicle else ""
        
        # Calculate distance if odometer readings are provided
        distance = 0
        start_odo = None
        end_odo = None
        
        try:
            if self.distance_km:
                distance = int(self.distance_km)
            elif self.start_odometer and self.end_odometer:
                start_odo = int(self.start_odometer)
                end_odo = int(self.end_odometer)
                distance = end_odo - start_odo if end_odo > start_odo else 0
        except ValueError:
            distance = 0
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        if self.editing_id:
            # Update existing trip
            cursor.execute('''
                UPDATE trips 
                SET date = ?, start_location = ?, end_location = ?, start_odometer = ?,
                    end_odometer = ?, distance_km = ?, purpose = ?, trip_type = ?,
                    license_plate = ?, client_project = ?, notes = ?, fuel_cost = ?,
                    parking_cost = ?, toll_cost = ?
                WHERE id = ?
            ''', (self.trip_date, self.start_location, self.end_location, start_odo,
                  end_odo, distance, self.purpose, self.trip_type, license_plate,
                  self.client_project, self.notes, float(self.fuel_cost or 0),
                  float(self.parking_cost or 0), float(self.toll_cost or 0), self.editing_id))
            self.show_message(self.get_text("trip_updated"), "success")
            self.editing_id = None
        else:
            # Insert new trip
            cursor.execute('''
                INSERT INTO trips (date, start_location, end_location, start_odometer,
                                 end_odometer, distance_km, purpose, trip_type, license_plate,
                                 client_project, notes, fuel_cost, parking_cost, toll_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.trip_date, self.start_location, self.end_location, start_odo,
                  end_odo, distance, self.purpose, self.trip_type, license_plate,
                  self.client_project, self.notes, float(self.fuel_cost or 0),
                  float(self.parking_cost or 0), float(self.toll_cost or 0)))
            self.show_message(self.get_text("trip_added"), "success")
        
        conn.commit()
        conn.close()
        
        # Send webhook notification
        await self.send_webhook_notification(distance, self.trip_type)
        
        # Clear form and reload
        self.clear_trip_form()
        await self.load_trips()
        await self.calculate_monthly_summary()
    
    async def send_webhook_notification(self, distance: int, trip_type: str):
        """Send webhook notification"""
        if not self.settings.webhook_enabled or not self.settings.webhook_url:
            return
        
        try:
            reimbursement = distance * self.settings.mileage_rate if trip_type == 'zakelijk' else 0
            
            payload = {
                "type": "mileage_entry",
                "date": self.trip_date,
                "distance_km": distance,
                "trip_type": trip_type,
                "start_location": self.start_location,
                "end_location": self.end_location,
                "purpose": self.purpose,
                "reimbursement": round(reimbursement, 2),
                "license_plate": next((v.license_plate for v in self.vehicles if str(v.id) == self.selected_vehicle_id), ""),
                "timestamp": datetime.now().isoformat()
            }
            
            requests.post(
                self.settings.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
        except Exception as e:
            print(f"Webhook notification failed: {e}")
    
    async def load_trips(self):
        """Load recent trips"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, date, start_location, end_location, start_odometer, end_odometer,
                   distance_km, purpose, trip_type, license_plate, client_project, notes,
                   fuel_cost, parking_cost, toll_cost
            FROM trips 
            ORDER BY date DESC, id DESC 
            LIMIT 50
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        self.trips = [
            Trip(
                id=row[0], date=row[1], start_location=row[2], end_location=row[3],
                start_odometer=row[4], end_odometer=row[5], distance_km=row[6],
                purpose=row[7], trip_type=row[8], license_plate=row[9],
                client_project=row[10], notes=row[11], fuel_cost=row[12],
                parking_cost=row[13], toll_cost=row[14]
            ) for row in rows
        ]
    
    async def calculate_monthly_summary(self):
        """Calculate monthly statistics"""
        current_month = datetime.now().strftime('%Y-%m')
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Total km this month
        cursor.execute('SELECT SUM(distance_km) FROM trips WHERE date LIKE ?', (f'{current_month}%',))
        self.monthly_km = cursor.fetchone()[0] or 0
        
        # Business km this month
        cursor.execute('SELECT SUM(distance_km) FROM trips WHERE date LIKE ? AND trip_type = "zakelijk"', (f'{current_month}%',))
        self.monthly_business_km = cursor.fetchone()[0] or 0
        
        # Calculate reimbursement
        self.monthly_reimbursement = self.monthly_business_km * self.settings.mileage_rate
        
        conn.close()
    
    async def edit_trip(self, trip_id: int):
        """Load trip for editing"""
        trip = next((t for t in self.trips if t.id == trip_id), None)
        if trip:
            self.editing_id = trip_id
            self.trip_date = trip.date
            self.start_location = trip.start_location
            self.end_location = trip.end_location
            self.start_odometer = str(trip.start_odometer) if trip.start_odometer else ""
            self.end_odometer = str(trip.end_odometer) if trip.end_odometer else ""
            self.distance_km = str(trip.distance_km)
            self.purpose = trip.purpose
            self.trip_type = trip.trip_type
            self.client_project = trip.client_project
            self.notes = trip.notes
            self.fuel_cost = str(trip.fuel_cost)
            self.parking_cost = str(trip.parking_cost)
            self.toll_cost = str(trip.toll_cost)
            
            # Find matching vehicle
            vehicle = next((v for v in self.vehicles if v.license_plate == trip.license_plate), None)
            if vehicle:
                self.selected_vehicle_id = str(vehicle.id)
    
    async def delete_trip(self, trip_id: int):
        """Delete trip"""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('DELETE FROM trips WHERE id = ?', (trip_id,))
        conn.commit()
        conn.close()
        
        self.show_message(self.get_text("trip_deleted"), "success")
        await self.load_trips()
        await self.calculate_monthly_summary()
    
    def clear_trip_form(self):
        """Clear trip form"""
        self.trip_date = ""
        self.start_location = ""
        self.end_location = ""
        self.start_odometer = ""
        self.end_odometer = ""
        self.distance_km = ""
        self.purpose = ""
        self.client_project = ""
        self.notes = ""
        self.fuel_cost = "0"
        self.parking_cost = "0"
        self.toll_cost = "0"
        self.editing_id = None
    
    def show_message(self, text: str, msg_type: str = "info"):
        """Show message to user"""
        self.message = text
        self.message_type = msg_type
    
    def clear_message(self):
        """Clear message"""
        self.message = ""
        self.message_type = ""

def login_page() -> rx.Component:
    """Login page component"""
    return rx.container(
        rx.vstack(
            rx.heading(State.get_text("title"), size="9", text_align="center", color="#1a365d"),
            rx.card(
                rx.vstack(
                    rx.input(
                        placeholder=State.get_text("username"),
                        value=State.username,
                        on_change=State.set_username,
                        width="100%"
                    ),
                    rx.input(
                        placeholder=State.get_text("password"),
                        type="password",
                        value=State.password,
                        on_change=State.set_password,
                        width="100%"
                    ),
                    rx.cond(
                        State.login_error,
                        rx.text(State.login_error, color="red", size="2")
                    ),
                    rx.button(
                        State.get_text("login"),
                        on_click=State.login,
                        width="100%",
                        size="3",
                        color_scheme="blue"
                    ),
                    spacing="3",
                    width="100%"
                ),
                size="4"
            ),
            spacing="6",
            align="center",
            min_height="100vh",
            justify="center"
        ),
        max_width="400px",
        margin="0 auto",
        padding="1rem"
    )

def trip_form() -> rx.Component:
    """Trip entry form component"""
    return rx.card(
        rx.vstack(
            rx.heading(
                rx.cond(
                    State.editing_id,
                    State.get_text("edit"),
                    State.get_text("add_trip")
                ),
                size="6"
            ),
            
            # Basic trip info
            rx.flex(
                rx.input(
                    type="date",
                    value=State.trip_date,
                    on_change=State.set_trip_date,
                    placeholder=State.get_text("date")
                ),
                rx.select(
                    [f"{v.license_plate} ({v.brand} {v.model})" for v in State.vehicles],
                    value=State.selected_vehicle_id,
                    on_change=State.set_selected_vehicle_id,
                    placeholder="Selecteer voertuig"
                ),
                direction="column",
                spacing="2",
                width="100%"
            ),
            
            # Locations
            rx.flex(
                rx.input(
                    value=State.start_location,
                    on_change=State.set_start_location,
                    placeholder=State.get_text("start_location")
                ),
                rx.input(
                    value=State.end_location,
                    on_change=State.set_end_location,
                    placeholder=State.get_text("end_location")
                ),
                direction="column",
                spacing="2",
                width="100%"
            ),
            
            # Distance tracking
            rx.text("Kilometerstand of afstand:", weight="bold", size="3"),
            rx.flex(
                rx.input(
                    type="number",
                    value=State.start_odometer,
                    on_change=[State.set_start_odometer, State.calculate_distance],
                    placeholder=State.get_text("start_odometer")
                ),
                rx.input(
                    type="number",
                    value=State.end_odometer,
                    on_change=[State.set_end_odometer, State.calculate_distance],
                    placeholder=State.get_text("end_odometer")
                ),
                rx.input(
                    type="number",
                    value=State.distance_km,
                    on_change=State.set_distance_km,
                    placeholder=State.get_text("distance_km")
                ),
                direction="column",
                spacing="2",
                width="100%"
            ),
            
            # Trip details
            rx.flex(
                rx.select(
                    ["zakelijk", "prive", "woon_werk"],
                    value=State.trip_type,
                    on_change=State.set_trip_type,
                    placeholder=State.get_text("trip_type")
                ),
                rx.input(
                    value=State.purpose,
                    on_change=State.set_purpose,
                    placeholder=State.get_text("purpose")
                ),
                rx.input(
                    value=State.client_project,
                    on_change=State.set_client_project,
                    placeholder=State.get_text("client_project")
                ),
                direction="column",
                spacing="2",
                width="100%"
            ),
            
            # Costs (optional)
            rx.text("Kosten (optioneel):", weight="bold", size="3"),
            rx.flex(
                rx.input(
                    type="number",
                    step="0.01",
                    value=State.fuel_cost,
                    on_change=State.set_fuel_cost,
                    placeholder=State.get_text("fuel_cost")
                ),
                rx.input(
                    type="number",
                    step="0.01",
                    value=State.parking_cost,
                    on_change=State.set_parking_cost,
                    placeholder=State.get_text("parking_cost")
                ),
                rx.input(
                    type="number",
                    step="0.01",
                    value=State.toll_cost,
                    on_change=State.set_toll_cost,
                    placeholder=State.get_text("toll_cost")
                ),
                direction="column",
                spacing="2",
                width="100%"
            ),
            
            # Notes
            rx.text_area(
                value=State.notes,
                on_change=State.set_notes,
                placeholder=State.get_text("notes"),
                rows=2
            ),
            
            # Action buttons
            rx.flex(
                rx.button(
                    State.get_text("save"),
                    on_click=State.add_trip,
                    size="3",
                    color_scheme="blue"
                ),
                rx.cond(
                    State.editing_id,
                    rx.button(
                        State.get_text("cancel"),
                        on_click=State.clear_trip_form,
                        variant="soft",
                        size="3"
                    )
                ),
                spacing="2",
                justify="center"
            ),
            spacing="3",
            width="100%"
        ),
        size="3"
    )

def monthly_summary() -> rx.Component:
    """Monthly summary component"""
    return rx.card(
        rx.vstack(
            rx.heading("Maandoverzicht", size="6"),
            rx.flex(
                rx.stat(
                    rx.stat_label("Totaal km"),
                    rx.stat_number(f"{State.monthly_km} km"),
                    rx.stat_help_text("Deze maand")
                ),
                rx.stat(
                    rx.stat_label("Zakelijk km"),
                    rx.stat_number(f"{State.monthly_business_km} km"),
                    rx.stat_help_text(f"€{State.monthly_reimbursement:.2f} vergoeding")
                ),
                spacing="4",
                width="100%",
                wrap="wrap"
            ),
            spacing="3",
            width="100%"
        ),
        size="3"
    )

def trips_list() -> rx.Component:
    """Trips list component"""
    return rx.card(
        rx.vstack(
            rx.heading(State.get_text("recent_trips"), size="6"),
            rx.foreach(
                State.trips,
                lambda trip: rx.card(
                    rx.vstack(
                        rx.flex(
                            rx.text(trip.date, weight="bold"),
                            rx.text(f"{trip.distance_km} km", weight="bold", color="blue"),
                            rx.badge(
                                trip.trip_type,
                                color_scheme="green" if trip.trip_type == "zakelijk" else 
                                           "gray" if trip.trip_type == "prive" else "orange"
                            ),
                            justify="between",
                            align="center",
                            width="100%"
                        ),
                        rx.flex(
                            rx.text(f"📍 {trip.start_location}", size="2"),
                            rx.text(f"🏁 {trip.end_location}", size="2"),
                            direction="column",
                            spacing="1"
                        ),
                        rx.cond(
                            trip.license_plate,
                            rx.text(f"🚗 {trip.license_plate}", size="2", color="gray")
                        ),
                        rx.cond(
                            trip.purpose,
                            rx.text(f"📝 {trip.purpose}", size="2", color="gray")
                        ),
                        rx.cond(
                            trip.client_project,
                            rx.text(f"👥 {trip.client_project}", size="2", color="blue")
                        ),
                        rx.cond(
                            trip.start_odometer and trip.end_odometer,
                            rx.text(f"🔢 {trip.start_odometer} → {trip.end_odometer} km", size="2", color="gray")
                        ),
                        rx.cond(
                            (trip.fuel_cost + trip.parking_cost + trip.toll_cost) > 0,
                            rx.text(f"💰 €{trip.fuel_cost + trip.parking_cost + trip.toll_cost:.2f}", size="2", color="red")
                        ),
                        rx.flex(
                            rx.button(
                                State.get_text("edit"),
                                on_click=lambda trip_id=trip.id: State.edit_trip(trip_id),
                                variant="soft",
                                size="1"
                            ),
                            rx.button(
                                State.get_text("delete"),
                                on_click=lambda trip_id=trip.id: State.delete_trip(trip_id),
                                variant="soft",
                                color_scheme="red",
                                size="1"
                            ),
                            spacing="2"
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    size="2"
                )
            ),
            spacing="3",
            width="100%"
        ),
        size="3"
    )

def vehicles_dialog() -> rx.Component:
    """Vehicles management dialog"""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(State.get_text("vehicles"), variant="soft")
        ),
        rx.dialog.content(
            rx.dialog.title(State.get_text("vehicles")),
            rx.vstack(
                # Add vehicle form
                rx.text(State.get_text("add_vehicle"), weight="bold"),
                rx.input(
                    value=State.vehicle_license_plate,
                    on_change=State.set_vehicle_license_plate,
                    placeholder=State.get_text("license_plate")
                ),
                rx.flex(
                    rx.input(
                        value=State.vehicle_brand,
                        on_change=State.set_vehicle_brand,
                        placeholder=State.get_text("brand")
                    ),
                    rx.input(
                        value=State.vehicle_model,
                        on_change=State.set_vehicle_model,
                        placeholder=State.get_text("model")
                    ),
                    spacing="2",
                    width="100%"
                ),
                rx.flex(
                    rx.select(
                        FUEL_TYPES,
                        value=State.vehicle_fuel_type,
                        on_change=State.set_vehicle_fuel_type
                    ),
                    rx.input(
                        value=State.vehicle_lease_company,
                        on_change=State.set_vehicle_lease_company,
                        placeholder=State.get_text("lease_company")
                    ),
                    spacing="2",
                    width="100%"
                ),
                rx.button(
                    State.get_text("add_vehicle"),
                    on_click=State.add_vehicle
                ),
                
                # Existing vehicles
                rx.divider(),
                rx.text("Bestaande voertuigen:", weight="bold"),
                rx.foreach(
                    State.vehicles,
                    lambda vehicle: rx.card(
                        rx.vstack(
                            rx.flex(
                                rx.text(vehicle.license_plate, weight="bold"),
                                rx.text(f"{vehicle.brand} {vehicle.model}"),
                                justify="between"
                            ),
                            rx.text(f"{vehicle.fuel_type} • {vehicle.lease_company}", size="2", color="gray"),
                            spacing="1"
                        ),
                        size="1"
                    )
                ),
                
                # Close button
                rx.flex(
                    rx.dialog.close(
                        rx.button("Sluiten", variant="soft")
                    ),
                    justify="end"
                ),
                spacing="3",
                width="100%"
            )
        ),
        open=State.show_vehicles,
        on_open_change=State.set_show_vehicles
    )

def settings_dialog() -> rx.Component:
    """Settings dialog component"""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(State.get_text("settings"), variant="soft")
        ),
        rx.dialog.content(
            rx.dialog.title(State.get_text("settings")),
            rx.vstack(
                rx.text("Taal/Locale:"),
                rx.select(
                    ["nl_NL", "en_US"],
                    value=State.settings.locale,
                    on_change=lambda v: State.settings.set_locale(v)
                ),
                
                rx.text(State.get_text("mileage_rate")),
                rx.input(
                    type="number",
                    step="0.01",
                    value=State.settings.mileage_rate,
                    on_change=lambda v: State.settings.set_mileage_rate(float(v) if v else 0.23),
                    placeholder="0.23"
                ),
                
                rx.text(State.get_text("webhook_url")),
                rx.input(
                    value=State.settings.webhook_url,
                    on_change=lambda v: State.settings.set_webhook_url(v),
                    placeholder="https://your-webhook-url.com/webhook"
                ),
                
                rx.flex(
                    rx.checkbox(
                        checked=State.settings.webhook_enabled,
                        on_change=lambda v: State.settings.set_webhook_enabled(v)
                    ),
                    rx.text(State.get_text("webhook_enabled")),
                    spacing="2",
                    align="center"
                ),
                
                rx.flex(
                    rx.dialog.close(
                        rx.button(State.get_text("cancel"), variant="soft")
                    ),
                    rx.dialog.close(
                        rx.button(
                            State.get_text("save_settings"),
                            on_click=State.save_settings
                        )
                    ),
                    spacing="2",
                    justify="end"
                ),
                spacing="3",
                width="100%"
            )
        ),
        open=State.show_settings,
        on_open_change=State.set_show_settings
    )

def main_app() -> rx.Component:
    """Main application component"""
    return rx.container(
        rx.vstack(
            # Header
            rx.flex(
                rx.heading("🚗 " + State.get_text("title"), size="7", color="#1a365d"),
                rx.flex(
                    vehicles_dialog(),
                    settings_dialog(),
                    rx.button(
                        State.get_text("logout"),
                        on_click=State.logout,
                        variant="soft"
                    ),
                    spacing="2"
                ),
                justify="between",
                align="center",
                width="100%",
                padding_bottom="1rem"
            ),
            
            # Message display
            rx.cond(
                State.message,
                rx.callout(
                    State.message,
                    icon="info" if State.message_type != "error" else "alert-triangle",
                    color="green" if State.message_type == "success" else 
                          "red" if State.message_type == "error" else "blue",
                    size="2",
                    on_click=State.clear_message
                )
            ),
            
            # Monthly summary
            monthly_summary(),
            
            # Trip entry form
            trip_form(),
            
            # Trips list
            trips_list(),
            
            spacing="4",
            width="100%"
        ),
        max_width="800px",
        margin="0 auto",
        padding="1rem"
    )

def index() -> rx.Component:
    """Main index component"""
    return rx.cond(
        State.is_authenticated,
        main_app(),
        login_page()
    )

# Create the app with proper State
app = rx.App(
    state=State,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ]
)

# Add PWA manifest and service worker
app.add_page(index, route="/", title="Kilometerregistratie PWA")

if __name__ == "__main__":
    print("Starting Kilometerregistratie PWA...")
    # For development, use reflex run command instead of app.run()
    #