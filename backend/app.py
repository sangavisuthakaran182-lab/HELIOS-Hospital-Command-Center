from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# =========================================================
# INITIAL HOSPITAL STATE
# =========================================================

hospital = {

    "beds": 120,
    "doctors": 26,
    "nurses": 57,
    "ventilators": 18,

    "emergency_patients": 35,
    "emergency_arrivals": 8,

    "emergency_beds": 10,
    "emergency_doctors": 3,
    "emergency_nurses": 7
}


# =========================================================
# RESOURCE POOLS
#
# These are CONFIGURABLE hospital inputs.
# They are not optimization rules.
# =========================================================

resource_pools = {

    "General": {
        "beds": 40,
        "doctors": 5,
        "nurses": 15
    },

    "ICU": {
        "beds": 8,
        "doctors": 3,
        "nurses": 6
    },

    "OPD": {
        "beds": 20,
        "doctors": 6,
        "nurses": 12
    }
}


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return "HELIOS Hospital Command Center is running!"


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/api/dashboard")
def dashboard():

    return jsonify({
        "hospital": hospital,
        "resource_pools": resource_pools
    })


# =========================================================
# SIMULATE EMERGENCY SURGE
# =========================================================

@app.route("/api/simulate", methods=["POST"])
def simulate():

    hospital["emergency_patients"] += 30

    hospital["emergency_arrivals"] += 12

    hospital["emergency_beds"] = max(
        1,
        hospital["emergency_beds"] - 8
    )

    hospital["emergency_doctors"] = max(
        1,
        hospital["emergency_doctors"] - 2
    )

    hospital["emergency_nurses"] = max(
        1,
        hospital["emergency_nurses"] - 4
    )

    return jsonify({
        "message": "Emergency surge simulated",
        "hospital": hospital
    })


# =========================================================
# BASIC OPTIMIZATION
# =========================================================

@app.route("/api/optimize", methods=["POST"])
def optimize():

    recommendations = []

    patients = hospital["emergency_patients"]

    if patients > 50:

        recommendations.append({
            "from": "Resource Pool",
            "to": "Emergency",
            "resource": "Beds",
            "quantity": 8
        })

        recommendations.append({
            "from": "Resource Pool",
            "to": "Emergency",
            "resource": "Doctors",
            "quantity": 2
        })

        recommendations.append({
            "from": "Resource Pool",
            "to": "Emergency",
            "resource": "Nurses",
            "quantity": 4
        })

        status = "HIGH RESOURCE PRESSURE"

    else:

        recommendations.append({
            "from": "System",
            "to": "Emergency",
            "resource": "Resources",
            "quantity": 0
        })

        status = "NORMAL"

    return jsonify({
        "status": status,
        "recommendations": recommendations
    })


# =========================================================
# WHAT-IF SCENARIO
# =========================================================

