from app import create_app, db  # Import z lokálního balíčku app
from app.models import *  # Importujte své modely
import os

# Získání názvu konfigurace z proměnné prostředí nebo default
config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)

# Zde můžete přidat příkazy pro Flask CLI pomocí app.cli.command()
# Například pro vytvoření databáze nebo seedování dat
@app.cli.command("seed-db")
def seed_db():
    """Seeds the database with initial data."""
    print("Seeding database...")
    
    # 1. Create Roles
    from app.utils.enums import UserRoleEnum
    roles = {}
    for role_enum in UserRoleEnum:
        role_name = role_enum.value
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=f"Default {role_name} role")
            db.session.add(role)
            print(f"Added role: {role_name}")
        roles[role_name] = role
    db.session.commit()

    # 2. Create Publishers
    publishers = []
    publisher_data = [
        {"name": "O'Reilly Media", "address": "Sebastopol, CA"},
        {"name": "Addison-Wesley", "address": "Boston, MA"},
        {"name": "Manning Publications", "address": "Shelter Island, NY"}
    ]
    for p_data in publisher_data:
        publisher = Publisher.query.filter_by(name=p_data["name"]).first()
        if not publisher:
            publisher = Publisher(**p_data)
            db.session.add(publisher)
            print(f"Added publisher: {p_data['name']}")
        publishers.append(publisher)
    db.session.commit()

    # 3. Create Authors
    from datetime import date
    authors = []
    author_data = [
        {"first_name": "Martin", "last_name": "Fowler", "birth_date": date(1963, 1, 1)},
        {"first_name": "Robert", "last_name": "Martin", "birth_date": date(1952, 1, 1)},
        {"first_name": "Eric", "last_name": "Evans", "birth_date": date(1965, 1, 1)}
    ]
    for a_data in author_data:
        author = Author.query.filter_by(first_name=a_data["first_name"], last_name=a_data["last_name"]).first()
        if not author:
            author = Author(**a_data)
            db.session.add(author)
            print(f"Added author: {a_data['first_name']} {a_data['last_name']}")
        authors.append(author)
    db.session.commit()

    # 4. Create Books
    book_data = [
        {
            "title": "Refactoring",
            "published_year": 1999,
            "isbn": "9780201485677",
            "publisher": publishers[1],
            "authors": [authors[0]]
        },
        {
            "title": "Clean Code",
            "published_year": 2008,
            "isbn": "9780132350884",
            "publisher": publishers[1],
            "authors": [authors[1]]
        },
        {
            "title": "Domain-Driven Design",
            "published_year": 2003,
            "isbn": "9780321125217",
            "publisher": publishers[1],
            "authors": [authors[2]]
        }
    ]
    for b_data in book_data:
        book = Book.query.filter_by(isbn=b_data["isbn"]).first()
        if not book:
            book = Book(
                title=b_data["title"],
                published_year=b_data["published_year"],
                isbn=b_data["isbn"],
                publisher=b_data["publisher"]
            )
            book.authors = b_data["authors"]
            db.session.add(book)
            print(f"Added book: {b_data['title']}")
    db.session.commit()

    # 5. Create Admin User
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com"
        )
        admin_user.password = "admin123"
        admin_user.roles.append(roles["admin"])
        db.session.add(admin_user)
        print("Added admin user: admin / admin123")
    db.session.commit()

    print("Seeding complete!")

if __name__ == '__main__':
    # Spuštění vývojového serveru (pro produkci použijte WSGI server jako Gunicorn)
    app.run(host='0.0.0.0', port=5000)  # Naslouchání na všech rozhraních
