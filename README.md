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

Clone the repository to your local machine:

```bash
git clone https://github.com/ElioMargiotta/Colormap.git

### 2. Create and Activate a Virtual Environment

Using a virtual environment helps manage project dependencies without affecting your global Python installation.

#### a. Navigate to the Project Directory

```bash
cd Colormap

#### b. Create the Virtual Environment

Create a virtual environment named `venv`:

```bash
python -m venv venv

#### c. Activate the Virtual Environment

**On Windows:**

```bash
venv\Scripts\activate

### 3. Install Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
