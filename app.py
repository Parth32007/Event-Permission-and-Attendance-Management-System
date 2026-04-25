# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import sys
import os
import json
from datetime import datetime

app = Flask(__name__)

# ===== CORS Configuration =====
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses to enable frontend-backend communication"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        db = pd.read_csv("database\reg.csv")
        
        # Check if this is a login or registration request
        login_method = request.form.get('LOGIN_METHOD', '').strip().lower()
        logpassw = request.form.get('LOGPASS', '').strip()
        
        # LOGIN LOGIC
        if login_method:
            print(f"[LOGIN] Attempting login with method={login_method}, password={logpassw}", flush=True)
            
            if not logpassw:
                print(f"[LOGIN ERROR] Password is missing", flush=True)
                return render_template('index.html', error="Password is required")
            
            try:
                logpassw_int = int(logpassw)
            except (ValueError, TypeError):
                print(f"[LOGIN ERROR] Password must be numeric: {logpassw}", flush=True)
                return render_template('index.html', error="Invalid password format")
            
            # LOGIN VIA EMAIL
            if login_method == 'email':
                logemail = request.form.get('LOGEMAIL', '').strip().lower()
                print(f"[LOGIN] Email login: {logemail}", flush=True)
                
                if not logemail:
                    print(f"[LOGIN ERROR] Email is missing", flush=True)
                    return render_template('index.html', error="Email is required")
                
                for idx, row in db.iterrows():
                    row_email = str(row['REGEMAIL']).strip().lower()
                    row_password = str(int(row['PASSWORD'])).strip() if pd.notna(row['PASSWORD']) else ''
                    row_role = str(row['ROLE']).strip().lower()
                    
                    print(f"[LOGIN] Checking row {idx}: email={row_email}, role={row_role}", flush=True)
                    
                    # Compare: email match, password match (as int)
                    if (row_email == logemail and row_password == str(logpassw_int)):
                        
                        print(f"[LOGIN SUCCESS] User {row['FULLNAME']} logged in as {row_role} via EMAIL", flush=True)
                        phone = str(row['PHONENUMBER']).strip()
                        
                        if row_role == "student":
                            return redirect(url_for("student_page", usr=row['FULLNAME'], rgml=logemail, phNo=phone))
                        elif row_role == "teacher":
                            return redirect(url_for("teacher_page", usr=row['FULLNAME'], rgml=logemail, phNo=phone))
                        elif row_role == "organizer":
                            return redirect(url_for("event_coord_page", usr=row['FULLNAME'], rgml=logemail, phNo=phone))
                
                print(f"[LOGIN FAILED] No matching user found for email {logemail}", flush=True)
                return render_template('index.html', error="Invalid email or password")
            
            # LOGIN VIA PHONE
            elif login_method == 'phone':
                logphone = request.form.get('LOGPHONE', '').strip()
                print(f"[LOGIN] Phone login: {logphone}", flush=True)
                
                if not logphone:
                    print(f"[LOGIN ERROR] Phone is missing", flush=True)
                    return render_template('index.html', error="Phone number is required")
                
                for idx, row in db.iterrows():
                    row_phone = str(row['PHONENUMBER']).strip()
                    row_password = str(int(row['PASSWORD'])).strip() if pd.notna(row['PASSWORD']) else ''
                    row_role = str(row['ROLE']).strip().lower()
                    
                    print(f"[LOGIN] Checking row {idx}: phone={row_phone}, role={row_role}", flush=True)
                    
                    # Compare: phone match, password match (as int)
                    if (row_phone == logphone and row_password == str(logpassw_int)):
                        
                        print(f"[LOGIN SUCCESS] User {row['FULLNAME']} logged in as {row_role} via PHONE", flush=True)
                        email = str(row['REGEMAIL']).strip().lower()
                        
                        if row_role == "student":
                            return redirect(url_for("student_page", usr=row['FULLNAME'], rgml=email, phNo=logphone))
                        elif row_role == "teacher":
                            return redirect(url_for("teacher_page", usr=row['FULLNAME'], rgml=email, phNo=logphone))
                        elif row_role == "organizer":
                            return redirect(url_for("event_coord_page", usr=row['FULLNAME'], rgml=email, phNo=logphone))
                
                print(f"[LOGIN FAILED] No matching user found for phone {logphone}", flush=True)
                return render_template('index.html', error="Invalid phone number or password")
        
        # REGISTRATION LOGIC
        else:
            fullname = request.form.get('FULLNAME', '').strip()
            regmail = request.form.get('REGEMAIL', '').strip().lower()
            passw = request.form.get('PASSWORD', '').strip()
            role = request.form.get('ROLE', '').strip().lower()
            phone = request.form.get('PHONENUMBER', '').strip()

            print(f"[REGISTER] Attempting registration: {fullname}, {regmail}, role={role}", flush=True)

            # Validate registration input
            if not all([fullname, regmail, passw, role, phone]):
                print(f"[REGISTER ERROR] Missing required fields: fullname={bool(fullname)}, email={bool(regmail)}, password={bool(passw)}, role={bool(role)}, phone={bool(phone)}", flush=True)
                return render_template('index.html', error="All fields are required")

            # Validate password is numeric
            if not passw.isdigit():
                print(f"[REGISTER ERROR] Password must be numeric: {passw}", flush=True)
                return render_template('index.html', error="Password must contain only numbers (e.g., 123456)")

            # Validate password length
            if len(passw) < 3:
                print(f"[REGISTER ERROR] Password too short: {len(passw)} chars", flush=True)
                return render_template('index.html', error="Password must be at least 3 digits long")

            # Validate role
            if role not in ['student', 'organizer', 'teacher']:
                print(f"[REGISTER ERROR] Invalid role: {role}", flush=True)
                return render_template('index.html', error="Invalid role selected")

            # Check if user already exists
            for _, row in db.iterrows():
                if str(row['FULLNAME']).strip().lower() == fullname.lower() and str(row['REGEMAIL']).strip().lower() == regmail:
                    print(f"[REGISTER ERROR] User already exists: {fullname} ({regmail})", flush=True)
                    return render_template('index.html', error="User already exists with this email")
            
            # Check if phone number already exists (CRITICAL FIX: prevent duplicate phones)
            for _, row in db.iterrows():
                if str(row['PHONENUMBER']).strip() == phone.strip():
                    print(f"[REGISTER ERROR] Phone number already registered: {phone}", flush=True)
                    return render_template('index.html', error="This phone number is already registered. Please use a unique phone number.")

            try:
                # Create new user row
                new_row = pd.DataFrame([{
                    "FULLNAME": fullname,
                    "REGEMAIL": regmail,
                    "PASSWORD": int(passw),
                    "ROLE": role,
                    "PHONENUMBER": phone
                }])

                # Append to CSV
                new_row.to_csv("database\reg.csv", mode="a", header=False, index=False)
                print(f"[REGISTER SUCCESS] New user registered: {fullname} ({role})", flush=True)

                if role == 'student':
                    return redirect(url_for("student_page", usr=fullname, rgml=regmail, phNo=phone))
                elif role == 'organizer':
                    return redirect(url_for("event_coord_page", usr=fullname, rgml=regmail, phNo=phone))
                elif role == 'teacher':
                    return redirect(url_for("teacher_page", usr=fullname, rgml=regmail, phNo=phone))
            except Exception as e:
                print(f"[REGISTER ERROR] Exception during registration: {str(e)}", flush=True)
                import traceback
                traceback.print_exc(file=sys.stdout)
                return render_template('index.html', error=f"Registration failed: {str(e)}")
    else:
        return render_template('index.html')

