
from flask import request, jsonify, Blueprint
from flask_restful import Resource
import pandas as pd
from  app.model.models import db, Department
from flask_sqlalchemy import SQLAlchemy

departments_blueprint = Blueprint('departments_blueprint', __name__)
db = SQLAlchemy()

historical_files_dir = '/Users/Chuz/Documents/Flask/first_attempt/historical_files/'
API_BATCH_PROCESSING_LIMIT = 1000



class DepartmentResource(Resource):
    """
    DepartmentResource is a Flask-RESTful Resource that defines the endpoints
    for creating, reading, updating, and deleting departments.
    """
    @departments_blueprint.before_request
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


    @departments_blueprint.before_request
    def validate_request_size(data):
        if len(data) > API_BATCH_PROCESSING_LIMIT:
            result = False
        else:
            result = True
        return result

    @departments_blueprint.route('/departments', methods=['POST'])
    def create_department():
        """
        Creates a new department.

        Parameters:
        - `id`: the department's ID
        - `department`: the department's name
        """
        # Define Data Dictionary, change this later on
        data_types = {'id': int, 
                      'department': str}  
        # Get data from request
        data = request.json['data']
        # Check the list has a batch limit
        process_request = validate_request_size(data)
        
        # Check if the request will be processed

        # Check if the request will be processed
        if process_request:
            # Sets up ojbect name for further valiation
            object_name = "Department"
            validated_results, bad_objects = validate_object(data, data_types, object_name)
            # TODO LOG BAD OBJECTS
            # Add to the db all rows that are valid according to the data dict rules
            db.session.add_all(validated_results)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                return jsonify({'message': 'An error occurred while creating the Department.'}), 500
            message = 'Department(s) created successfully'
            return jsonify({'message': str(message)}), 201
        else:
            message = f'Validation failed. Please check your input keep the items \
                limit to {API_BATCH_PROCESSING_LIMIT} items.'
            return jsonify({'message': str(message)}), 500


    @departments_blueprint.route('/departments/<int:id>', methods=['GET'])
    def get_department(id):
        """
        Retrieves a department by id.

        Parameters:
        - `id`: the department's ID
        """
        department = Department.query.get(id)
        if department is None:
            return jsonify({'message': 'Department not found.'}), 404
        return jsonify(department.as_dict())

    @departments_blueprint.route('/departments/<int:id>', methods=['PUT'])
    def update_department(id):
        """
        Updates a department by id.

        Parameters:
        - `id`: the department's ID
        - `department`: the department's name
        """
        data = request.get_json()
        department = Department.query.get(id)
        if department is None:
            return jsonify({'message': 'Department not found.'}), 404
        department.department = data['department']
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({'message': 'An error occurred while updating the department.'}), 500
        return jsonify(department.as_dict())

    @departments_blueprint.route('/departments/<int:id>', methods=['DELETE'])
    def delete_department(id):
        """
        Deletes a department by id.

        Parameters:
        - `id`: the department's ID
        """
        department = Department.query.get(id)
        if department is None:
            return jsonify({'message': 'Department not found.'}), 404
        try:
            db.session.delete(department)
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({'message': 'An error occurred while deleting the department.'}), 500
        return jsonify(department.as_dict())
    

    @departments_blueprint.route('/departments/load', methods=['POST'])
    def load_departments():

        try:

            if str(request.json['drop_all']) == "True" :
            # Drop all data from the Job table
                db.session.query(Department).delete()
                db.session.commit()

            file_name = historical_files_dir + request.json['file_name']

            # Read the CSV file using pandas
            df = pd.read_csv(file_name, header=None, names=['id','department'], dtype=str)

            # Map the DataFrame rows to Department objects and insert them into the database
            for index, row in df.iterrows():
                department = Department(id=row['id'], department=row['department'])
                db.session.add(department)
            db.session.commit()
            return jsonify({'message': 'Data loaded successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500