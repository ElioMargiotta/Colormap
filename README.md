# Color Map Web Application

This repository contains a Flask-based web application designed for analyzing and visualizing FTIR spectral data from CSV files. The tool streamlines the process of managing, processing, and visualizing data with an interactive web interface—ideal for laboratory environments and data-driven analysis projects.

## Features

- **User Authentication:**  
  Secure login/logout functionality using dummy credentials.
  
- **File Management:**  
  - Create, rename, and delete folders to organize your CSV files.
  - Upload CSV files to designated folders.
  
- **Data Visualization & Analysis:**  
  - Display CSV data and generate plots using matplotlib.
  - Combine plots from multiple CSV files.
  
- **Database Management:**  
  Uses SQLite with SQLAlchemy to manage tasks (representing CSV files and their metadata).

## Setup Instructions

### 1. Clone the Repository
git clone https://github.com/ElioMargiotta/Colormap.git

### 2. Create and Activate a Virtual Environment

#### a. Navigate to the Project Directory
cd Colormap

#### b. Create the Virtual Environment
python -m venv venv

#### c. Activate the Virtual Environment
venv\Scripts\activate

### 3. Install Dependencies
pip install -r requirements.txt
