from flask import Flask,render_template,request,redirect,url_for,session,jsonify
from flask import current_app as app
from models.models import *
from datetime import date,datetime
from flask_mail import Mail, Message
from app import mail
from sqlalchemy import or_

today = date.today()
@app.route("/",methods=["GET","POST"])
def login():
    message=None
    if request.method=="POST":
        email=request.form.get("email")
        pwd=request.form.get("pwd")
        stu=Student.query.filter_by(email=email,password=pwd).first()
        par=Parent.query.filter_by(email=email,password_hash=pwd).first()
        war=Warden.query.filter_by(email=email,password_hash=pwd).first()
        if stu:
            session['id']=stu.admno
            session['role']=stu.role
            return redirect(url_for("sportal"))
        if par:
            session['id']=par.id
            session['role']=par.role
            return redirect(url_for("pportal"))
        if war:
            session['id']=war.id
            session['role']=war.role 
            return redirect(url_for("wportal"))
        else:
            message="Failed to fetch"
    return render_template("login.html",message=message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register",methods=["GET","POST"])
def register():
    return render_template("reg.html")


@app.route("/regpar",methods=["GET","POST"])
def regpar():
    message=None
    if request.method=="POST":
        admno=request.form.get("admno")
        stud=Student.query.filter_by(admno=admno).first()
        if stud:
            par_name=request.form.get("fname")
            addressp=stud.address
            par_role=request.form.get("par_role")
            email=request.form.get("email")
            phone=request.form.get("phone")
            password_hash=request.form.get("pwd")
            if not Parent.query.filter_by(email=email).first():
                new_user=Parent(par_name=par_name,addressp=addressp,par_role=par_role,password_hash=password_hash,email=email,phone=phone)
                db.session.add(new_user)
                db.session.commit()
                stud.parent_id=new_user.id
                db.session.commit()
                return redirect("/")
            else:
                message="User Already Exists"
        else:
            message="Student not found"
    return render_template("regpar.html",message=message)

@app.route("/regward",methods=["GET","POST"])
def regward():
    if request.method=="POST":
        full_name=request.form.get("fname")
        address=request.form.get("address")
        hostel_name=request.form.get("hostel_name")
        email=request.form.get("email")
        phone_number=request.form.get("ph")
        password=request.form.get("pwd")

        if not Warden.query.filter_by(email=email).first():
            new_user=Warden(
                email=email,
                war_name=full_name,
                phone=phone_number,
                war_address=address,
                hos_name_war=hostel_name,
                password_hash=password
                )
            db.session.add(new_user)
            db.session.commit()
        else:
            return render_template("regward.html")
        return redirect("/")
    return render_template("regward.html")

@app.route("/regadmin",methods=["GET","POST"])
def regadmin():
    return render_template("regadmin.html")

@app.route("/regstud",methods=["GET","POST"])
def regstud():
    if request.method=="POST":
        full_name=request.form.get("fname")
        admno=request.form.get("admno")
        year=request.form.get("year")
        department=request.form.get("department")
        address=request.form.get("address")
        hostel_name=request.form.get("hostel_name")
        hostel_room=request.form.get("hostel_room")
        email=request.form.get("email")
        phone_number=request.form.get("ph")
        password=request.form.get("pwd")

        if not Student.query.filter_by(admno=admno).first():
            new_user=Student(
                email=email,
                full_name=full_name,
                admno=admno,
                study_year=year,
                phone_number=phone_number,
                department=department,
                address=address,
                hostel_name=hostel_name,
                hostel_room=hostel_room,
                password=password
                )
            db.session.add(new_user)
            db.session.commit()
        else:
            return render_template("regstud.html")
        return redirect("/")
    return render_template("regstud.html")

@app.route("/sportal")
def sportal():
    role=session.get('role')
    if role == 'student':
        gp=GatePassRequest.query.filter_by(student_id=session['id']).all()
        return render_template("studentportal.html",gp=gp)
    else:
        return redirect("/")
    
@app.route("/gpassreq/<int:id>",methods=["GET","POST"])
def gpassreq(id):
    message = None
    if request.method == 'POST':
        student_id = id
        student = Student.query.filter_by(admno=id).first()
        parent_id = student.parent_id if student else None
        
        if parent_id:
            parent = Parent.query.filter_by(id=parent_id).first()
            request_date = datetime.today()
            request_time = datetime.now().strftime("%I:%M:%S %p")
            pass_type = request.form.get('pass_type')
            reason = request.form.get('reason')
            place = request.form.get('place')
            gdate = request.form.get('gdate')
            going_date = datetime.strptime(gdate, "%Y-%m-%d").date()
            gtime = request.form.get('going_time')
            time_obj = datetime.strptime(gtime, "%H:%M")
            going_time = time_obj.strftime("%I:%M:%S %p")
            rdate = request.form.get('rdate')
            return_date = datetime.strptime(rdate, "%Y-%m-%d").date()

            newgpassentry = GatePassRequest(
                student_id=student_id,
                parent_id=parent_id,
                request_date=request_date,
                request_time=request_time,
                pass_type=pass_type,
                reason=reason,
                place=place,
                going_date=going_date,
                going_time=going_time,
                return_date=return_date
            )
            db.session.add(newgpassentry)
            db.session.commit()

            # Send email notification to the parent
            if parent and parent.email:
                try:
                    msg = Message("Gatepass Request Notification",
                                  recipients=[parent.email])
                    msg.body = f"""
                    Dear {parent.par_name},

                    Your child, {student.full_name}, has submitted a gatepass request.
                    
                    Request Details:
                    - Reason: {reason}
                    - Destination: {place}
                    - Going Date: {going_date}
                    - Return Date: {return_date}
                    - Status: Pending Parent Approval

                    Please log in to your portal to approve or reject the request.

                    Regards,
                    Hostel Management System
                    """
                    mail.send(msg)
                except Exception as e:
                    print("Failed to send email:", e)

        else:
            message = "Parent not yet Registered"
            return render_template("gatepassreq.html", message=message)

        return redirect(url_for("sportal"))

    return render_template("gatepassreq.html", message=message)

@app.route("/dwnl1/<int:id>")
def dwnl1(id):
    gatep=GatePassRequest.query.filter_by(student_id=id).all()
    return render_template("dwnl1.html",gatep=gatep)

@app.route("/dwnloadgp/<int:id>")
def dwnloadgp(id):
    gatepass=GatePassRequest.query.filter_by(id=id).first()
    return render_template("dwnloadgp.html",gatepass=gatepass)

@app.route("/pportal")
def pportal():
    role=session.get('role')
    if role == 'parent':
        gpass=db.session.query(GatePassRequest,Student.full_name).join(Student, Student.admno == GatePassRequest.student_id).filter(GatePassRequest.parent_id==session['id'])
        gp=GatePassRequest.query.filter_by(parent_id=session['id']).all()
        return render_template("parentportal.html",gp=gpass,gpass=gp)
    else:
        return redirect("/")

@app.route("/parentsanction/<int:id>",methods=["POST","GET"])
def psanction(id):
    obj=GatePassRequest.query.filter_by(id=id).first()
    if request.method=='POST':
        if "approve" in request.form:
            post_status = "parent_approved"
            obj.status=post_status
            db.session.commit()
            return redirect("/pportal")
        elif "reject" in request.form:
            post_status = "rejected"
            obj.status=post_status
            db.session.commit()
            return redirect("/pportal")
    return render_template("parentsanction.html",gp=obj)

@app.route("/allgpas")
def allg():
    role=session.get('role')
    if role == 'parent':
        gp=GatePassRequest.query.filter_by(parent_id=session['id']).all()
        return render_template("allgpass.html",gp=gp)
    else:
        return redirect("/")
    
@app.route("/wportal")
def wportal():
    role=session.get('role')
    if role == 'warden':
        hname=Warden.query.filter_by(id=session['id']).first().hos_name_war
        today = date.today()
        students_outside = (
        db.session.query(GatePassRequest.student_id)
        .join(Student, Student.admno == GatePassRequest.student_id)
        .filter(GatePassRequest.going_date <= today)
        .filter(GatePassRequest.return_date >= today)
        .filter(Student.hostel_name == hname)
        .filter(GatePassRequest.status=='approved')
        .distinct()
        .count())
        pendingpass=(
            db.session.query(GatePassRequest.student_id)
            .join(Student,Student.admno == GatePassRequest.student_id)
            .filter(Student.hostel_name == hname)
            .filter(GatePassRequest.status == 'parent_approved')
            .count()
        )
        notify=(
            db.session.query(GatePassRequest.student_id, Student.full_name,GatePassRequest.id)
            .join(Student, Student.admno == GatePassRequest.student_id)
            .filter(Student.hostel_name == hname)
            .filter(GatePassRequest.status == 'parent_approved')
            .all()
        )

        return render_template("wardenportal.html",students_outside=students_outside,pendingpass=pendingpass,notify=notify)
    else:
        return redirect("/")
    
@app.route("/cabbook")
def cabbook():
    return render_template("cabbooking.html")

@app.route("/studentlog")
def studentlog():
    role=session.get('role')
    if role == 'warden':
        hname=Warden.query.filter_by(id=session['id']).first().hos_name_war
        sdetails=(
            db.session.query(Student.full_name,Student.admno,Student.hostel_room,GatePassRequest.request_date,GatePassRequest.request_time,GatePassRequest.going_date,GatePassRequest.going_time)
            .join(Student, Student.admno == GatePassRequest.student_id)
            .filter(Student.hostel_name == hname)
            .filter(GatePassRequest.status == 'approved')
            .all()
        )
        return render_template("student-log.html",students=sdetails)
    else:
        return redirect("/")

@app.route("/homelog")
def homelog():
    role=session.get('role')
    if role == 'warden':
        hname=Warden.query.filter_by(id=session['id']).first().hos_name_war
        sdetails=(
            db.session.query(Student.full_name,Student.admno,Student.hostel_room,GatePassRequest.going_date,GatePassRequest.going_time,GatePassRequest.status,GatePassRequest.id)
            .join(Student, Student.admno == GatePassRequest.student_id)
            .filter(Student.hostel_name == hname)
            .filter(GatePassRequest.pass_type == 'homegoing')
            .all()
        )
    return render_template("homelog.html",students=sdetails)

@app.route("/movementlog")
def movelog():
    role=session.get('role')
    if role == 'warden':
        hname=Warden.query.filter_by(id=session['id']).first().hos_name_war
        sdetails=(
            db.session.query(Student.full_name,Student.admno,Student.hostel_room,GatePassRequest.going_date,GatePassRequest.going_time,GatePassRequest.status,GatePassRequest.id)
            .join(Student, Student.admno == GatePassRequest.student_id)
            .filter(Student.hostel_name == hname)
            .filter(GatePassRequest.pass_type == 'movement')
            .all()
        )
    return render_template("Movementlog.html",students=sdetails)

@app.route("/wardensanction/<int:id>",methods=["POST","GET"])
def wsanction(id):
    obj=GatePassRequest.query.filter_by(id=id).first()
    admno=obj.student_id
    studendetails=Student.query.filter_by(admno=admno).first()
    if request.method=='POST':
        if "approve" in request.form:
            post_status = "approved"
            obj.status=post_status
            db.session.commit()
            try:
                msg = Message("Gatepass Request Notification",
                                  recipients=[studendetails.email])
                msg.body = f"""
                    Dear {studendetails.full_name},

                    Your gate pass request has been **approved**.

                    You can download your gate pass using the link below:

                    🔗 [Download Gatepass](http://127.0.0.1:5000/api/download-gatepass/{admno})  
                        or copy and paste this URL into your browser:  
                        http://127.0.0.1:5000/api/download-gatepass/{admno}

                    Best regards,  
                    **Hostel Management System**
    """
                mail.send(msg)
            except Exception as e:
                    print("Failed to send email:", e)

            return redirect("/wportal")
        elif "reject" in request.form:
            post_status = "rejected"
            obj.status=post_status
            db.session.commit()
            return redirect("/wportal")
    return render_template("wardensanction.html",gp=obj)

@app.route("/linkstudent",methods=["GET","POST"])
def linkstudent():
    role=session.get('role')
    if role=='parent':
        message=None
        if request.method=="POST":
            admno=request.form.get("admno")
            stud=Student.query.filter_by(admno=admno).first()
            if stud:
                if stud.parent_id:
                    message="Parent already registered"
                else:
                    stud.parent_id=session['id']
                    db.session.commit()
                    return redirect("/pportal")
            else:
                message="Student not found"
        return render_template("linkstudent.html",message=message)
    else:
        return redirect("/")
    
@app.route("/studentlog/searchslog")
def searchslog():
    searchstud=None
    query = request.args.get('query', '')
    role=session.get('role')
    econ=session.get('id')
    if econ==None:
        return redirect(url_for("login"))
    hname=Warden.query.filter_by(id=session['id']).first().hos_name_war
    if query!='':
        if role=='warden':
            searchstud=(
    db.session.query(
        Student.full_name, 
        Student.admno, 
        Student.hostel_room, 
        GatePassRequest.request_date, 
        GatePassRequest.request_time, 
        GatePassRequest.going_date, 
        GatePassRequest.going_time
    )
    .join(Student, Student.admno == GatePassRequest.student_id)
    .filter(Student.hostel_name == hname)
    .filter(GatePassRequest.status == 'approved')
    .filter(or_(Student.full_name.ilike(f"%{query}%"), Student.admno.ilike(f"%{query}%")))
    .all()
)

        else:
            return redirect(url_for("login"))

    return render_template("student-log.html",students=searchstud)

@app.route("/movementlog/searchslog")
def searchmlog():
    searchstud=None
    query = request.args.get('query', '')
    role=session.get('role')
    econ=session.get('id')
    if econ==None:
        return redirect(url_for("login"))
    hname=Warden.query.filter_by(id=session['id']).first().hos_name_war
    if query!='':
        if role=='warden':
            searchstud=(
    db.session.query(
        Student.full_name, 
        Student.admno, 
        Student.hostel_room, 
        GatePassRequest.request_date, 
        GatePassRequest.request_time, 
        GatePassRequest.going_date, 
        GatePassRequest.going_time
    )
    .join(Student, Student.admno == GatePassRequest.student_id)
    .filter(Student.hostel_name == hname)
    .filter(GatePassRequest.status == 'approved')
    .filter(GatePassRequest.pass_type == 'movement')
    .filter(or_(Student.full_name.ilike(f"%{query}%"), Student.admno.ilike(f"%{query}%")))
    .all()
)

        else:
            return redirect(url_for("login"))

    return render_template("Movementlog.html",students=searchstud)

@app.route("/homelog/searchslog")
def searchhlog():
    searchstud=None
    query = request.args.get('query', '')
    role=session.get('role')
    econ=session.get('id')
    if econ==None:
        return redirect(url_for("login"))
    hname=Warden.query.filter_by(id=session['id']).first().hos_name_war
    if query!='':
        if role=='warden':
            searchstud=(
    db.session.query(
        Student.full_name, 
        Student.admno, 
        Student.hostel_room, 
        GatePassRequest.request_date, 
        GatePassRequest.request_time, 
        GatePassRequest.going_date, 
        GatePassRequest.going_time
    )
    .join(Student, Student.admno == GatePassRequest.student_id)
    .filter(Student.hostel_name == hname)
    .filter(GatePassRequest.status == 'approved')
    .filter(GatePassRequest.pass_type == 'homegoing')
    .filter(or_(Student.full_name.ilike(f"%{query}%"), Student.admno.ilike(f"%{query}%")))
    .all()
)

        else:
            return redirect(url_for("login"))

    return render_template("homelog.html",students=searchstud)

