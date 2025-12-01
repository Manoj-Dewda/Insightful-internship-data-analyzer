from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import logging
import os

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__, static_folder='frontend')
CORS(app)  # Enable CORS for all domains on all routes

# Load and process data
try:
    # Load data from CSV file
    df = pd.read_csv('attached_assets/CleanedData.csv')
    logging.info(f"Successfully loaded data with {len(df)} records")
except Exception as e:
    logging.error(f"Error loading data: {e}")
    df = pd.DataFrame()

# API endpoint to get top domains (job titles)
@app.route('/api/top-domains', methods=['GET'])
def get_top_domains():
    try:
        # Count occurrences of each job title
        domain_counts = df['Job Title'].value_counts().reset_index()
        domain_counts.columns = ['domain', 'count']

        # Convert to dictionary for JSON response
        top_domains = domain_counts.head(10).to_dict(orient='records')
        return jsonify(top_domains)
    except Exception as e:
        logging.error(f"Error in get_top_domains: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get salary insights by domain
@app.route('/api/salary-insights', methods=['GET'])
def get_salary_insights():
    try:
        # Group by job title and calculate average salary
        salary_insights = df.groupby('Job Title')['avg_salary'].mean().reset_index()
        salary_insights.columns = ['domain', 'avg_salary']

        # Sort by average salary in descending order
        salary_insights = salary_insights.sort_values('avg_salary', ascending=False)

        # Convert to dictionary for JSON response
        return jsonify(salary_insights.head(10).to_dict(orient='records'))
    except Exception as e:
        logging.error(f"Error in get_salary_insights: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get jobs by city
@app.route('/api/jobs-by-city', methods=['GET'])
def get_jobs_by_city():
    try:
        # Clean location data (remove specific details like "Work from home")
        location_counts = df['Location'].value_counts().reset_index()
        location_counts.columns = ['city', 'count']

        # Convert to dictionary for JSON response
        return jsonify(location_counts.head(10).to_dict(orient='records'))
    except Exception as e:
        logging.error(f"Error in get_jobs_by_city: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get all domains (job titles)
@app.route('/api/domains', methods=['GET'])
def get_domains():
    try:
        domains = df['Job Title'].unique().tolist()
        return jsonify(domains)
    except Exception as e:
        logging.error(f"Error in get_domains: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get company hiring patterns
@app.route('/api/company-hiring', methods=['GET'])
def get_company_hiring():
    try:
        company_counts = df['Company'].value_counts().reset_index()
        company_counts.columns = ['company', 'count']

        # Convert to dictionary for JSON response
        return jsonify(company_counts.head(10).to_dict(orient='records'))
    except Exception as e:
        logging.error(f"Error in get_company_hiring: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get salary ranges by domain
@app.route('/api/salary-ranges', methods=['GET'])
def get_salary_ranges():
    try:
        # Group by job title and calculate min, max, and average salary
        salary_ranges = df.groupby('Job Title').agg({
            'min_salary': 'mean',
            'max_salary': 'mean',
            'avg_salary': 'mean'
        }).reset_index()

        # Convert to dictionary for JSON response
        return jsonify(salary_ranges.to_dict(orient='records'))
    except Exception as e:
        logging.error(f"Error in get_salary_ranges: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get filtered data
@app.route('/api/filter-data', methods=['GET'])
def filter_data():
    try:
        # Get filter parameters from request
        domain = request.args.get('domain')
        location = request.args.get('location')
        min_salary = request.args.get('min_salary')

        filtered_df = df.copy()

        # Apply filters if provided
        if domain and domain != 'All':
            filtered_df = filtered_df[filtered_df['Job Title'] == domain]
        if location and location != 'All':
            filtered_df = filtered_df[filtered_df['Location'] == location]
        if min_salary:
            min_salary = float(min_salary)
            filtered_df = filtered_df[filtered_df['avg_salary'] >= min_salary]

        # Convert to dictionary for JSON response
        return jsonify(filtered_df.to_dict(orient='records'))
    except Exception as e:
        logging.error(f"Error in filter_data: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get domain comparison data
@app.route('/api/compare-domains', methods=['GET'])
def compare_domains():
    try:
        # Get domains to compare from request
        domain1 = request.args.get('domain1')
        domain2 = request.args.get('domain2')

        if not domain1 or not domain2:
            return jsonify({"error": "Both domains are required for comparison"}), 400

        # Filter data for each domain
        domain1_data = df[df['Job Title'] == domain1]
        domain2_data = df[df['Job Title'] == domain2]

        # Calculate aggregate statistics for each domain
        comparison = {
            'domain1': {
                'name': domain1,
                'count': len(domain1_data),
                'avg_salary': domain1_data['avg_salary'].mean(),
                'min_salary': domain1_data['min_salary'].mean(),
                'max_salary': domain1_data['max_salary'].mean(),
                'top_companies': domain1_data['Company'].value_counts().head(5).to_dict(),
                'top_locations': domain1_data['Location'].value_counts().head(5).to_dict()
            },
            'domain2': {
                'name': domain2,
                'count': len(domain2_data),
                'avg_salary': domain2_data['avg_salary'].mean(),
                'min_salary': domain2_data['min_salary'].mean(),
                'max_salary': domain2_data['max_salary'].mean(),
                'top_companies': domain2_data['Company'].value_counts().head(5).to_dict(),
                'top_locations': domain2_data['Location'].value_counts().head(5).to_dict()
            }
        }

        return jsonify(comparison)
    except Exception as e:
        logging.error(f"Error in compare_domains: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get all locations
@app.route('/api/locations', methods=['GET'])
def get_locations():
    try:
        locations = df['Location'].unique().tolist()
        return jsonify(locations)
    except Exception as e:
        logging.error(f"Error in get_locations: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to get key insights
@app.route('/api/key-insights', methods=['GET'])
def get_key_insights():
    try:
        insights = {
            'top_paying_domain': df.groupby('Job Title')['avg_salary'].mean().sort_values(ascending=False).head(1).index[0],
            'top_hiring_domain': df['Job Title'].value_counts().index[0],
            'top_hiring_company': df['Company'].value_counts().index[0],
            'top_location': df['Location'].value_counts().index[0],
            'avg_internship_salary': df['avg_salary'].mean(),
            'total_companies': df['Company'].nunique(),
            'total_domains': df['Job Title'].nunique(),
            'total_listings': len(df)
        }
        return jsonify(insights)
    except Exception as e:
        logging.error(f"Error in get_key_insights: {e}")
        return jsonify({"error": str(e)}), 500

# Serve frontend files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)