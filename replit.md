# Regulatory Narrative Generator

## Overview

This is a Flask-based web application designed to generate professional regulatory case narratives from structured pharmaceutical data. The system processes regulatory data (adverse events, drug information, patient details) and automatically generates standardized narrative reports commonly used in regulatory submissions.

## System Architecture

### Frontend Architecture
- **Technology**: HTML5, CSS3, JavaScript with jQuery
- **UI Framework**: Bootstrap 5 with dark theme
- **Data Table**: DataTables library for interactive data display
- **Design Pattern**: Single-page application with tabbed interface
- **Responsive Design**: Mobile-friendly layout with Bootstrap grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Server**: Gunicorn WSGI HTTP Server
- **Language**: Python 3.11
- **Architecture Pattern**: MVC (Model-View-Controller)
- **Deployment**: Autoscale deployment on Replit infrastructure

### Data Processing
- **Library**: Pandas for data manipulation
- **Text Processing**: Custom narrative generation engine
- **Grammar Engine**: Inflect library for proper English grammar
- **Date Handling**: Python-dateutil for flexible date parsing

## Key Components

### Core Application Files
- **`main.py`**: Application entry point and server configuration
- **`app.py`**: Main Flask application with route definitions
- **`narrative_utils.py`**: Core narrative generation logic and utilities
- **`templates/index.html`**: Main web interface template
- **`static/js/app.js`**: Frontend JavaScript for data handling and API calls
- **`static/css/custom.css`**: Custom styling for the application

### Narrative Generation Engine
- **Data Validation**: Handles missing or malformed data gracefully
- **Text Assembly**: Constructs coherent narratives from structured data
- **Grammar Processing**: Ensures proper English grammar and syntax
- **Date Formatting**: Standardizes date formats for regulatory compliance
- **Data Grouping**: Processes multiple records per regulatory ID

### Configuration Files
- **`.replit`**: Replit environment configuration with Python 3.11
- **`pyproject.toml`**: Python project dependencies and metadata
- **`uv.lock`**: Locked dependency versions for reproducible builds

## Data Flow

1. **Data Input**: Users paste tabular data from clipboard (Excel/CSV format)
2. **Data Processing**: Frontend JavaScript parses and validates data structure
3. **API Request**: Structured data sent to Flask backend via POST request
4. **Narrative Generation**: Backend processes data through narrative engine
5. **Response**: Generated narratives returned as JSON response
6. **Display**: Frontend renders narratives in formatted output tab

### Expected Data Schema
The system expects data with these columns:
- `regulatory_ID`: Unique case identifier
- `case_justification`, `case_type`: Case classification
- `reporter_type`, `publication_title`, `country`: Source information
- `IRD`: Initial Receipt Date
- `age`, `gender`: Patient demographics
- `suspect_drug`, `co_suspect_drug`: Drug information
- `event`: Adverse event description
- `medical_history`, `past_drug_therapy`: Patient history
- `concurrent_condition`, `concomitant_medication`: Concurrent factors
- `dose`, `frequency`, `route`, `indication`: Drug administration details
- `suspect_drug_start_date`: Drug initiation date

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Pandas**: Data manipulation and analysis
- **Gunicorn**: Production WSGI server
- **Inflect**: English grammar and pluralization
- **Python-dateutil**: Flexible date parsing
- **Flask-SQLAlchemy**: Database ORM (configured but not actively used)
- **Psycopg2-binary**: PostgreSQL adapter (available for future use)

### Frontend Libraries
- **Bootstrap 5**: UI framework and responsive design
- **jQuery**: DOM manipulation and AJAX requests
- **DataTables**: Interactive table functionality
- **Bootstrap Icons**: Icon library

### System Dependencies
- **PostgreSQL**: Database system (available but not currently used)
- **OpenSSL**: Secure communications
- **Gunicorn**: Production server

## Deployment Strategy

### Environment Configuration
- **Platform**: Replit with Nix package management
- **Python Version**: 3.11 with stable-24_05 channel
- **Server**: Gunicorn with auto-scaling deployment
- **Port Configuration**: Binds to 0.0.0.0:5000 with port forwarding

### Production Settings
- **Process Management**: Gunicorn with reuse-port and reload options
- **Security**: Session secret key from environment variables
- **Logging**: Debug-level logging for development
- **Scaling**: Autoscale deployment target for variable load

### Development Workflow
- **Run Configuration**: Parallel workflow execution
- **Development Server**: Auto-reload enabled for code changes
- **Port Management**: Automatic port detection and forwarding

## Changelog

```
Changelog:
- June 19, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

### Architecture Decisions Rationale

**Flask Framework Choice**: Selected for its simplicity and flexibility in building web APIs. Flask provides minimal overhead while offering extensive customization options for regulatory data processing requirements.

**Pandas for Data Processing**: Chosen for its robust data manipulation capabilities, particularly useful for handling structured regulatory data with missing values and complex grouping operations.

**Client-Side Data Processing**: JavaScript handles initial data parsing to reduce server load and provide immediate feedback to users about data format issues.

**Bootstrap Dark Theme**: Provides professional appearance suitable for regulatory environments while maintaining accessibility and responsive design.

**Gunicorn Deployment**: Production-ready WSGI server that handles concurrent requests efficiently, essential for processing multiple regulatory cases simultaneously.

**Modular Code Structure**: Separated narrative generation logic from web framework to enable future expansion and testing of the core business logic.