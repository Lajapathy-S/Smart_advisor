# Quick Start Guide - Streamlit Frontend

## 🚀 Running the Streamlit Application

### Option 1: Using the run script (Easiest)
```bash
python run.py
```

### Option 2: Direct Streamlit command
```bash
streamlit run src/frontend/app.py
```

### Option 3: Using Streamlit with custom port
```bash
streamlit run src/frontend/app.py --server.port 8501
```

## 📋 Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `config/.env.example` to `config/.env`
   - Add your `OPENAI_API_KEY` in the `.env` file

3. **Initialize the vector database** (optional but recommended):
   ```bash
   python scripts/initialize_db.py
   ```

## 🎯 Features Available in Streamlit UI

### 1. 💬 Chat Interface
- Interactive chatbot for asking questions
- Supports natural language queries about:
  - Degree planning
  - Career guidance
  - Skills analysis

### 2. 📋 Degree Planning Tab
- View personalized degree plans
- See semester-by-semester course recommendations
- Track completed courses
- Visual course path display

### 3. 💼 Career Mentorship Tab
- Explore career information
- View required skills for job roles
- See career trajectories
- Get salary range information

### 4. 🔍 Skills Gap Analysis Tab
- Analyze your skills against job requirements
- Identify missing competencies
- Get personalized recommendations
- View readiness scores

## 🎨 UI Features

- **Sidebar Navigation**: Easy switching between features
- **User Profile**: Set your degree, year, and completed courses
- **Skills Input**: Add your technical and soft skills
- **Interactive Chat**: Real-time conversation with the AI advisor
- **Data Visualization**: Tables and metrics for easy understanding
- **ADA Compliant**: Accessible design for all users

## 🔧 Troubleshooting

### Streamlit won't start
- Make sure Streamlit is installed: `pip install streamlit`
- Check if port 8501 is available
- Try a different port: `streamlit run src/frontend/app.py --server.port 8502`

### Chatbot not responding
- Verify your `OPENAI_API_KEY` is set correctly in `config/.env`
- Check that the vector database is initialized
- Review error messages in the Streamlit interface

### Module import errors
- Ensure you're running from the project root directory
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check that Python path includes the project root

## 📱 Accessing the Application

Once running, the application will be available at:
- **Local**: http://localhost:8501
- **Network**: http://your-ip-address:8501

## 💡 Tips

1. **First Time Setup**: 
   - Fill in your user profile in the sidebar
   - Add your completed courses
   - Input your skills for better analysis

2. **Best Practices**:
   - Be specific in your questions for better responses
   - Use the tabs to explore different features
   - Check the structured data expanders for detailed information

3. **Keyboard Shortcuts**:
   - Press `R` to rerun the app
   - Press `C` to clear cache
   - Use `Ctrl+C` to stop the server

## 🎓 Example Queries

Try these in the chat interface:

- "What courses do I need for Information Systems degree?"
- "What skills are required for a Business Analyst role?"
- "Compare my skills with Data Analyst requirements"
- "Show me the career path for Information Systems Manager"
- "What prerequisites do I need for IS 3310?"

Enjoy using the AI Smart Advisor! 🎉
