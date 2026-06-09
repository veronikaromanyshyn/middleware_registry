import sqlite3


def create_database():
    connection = sqlite3.connect("registry.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deployment_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_name TEXT NOT NULL,
            version TEXT,
            target_device TEXT,
            installation_method TEXT,
            demo_example TEXT,
            dependencies TEXT,
            launch_result TEXT,
            problems TEXT,
            educational_value INTEGER,
            status TEXT,
            logo_image TEXT,
            installation_image TEXT,
            launch_image TEXT,
            demo_image TEXT
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Базу даних успішно створено!")