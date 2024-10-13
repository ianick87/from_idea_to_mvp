from django.shortcuts import render, get_object_or_404, redirect
from .models import Data
from .forms import DataForm
from .forms import CSVUploadForm
from django.contrib import messages
import csv
from .services.ai_service import AiService


def data_list(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle CSV import
            csv_file = request.FILES["csv_file"]
            try:
                data = csv_file.read().decode("utf-8").splitlines()
                reader = csv.DictReader(data)
                for row in reader:
                    Data.objects.create(
                        name=row["name"],
                        age=int(row["age"]),
                        gender=row["gender"],
                        weight=float(row["weight"]),
                        height=float(row["height"]),
                        temperature=float(row["temperature"]),
                        pulse=int(row["pulse"]),
                        blood_pressure=row["blood_pressure"],
                        headache=row["headache"].strip().lower() == "true",
                        stomach_pain=row["stomach_pain"].strip().lower() == "true",
                        throat_pain=row["throat_pain"].strip().lower() == "true",
                        has_disease=row["has_disease"].strip().lower() == "true",
                    )
                messages.success(request, "Patients imported successfully!")
                return redirect("data_list")
            except Exception as e:
                messages.error(request, f"Error importing data: {str(e)}")
                return redirect("data_list")
    else:
        form = CSVUploadForm()

    datas = Data.objects.all()
    return render(request, "data_list.html", {"datas": datas, "form": form})


def data_detail(request, pk):
    data = get_object_or_404(Data, pk=pk)
    return render(request, "data_detail.html", {"data": data})


def data_new(request):
    if request.method == "POST":
        form = DataForm(request.POST)
        if form.is_valid():
            data = form.save()
            return redirect("data_detail", pk=data.pk)
    else:
        form = DataForm()
    return render(request, "data_edit.html", {"form": form})


def data_edit(request, pk):
    data = get_object_or_404(Data, pk=pk)
    if request.method == "POST":
        form = DataForm(request.POST, instance=data)
        if form.is_valid():
            data = form.save()
            return redirect("data_detail", pk=data.pk)
    else:
        form = DataForm(instance=data)
    return render(request, "data_edit.html", {"form": form})


def data_delete(request, pk):
    data = get_object_or_404(Data, pk=pk)
    data.delete()
    return redirect("data_list")


def train_model_view(request):
    ai_service = AiService()
    try:
        # Train the model and get detailed performance metrics
        results = ai_service.train_model()
        # Extract the metrics from the results dictionary 				model = results[‘model']
        accuracy = results["accuracy"]
        precision = results["precision"]
        recall = results["recall"]
        f1_score = results["f1_score"]
        confusion_matrix = results["confusion_matrix"]

        # Pass the metrics to the template
        context = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "confusion_matrix": confusion_matrix,
        }
        return render(request, "train_model.html", context)

    except ValueError as e:
        return render(request, "train_model.html", {"error": str(e)})


def diagnose_view(request):
    if request.method == "POST":
        form = DataForm(request.POST)
        if form.is_valid():
            data_data = form.cleaned_data
            # Prepare input data
            input_data = [
                data_data["age"],
                0 if data_data["gender"] == "M" else 1,
                data_data["weight"],
                data_data["height"],
                data_data["temperature"],
                data_data["pulse"],
                # Convert blood pressure
                float(data_data["blood_pressure"].split("/")[0]),
                float(data_data["blood_pressure"].split("/")[1]),
                int(data_data["headache"]),
                int(data_data["stomach_pain"]),
                int(data_data["throat_pain"]),
            ]
            ai_service = AiService()
            try:
                prediction, confidence = ai_service.get_prediction(input_data)
                return render(
                    request,
                    "diagnosis_result.html",
                    {
                        "prediction": prediction,
                        "confidence": confidence * 100,
                        "data_name": data_data["name"],
                    },
                )
            except FileNotFoundError as e:
                return render(
                    request,
                    "diagnose.html",
                    {"form": form, "error": str(e)},
                )
    else:
        form = DataForm()
    return render(request, "diagnose.html", {"form": form})
