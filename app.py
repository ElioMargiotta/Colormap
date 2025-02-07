import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import base64
import plotly.express as px
from flask import Flask, render_template, url_for, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from io import BytesIO
from scipy.integrate import simpson
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.colors as mcolors
import shutil  # Import shutil to remove folders
matplotlib.use('Agg')  # Use a non-interactive backend

# Dummy user credentials
USERNAME = "Alba"
PASSWORD = "jesuisjeune"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' # set-up the database (stored in test.db)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this to a secure key
db = SQLAlchemy(app) # initialize the database

class Todo(db.Model): # create a class for the database
    id = db.Column(db.Integer, primary_key=True) # create a column for the id
    content = db.Column(db.String(200), nullable=False) # create a column for the content
    completed = db.Column(db.Integer, default=0) # create a column for the completion status
    date_created = db.Column(db.DateTime, default=datetime.utcnow) # create a column for the date created

    def __repr__(self): #every time we create a new task, it will return the id
        return '<Task %r>' % self.id

# ✅ Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check credentials
        if username == USERNAME and password == PASSWORD:
            session['user'] = username  # Store user in session
            return redirect(url_for('index'))  # Redirect to home page
        else:
            return render_template('login.html', error="Invalid username or password.")

    return render_template('login.html')


# ✅ Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from session
    return redirect(url_for('login'))  # Redirect to login page