@app.route("/api/scenario", methods=["POST"])
def scenario():

    data = request.get_json()

    patients = int(data.get("patients", 0))
    arrivals = int(data.get("arrivals", 0))
    beds = int(data.get("beds", 0))
    doctors = int(data.get("doctors", 0))
    nurses = int(data.get("nurses", 0))
    ventilators = int(data.get("ventilators", 0))


    # =====================================================
    # DEMAND CALCULATION
    # =====================================================

    required_beds = max(
        10,
        int(patients * 0.8)
    )

    required_doctors = max(
        2,
        int(patients / 15)
    )

    required_nurses = max(
        4,
        int(patients / 7)
    )

    required_ventilators = max(
        1,
        int(patients * 0.08)
    )


    # =====================================================
    # DEFICIT CALCULATION
    # =====================================================

    bed_deficit = max(
        0,
        required_beds - beds
    )

    doctor_deficit = max(
        0,
        required_doctors - doctors
    )

    nurse_deficit = max(
        0,
        required_nurses - nurses
    )

    ventilator_deficit = max(
        0,
        required_ventilators - ventilators
    )


    total_deficit = (
        bed_deficit
        + doctor_deficit
        + nurse_deficit
        + ventilator_deficit
    )


    # =====================================================
    # SURGE DETECTION
    # =====================================================

    if arrivals >= 20 or patients >= 60:

        surge_status = "SURGE DETECTED"

    elif arrivals >= 12 or patients >= 45:

        surge_status = "MODERATE PRESSURE"

    else:

        surge_status = "NORMAL"


    # =====================================================
    # RESOURCE STATUS
    # =====================================================

    if total_deficit == 0:

        resource_status = "RESOURCES SUFFICIENT"

    elif total_deficit <= 10:

        resource_status = "MINOR RESOURCE SHORTAGE"

    else:

        resource_status = "CRITICAL RESOURCE SHORTAGE"


    # =====================================================
    # DYNAMIC RESOURCE ALLOCATION
    # =====================================================

    allocations = []

    remaining_beds = bed_deficit
    remaining_doctors = doctor_deficit
    remaining_nurses = nurse_deficit


    # -----------------------------------------------------
    # Sort departments according to available capacity
    #
    # This means HELIOS examines the resource pools
    # instead of blindly selecting one department.
    # -----------------------------------------------------

    departments = sorted(
        resource_pools.keys(),
        key=lambda department:
            resource_pools[department]["beds"],
        reverse=True
    )


    # -----------------------------------------------------
    # BED ALLOCATION
    # -----------------------------------------------------

    for department in departments:

        if remaining_beds <= 0:
            break

        available = resource_pools[
            department
        ]["beds"]

        allocation = min(
            available,
            remaining_beds
        )

        if allocation > 0:

            allocations.append({

                "from": department,

                "to": "Emergency",

                "resource": "Beds",

                "quantity": allocation,

                "reason":
                    f"{department} has "
                    f"{available} available beds"

            })

            remaining_beds -= allocation


    # -----------------------------------------------------
    # DOCTOR ALLOCATION
    # -----------------------------------------------------

    for department in departments:

        if remaining_doctors <= 0:
            break

        available = resource_pools[
            department
        ]["doctors"]

        allocation = min(
            available,
            remaining_doctors
        )

        if allocation > 0:

            allocations.append({

                "from": department,

                "to": "Emergency",

                "resource": "Doctors",

                "quantity": allocation,

                "reason":
                    f"{department} has "
                    f"{available} available doctors"

            })

            remaining_doctors -= allocation


    # -----------------------------------------------------
    # NURSE ALLOCATION
    # -----------------------------------------------------

    for department in departments:

        if remaining_nurses <= 0:
            break

        available = resource_pools[
            department
        ]["nurses"]

        allocation = min(
            available,
            remaining_nurses
        )

        if allocation > 0:

            allocations.append({

                "from": department,

                "to": "Emergency",

                "resource": "Nurses",

                "quantity": allocation,

                "reason":
                    f"{department} has "
                    f"{available} available nurses"

            })

            remaining_nurses -= allocation


    # =====================================================
    # UNRESOLVED DEFICIT
    # =====================================================

    unresolved = {

        "beds": remaining_beds,

        "doctors": remaining_doctors,

        "nurses": remaining_nurses,

        "ventilators": ventilator_deficit

    }


    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return jsonify({

        "scenario": {

            "patients": patients,

            "arrivals": arrivals,

            "beds": beds,

            "doctors": doctors,

            "nurses": nurses,

            "ventilators": ventilators

        },


        "demand": {

            "required_beds":
                required_beds,

            "required_doctors":
                required_doctors,

            "required_nurses":
                required_nurses,

            "required_ventilators":
                required_ventilators

        },


        "deficit": {

            "beds":
                bed_deficit,

            "doctors":
                doctor_deficit,

            "nurses":
                nurse_deficit,

            "ventilators":
                ventilator_deficit,

            "total":
                total_deficit

        },


        "surge_status":
            surge_status,


        "resource_status":
            resource_status,


        "allocations":
            allocations,


        "unresolved":
            unresolved

    })


# =========================================================
# RESET
# =========================================================

@app.route("/api/reset", methods=["POST"])
def reset():

    hospital.update({

        "beds": 120,

        "doctors": 26,

        "nurses": 57,

        "ventilators": 18,

        "emergency_patients": 35,

        "emergency_arrivals": 8,

        "emergency_beds": 10,

        "emergency_doctors": 3,

        "emergency_nurses": 7

    })


    return jsonify({

        "message":
            "Hospital state reset",

        "hospital":
            hospital,

        "resource_pools":
            resource_pools

    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )