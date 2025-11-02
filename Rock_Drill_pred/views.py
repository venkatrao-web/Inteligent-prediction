from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from User_Admin_app.models import CustomUser  # ✅ Updated app name
import pandas as pd
import numpy as np
import pickle
import os

# ML imports
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor


# -----------------------------
# 🔹 Train ML Models and Compare (Rock Drillability)
# -----------------------------
def train_model(request):
    try:
        # Dataset path
        data_path = os.path.join(settings.MEDIA_ROOT, 'balanced_rock_drillability_10000.csv')
        data = pd.read_csv(data_path)

        # Split features and target
        X = data.drop(columns=['Drillability_Index'])
        y = data['Drillability_Index']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Save the scaler
        scaler_path = os.path.join(settings.MEDIA_ROOT, 'models', 'scaler.pkl')
        os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)

        # Define models
        models = {
            "Linear Regression": LinearRegression(),
            "Support Vector Regressor": SVR(kernel='rbf', C=100, gamma=0.1),
            "Random Forest": RandomForestRegressor(n_estimators=200, random_state=42),
            "Decision Tree": DecisionTreeRegressor(random_state=42),
            "KNN Regressor": KNeighborsRegressor(n_neighbors=5)
        }

        results = []

        # Train and evaluate models
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)

            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            # Save model to media/models folder
            model_path = os.path.join(settings.MEDIA_ROOT, 'models', f"{name.replace(' ', '_').lower()}.pkl")
            with open(model_path, 'wb') as file:
                pickle.dump(model, file)

            results.append({
                "Model": name,
                "R2_Score": round(r2, 4),
                "MSE": round(mse, 4),
                "MAE": round(mae, 4)
            })

        # Sort by R²
        results_df = pd.DataFrame(results).sort_values(by="R2_Score", ascending=False)

        context = {
            "results": results_df.to_dict(orient='records'),
            "best_model": results_df.iloc[0]["Model"]
        }

        return render(request, 'train_result.html', context)

    except Exception as e:
        return render(request, 'train_result.html', {'error': f'Error during training: {str(e)}'})


# -----------------------------
# 🔹 Load specific model and scaler
# -----------------------------
def load_model_and_scaler(algorithm_name):
    model_file = f"{algorithm_name.replace(' ', '_').lower()}.pkl"
    model_path = os.path.join(settings.MEDIA_ROOT, 'models', model_file)
    scaler_path = os.path.join(settings.MEDIA_ROOT, 'models', 'scaler.pkl')

    if os.path.exists(model_path) and os.path.exists(scaler_path):
        with open(model_path, 'rb') as f1, open(scaler_path, 'rb') as f2:
            model = pickle.load(f1)
            scaler = pickle.load(f2)
        return model, scaler
    return None, None


# -----------------------------
# 🔹 Input Page for Rock Drillability Prediction
# -----------------------------
def input_page(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_page')

    user = CustomUser.objects.get(id=user_id)

    if not user.is_approved:
        return render(request, 'result.html', {
            'error': 'Your account is not yet approved by the admin. Please wait for approval.'
        })

    algorithms = [
        "Linear Regression",
        "Support Vector Regressor",
        "Random Forest",
        "Decision Tree",
        "KNN Regressor"
    ]

    if request.method == 'POST':
        try:
            algorithm = request.POST.get('algorithm')
            model, scaler = load_model_and_scaler(algorithm)

            if model is None or scaler is None:
                return render(request, 'result.html', {'error': f'{algorithm} model not found. Please train first.'})

            # Collect form inputs
            depth = float(request.POST.get('depth'))
            porosity = float(request.POST.get('porosity'))
            density = float(request.POST.get('density'))
            gamma = float(request.POST.get('gamma'))
            sonic = float(request.POST.get('sonic'))
            resistivity = float(request.POST.get('resistivity'))
            pressure = float(request.POST.get('pressure'))

            # Prepare input
            input_data = np.array([[depth, porosity, density, gamma, sonic, resistivity, pressure]])
            input_scaled = scaler.transform(input_data)

            # Predict
            prediction = model.predict(input_scaled)[0]

            return render(request, 'result.html', {
                'result': f'{prediction:.2f}',
                'algorithm': algorithm
            })

        except Exception as e:
            return render(request, 'result.html', {'error': f'Error during prediction: {str(e)}'})

    return render(request, 'input.html', {'username': user.username, 'algorithms': algorithms})


# -----------------------------
# 🔹 Result Page
# -----------------------------
def result_page(request):
    if not request.session.get('user_id'):
        return redirect('login_page')
    return render(request, 'result.html')
