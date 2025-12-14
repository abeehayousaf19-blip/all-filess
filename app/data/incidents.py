def insert_incidents(conn, date, incident_type, severity, status, description, reported_by=None):
    cursor = conn.cursor()

    query = """
       INSERT INTO cyber_incidents
       (date, incident_type, severity, status, description, reported_by)
       VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (date, incident_type, severity, status, description, reported_by))
    conn.commit()

    return cursor.lastrowid
