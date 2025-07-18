# 📝 Functional Requirements Document
## Tiara Clinic Excel Wizard

---

## 1. Project Overview

This internal web application enables clinic staff to:

- Manage clinic visit records (create, read, update, delete)
- Authenticate via email-based OTP (no signup)
- Import visit data from Excel files
- Export existing data to both Excel and PDF formats
- Visualize data through dynamic charts
- Support dark mode and responsive design

---

## 2. Folder Structure

TiaraClinicExcelWizard/
├── run.py # Flask app entry point
├── requirements.txt # Dependency list
│
├── clinic_app/ # Main application package
│ ├── init.py # App factory & extensions init
│ ├── config.py # Config settings (DB, mail, secret)
│ │
│ ├── models/
│ │ ├── init.py
│ │ ├── user.py # User model (id, email, role)
│ │ └── clinic_visit.py # ClinicVisit model
│ │
│ ├── routes/
│ │ ├── auth.py # OTP login/logout routes
│ │ ├── dashboard.py # CRUD + stats endpoints
│ │ ├── import_wizard.py # Excel import & preview
│ │ └── export.py # Excel/PDF export routes
│ │
│ ├── templates/ # Jinja2 HTML templates
│ │ ├── base.html
│ │ ├── home.html
│ │ ├── login.html
│ │ ├── verify.html
│ │ ├── dashboard.html
│ │ ├── import_wizard.html
│ │ └── export_report.html # Used for PDF generation
│ │
│ ├── static/ # Static assets
│ │ ├── css/style.css # CSS (dark mode, animations, responsive)
│ │ └── js/dashboard-enhancements.js # Table logic, charts UI
│ │
│ ├── utils/
│ │ ├── seed.py # Seeds admin and standard users
│ │ └── excel_parser.py # Validates Excel spreadsheet structure
│ │
│ ├── uploads/ # Temporary Excel uploads
│ └── exports/ # Generated files (Excel, PDF)
│
└── tests/
└── test_app.py # Test suite (pytest)


---

## 3. Data Models

### `User`
| Field | Type    | Description                    |
|-------|---------|--------------------------------|
| id    | Integer | Unique identifier (PK)         |
| email | String  | Login email address            |
| role  | String  | `admin` or `user`              |

### `ClinicVisit`
| Field           | Type      | Description                                     |
|-----------------|-----------|-------------------------------------------------|
| id              | Integer   | Unique identifier (PK)                          |
| user_id         | Integer   | Foreign key referencing User                    |
| visit_date      | Date      | Clinic visit date                               |
| treatment       | String    | Treatment description                           |
| payment_method  | String    | How payment was made                            |
| actual_amount   | Float     | Full amount of visit                            |
| deposit_paid    | Boolean   | Whether a standard £100 deposit was paid        |
| deposit_amount  | Float     | Auto £100 if deposit_paid = true                |
| deposit_method  | String    | "Online" or "In-Store"                          |
| net_amount      | Float     | actual_amount minus deposit_amount              |
| month           | String    | Visit month (e.g. "Jan")                        |
| year            | Integer   | Visit year                                      |

---

## 4. Authentication Flow

- **/login**: Email login; sends 6-digit OTP via email for seeded users
- **/verify**: OTP verification; logs user in via Flask-Login
- **/logout**: Logs user out
- Only seeded accounts allowed access

---

## 5. Dashboard Features (CRUD + Charts)

### Table UI

- Editable visit records
- Calendar widget for dates (flatpickr)
- Checkbox & dropdown for deposit handling (auto-calculates net)
- Inline Save/Delete buttons with spinner and animations
- Editable Add Row button for new entries
- Footer shows total of actual_amount
- Drag-and-drop row sorting (Sortable.js)
- Dark mode support

### Charts

- **Pie Chart**: Treatment distribution
- **Bar Chart**: Net revenue per treatment
- Data fetched from `/api/dashboard/stats`

---

## 6. Excel Import Wizard

- **/import**: Upload `.xlsx` file with expected columns:
  `visit_date`, `treatment`, `payment_method`, `actual_amount`, `deposit_paid`, `deposit_method`, `month`, `year`
- Validates structure, displays errors, and stores data in session
- **/import/preview**: Shows preview and enables admin to import rows into DB

---

## 7. Export & Reporting

- **/export_excel**: Exports filtered visit records to `.xlsx`
- **/export_pdf**: Converts `export_report.html` into PDF using pdfkit

---

## 8. UI/UX Design

- Consistent styling in `style.css`
- Animations:
  - `flashGreen` on save
  - `flashRed` on delete
  - Fade in/out for rows
- Responsive: Collapsible table rows on small screens
- Dark mode toggle affects tables, forms, buttons, alerts

---

## 9. Seed Data

Run `utils/seed.py` to seed:

- **Admin**: h.thiara0@yahoo.com
- **User1**: tiara.aesthetics@gmail.com
- **User2**: info@tiaraclinics.com

No registration page required.

---

## 10. Deployment Notes

- Requires wkhtmltopdf installed for PDF export
- Configuration via `config.py` using environment variables
- Deploy using `gunicorn`, e.g.:
  ```bash
  gunicorn -w 4 -b 0.0.0.0:5000 run:app
.env file required for SECRET_KEY and mail settings
