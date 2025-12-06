import sqlite3
from pathlib import Path


def main():
    db_path = Path(__file__).resolve().parent.parent / "database" / "result_tracker.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("Students:")
    for row in cur.execute("SELECT student_id, name, roll_no FROM students ORDER BY student_id"):
        print(row)

    print("\nResults:")
    for row in cur.execute(
        "SELECT result_id, student_id, subject_id, marks_obtained, grade, semester, published "
        "FROM results ORDER BY result_id"
    ):
        print(row)

    conn.close()


if __name__ == "__main__":
    main()

