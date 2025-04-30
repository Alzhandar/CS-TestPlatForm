# CS Test Platform

CS Test Platform is an advanced Django-based web application designed for creating, managing, and taking interactive tests and quizzes, primarily focused on Computer Science topics. The platform offers a comprehensive solution for educational purposes, self-assessment, and knowledge validation.

## Key Features

- **Topic-based Test Organization**: Tests are organized by topics, making navigation and learning structured
- **Interactive Testing System**: User-friendly interface for answering multiple-choice questions
- **Progress Tracking**: Monitor your progress across various topics and tests
- **Personal Dashboard**: Individual statistics, achievements, and error tracking
- **Leaderboard**: Competitive ranking system to compare results with other users
- **Admin Interface**: Comprehensive management of questions, topics, and user data
- **JSON Import/Export**: Easy addition or backup of questions via JSON format
- **Responsive Design**: Works on computers, tablets, and mobile devices

## Technologies

- **Backend**: Django 5.1, Python 3.12
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: PostgreSQL 16
- **Deployment**: Docker, Nginx, Gunicorn
- **Authentication**: Built-in Django authentication system
- **Cache**: Redis (optional)

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16 (or Docker)
- Git

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Cs-TestPlatform.git
   cd Cs-TestPlatform
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a .env file with necessary environment variables:
   ```bash
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database settings
   DB_NAME=testplatform
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at: http://127.0.0.1:8000

### Deployment with Docker

1. Make sure Docker and Docker Compose are installed

2. Create a .env file with environment variables (similar to local installation, but with DB_HOST=db)

3. Build and run the containers:
   ```bash
   docker-compose up -d
   ```

4. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. Access the application at: http://localhost (or configured domain)

## Usage Guide

### Admin Functions

1. **Adding Topics**: Log in as an administrator and add topics through the admin interface
2. **Creating Questions**: Add questions manually or import them via JSON
3. **Importing Questions**:
   - Go to the questions page in the admin panel
   - Click "Import from JSON"
   - Upload a JSON file or paste JSON content into the editor
   - Select a topic and submit

### User Functions

1. **Taking Tests**: Browse available topics and start tests
2. **Tracking Progress**: View your progress on the profile page
3. **Error Analysis**: Check your past mistakes to improve learning
4. **Leaderboard**: Compare your results with other users

## JSON Format for Questions

```json
[
  {
    "text": "Question text",
    "option1": "First option",
    "option2": "Second option",
    "option3": "Third option",
    "option4": "Fourth option",
    "correct_option": 1,
    "explanation": "Optional explanation of the answer"
  },
  {
    "text": "Another question",
    "option1": "Option A",
    "option2": "Option B",
    "option3": "Option C",
    "option4": "Option D",
    "correct_option": 3,
    "explanation": "Explanation text"
  }
]
```

