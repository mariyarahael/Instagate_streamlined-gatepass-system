from flask import request, jsonify, session, Response
from flask_restful import Resource
from models.models import Student, GatePassRequest
from reportlab.pdfgen import canvas
import io

class StudentLoginAPI(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        student = Student.query.filter_by(email=email, password=password).first()
        if student:
            session['id'] = student.admno
            session['role'] = student.role
            return {"message": "Login successful", "student_id": student.admno}
        else:
            return {"message": "Invalid credentials"}, 401

class DownloadGatePassAPI(Resource):
    def get(self, student_id):
        gate_pass = GatePassRequest.query.filter_by(student_id=student_id).order_by(GatePassRequest.id.desc()).first()
        
        if not gate_pass:
            return jsonify({"message": "No gate pass found for this student"}), 404

        # Create a PDF in memory
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)

        pdf.drawString(100, 750, f"Gate Pass for {gate_pass.student_id}")
        pdf.drawString(100, 730, f"Pass Type: {gate_pass.pass_type}")
        pdf.drawString(100, 710, f"Reason: {gate_pass.reason}")
        pdf.drawString(100, 690, f"Going Date: {gate_pass.going_date}")
        pdf.drawString(100, 670, f"Return Date: {gate_pass.return_date}")
        pdf.drawString(100, 650, f"Status: {gate_pass.status}")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)

        return Response(buffer, mimetype='application/pdf',
                        headers={"Content-Disposition": f"attachment;filename=gate_pass_{student_id}.pdf"})
