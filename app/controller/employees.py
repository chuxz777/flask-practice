
from flask import request, jsonify, Blueprint
from flask_restful import Resource
from datetime import datetime
import logging
import pandas as pd
import psycopg2
from app.model.models import db, Employee
from flask_sqlalchemy import SQLAlchemy

employees_blueprint = Blueprint('employees_blueprint', __name__)
db = SQLAlchemy()


historical_files_dir = '/Users/Chuz/Documents/Flask/first_attempt/historical_files/'
API_BATCH_PROCESSING_LIMIT = 1000

@employees_blueprint.route('/employees')
# Define routes for creating, reading, updating, and deleting employees
class EmployeeResource(Resource):

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

    @employees_blueprint.route('/employees', methods=['POST'])
    def create_employee():
        """
        Create a new employee.

        Parameters:
        id (int): the employee's ID number
        name (str): the employee's name
        datetime (str): the employee's date of hire
        department_id (int): the ID number of the employee's department
        job_id (int): the ID number of the employee's job

        Returns:
        A JSON object containing the new employee's information.
        """
        data = request.get_json()
        # Define Data Dictionary, change this later on
        # TODO VALIDATE DATE FORMAT 
        data_types = {'id': int, 
                      'name': str, 
                      'datetime': str,  
                      'department_id': str,  
                      'job_id': int
                      }  
        # Get data from request
        data = request.json['data']
        # Check the list has a batch limit
        process_request = validate_request_size(data)
        # Check if the request will be processed
        if process_request:
            # Sets up ojbect name for further valiation
            object_name = "Employee"
            validated_results, bad_objects = validate_object(data, data_types, object_name)
            # TODO LOG BAD OBJECTS
            # Add to the db all rows that are valid according to the data dict rules
            db.session.add_all(validated_results)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                return jsonify({'message': 'An error occurred while creating the Employee.'}), 500

            return jsonify({'message':'User(s) created successfully'}), 201
        else:
            message = f'Validation failed. Please check your input keep the items \
                limit to {API_BATCH_PROCESSING_LIMIT} items.'
            return jsonify({'message':str(message)}), 500

    @employees_blueprint.route('/employees/<int:id>', methods=['GET'])
    def get_employee(id):
        """
        Get an employee's information.

        Parameters:
        id (int): the employee's ID number

        Returns:
        A JSON object containing the employee's information.
        """
        try:
            employee = Employee.query.get(id)
            return jsonify(employee.as_dict())
        except Exception as e:
            return jsonify({'error': str(e)})
        finally:
            db.session.close()

    @employees_blueprint.route('/employees/<int:id>', methods=['PUT'])
    def update_employee(id):
        """
        Update an employee's information.

        Parameters:
        id (int): the employee's ID number
        name (str): the employee's name
        datetime (str): the employee's date of hire
        department_id (int): the ID number of the employee's department
        job_id (int): the ID number of the employee's job

        Returns:
        A JSON object containing the updated employee's information.
        """
        data = request.get_json()
        try:
            employee = Employee.query.get(id)
            employee.name = data['name']
            employee.datetime = datetime.strptime(data['datetime'], "%Y-%m-%dT%H:%M:%SZ")  
            employee.department_id = data['department_id']
            employee.job_id = data['job_id']
            db.session.commit()
            return jsonify(employee.as_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)})
        finally:
            db.session.close()

    @employees_blueprint.route('/employees/<int:id>', methods=['DELETE'])
    def delete_employee(id):
        """
        Delete an employee.

        Parameters:
        id (int): the employee's ID number

        Returns:
        A message indicating that the employee was deleted.
        """
        try:
            employee = Employee.query.get(id)
            db.session.delete(employee)
            db.session.commit()
            return jsonify({'message': 'Employee deleted.'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)})
        finally:
            db.session.close()

    @employees_blueprint.route('/employees/load', methods=['POST'])
    def load_employees():

        try:
            if str(request.json['drop_all']) == "True" :
            # Drop all data from the Job table
                db.session.query(Employee).delete()
                db.session.commit()


            file_name = historical_files_dir + request.json['file_name']
            # Read the CSV file using pandas
            df = pd.read_csv(file_name, header=None, names=['id','name', 'datetime','department_id','job_id'], 
                             dtype=str, na_values=['', 'NaN', 'N/A', 'na'])
            # Records with incomplete data will need to replace nan with None to work well with db logic
            df = df.replace({np.nan: None})

            for index, row in df.iterrows():
                try:
                    employee = Employee(id=row['id'], 
                                        name=row['name'],  
                                        datetime = datetime.strptime(row['datetime'], "%Y-%m-%dT%H:%M:%SZ") , 
                                        department_id=row['department_id'], 
                                        job_id=row['job_id'])
                    db.session.add(employee)
                    db.session.commit()

                except (ValueError, TypeError) as e:
                # Log the bad row to a file
                    logging.error(f"Bad row {index}: {row}. Error: {str(e)}")
                    db.session.rollback()
                    continue
                except psycopg2.Error as e:
                    logging.error(f"Bad row {index}: {row}. Error: {str(e)}")
                    db.session.rollback()
                    continue

            return jsonify({'message': 'Data loaded successfully'}), 201
        except Exception as e:
            logging.error({'error': str(e)})

            return jsonify({'error': str(e)}), 500