APPLICATION_CSV = os.path.join('database', 'applications.csv')

# Define column dtypes to prevent pandas from inferring float for empty columns
APPLICATION_DTYPES = {
    'app_id': 'int64',
    'student_name': 'str',
    'student_email': 'str',
    'event_name': 'str',
    'teacher_emails': 'str',
    'message': 'str',
    'status': 'str',
    'decision_by': 'str',
    'coordinator_ack': 'str',
    'student_acknowledged': 'str',
    'submitted_at': 'str',
    'decided_at': 'str',
    'student_ack_at': 'str'
}

def read_applications_csv():
    """Read applications CSV with proper dtypes to avoid float64 conversion"""
    return pd.read_csv(APPLICATION_CSV, dtype=APPLICATION_DTYPES)

def ensure_application_csv():
    if not os.path.exists(APPLICATION_CSV):
        df = pd.DataFrame([{
            'app_id': [],
            'student_name': [],
            'student_email': [],
            'event_name': [],
            'teacher_emails': [],
            'message': [],
            'status': [],
            'decision_by': [],
            'coordinator_ack': [],
            'student_acknowledged': [],
            'submitted_at': [],
            'decided_at': [],
            'student_ack_at': []
        }])
        df = df.iloc[0:0]
        df.to_csv(APPLICATION_CSV, index=False)


@app.route('/student/<usr>/<rgml>/<phNo>', methods=["POST", "GET"])
def student_page(usr, rgml, phNo):
    ensure_application_csv()
    return render_template("student-dashboard-final.html", usr=usr, rgml=rgml, pNo=phNo)

@app.route("/eventcoord/<usr>/<rgml>/<phNo>", methods=["POST", "GET"])
def event_coord_page(usr, rgml, phNo):
    return render_template("event_coordinator_portal.html", usr=usr, rgml=rgml, pNo=phNo)

@app.route ("/faculty/<usr>/<rgml>/<phNo>", methods = ["POST", "GET"])
def teacher_page(usr, rgml, phNo):
    ensure_application_csv()
    return render_template("teacher_portal.html",usr=usr, rgml = rgml, pNo = phNo)


