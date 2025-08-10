import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Teacher, Student, SessionToken, AuditLog
from .utils import hash_password, verify_password, make_token, token_expires, calculate_new_marks
from .auth import token_required


@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    try:
        payload = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    username = payload.get("username", "").strip()
    password = payload.get("password", "")
    name = payload.get("name", "").strip()


    if not username or not password:
        return JsonResponse({"error": "Both username and password are required"}, status=400)

    if Teacher.objects.filter(username=username).exists():
        return JsonResponse({"error": f"Username '{username}' is already taken"}, status=400)
    if not name:
        return JsonResponse({"error": "Name is required"}, status=400)

    pw_hash, salt = hash_password(password)
    Teacher.objects.create(username=username, password_hash=pw_hash, salt=salt)

    return JsonResponse({"success": True, "message": f"Teacher {username} registered successfully"})


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        payload = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    username = payload.get("username", "").strip()
    password = payload.get("password", "")

    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    teacher = Teacher.objects.filter(username=username).first()
    if not teacher or not verify_password(password, teacher.salt, teacher.password_hash):
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    # create session token
    token = make_token()
    expires_at = token_expires()
    SessionToken.objects.create(token=token, teacher=teacher, expires_at=expires_at)

    return JsonResponse({"token": token, "expires_at": expires_at.isoformat()})


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def logout_view(request):
    if hasattr(request, "session_token"):
        request.session_token.delete()
    return JsonResponse({"success": True, "message": "Logged out successfully"})


@csrf_exempt
@require_http_methods(["GET"])
@token_required
def list_students(request):
    students = Student.objects.all().order_by("name", "subject")
    data = [
        {
            "id": s.id,
            "name": s.name,
            "subject": s.subject,
            "marks": s.marks
        } for s in students
    ]
    return JsonResponse({"count": len(data), "students": data})


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def add_student(request):
    try:
        payload = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = payload.get("name", "").strip()
    subject = payload.get("subject", "").strip()

    try:
        marks = int(payload.get("marks", -1))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Marks must be a number"}, status=400)

    if not name or not subject:
        return JsonResponse({"error": "Name and subject are required"}, status=400)

    if not (0 <= marks <= 100):
        return JsonResponse({"error": "Marks should be between 0 and 100"}, status=400)

    try:
        with transaction.atomic():
            existing = Student.objects.select_for_update().filter(
                name__iexact=name,
                subject__iexact=subject
            ).first()

            if existing:
                try:
                    updated_marks = calculate_new_marks(existing.marks, marks)
                except ValueError as e:
                    return JsonResponse({"error": str(e)}, status=400)

                old_marks = existing.marks
                existing.marks = updated_marks
                existing.save()

                AuditLog.objects.create(
                    teacher=request.teacher,
                    student=existing,
                    action="UPDATE",
                    field="marks",
                    old_value=str(old_marks),
                    new_value=str(updated_marks)
                )

                return JsonResponse({"success": True, "action": "updated", "student_id": existing.id})
            else:
                new_student = Student.objects.create(name=name, subject=subject, marks=marks)
                AuditLog.objects.create(
                    teacher=request.teacher,
                    student=new_student,
                    action="INSERT",
                    new_value=f"{name} - {subject} - {marks}"
                )
                return JsonResponse({"success": True, "action": "inserted", "student_id": new_student.id})

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {e}"}, status=500)



@csrf_exempt
@require_http_methods(["PUT"])
@token_required
def update_marks(request):
    try:
        data = json.loads(request.body)
        student_id = int(data.get("student_id"))
        marks = int(data.get("marks"))
    except Exception:
        return JsonResponse({"error": "invalid input"}, status=400)

    if marks < 0 or marks > 100:
        return JsonResponse({"error": "marks must be 0..100"}, status=400)

    try:
        with transaction.atomic():
            s = Student.objects.select_for_update().get(id=student_id)
            old = s.marks
            s.marks = marks
            s.save()
            AuditLog.objects.create(teacher=request.teacher, student=s,
                                    action="UPDATE", field="marks",
                                    old_value=str(old), new_value=str(marks))
            return JsonResponse({"ok": True, "student_id": s.id, "marks": s.marks})
    except Student.DoesNotExist:
        return JsonResponse({"error": "student not found"}, status=404)
    except Exception as e:

        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
@token_required
def delete_student(request):
    try:
        payload = json.loads(request.body)
        student_id = int(payload.get("student_id", 0))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid student_id"}, status=400)

    try:
        with transaction.atomic():
            student = Student.objects.select_for_update().get(id=student_id)

            AuditLog.objects.create(
                teacher=request.teacher,
                student=student,
                action="DELETE",
                old_value=f"{student.name} - {student.subject} - {student.marks}"
            )

            student.delete()

        return JsonResponse({"success": True, "message": "Student deleted"})

    except Student.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)




