# ✅ Protect the Home Page - Only logged-in users can access
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:  # Check if user is logged in
        return redirect(url_for('login'))  # Redirect to login page

    base_path = 'input'
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    if request.method == 'POST':  # Create a new folder
        new_folder = request.form.get('new_folder', '').strip()
        if new_folder:
            folder_path = os.path.join(base_path, new_folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                return redirect(f"/?folder={new_folder}")

    selected_folder = request.args.get('folder')
    tasks = []
    if selected_folder:
        folder_path = os.path.join(base_path, selected_folder)
        if os.path.exists(folder_path):
            tasks = Todo.query.filter(Todo.content.like(f"{selected_folder}/%")).order_by(Todo.date_created).all()
        else:
            return f"The folder '{selected_folder}' does not exist."

    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

    return render_template('index.html', folders=folders, selected_folder=selected_folder, tasks=tasks)

@app.route('/upload', methods=['POST'])
def upload():
    base_path = 'input'
    folder = request.form.get('folder')

    if not folder:
        return "No folder selected. Please select a folder first."

    folder_path = os.path.join(base_path, folder)
    if not os.path.exists(folder_path):
        return f"Folder '{folder}' does not exist."

    files = request.files.getlist('file')
    for file in files:
        if file and file.filename.endswith('.csv'):
            file_path = os.path.join(folder_path, file.filename)

            if os.path.exists(file_path):
                return f"File '{file.filename}' already exists in folder '{folder}'."

            file.save(file_path)
            new_task = Todo(content=f"{folder}/{file.filename}")
            db.session.add(new_task)

    try:
        db.session.commit()
        return redirect(f"/?folder={folder}")  # Redirect back to home with the selected folder
    except Exception as e:
        return f"There was an issue saving the files: {e}"

    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    file_path = os.path.join('input', task_to_delete.content)  # Full file path

    # Extract folder name before deleting the file
    folder = os.path.dirname(task_to_delete.content)

    try:
        os.remove(file_path)  # Delete file
        db.session.delete(task_to_delete)  # Delete from database
        db.session.commit()
        return redirect(f"/?folder={folder}")  # Redirect to home with folder context
    except Exception as e:
        return f"There was a problem deleting that task: {e}"

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    old_file_path = os.path.join('input', task.content)  # Full path to the existing file
    folder = os.path.dirname(task.content)  # Extract the folder name

    if not os.path.exists(old_file_path):
        return 'The file does not exist.'

    if request.method == 'POST':
        new_file_name = request.form['content'].strip()  # Get the new file name
        csv_data = request.form.get('csv_data', '').strip()  # Get the updated file content

        if not new_file_name.endswith('.csv'):
            return 'Invalid file name. The new file name must end with ".csv".'

        new_file_path = os.path.join('input', folder, new_file_name)

        try:
            # ✅ Always update the content of the existing file
            with open(old_file_path, 'w', newline='') as f:
                f.write(csv_data)

            # ✅ If the file name changed, rename it and update the database
            if new_file_path != old_file_path:
                os.rename(old_file_path, new_file_path)
                task.content = f"{folder}/{new_file_name}"  # Update database with new file path

            db.session.commit()
            return redirect(f"/?folder={folder}")  # ✅ Redirect to selected folder
        except Exception as e:
            return f'There was an issue updating your file: {e}'

    else:
        base_file_name = os.path.basename(task.content)  # Extract only the filename
        try:
            with open(old_file_path, 'r') as f:
                csv_data = f.read()  # Load the file content

            return render_template('update.html', task=task, csv_data=csv_data, base_file_name=base_file_name, folder=folder)
        except Exception as e:
            return f'There was an issue loading your file: {e}'


@app.route('/read_csv/<int:id>')  # read csv file
def read_csv(id):
    task = Todo.query.get_or_404(id)  # Get the task associated with the file
    file_path = os.path.join('input', task.content)  # Path to the uploaded CSV file

    if not os.path.exists(file_path):
        return f"File {task.content} does not exist."

    try:
        # Import the CSV file into a DataFrame.
        data = pd.read_csv(file_path)

        # Assume the first column in the DataFrame is the coordinate column.
        first_col_name = data.columns[0]

        # Split that column into x and y using ';' as the separator.
        data[['x', 'y']] = data[first_col_name].str.split(';', expand=True)
        data[['x', 'y']] = data[['x', 'y']].astype(int)

        # Drop the original coordinate column.
        data.drop(first_col_name, axis=1, inplace=True)

        # Dynamically determine intensity columns (all columns except 'x' and 'y')
        intensity_columns = [col for col in data.columns if col not in ['x', 'y']]

        # Define the custom colormap.
        colors = [
            (0.0, '#000000'),
            (0.01, '#000e39'),
            (0.05, '#001e6b'),
            (0.10, '#0036a4'),
            (0.15, '#004fbf'),
            (0.20, '#0a4efc'),
            (0.25, '#0a7ff5'),
            (0.30, '#0afccb'),
            (0.35, '#4cff8b'),
            (0.40, '#6afc4a'),
            (0.45, '#b3fc0a'),
            (0.50, '#f0ec10'),
            (0.55, '#fcc30a'),
            (0.60, '#ff8300'),
            (0.65, '#ff4300'),
            (0.70, '#d63900'),
            (0.75, '#9a2e00'),
            (0.80, '#660000'),
            (0.85, '#440000'),
            (0.90, '#2c0000'),
            (1.0, '#000000')
        ]
        cmap = mcolors.LinearSegmentedColormap.from_list('continuous_cmap', colors)

        # Create subplots for all intensity columns.
        n_plots = len(intensity_columns)
        fig, axs = plt.subplots(1, n_plots, figsize=(5 * n_plots, 5))

        # If there is only one intensity column, ensure axs is iterable.
        if n_plots == 1:
            axs = [axs]

        # Loop through each intensity column.
        for idx, sample in enumerate(intensity_columns):
            # Extract the intensity data for the current column.
            intensity = data[sample].to_numpy()

            # Get x and y coordinates.
            x = data['x'].to_numpy()
            y = data['y'].to_numpy()
            x_max = np.max(x)
            y_max = np.max(y)

            # Create an empty grid filled with NaN.
            grid = np.full((y_max, x_max), np.nan)

            # Populate the grid based on the coordinates.
            for i in range(len(x)):
                # Adjust for zero-based indexing.
                row = y[i] - 1  # y corresponds to row index.
                col = x[i] - 1  # x corresponds to column index.
                grid[row, col] = intensity[i]

            # Plot the grid as a heatmap using imshow.
            im = axs[idx].imshow(grid, cmap=cmap, interpolation='nearest', origin='lower', vmin=0, vmax=70000)
            axs[idx].set_title(sample)
            axs[idx].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
            for spine in axs[idx].spines.values():
                spine.set_visible(False)

        # Adjust layout to leave space for the colorbar on the right.
        # The 'right' parameter is set to 0.85 so that the colorbar won't overlap the subplots.
        fig.subplots_adjust(right=0.85)

        # Create a new axes on the right for the colorbar.
        # [left, bottom, width, height] are in figure fraction coordinates.
        cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.7])
        fig.colorbar(im, cax=cbar_ax)

        # Use tight_layout with a rect to further adjust the layout, leaving space on the right.
        plt.tight_layout(rect=[0, 0, 0.85, 1])

        # Save the figure to the static folder before closing the plot.
        color_plot_path = os.path.join('static', 'color_plot.png')
        plt.savefig(color_plot_path)
        plt.close()  # Close the figure to free resources

        # Render the template and pass the path to the saved image.
        return render_template('pplot_combined.html', plot_path=color_plot_path)
    
    except Exception as e:
        return f"There was an issue processing the file: {e}"