@app.route('/submit_application', methods=['POST'])
def submit_application():
    try:
        data = request.get_json()
        student_name = data.get('student_name', '').strip()
        student_email = data.get('student_email', '').strip().lower()
        event_name = data.get('event_name', '').strip()
        teacher_emails = data.get('teacher_emails', [])
        message = data.get('message', '').strip()

        if not student_name or not student_email or not event_name or not teacher_emails or not message:
            return jsonify({'success': False, 'message': 'All application fields are required.'}), 400

        teacher_emails = [email.strip().lower() for email in teacher_emails if email.strip()]
        if not teacher_emails:
            return jsonify({'success': False, 'message': 'At least one teacher email is required.'}), 400

        # Validate teacher emails exist in registration database
        db = pd.read_csv("database\reg.csv")
        registered_teachers = set()
        for _, row in db.iterrows():
            if str(row['ROLE']).strip().lower() == 'teacher':
                registered_teachers.add(str(row['REGEMAIL']).strip().lower())
        
        invalid_teachers = [email for email in teacher_emails if email not in registered_teachers]
        if invalid_teachers:
            return jsonify({'success': False, 'message': f'Invalid teacher email(s): {", ".join(invalid_teachers)}. Only registered teachers can receive applications.'}), 400

        ensure_application_csv()
        applications = read_applications_csv()
        
        # Check for existing applications for this student and event
        existing_apps = applications[(applications['student_email'].str.strip().str.lower() == student_email) & 
                                     (applications['event_name'].str.strip() == event_name)]
        
        if not existing_apps.empty:
            # If any existing application for this event is 'approved', prevent further applications
            if any(existing_apps['status'] == 'approved'):
                return jsonify({'success': False, 'message': 'You already have an approved application for this event. No further applications are allowed.'}), 400
            
            # If there is a pending application, maybe we should allow or block?
            # User said "apply again and again" if rejected.
            # Let's allow if they are all rejected.

        try:
            next_id = int(applications['app_id'].max()) + 1 if not applications.empty else 1
        except Exception:
            next_id = 1
        
        row = {
            'app_id': next_id,
            'student_name': student_name,
            'student_email': student_email,
            'event_name': event_name,
            'teacher_emails': json.dumps(teacher_emails),
            'message': message,
            'status': 'pending',
            'decision_by': '{}',
            'coordinator_ack': 'no',
            'student_acknowledged': 'no',
            'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'decided_at': '',
            'student_ack_at': ''
        }
        new_row = pd.DataFrame([row])
        applications = pd.concat([applications, new_row], ignore_index=True)
        applications.to_csv(APPLICATION_CSV, index=False)
        return jsonify({'success': True, 'message': 'Application submitted successfully.'}), 200
    except Exception as e:
        print(f"[ERROR] submit_application: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/student_applications')
def get_student_applications():
    """Get applications for a specific student with all teacher decisions"""
    email = request.args.get('email', '').strip().lower()
    if not email:
        return jsonify({'success': False, 'message': 'Email query parameter is required.'}), 400
    ensure_application_csv()
    apps = read_applications_csv()
    apps = apps[apps['student_email'].str.strip().str.lower() == email]
    result = []
    for _, row in apps.iterrows():
        # FIXED: Parse decision_by as JSON to get all teacher decisions
        all_decisions = {}
        try:
            if pd.notna(row['decision_by']) and row['decision_by'].strip().startswith('{'):
                all_decisions = json.loads(row['decision_by'])
        except Exception:
            all_decisions = {}
        
        result.append({
            'app_id': int(row['app_id']),
            'event_name': row['event_name'],
            'teacher_emails': json.loads(row['teacher_emails']),
            'message': row['message'],
            'status': row['status'],
            'decision_by': all_decisions,  # Now returns all teacher decisions
            'submitted_at': row['submitted_at'],
            'decided_at': row['decided_at'] if pd.notna(row['decided_at']) and str(row['decided_at']).strip() else None,
            'student_name': row['student_name'],
            'student_email': row['student_email'],
            'student_acknowledged': row['student_acknowledged'] if pd.notna(row['student_acknowledged']) else 'no',
            'student_ack_at': row['student_ack_at'] if pd.notna(row['student_ack_at']) and str(row['student_ack_at']).strip() else None
        })
    return jsonify({'success': True, 'applications': result}), 200


@app.route('/teacher_applications')
def get_teacher_applications():
    """Get applications assigned to a specific teacher with all faculty decisions"""
    email = request.args.get('email', '').strip().lower()
    if not email:
        return jsonify({'success': False, 'message': 'Email query parameter is required.'}), 400
    ensure_application_csv()
    apps = read_applications_csv()
    result = []
    for _, row in apps.iterrows():
        try:
            teacher_emails = json.loads(row['teacher_emails'])
        except Exception:
            teacher_emails = []
        if email in [t.strip().lower() for t in teacher_emails]:
            # FIXED: Parse decision_by as JSON to get all teacher decisions
            all_decisions = {}
            try:
                if pd.notna(row['decision_by']) and row['decision_by'].strip().startswith('{'):
                    all_decisions = json.loads(row['decision_by'])
            except Exception:
                all_decisions = {}
            
            result.append({
                'app_id': int(row['app_id']),
                'student_name': row['student_name'],
                'student_email': row['student_email'],
                'event_name': row['event_name'],
                'teacher_emails': teacher_emails,
                'message': row['message'],
                'status': row['status'],
                'decision_by': all_decisions,  # Now returns all decisions as dict
                'teacher_current_decision': all_decisions.get(email),  # This teacher's decision

                'submitted_at': row['submitted_at'],
                'decided_at': row['decided_at'] if pd.notna(row['decided_at']) and str(row['decided_at']).strip() else None,
                'coordinator_ack': row['coordinator_ack'] if pd.notna(row['coordinator_ack']) else 'no'
            })
    return jsonify({'success': True, 'applications': result}), 200


@app.route('/application_decision', methods=['POST'])
def application_decision():
    """
    FIXED: Track ALL teacher decisions in JSON format
    Previously only last decision was stored (broken multi-faculty logic)
    Now stores: {"teacher1@email.com": "approved", "teacher2@email.com": "rejected"}
    """
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        decision = data.get('decision')
        teacher_email = data.get('teacher_email', '').strip().lower()

        if not app_id or decision not in ['approved', 'rejected'] or not teacher_email:
            return jsonify({'success': False, 'message': 'Invalid request data.'}), 400

        ensure_application_csv()
        apps = read_applications_csv()
        app_id = int(app_id)
        matched = apps['app_id'] == app_id
        if not any(matched):
            return jsonify({'success': False, 'message': 'Application not found.'}), 404

        idx = apps[matched].index[0]
        try:
            teacher_emails = json.loads(apps.at[idx, 'teacher_emails'])
        except Exception:
            teacher_emails = []
        if teacher_email not in [t.strip().lower() for t in teacher_emails]:
            return jsonify({'success': False, 'message': 'You are not assigned to review this application.'}), 403

        # CRITICAL FIX: Store all teacher decisions as JSON, not just last one
        try:
            teacher_decisions = json.loads(apps.at[idx, 'decision_by']) if pd.notna(apps.at[idx, 'decision_by']) and isinstance(apps.at[idx, 'decision_by'], str) and apps.at[idx, 'decision_by'].strip().startswith('{') else {}
        except Exception:
            teacher_decisions = {}
        
        # Add/update this teacher's decision
        teacher_decisions[teacher_email] = decision
        
        # Update record
        apps.at[idx, 'decision_by'] = json.dumps(teacher_decisions)  # Store as JSON
        apps.at[idx, 'decided_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Set status based on all decisions
        # Status is 'approved' only if all teachers approved
        all_decisions = list(teacher_decisions.values())
        if len(all_decisions) == len(teacher_emails):
            # All teachers have decided
            if all(d == 'approved' for d in all_decisions):
                apps.at[idx, 'status'] = 'approved'
            elif any(d == 'rejected' for d in all_decisions):
                apps.at[idx, 'status'] = 'rejected'
            else:
                apps.at[idx, 'status'] = 'pending'
        else:
            # Not all teachers have decided yet
            apps.at[idx, 'status'] = 'pending'
        
        # Reset coordinator ack when decision changes
        apps.at[idx, 'coordinator_ack'] = 'no'
        
        apps.to_csv(APPLICATION_CSV, index=False)
        print(f"[INFO] Teacher {teacher_email} made decision {decision} on app {app_id}. Current decisions: {teacher_decisions}", flush=True)
        return jsonify({'success': True, 'message': 'Decision recorded.', 'all_decisions': teacher_decisions}), 200
    except Exception as e:
        print(f"[ERROR] application_decision: {e}", flush=True)
        import traceback
        traceback.print_exc(file=sys.stdout)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/delete_application', methods=['POST'])
def delete_application():
    """Delete an application by app_id"""
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        
        if not app_id:
            return jsonify({'success': False, 'message': 'Application ID is required'}), 400
        
        ensure_application_csv()
        apps = read_applications_csv()
        app_id = int(app_id)
        matched = apps['app_id'] == app_id
        
        if not any(matched):
            return jsonify({'success': False, 'message': 'Application not found'}), 404
        
        # Delete the application row
        idx = apps[matched].index[0]
        apps = apps.drop(idx)
        apps.to_csv(APPLICATION_CSV, index=False)
        
        print(f"[INFO] Application {app_id} deleted successfully", flush=True)
        return jsonify({'success': True, 'message': 'Application deleted successfully'}), 200
    except Exception as e:
        print(f"[ERROR] delete_application: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route("/update_profile", methods=["POST"])
def update_profile():
    from flask import jsonify
    
    try:
        # Get the data from the request
        data = request.get_json()
        current_email = data.get('current_email', '').strip().lower()
        new_fullname = data.get('new_fullname', '').strip()
        new_phone = data.get('new_phone', '').strip()
        new_password = data.get('new_password', '').strip()
        
        print(f"[DEBUG] Received update request: currentEmail={current_email}, newFullName={new_fullname}, newPhone={new_phone}, newPassword={'***' if new_password else ''}", flush=True)
        
        # Validate inputs
        if not current_email or not new_fullname or not new_phone:
            print("[DEBUG] Validation failed - empty fields", flush=True)
            return jsonify({
                "success": False, 
                "message": "Full Name and Phone Number are required"
            }), 400
        
        # Validate password if provided
        if new_password:
            if not new_password.isdigit():
                print("[DEBUG] Validation failed - password not numeric", flush=True)
                return jsonify({
                    "success": False, 
                    "message": "Password must be numeric"
                }), 400
            try:
                int(new_password)  # Ensure it's a valid int
            except ValueError:
                return jsonify({
                    "success": False, 
                    "message": "Invalid password format"
                }), 400
        
        # Read the CSV file
        db = pd.read_csv("database\reg.csv")
        print(f"[DEBUG] Loaded database with {len(db)} rows", flush=True)
        print(f"[DEBUG] Database emails (lowercase): {[str(email).strip().lower() for email in db['REGEMAIL']]}", flush=True)
        print(f"[DEBUG] Column dtypes: {db.dtypes.to_dict()}", flush=True)
        
        # Find and update the user - using case-insensitive comparison
        user_found = False
        for idx, row in db.iterrows():
            db_email = str(row['REGEMAIL']).strip().lower()
            print(f"[DEBUG] Comparing '{current_email}' with '{db_email}'", flush=True)
            
            if db_email == current_email:
                db.at[idx, 'FULLNAME'] = new_fullname
                
                # Convert phone to appropriate type (try int, fallback to string)
                try:
                    db.at[idx, 'PHONENUMBER'] = int(new_phone)
                    print(f"[DEBUG] Phone converted to int: {int(new_phone)}", flush=True)
                except (ValueError, TypeError) as e:
                    db.at[idx, 'PHONENUMBER'] = new_phone
                    print(f"[DEBUG] Phone conversion failed ({e}), storing as string: {new_phone}", flush=True)
                
                # Update password if provided
                if new_password:
                    db.at[idx, 'PASSWORD'] = int(new_password)
                    print(f"[DEBUG] Password updated", flush=True)
                
                user_found = True
                print(f"[DEBUG] User found and updated at index {idx}", flush=True)
                print(f"[DEBUG] Updated values - FULLNAME: {new_fullname}, PHONENUMBER: {db.at[idx, 'PHONENUMBER']}", flush=True)
                break
        
        # Check if user was found
        if not user_found:
            print(f"[DEBUG] User with email '{current_email}' not found in database", flush=True)
            return jsonify({
                "success": False, 
                "message": f"User with email '{current_email}' not found in database"
            }), 404
        
        # Save the updated CSV file with proper formatting
        db.to_csv("database\reg.csv", index=False)
        print(f"[DEBUG] Database saved successfully to database\reg.csv", flush=True)
        
        return jsonify({
            "success": True, 
            "message": "Profile updated and saved successfully to database!"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Exception in update_profile: {str(e)}", flush=True)
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        return jsonify({
            "success": False, 
            "message": f"Error updating profile: {str(e)}"
        }), 500


# Event management endpoints
EVENTS_FILE = "database/events.json"

def ensure_events_file():
    """Ensure events.json and its directory exist"""
    import os
    events_dir = os.path.dirname(EVENTS_FILE)
    
    # Create directory if it doesn't exist
    if not os.path.exists(events_dir):
        os.makedirs(events_dir)
        print(f"[INFO] Created directory: {events_dir}", flush=True)
    
    # Create file if it doesn't exist
    if not os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'w') as f:
            json.dump({"events": []}, f, indent=2)
        print(f"[INFO] Created events file: {EVENTS_FILE}", flush=True)

@app.route('/get_teachers')
def get_teachers():
    """Get list of registered teachers for student application form"""
    try:
        db = pd.read_csv("database\reg.csv")
        teachers = []
        for _, row in db.iterrows():
            if str(row['ROLE']).strip().lower() == 'teacher':
                teachers.append({
                    'name': str(row['FULLNAME']).strip(),
                    'email': str(row['REGEMAIL']).strip().lower()
                })
        return jsonify({'success': True, 'teachers': teachers}), 200
    except Exception as e:
        print(f"[ERROR] get_teachers: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/get_events')
def get_events():
    """Fetch all coordinator events and remove expired ones"""
    try:
        ensure_events_file()
        with open(EVENTS_FILE, 'r') as f:
            data = json.load(f)
        
        # Remove expired events
        current_datetime = datetime.now()
        active_events = []
        removed_count = 0
        
        for event in data.get('events', []):
            try:
                # Combine end date and end time
                event_end_str = f"{event.get('endDate')} {event.get('endTime')}"
                event_end_datetime = datetime.strptime(event_end_str, '%Y-%m-%d %H:%M')
                
                # Keep event if it hasn't ended yet, OR if it has ended less than 2 minutes ago
                time_diff = current_datetime - event_end_datetime
                if current_datetime <= event_end_datetime or time_diff.total_seconds() <= 120:
                    active_events.append(event)
                else:
                    removed_count += 1
                    print(f"[INFO] Removed expired event: {event.get('name')} (Expired for {int(time_diff.total_seconds())}s)", flush=True)
            except Exception as e:
                print(f"[WARNING] Could not parse event time: {event}, error: {e}", flush=True)
                # Keep event if we can't parse the time (better to keep than delete)
                active_events.append(event)
        
        # Update file if any events were removed
        if removed_count > 0:
            data['events'] = active_events
            with open(EVENTS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[INFO] Removed {removed_count} expired events from database", flush=True)
        
        # --- CLEANUP ACKNOWLEDGED APPLICATIONS ---
        # If student acknowledged AND (event is expired OR event is deleted)
        try:
            ensure_application_csv()
            apps = read_applications_csv()
            active_event_names = [e.get('name') for e in active_events]
            
            # Logic: Delete if student_acknowledged is 'yes' AND event_name is not in active_event_names
            # This covers both expired events (removed above) and deleted events (not in file)
            mask_to_delete = (apps['student_acknowledged'] == 'yes') & (~apps['event_name'].isin(active_event_names))
            
            if mask_to_delete.any():
                deleted_apps_count = mask_to_delete.sum()
                apps = apps[~mask_to_delete]
                apps.to_csv(APPLICATION_CSV, index=False)
                print(f"[CLEANUP] Deleted {deleted_apps_count} acknowledged applications for expired/deleted events.", flush=True)
        except Exception as e:
            print(f"[WARNING] Application cleanup failed: {e}", flush=True)
        # ------------------------------------------

        print(f"[INFO] get_events: Returning {len(active_events)} active events", flush=True)
        return jsonify(active_events), 200
    except Exception as e:
        print(f"[ERROR] get_events: {e}", flush=True)
        return jsonify([]), 200

@app.route('/save_event', methods=['POST', 'OPTIONS'])
def save_event():
    """Save a new event created by coordinator with validation"""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        print(f"[save_event] Request received from {request.remote_addr}", flush=True)
        print(f"[save_event] Content-Type: {request.content_type}", flush=True)
        
        ensure_events_file()
        data = request.get_json()
        
        if not data:
            print(f"[save_event] ERROR: No JSON data received", flush=True)
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        print(f"[save_event] Received data: {data}", flush=True)
        
        # Validate required fields
        required_fields = ['name', 'startDate', 'startTime', 'endDate', 'endTime', 'location', 'description']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            msg = f"Missing required fields: {', '.join(missing_fields)}"
            print(f"[save_event] ERROR: {msg}", flush=True)
            return jsonify({"success": False, "message": msg}), 400
        
        # Validate date/time formats
        try:
            start_dt = datetime.strptime(f"{data['startDate']} {data['startTime']}", '%Y-%m-%d %H:%M')
            end_dt = datetime.strptime(f"{data['endDate']} {data['endTime']}", '%Y-%m-%d %H:%M')
            print(f"[save_event] Date parsing successful: {start_dt} to {end_dt}", flush=True)
        except ValueError as e:
            msg = f"Invalid date/time format. Use YYYY-MM-DD for dates and HH:MM for times. Error: {str(e)}"
            print(f"[save_event] ERROR: {msg}", flush=True)
            return jsonify({"success": False, "message": msg}), 400
        
        # Validate end time is after start time
        if end_dt <= start_dt:
            msg = f"Event end time ({end_dt}) must be after start time ({start_dt})"
            print(f"[save_event] ERROR: {msg}", flush=True)
            return jsonify({"success": False, "message": msg}), 400
        
        # Validate event name is not empty
        if not data['name'].strip():
            print(f"[save_event] ERROR: Event name cannot be empty", flush=True)
            return jsonify({"success": False, "message": "Event name cannot be empty"}), 400
        
        # Read existing events
        print(f"[save_event] Reading from {EVENTS_FILE}", flush=True)
        with open(EVENTS_FILE, 'r') as f:
            events_data = json.load(f)
        
        # Create new event
        new_event = {
            'id': int(datetime.now().timestamp() * 1000),
            'name': data['name'].strip(),
            'startDate': data['startDate'],
            'startTime': data['startTime'],
            'endDate': data['endDate'],
            'endTime': data['endTime'],
            'location': data['location'].strip(),
            'description': data['description'].strip()
        }
        
        print(f"[save_event] Creating event with ID: {new_event['id']}", flush=True)
        
        # Add to events list and save
        events_data["events"].append(new_event)
        
        print(f"[save_event] Writing to {EVENTS_FILE}", flush=True)
        with open(EVENTS_FILE, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        print(f"[save_event] SUCCESS: Event saved - {new_event['name']} (ID: {new_event['id']}, starts {start_dt}, ends {end_dt})", flush=True)
        return jsonify({"success": True, "message": "Event saved to server", "event_id": new_event['id']}), 201
        
    except Exception as e:
        print(f"[save_event] EXCEPTION: {e}", flush=True)
        import traceback
        traceback.print_exc(file=sys.stdout)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/update_event', methods=['POST', 'OPTIONS'])
def update_event():
    """Update an existing event created by coordinator"""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        print(f"[update_event] Request received from {request.remote_addr}", flush=True)
        ensure_events_file()
        data = request.get_json()
        
        if not data:
            print(f"[update_event] ERROR: No JSON data received", flush=True)
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        event_id = data.get('id')
        if not event_id:
            print(f"[update_event] ERROR: Event ID is required", flush=True)
            return jsonify({"success": False, "message": "Event ID is required"}), 400
        
        print(f"[update_event] Updating event ID: {event_id}", flush=True)
        print(f"[update_event] Received data: {data}", flush=True)
        
        # Validate required fields
        required_fields = ['name', 'startDate', 'startTime', 'endDate', 'endTime', 'location', 'description']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            msg = f"Missing required fields: {', '.join(missing_fields)}"
            print(f"[update_event] ERROR: {msg}", flush=True)
            return jsonify({"success": False, "message": msg}), 400
        
        # Validate date/time formats
        try:
            start_dt = datetime.strptime(f"{data['startDate']} {data['startTime']}", '%Y-%m-%d %H:%M')
            end_dt = datetime.strptime(f"{data['endDate']} {data['endTime']}", '%Y-%m-%d %H:%M')
            print(f"[update_event] Date parsing successful: {start_dt} to {end_dt}", flush=True)
        except ValueError as e:
            msg = f"Invalid date/time format. Use YYYY-MM-DD for dates and HH:MM for times. Error: {str(e)}"
            print(f"[update_event] ERROR: {msg}", flush=True)
            return jsonify({"success": False, "message": msg}), 400
        
        # Validate end time is after start time
        if end_dt <= start_dt:
            msg = f"Event end time ({end_dt}) must be after start time ({start_dt})"
            print(f"[update_event] ERROR: {msg}", flush=True)
            return jsonify({"success": False, "message": msg}), 400
        
        # Validate event name is not empty
        if not data['name'].strip():
            print(f"[update_event] ERROR: Event name cannot be empty", flush=True)
            return jsonify({"success": False, "message": "Event name cannot be empty"}), 400
        
        # Read existing events
        with open(EVENTS_FILE, 'r') as f:
            events_data = json.load(f)
        
        # Find and update the event
        event_found = False
        for i, event in enumerate(events_data.get('events', [])):
            if event.get('id') == event_id:
                # Update the event
                events_data['events'][i] = {
                    'id': event_id,
                    'name': data['name'].strip(),
                    'startDate': data['startDate'],
                    'startTime': data['startTime'],
                    'endDate': data['endDate'],
                    'endTime': data['endTime'],
                    'location': data['location'].strip(),
                    'description': data['description'].strip()
                }
                event_found = True
                print(f"[update_event] Event found and updated: {data['name']}", flush=True)
                break
        
        if not event_found:
            print(f"[update_event] ERROR: Event with ID {event_id} not found", flush=True)
            return jsonify({"success": False, "message": f"Event with ID {event_id} not found"}), 404
        
        # Write updated events to file
        with open(EVENTS_FILE, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        print(f"[update_event] SUCCESS: Event updated - {data['name']} (ID: {event_id})", flush=True)
        return jsonify({"success": True, "message": "Event updated successfully", "event_id": event_id}), 200
        
    except Exception as e:
        print(f"[update_event] EXCEPTION: {e}", flush=True)
        import traceback
        traceback.print_exc(file=sys.stdout)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/delete_event', methods=['POST', 'OPTIONS'])
def delete_event():
    """Delete an event created by coordinator"""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        print(f"[delete_event] Request received from {request.remote_addr}", flush=True)
        ensure_events_file()
        data = request.get_json()
        
        if not data:
            print(f"[delete_event] ERROR: No JSON data received", flush=True)
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        event_id = data.get('id')
        if not event_id:
            print(f"[delete_event] ERROR: Event ID is required", flush=True)
            return jsonify({"success": False, "message": "Event ID is required"}), 400
        
        print(f"[delete_event] Deleting event ID: {event_id}", flush=True)
        
        # Read existing events
        with open(EVENTS_FILE, 'r') as f:
            events_data = json.load(f)
        
        # Find and remove the event
        event_found = False
        event_name = None
        original_count = len(events_data.get('events', []))
        events_data['events'] = [e for e in events_data.get('events', []) if e.get('id') != event_id]
        
        if len(events_data['events']) < original_count:
            event_found = True
            # Get the deleted event name from the original list
            for event in events_data.get('events', []):
                if event.get('id') == event_id:
                    event_name = event.get('name', 'Unknown')
                    break
        
        if not event_found:
            print(f"[delete_event] ERROR: Event with ID {event_id} not found", flush=True)
            return jsonify({"success": False, "message": f"Event with ID {event_id} not found"}), 404
        
        # Write updated events to file
        with open(EVENTS_FILE, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        print(f"[delete_event] SUCCESS: Event deleted - ID: {event_id}", flush=True)
        return jsonify({"success": True, "message": "Event deleted successfully", "event_id": event_id}), 200
        
    except Exception as e:
        print(f"[delete_event] EXCEPTION: {e}", flush=True)
        import traceback
        traceback.print_exc(file=sys.stdout)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/coordinator_acknowledge', methods=['POST'])
def coordinator_acknowledge():
    """Coordinator acknowledges/views teacher's decision"""
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        
        if not app_id:
            return jsonify({'success': False, 'message': 'Application ID is required'}), 400
        
        ensure_application_csv()
        apps = read_applications_csv()
        app_id = int(app_id)
        matched = apps['app_id'] == app_id
        
        if not any(matched):
            return jsonify({'success': False, 'message': 'Application not found'}), 404
        
        idx = apps[matched].index[0]
        apps.at[idx, 'coordinator_ack'] = 'yes'
        apps.to_csv(APPLICATION_CSV, index=False)
        
        print(f"[INFO] Coordinator acknowledged application {app_id}", flush=True)
        return jsonify({'success': True, 'message': 'Application acknowledged'}), 200
    except Exception as e:
        print(f"[ERROR] coordinator_acknowledge: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/student_acknowledge', methods=['POST'])
def student_acknowledge():
    """Student acknowledges teacher's decision"""
    try:
        data = request.get_json()
        app_id = data.get('app_id')
        student_email = data.get('student_email', '').strip().lower()
        
        if not app_id or not student_email:
            return jsonify({'success': False, 'message': 'Application ID and student email are required'}), 400
        
        ensure_application_csv()
        apps = read_applications_csv()
        app_id = int(app_id)
        matched = apps['app_id'] == app_id
        
        if not any(matched):
            return jsonify({'success': False, 'message': 'Application not found'}), 404
        
        idx = apps[matched].index[0]
        if apps.at[idx, 'student_email'].strip().lower() != student_email:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        apps.at[idx, 'student_acknowledged'] = 'yes'
        apps.at[idx, 'student_ack_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        apps.to_csv(APPLICATION_CSV, index=False)
        
        print(f"[INFO] Student {student_email} acknowledged application {app_id}", flush=True)
        return jsonify({'success': True, 'message': 'Decision acknowledged'}), 200
    except Exception as e:
        print(f"[ERROR] student_acknowledge: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/event_analytics')
def event_analytics():
    """Get analytics for coordinator dashboard - all applications with faculty decisions"""
    try:
        ensure_application_csv()
        apps = read_applications_csv()
        
        # Group by event name
        analytics = {}
        for _, row in apps.iterrows():
            event_name = row['event_name']
            if event_name not in analytics:
                analytics[event_name] = {
                    'event_name': event_name,
                    'students': {}  # Will store by student_email
                }
            
            student_email = row['student_email'].strip().lower()
            
            # Initialize student if not exists
            if student_email not in analytics[event_name]['students']:
                analytics[event_name]['students'][student_email] = {
                    'student_name': row['student_name'],
                    'student_email': student_email,
                    'applications': [],
                    'decisions': {},  # decision_by -> decision
                    'has_approval': False,
                    'has_multiple_approvals': False
                }
            
            # Add application details
            # FIXED: Parse decision_by as JSON to get all teacher decisions
            all_decisions = {}
            try:
                if pd.notna(row['decision_by']) and row['decision_by'].strip().startswith('{'):
                    all_decisions = json.loads(row['decision_by'])
            except Exception:
                all_decisions = {}
            
            app_data = {
                'app_id': int(row['app_id']),
                'teacher_emails': json.loads(row['teacher_emails']) if pd.notna(row['teacher_emails']) else [],
                'status': row['status'],
                'decision_by': all_decisions,  # Now returns all decisions
                'submitted_at': row['submitted_at'],
                'decided_at': row['decided_at'] if pd.notna(row['decided_at']) else None
            }
            analytics[event_name]['students'][student_email]['applications'].append(app_data)
            
            # Track all teacher decisions
            if all_decisions:
                for teacher_email, decision in all_decisions.items():
                    analytics[event_name]['students'][student_email]['decisions'][teacher_email] = decision
                    if decision == 'approved':
                        analytics[event_name]['students'][student_email]['has_approval'] = True
        
        # Convert to list format and identify students with multiple approvals
        result = []
        for event_name, event_data in analytics.items():
            students_list = []
            for student_email, student_data in event_data['students'].items():
                # Check if student has multiple faculty decisions
                approval_count = sum(1 for decision in student_data['decisions'].values() if decision == 'approved')
                rejection_count = sum(1 for decision in student_data['decisions'].values() if decision == 'rejected')
                pending_count = len(student_data['applications']) - len(student_data['decisions'])
                
                student_data['has_multiple_approvals'] = approval_count > 1
                student_data['approval_count'] = approval_count
                student_data['rejection_count'] = rejection_count
                student_data['pending_count'] = pending_count
                student_data['total_faculty_reviews'] = len(student_data['decisions'])
                
                students_list.append(student_data)
            
            result.append({
                'event_name': event_name,
                'students': students_list,
                'total_students': len(students_list),
                'students_with_approvals': sum(1 for s in students_list if s['has_approval']),
                'students_with_multiple_approvals': sum(1 for s in students_list if s['has_multiple_approvals'])
            })
        
        return jsonify({'success': True, 'analytics': result}), 200
    except Exception as e:
        print(f"[ERROR] event_analytics: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/event_approved_students/<event_name>')
def get_event_approved_students(event_name):
    """Get students with faculty decisions for a specific event"""
    try:
        ensure_application_csv()
        apps = read_applications_csv()
        
        # Filter applications for the event
        event_apps = apps[apps['event_name'] == event_name]
        
        # Group by student to track all decisions
        students_dict = {}
        for _, row in event_apps.iterrows():
            student_email = row['student_email'].strip().lower()
            
            if student_email not in students_dict:
                students_dict[student_email] = {
                    'student_name': row['student_name'],
                    'student_email': student_email,
                    'decisions': {},  # teacher_email -> status
                    'applications': [],
                    'approval_count': 0,
                    'rejection_count': 0,
                    'pending_count': 0,
                    'total_faculty_reviews': 0
                }
            
            # FIXED: Parse decision_by as JSON to get all teacher decisions
            all_decisions = {}
            try:
                if pd.notna(row['decision_by']) and row['decision_by'].strip().startswith('{'):
                    all_decisions = json.loads(row['decision_by'])
            except Exception:
                all_decisions = {}
            
            # Track all decisions
            if all_decisions:
                for teacher_email, decision in all_decisions.items():
                    students_dict[student_email]['decisions'][teacher_email] = decision
                    
                    if decision == 'approved':
                        students_dict[student_email]['approval_count'] += 1
                    elif decision == 'rejected':
                        students_dict[student_email]['rejection_count'] += 1
            else:
                students_dict[student_email]['pending_count'] += 1
            
            students_dict[student_email]['applications'].append({
                'app_id': int(row['app_id']),
                'status': row['status'],
                'submitted_at': row['submitted_at'],
                'all_decisions': all_decisions  # Include all decisions in response
            })
        
        # Calculate total faculty reviews and multiple approvals
        students = []
        for student_email, student_data in students_dict.items():
            student_data['total_faculty_reviews'] = len(student_data['decisions'])
            student_data['has_multiple_approvals'] = student_data['approval_count'] > 1
            students.append(student_data)
        
        return jsonify({'success': True, 'students': students}), 200
    except Exception as e:
        print(f"[ERROR] get_event_approved_students: {e}", flush=True)
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
