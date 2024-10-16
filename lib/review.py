from __init__ import CURSOR, CONN
from employee import Employee

class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year  # This will call the year setter for validation
        self.summary = summary  # This will call the summary setter for validation
        self.employee_id = employee_id  # This will call the employee_id setter for validation

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            f"Employee: {self.employee_id}>"
        )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer.")
        if value < 2000:
            raise ValueError("Year must be greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int) or Employee.find_by_id(value) is None:
            raise ValueError("Invalid employee ID.")
        self._employee_id = value

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT NOT NULL,
            summary TEXT NOT NULL,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances."""
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert or update the current Review object in the database."""
        if self.id is None:  # New review, insert into DB
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid  # Set the id to the last inserted row's id
            Review.all[self.id] = self  # Save in the local dictionary
        else:  # Existing review, update in DB
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save it to the database."""
        review = cls(year, summary, employee_id)
        review.save()  # Save to the database
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        if row is None:
            return None  # Handle case where row is None

        review = cls.all.get(row[0])
        if review:
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3], id=row[0])
            cls.all[review.id] = review

        return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance by its ID."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row)  # Handle row creation

    def update(self):
        """Update the corresponding table row for the current Review instance."""
        if self.id is None:
            raise ValueError("Cannot update a review that has not been saved.")
        self.save()  # This will handle the update

    def delete(self):
        """Delete the corresponding table row and local dictionary entry."""
        if self.id is None:
            raise ValueError("Cannot delete a review that has not been saved.")

        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Review.all[self.id]  # Remove from local dictionary
        self.id = None  # Reset the ID after deletion

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances."""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
