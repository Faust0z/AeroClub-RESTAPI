import random

from faker import Faker
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Roles, Users, Planes, PlaneStatus, PaymentTypes, Balances, AirportCodes, ItineraryTypes

fake = Faker()


def create_roles():
    db.session.add(Roles(name="User"))
    db.session.add(Roles(name="Instructor"))
    db.session.add(Roles(name="Admin"))
    db.session.commit()
    print(f"Added User, Instructor and Admin roles to the database.")


def create_airport_codes():
    for n in range(8):
        db.session.add(AirportCodes(code=f"A{n}{n + 1}"))
    db.session.commit()
    print(f"Airport codes created.")


def create_payment_types():
    db.session.add(PaymentTypes(type="Check"))
    db.session.add(PaymentTypes(type="Cash"))
    db.session.add(PaymentTypes(type="Transfer"))
    db.session.add(PaymentTypes(type="Flight Session"))
    print(f"Added payment types: Check, Cash, Transfer and Flight Session to the database.")


def create_plane_status():
    db.session.add(PlaneStatus(state="Active"))
    db.session.add(PlaneStatus(state="Under maintenance"))
    db.session.add(PlaneStatus(state="Disabled"))
    db.session.add(PlaneStatus(state="Out of service"))
    db.session.commit()
    print(f"Added plane status: Active, In maintenance, Disabled and Out of service to the database.")


def create_postman_users():
    user_role = db.session.scalar(db.select(Roles).where(Roles.name == "User"))
    instructor_role = db.session.scalar(db.select(Roles).where(Roles.name == "Instructor"))
    admin_role = db.session.scalar(db.select(Roles).where(Roles.name == "Admin"))
    user = Users(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email="postman_user@email.com",
        password=generate_password_hash("postman_password"),
        phone_number=fake.phone_number(),
        created_at=fake.date_between(start_date='-2y', end_date='today'),
        status=True,
        roles=[user_role]
    )
    user.balance = Balances(balance=0, user_id=user.id)
    db.session.add(user)

    instructor = Users(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email="postman_instructor@email.com",
        password=generate_password_hash("postman_password"),
        phone_number=fake.phone_number(),
        created_at=fake.date_between(start_date='-2y', end_date='today'),
        status=True,
        roles=[instructor_role, user_role]
    )
    instructor.balance = Balances(balance=0, user_id=user.id)
    db.session.add(instructor)

    admin = Users(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email="postman_admin@email.com",
        password=generate_password_hash("postman_password"),
        phone_number=fake.phone_number(),
        created_at=fake.date_between(start_date='-2y', end_date='today'),
        status=True,
        roles=[user_role, admin_role]
    )
    admin.balance = Balances(balance=0, user_id=user.id)
    db.session.add(admin)

    db.session.commit()
    print(f"Added postman ready example users to the database with the emails: "
          f"postman_user@email.com, "
          f"postman_instructor@email.com and "
          f"postman_admin@email.com.")


def create_random_users(amount: int):
    roles = db.session.query(Roles).all()
    user_role = db.session.scalar(db.select(Roles).where(Roles.name == "User"))

    for _ in range(amount):
        user = Users(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            password=generate_password_hash("password123"),
            phone_number=fake.phone_number(),
            created_at=fake.date_between(start_date='-2y', end_date='today'),
            disabled_at=None,
            address=fake.address(),
            status=True,
            roles=[random.choice(roles)]
        )
        if not "User" in user.roles:
            user.roles.append(user_role)

        user.balance = Balances(balance=0, user_id=user.id)

        db.session.add(user)

    db.session.commit()
    print(f"Added {amount} random users to the database.")


def create_planes():
    plane_status = db.session.query(PlaneStatus).all()
    sample_planes = [
        {
            "brand": "Cessna",
            "model": "172 Skyhawk",
            "registration": "LV-ABC",
            "category": "Single Engine Piston",
            "consumption_per_hour": 36,
            "fare": 180.0,
            "description": "Reliable trainer aircraft, great for student pilots."
        },
        {
            "brand": "Piper",
            "model": "PA-28 Cherokee",
            "registration": "LV-XYZ",
            "category": "Single Engine Piston",
            "consumption_per_hour": 34,
            "fare": 170.0,
            "description": "Low-wing trainer, comfortable and versatile."
        },
        {
            "brand": "Beechcraft",
            "model": "Baron G58",
            "registration": "LV-BAR",
            "category": "Twin Engine Piston",
            "consumption_per_hour": 92,
            "fare": 400.0,
            "description": "Twin-engine trainer, suitable for complex ratings."
        },
        {
            "brand": "Diamond",
            "model": "DA40",
            "registration": "LV-D40",
            "category": "Single Engine Piston",
            "consumption_per_hour": 28,
            "fare": 200.0,
            "description": "Modern composite trainer with advanced avionics."
        },
        {
            "brand": "Tecnam",
            "model": "P2006T",
            "registration": "LV-200",
            "category": "Twin Engine Piston",
            "consumption_per_hour": 65,
            "fare": 350.0,
            "description": "Light twin trainer, very efficient."
        }
    ]

    for plane in sample_planes:
        db.session.add(
            Planes(
                brand=plane["brand"],
                model=plane["model"],
                registration=plane["registration"],
                category=plane["category"],
                acquisition_date=fake.date_between(start_date='-10y', end_date='-1y'),
                consumption_per_hour=plane["consumption_per_hour"],
                fare=plane["fare"],
                description=plane["description"],
                plane_status=random.choice(plane_status)
            )
        )

    db.session.commit()
    print(f"Added {len(sample_planes)} planes to the database.")


def create_itinerary_types():
    itinerary_types = [
        ItineraryTypes(type="Solo flight"),
        ItineraryTypes(type="Dual flight"),
        ItineraryTypes(type="Cross-country flight"),
        ItineraryTypes(type="Instrument hood flight"),
        ItineraryTypes(type="Night flight"),
    ]

    db.session.add_all(itinerary_types)
    db.session.commit()
    print("Added itinerary types: Solo, Dual, Cross-country, Instrument hood, Night.")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        # create_airport_codes(10)
        # create_payment_types()
        # create_roles()
        # create_postman_users()
        # create_plane_status()
        # create_planes()
        create_itinerary_types()
        # create_random_users(20)  # adjust number as needed
