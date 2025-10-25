# 🧠 Project Usage Manual

## ⚙️ External Dependencies
Before running the project, make sure you have the following installed and set up:
- **Git** installed on your system
- **Python** installed on your system   
- **Gemini API Key** (get it from your Gemini account)

---

## 🚀 Steps to Run the Project

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/omprakash0224/JobTailor
cd JobTailor
```

### **Step 2: Create a .env File**
create a .env file in root folder. Inside .env file:-
```bash
FLASK_APP=app.py
FLASK_ENV=development
GEMINI_API_KEY=paste-your-api-key-here
```
### **Step 3: Install Dependencies**
Run the following command in your terminal to install all required packages:
```bash
pip install -r requirements.txt
```
### **Step 4: Initialize the Database**
Run the following command in your terminal:-
```bash
python init_db.py
```
### **Step 5: Start the Application**
Run the following command in your terminal:-
```bash
python main.py
```

## ✅ You’re All Set!
Once the app starts running, open the provided localhost URL in your browser and start using the project! 🎉