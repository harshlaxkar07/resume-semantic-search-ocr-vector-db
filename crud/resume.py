from app.database import get_database


def create_resume(
    original_filename: str,
    stored_filename: str,
    pdf_path: str,
    raw_text: str,
) -> int:
    """
    Insert resume details into database.
    """

    query = """
        INSERT INTO resumes
        (
            original_filename,
            stored_filename,
            pdf_path,
            raw_text
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    """

    with get_database() as db:

        db.cursor.execute(
            query,
            (
                original_filename,
                stored_filename,
                pdf_path,
                raw_text,
            ),
        )

        resume_id = db.cursor.lastrowid

    return resume_id


def get_resume_by_id(
    resume_id: int,
) -> dict | None:
    """
    Fetch resume by ID.
    """

    query = """
        SELECT
            id,
            original_filename,
            stored_filename,
            pdf_path,
            raw_text,
            uploaded_at
        FROM resumes
        WHERE id = %s
    """

    with get_database() as db:

        db.cursor.execute(
            query,
            (resume_id,),
        )

        return db.cursor.fetchone()


def get_all_resumes() -> list[dict]:
    """
    Fetch all resumes.

    Used later for search testing.
    """

    query = """
        SELECT
            id,
            original_filename,
            stored_filename,
            pdf_path,
            raw_text,
            uploaded_at
        FROM resumes
        ORDER BY id DESC
    """

    with get_database() as db:

        db.cursor.execute(query)

        return db.cursor.fetchall()