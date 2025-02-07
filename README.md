# Color Map Web Application

This repository contains a Flask-based web application designed for analyzing and visualizing FTIR spectral data from CSV files. The tool streamlines the process of managing, processing, and visualizing data with an interactive web interface—ideal for laboratory environments and data-driven analysis projects.

## Features

- **User Authentication:**  
  Secure login/logout functionality using dummy credentials.
  
- **File Management:**  
  - Create, rename, and delete folders to organize your CSV files.
  - Upload CSV files to designated folders.
  
- **Data Visualization & Analysis:**  
  - Display CSV data and generate interactive plots using Plotly.
  - Combine plots from multiple CSV files.
  - Perform numerical integration (using Simpson's rule) on CSV data.
  
- **Database Management:**  
  Uses SQLite with SQLAlchemy to manage tasks (representing CSV files and their metadata).

## Why It's Useful

This application automates the process of managing and analyzing FTIR spectra data. It allows users to:
- Easily upload and organize CSV files.
- Visualize data interactively.
- Perform numerical analysis directly from a web interface.

These features help reduce manual errors and save time in data analysis workflows, making the tool practical for research and laboratory environments.

## Setup Instructions

### 1. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/ElioMargiotta/FTIR-analysis.git
