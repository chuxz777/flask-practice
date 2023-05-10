
from flask import request, jsonify, Blueprint
from flask_restful import Api, Resource
import pandas as pd
from app.model.models import db, Job
from flask_sqlalchemy import SQLAlchemy


jobs_blueprint = Blueprint('jobs_blueprint', __name__)
db = SQLAlchemy()
api = Api(jobs_blueprint)


historical_files_dir = '/Users/Chuz/Documents/Flask/first_attempt/historical_files/'
API_BATCH_PROCESSING_LIMIT = 1000

def validate_object(data, data_types, object_name):
    validated_results = []
    bad_objects = []
    result = 'False'

    for item in data:
        object_validation = []
        # This creates an object base
        new_object = globals()[object_name](**item)
        # Make sure the data type is ok 
        for attr, attr_type in data_types.items():
            # Checks individualy attribute by attribute against the data dict
            if type(getattr(new_object, attr)) != attr_type:
                result = False
                print(f'Invalid data type for {attr}')
            else:
                result = True
                print(f'Valid data type for {attr}')
                object_validation.append(result)  
        if all(object_validation):
            validated_results.append(new_object)
        else:
            bad_objects.append(new_object)

    return validated_results, bad_objects



def validate_request_size(data):
    if len(data) > API_BATCH_PROCESSING_LIMIT:
        result = False
    else:
        result = True
    return result

@jobs_blueprint.route('/jobs')

# Define endpoints for Job resource
class JobResource(Resource):
    


    @jobs_blueprint.route('/jobs', methods=['POST'])
    def create_user():
        # Define Data Dictionary, change this later on
        data_types = {'id': int, 
                      'job': str}  
        # Get data from request
        data = request.json['data']
        # Check the list has a batch limit
        process_request = validate_request_size(data)
        # Check if the request will be processed
        if process_request:
            # Sets up ojbect name for further valiation
            object_name = "Job"
            validated_results, bad_objects = validate_object(data, data_types, object_name)
            # TODO LOG BAD OBJECTS
            # Add to the db all rows that are valid according to the data dict rules
            db.session.add_all(validated_results)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                return jsonify({'message': 'An error occurred while creating the Job.'}), 500
            message = 'User(s) created successfully'
            return jsonify({'message': str(message)}), 201
        else:
            message = f'Validation failed. Please check your input keep the items \
                limit to {API_BATCH_PROCESSING_LIMIT} items.'
            return jsonify({'message': str(message)}), 500
    
    @jobs_blueprint.route('/jobs/<int:id>', methods=['GET'])
    def get_job(id):
        """
        Retrieves the job with the specified id from the database.

        :param id: id of the job to retrieve
        :return: JSON object representing the job
        """
        job = Job.query.get(id)
        if job is None:
            return jsonify({'message': 'Job not found.'}), 404
        return jsonify(job.as_dict())

    @jobs_blueprint.route('/jobs', methods=['PUT'])
    def update_job(id):
        """
        Updates the job with the specified id in the database.

        :param id: id of the job to update
        :return: JSON object representing the updated job
        """
        data = request.get_json()
        job = Job.query.get(id)
        if job is None:
            return jsonify({'message': 'Job not found.'}), 404
        job.job = data['job']
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({'message': 'An error occurred while updating the job.'}), 500
        return jsonify(job.as_dict())

    @jobs_blueprint.route('/jobs', methods=['DELETE'])
    def delete_job(id):
        """
        Deletes the job with the specified id from the database.

        :param id: id of the job to delete
        :return: JSON object representing the deleted job
        """
        job = Job.query.get(id)
        if job is None:
            return jsonify({'message': 'Job not found.'}), 404
        try:
            db.session.delete(job)
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({'message': 'An error occurred while deleting the job.'}), 500
        return jsonify(job.as_dict())
    
    @jobs_blueprint.route('/jobs/drop-all', methods=['DELETE'])
    def drop_all_jobs():
        try:
            db.session.query(Job).delete()
            db.session.commit()
            return jsonify({'message': 'All jobs dropped successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    

    @jobs_blueprint.route('/jobs/load', methods=['POST'])
    def load_jobs():

        try:
            if str(request.json['drop_all']) == "True" :
            # Drop all data from the Job table
                db.session.query(Job).delete()
                db.session.commit()
                    
            file_name = historical_files_dir + request.json['file_name']
        
            # Read the CSV file using pandas
            df = pd.read_csv(file_name, header=None, names=['id','job'])

            # Map the DataFrame rows to Job objects and insert them into the database
            for index, row in df.iterrows():
                job = Job(id=row['id'], job=row['job'])
                db.session.add(job)
            db.session.commit()
            return jsonify({'message': 'Data loaded successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500