@app.route('/plot_combined', methods=['POST'])
def plot_combined():
    # Get a list of selected file names from the form
    selected_files = request.form.getlist('selected_files')
    if not selected_files:
        return "No files selected. Please select at least one file."

    try:
        import os
        import numpy as np
        import pandas as pd
        import matplotlib
        matplotlib.use('Agg')  # Use a non-interactive backend
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors

        # List to store the path of each generated plot
        plot_paths = []

        # Process each selected file
        for file_name in selected_files:
            file_path = os.path.join('input', file_name)
            if not os.path.exists(file_path):
                return f"File {file_name} does not exist."

            # Read the CSV file
            data = pd.read_csv(file_path)

            # Treat the first column as the coordinate column
            first_col = data.columns[0]
            data[['x', 'y']] = data[first_col].str.split(';', expand=True)
            data[['x', 'y']] = data[['x', 'y']].astype(int)
            data.drop(first_col, axis=1, inplace=True)

            # Dynamically determine intensity columns (all columns except 'x' and 'y')
            intensity_columns = [col for col in data.columns if col not in ['x', 'y']]

            # Define the custom colormap.
            colors = [
                (0.0, '#000000'),
                (0.01, '#000e39'),
                (0.05, '#001e6b'),
                (0.10, '#0036a4'),
                (0.15, '#004fbf'),
                (0.20, '#0a4efc'),
                (0.25, '#0a7ff5'),
                (0.30, '#0afccb'),
                (0.35, '#4cff8b'),
                (0.40, '#6afc4a'),
                (0.45, '#b3fc0a'),
                (0.50, '#f0ec10'),
                (0.55, '#fcc30a'),
                (0.60, '#ff8300'),
                (0.65, '#ff4300'),
                (0.70, '#d63900'),
                (0.75, '#9a2e00'),
                (0.80, '#660000'),
                (0.85, '#440000'),
                (0.90, '#2c0000'),
                (1.0, '#000000')
            ]
            cmap = mcolors.LinearSegmentedColormap.from_list('continuous_cmap', colors)

            # Create subplots for all intensity columns.
            n_plots = len(intensity_columns)
            fig, axs = plt.subplots(1, n_plots, figsize=(5 * n_plots, 5))

            # If there is only one intensity column, wrap axs in a list.
            if n_plots == 1:
                axs = [axs]

            # Process each intensity column
            for idx, sample in enumerate(intensity_columns):
                # Extract the intensity data for the current column.
                intensity = data[sample].to_numpy()

                # Get x and y coordinates.
                x = data['x'].to_numpy()
                y = data['y'].to_numpy()
                x_max = np.max(x)
                y_max = np.max(y)

                # Create an empty grid (with NaN for missing points).
                grid = np.full((y_max, x_max), np.nan)

                # Populate the grid based on the coordinates (adjusting for zero-indexing).
                for i in range(len(x)):
                    row = y[i] - 1  # y corresponds to row index.
                    col = x[i] - 1  # x corresponds to column index.
                    grid[row, col] = intensity[i]

                # Plot the grid as a heatmap.
                im = axs[idx].imshow(grid, cmap=cmap, interpolation='nearest', origin='lower', vmin=0, vmax=70000)
                axs[idx].set_title(sample)
                axs[idx].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
                for spine in axs[idx].spines.values():
                    spine.set_visible(False)

            # Adjust layout to leave space for the colorbar on the right.
            fig.subplots_adjust(right=0.85)
            # Create a dedicated axes for the colorbar.
            cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.7])
            fig.colorbar(im, cax=cbar_ax)
            plt.tight_layout(rect=[0, 0, 0.85, 1])

            # Save the figure to a unique file in the static folder.
            # Use the file name (without extension) to create a unique plot filename.
            plot_file = os.path.join('static', f"color_plot_combined.png")
            plt.savefig(plot_file)
            plt.close()  # Close the figure to free resources

            plot_paths.append(plot_file)

        # Render a template that displays all the generated plots.
        return render_template('plot_combined.html', plot_paths=plot_paths)

    except Exception as e:
        return f"There was an issue processing the files: {e}"

    
@app.route('/rename_folder', methods=['POST'])
def rename_folder():
    base_path = 'input'
    old_folder = request.form.get('old_folder', '').strip()
    new_folder = request.form.get('new_folder', '').strip()

    if not old_folder or not new_folder:
        return "Both old and new folder names are required."

    old_folder_path = os.path.join(base_path, old_folder)
    new_folder_path = os.path.join(base_path, new_folder)

    if not os.path.exists(old_folder_path):
        return f"Folder '{old_folder}' does not exist."

    if os.path.exists(new_folder_path):
        return f"Folder '{new_folder}' already exists. Choose another name."

    try:
        os.rename(old_folder_path, new_folder_path)  # Rename the folder

        # Update database records to reflect new folder name
        tasks = Todo.query.filter(Todo.content.like(f"{old_folder}/%")).all()
        for task in tasks:
            task.content = task.content.replace(f"{old_folder}/", f"{new_folder}/")
        
        db.session.commit()
        return redirect(f"/?folder={new_folder}")  # Redirect to the renamed folder
    except Exception as e:
        return f"There was an issue renaming the folder: {e}"

@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    base_path = 'input'
    folder = request.form.get('folder', '').strip()

    if not folder:
        return "Folder name is required."

    folder_path = os.path.join(base_path, folder)

    if not os.path.exists(folder_path):
        return f"Folder '{folder}' does not exist."

    try:
        # Delete all files inside the folder from the database
        Todo.query.filter(Todo.content.like(f"{folder}/%")).delete()
        db.session.commit()

        # Remove the folder and its contents
        shutil.rmtree(folder_path)  # Deletes the folder and its contents
        return redirect("/")  # Redirect to home after deletion
    except Exception as e:
        return f"There was an issue deleting the folder: {e}"



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
